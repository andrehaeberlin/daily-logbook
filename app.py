# file: app.py
"""
Diário de Bordo Contemporâneo v1.1 — A4 Landscape
Atualizações:
  - Intenção do dia adicionada ao cabeçalho.
  - Kanban substituído por Rastreador de Status na Captura.
  - Priorização focada no método Ivy Lee (3 itens) + Pomodoros.
  - Margem lateral nas Notas para Tags.
  - Metacognição simplificada.
  - Hábitos movidos para o rodapé.
"""

import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape 
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

version = "1.1-A4"

# ── Configurações de Página ───────────────────────────────────────────────────
PAGE_W, PAGE_H = landscape(A4)   # 297 x 210 mm  →  ~842 x 595 pt
MARGIN    = 8 * mm               # Margem para aproveitar bem o papel
CONTENT_W = PAGE_W - 2 * MARGIN

# ── Paleta de Cores ───────────────────────────────────────────────────────────
BLUE         = colors.HexColor("#2980b9")
BLUE_DARK    = colors.HexColor("#1a5276")
BLUE_LIGHT   = colors.HexColor("#ddeef8")
ORANGE       = colors.HexColor("#e67e22")
ORANGE_LIGHT = colors.HexColor("#fef0e3")
GREEN        = colors.HexColor("#27ae60")
GREEN_LIGHT  = colors.HexColor("#e6f9ee")
GRAY         = colors.HexColor("#c0c7cc")
GRAY_DARK    = colors.HexColor("#7f8c8d")
PANEL        = colors.HexColor("#fafafa")
TEXT         = colors.HexColor("#2c3e50")
REFL         = colors.HexColor("#f0f6fc")
LINE         = colors.HexColor("#e2e6ea")
WHITE        = colors.white

# ── Fontes ────────────────────────────────────────────────────────────────────
F  = "Helvetica"
FB = "Helvetica-Bold"
FI = "Helvetica-Oblique"

# ═══════════════════════════════════════════════════════════════════════════════
# Funções Auxiliares (Primitivas)
# ═══════════════════════════════════════════════════════════════════════════════
# Essas funções ajudam a desenhar elementos repetitivos sem poluir o código.

def box(c, x, y, w, h, title, fs=8, bar_h=15, color=BLUE):
    """Desenha uma caixa com uma barra de título colorida."""
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.5)
    c.setFillColor(PANEL)
    c.rect(x, y - h, w, h, fill=1, stroke=1)
    
    # Barra de título
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.rect(x, y - bar_h, w, bar_h, fill=1, stroke=0)
    
    # Texto do título
    c.setFillColor(WHITE)
    c.setFont(FB, fs)
    c.drawString(x + 5, y - bar_h + 4, title.upper())
    return y - bar_h

def softlines(c, x, y_top, w, h, lh=18, tag_margin=0):
    """Desenha linhas suaves. Se tag_margin > 0, cria uma linha vertical para tags."""
    c.setDash(1, 0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    n = int(h / lh)
    
    # Desenha a linha vertical para a área de Tags (se solicitado)
    if tag_margin > 0:
        c.setStrokeColor(GRAY)
        c.setDash(2, 2)
        c.line(x + tag_margin, y_top, x + tag_margin, y_top - (n * lh))
        c.setDash(1, 0) # Reseta o pontilhado
        c.setStrokeColor(LINE)

    # Desenha as linhas horizontais
    for i in range(1, n + 1):
        c.line(x + 5, y_top - i * lh, x + w - 5, y_top - i * lh)

def cb(c, x, y, size=9):
    """Desenha um checkbox quadrado."""
    c.setStrokeColor(GRAY_DARK)
    c.setLineWidth(0.7)
    c.setFillColor(WHITE)
    c.rect(x, y, size, size, fill=1, stroke=1)

def energy_bar(c, x, y, segments=5, seg_w=15, seg_h=10):
    """Desenha a barra de energia segmentada."""
    for i in range(segments):
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.7)
        c.setFillColor(WHITE)
        c.rect(x + i * (seg_w + 1), y, seg_w, seg_h, fill=1, stroke=1)

# ═══════════════════════════════════════════════════════════════════════════════
# Construtores das Seções do PDF
# ═══════════════════════════════════════════════════════════════════════════════

def draw_header(c, cursor):
    """Desenha o cabeçalho superior (Título, Data, Intenção)."""
    y = cursor

    # ── Faixa azul de título principal
    title_bar_h = 24
    c.setFillColor(BLUE)
    c.rect(MARGIN, y - title_bar_h, CONTENT_W, title_bar_h, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont(FB, 14)
    c.drawString(MARGIN + 6, y - title_bar_h + 7, "DIÁRIO DE BORDO")

    c.setFont(FB, 10)
    label = "DIA #"
    lw = c.stringWidth(label, FB, 10)
    c.drawString(MARGIN + CONTENT_W - 90, y - title_bar_h + 7, label)
    c.setStrokeColor(WHITE)
    c.setLineWidth(0.8)
    c.line(MARGIN + CONTENT_W - 90 + lw + 3, y - title_bar_h + 9, MARGIN + CONTENT_W - 6, y - title_bar_h + 9)

    y -= title_bar_h

    # ── Linha 1: DATA | ENERGIA | HIGIENE DIGITAL
    meta_h = 18
    c.setFillColor(BLUE_LIGHT)
    c.rect(MARGIN, y - meta_h, CONTENT_W, meta_h, fill=1, stroke=0)

    my = y - meta_h + 5
    mx = MARGIN + 6
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(mx, my, "DATA:")
    mx += c.stringWidth("DATA:", FB, 8) + 4
    c.setFont(F, 8)
    c.setFillColor(TEXT)
    c.drawString(mx, my, "____/____/_______")

    ex = MARGIN + CONTENT_W * 0.25
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(ex, my, "ENERGIA:")
    energy_bar(c, ex + c.stringWidth("ENERGIA:", FB, 8) + 4, my - 1, seg_w=14, seg_h=10)

    hx = MARGIN + CONTENT_W * 0.52
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx, my, "HIGIENE DIGITAL:")
    hx += c.stringWidth("HIGIENE DIGITAL:", FB, 8) + 6
    for label in ["OFF", "MESA LIMPA"]:
        cb(c, hx, my - 1, size=9)
        c.setFont(F, 8)
        c.setFillColor(TEXT)
        c.drawString(hx + 12, my, label)
        hx += c.stringWidth(label, F, 8) + 24

    y -= meta_h

    # ── Linha 2: INTENÇÃO DO DIA (A sua nova sugestão)
    int_h = 18
    c.setFillColor(colors.HexColor("#f5f8fa"))
    c.rect(MARGIN, y - int_h, CONTENT_W, int_h, fill=1, stroke=0)
    
    iy = y - int_h + 5
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(MARGIN + 6, iy, "INTENÇÃO DO DIA:")
    c.setFont(FI, 8)
    c.setFillColor(GRAY_DARK)
    c.drawString(MARGIN + 6 + c.stringWidth("INTENÇÃO DO DIA: ", FB, 8), iy, "(Palavra/frase que define as emoções)")
    
    c.setStrokeColor(LINE)
    c.line(MARGIN + 240, iy - 2, MARGIN + CONTENT_W - 6, iy - 2)

    return y - int_h

def draw_sections(c, cursor):
    """Desenha a área central de planejamento e execução."""
    GAP = 10
    COL_H = 360 # Altura central

    lw = (CONTENT_W - GAP) * 0.50 # Coluna A: 50%
    rw = (CONTENT_W - GAP) * 0.50 # Coluna B: 50%

    lx = MARGIN
    rx = MARGIN + lw + GAP

    # ── Coluna A: Captura e Rastreador ────────────────────────────────────────
    # Usando lh=24 para dar mais respiro na escrita manual (Brain Dump)
    yi_cap = box(c, lx, cursor, lw, COL_H, "1. Captura & Status (. A Fazer | / Em Curso | X Feito | -> Adiado)", fs=8)
    
    c.setDash(2, 3)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.45)
    linhas_captura = int((COL_H - 15) / 24)
    for i in range(linhas_captura):
        yy = yi_cap - (i + 1) * 24
        # Desenha um pequeno colchete para colocar o status
        c.setFont(F, 8)
        c.setFillColor(GRAY_DARK)
        c.drawString(lx + 5, yy + 3, "[   ]")
        # Linha para escrever
        c.line(lx + 22, yy, lx + lw - 5, yy)
    c.setDash()

    # ── Coluna B: Priorização (Ivy Lee) & Foco de Ouro ────────────────────────
    prio_h = 140
    yi_prio = box(c, rx, cursor, rw, prio_h, "2. Priorização & Foco de Ouro (80/20)", fs=8, color=ORANGE)
    
    # Box do Foco de Ouro (A Tarefa Mais Importante)
    fo_x = rx + 5
    fo_y = yi_prio - 45
    fo_w = rw - 10
    c.setFillColor(ORANGE_LIGHT)
    c.setStrokeColor(ORANGE)
    c.rect(fo_x, fo_y, fo_w, 40, fill=1, stroke=1)
    
    c.setFont(FB, 8)
    c.setFillColor(ORANGE)
    c.drawString(fo_x + 5, fo_y + 28, "1. FOCO DE OURO (Move o ponteiro):")
    c.setStrokeColor(ORANGE)
    c.line(fo_x + 5, fo_y + 22, fo_x + fo_w - 5, fo_y + 22)
    
    # Adicionando os Pomodoros ligados ao Foco de Ouro
    c.setFont(FB, 7.5)
    c.drawString(fo_x + 5, fo_y + 6, "POMODOROS:")
    px = fo_x + c.stringWidth("POMODOROS:", FB, 7.5) + 12
    for _ in range(8): # 8 Pomodoros para o Foco
        cb(c, px, fo_y + 5, size=8)
        px += 12

    # Prioridade 2 e 3 (Reduzindo a ansiedade)
    c.setFont(FB, 8)
    c.setFillColor(GRAY_DARK)
    c.drawString(rx + 5, fo_y - 20, "2. Prioridade Secundária:")
    c.setStrokeColor(LINE)
    c.line(rx + 5, fo_y - 25, rx + rw - 5, fo_y - 25)

    c.drawString(rx + 5, fo_y - 50, "3. Prioridade Secundária:")
    c.line(rx + 5, fo_y - 55, rx + rw - 5, fo_y - 55)

    # ── Coluna B: Notas Flexíveis com Tags ────────────────────────────────────
    notas_y = cursor - prio_h - GAP
    notas_h = COL_H - prio_h - GAP
    yi_n = box(c, rx, notas_y, rw, notas_h, "3. Notas Flexíveis & Fluxo", fs=8, color=BLUE_DARK)
    
    # Subtítulos da margem
    c.setFont(FI, 7)
    c.setFillColor(GRAY_DARK)
    c.drawString(rx + 5, yi_n - 12, "Tags (@)")
    c.drawString(rx + 45, yi_n - 12, "Anotações / Ideias / Bloqueios")

    # Linhas com a margem mágica (40 pontos da esquerda)
    softlines(c, rx, yi_n - 15, rw, notas_h - 20, lh=20, tag_margin=35)

    return cursor - COL_H - GAP

def draw_reflection(c, cursor):
    """Desenha a área de Metacognição simplificada e o próximo dia."""
    refl_h = 80
    GAP = 10  # ⬅️ ADICIONAMOS A VARIÁVEL AQUI PARA ESTA FUNÇÃO CONHECÊ-LA
    
    box(c, MARGIN, cursor, CONTENT_W, refl_h, "4. Fechamento — Metacognição", fs=8)
    inner_y = cursor - 15

    cells_w = CONTENT_W * 0.74
    cell_w  = (cells_w - 10) / 3
    cell_h  = refl_h - 18
    gap_c   = 4

    # Gatilhos mais diretos conforme sua sugestão
    cells = [
        ("O QUE FUNCIONOU?", "Fatos e vitórias de hoje"),
        ("ONDE TRAVEI?", "Causas e distrações"),
        ("AJUSTE PARA AMANHÃ:", "O que aprendi e vou mudar"),
    ]

    for i, (title, subtitle) in enumerate(cells):
        cx = MARGIN + 4 + i * (cell_w + gap_c)
        c.setFillColor(REFL)
        c.setStrokeColor(BLUE)
        c.rect(cx, inner_y - cell_h, cell_w, cell_h, fill=1, stroke=1)

        c.setFillColor(BLUE)
        c.rect(cx, inner_y - 14, cell_w, 14, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(FB, 8)
        tw = c.stringWidth(title, FB, 8)
        c.drawString(cx + (cell_w - tw) / 2, inner_y - 10, title)

        c.setFont(FI, 7)
        c.setFillColor(GRAY_DARK)
        c.drawString(cx + 5, inner_y - 24, subtitle)
        c.setStrokeColor(GRAY)
        c.line(cx + 5, inner_y - 28, cx + cell_w - 5, inner_y - 28)

        softlines(c, cx, inner_y - 30, cell_w, cell_h - 32, lh=15)

    # ── "Amanhã começa com:"
    tmr_x = MARGIN + 4 + 3 * (cell_w + gap_c) + 2
    tmr_w = CONTENT_W - (tmr_x - MARGIN) - 4
    
    c.setFillColor(BLUE_LIGHT)
    c.setStrokeColor(BLUE_DARK)
    c.rect(tmr_x, inner_y - cell_h, tmr_w, cell_h, fill=1, stroke=1)

    c.setFillColor(BLUE_DARK)
    c.rect(tmr_x, inner_y - 14, tmr_w, 14, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FB, 8)
    c.drawString(tmr_x + 5, inner_y - 10, "AMANHÃ COMEÇA COM:")

    softlines(c, tmr_x, inner_y - 14, tmr_w, cell_h - 14, lh=18)

    return cursor - refl_h - GAP

def draw_habits_and_footer(c, cursor):
    """Atualizado: Adicionado rastreador de Café junto aos Hábitos."""
    
    # ── Linha de hábitos no rodapé
    hab_h = 16
    c.setFillColor(colors.HexColor("#f5f8fa"))
    c.rect(MARGIN, cursor - hab_h, CONTENT_W, hab_h, fill=1, stroke=0)
    
    c.setStrokeColor(GRAY)
    c.line(MARGIN, cursor, MARGIN + CONTENT_W, cursor)
    c.line(MARGIN, cursor - hab_h, MARGIN + CONTENT_W, cursor - hab_h)

    hx = MARGIN + 6
    hy = cursor - hab_h + 4
    c.setFont(FB, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "HÁBITOS:")
    hx += c.stringWidth("HÁBITOS:", FB, 7.5) + 10

    # Hábitos binários (Sim/Não)
    for label in ["Exercício", "Leitura", "Estudos", "Sono"]:
        cb(c, hx, hy - 1, size=8)
        c.setFont(F, 7.5)
        c.setFillColor(TEXT)
        c.drawString(hx + 11, hy, label)
        hx += c.stringWidth(label, F, 7.5) + 20

    # NOVO: Rastreador de CAFÉ
    c.setFont(FB, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "CAFÉ:")
    hx += c.stringWidth("CAFÉ:", FB, 7.5) + 5
    for _ in range(4): # 4 Copos de café
        cb(c, hx, hy - 1, size=8)
        hx += 12
    
    hx += 10 # Espaço extra antes da água

    # Rastreador de ÁGUA
    c.setFont(FB, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "ÁGUA:")
    hx += c.stringWidth("ÁGUA:", FB, 7.5) + 5
    for _ in range(8):
        cb(c, hx, hy - 1, size=8)
        hx += 12

    cursor -= (hab_h + 8)

    # ── Citação Final
    quote = ('"Sem reflexão, a produtividade é apenas um ciclo mecânico."')
    c.setFont(FI, 9) 
    c.setFillColor(GRAY_DARK)
    qw = c.stringWidth(quote, FI, 9)
    c.drawString(MARGIN + CONTENT_W / 2 - qw / 2, cursor - 10, quote)

# ═══════════════════════════════════════════════════════════════════════════════
# Motor de Geração
# ═══════════════════════════════════════════════════════════════════════════════

def gerar_pdf(pdf_path: str) -> None:
    """Função principal que orquestra a geração do arquivo PDF."""
    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
    c.setTitle(f"Diário de Bordo Contemporâneo v{version}")

    # Começamos a desenhar de cima para baixo
    cursor = PAGE_H - MARGIN
    cursor = draw_header(c, cursor)
    cursor -= 5                        
    cursor = draw_sections(c, cursor)
    cursor = draw_reflection(c, cursor)
    draw_habits_and_footer(c, cursor)

    c.save()
    print(f"Sucesso! PDF gerado em: {os.path.abspath(pdf_path)}")

if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else f"diario_de_bordo_v{version}.pdf"
    try:
        gerar_pdf(output)
    except Exception as e:
        print(f"Ops! Erro ao gerar PDF: {e}", file=sys.stderr)
        sys.exit(1)