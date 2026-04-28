# file: app.py
"""
Diário de Bordo Contemporâneo v1.1.11 — A4 Landscape
Atualizações:
  - Refatoração: Princípio DRY aplicado com a função draw_checkbox_group.
  - Nova Feature: Adicionado indicador de Humor (Mood Tracker) com 5 faces.
  - Layout: Reordenação da barra de meta e ajuste de espaçamentos horizontais.
  - Nova Feature: Adicionado campos de Entrada e Saída.
  - Texto: Remoção de placeholder na linha de inspiração e linha elástica.
  - Layout: Campo de DATA movido para o cabeçalho principal.
"""

import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

version = "1.1.11-A4"

# ── Configurações de Página ───────────────────────────────────────────────────
PAGE_W, PAGE_H = landscape(A4)
MARGIN = 8 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

# ── Paleta de Cores ───────────────────────────────────────────────────────────
BLUE = colors.HexColor("#2980b9")
BLUE_DARK = colors.HexColor("#1a5276")
BLUE_LIGHT = colors.HexColor("#ddeef8")
ORANGE = colors.HexColor("#e67e22")
ORANGE_LIGHT = colors.HexColor("#fef0e3")
GREEN = colors.HexColor("#27ae60")
GRAY = colors.HexColor("#c0c7cc")
GRAY_DARK = colors.HexColor("#7f8c8d")
GRAY_LIGHT = colors.HexColor("#f4f6f7")
PANEL = colors.HexColor("#fafafa")
TEXT = colors.HexColor("#2c3e50")
REFL = colors.HexColor("#f0f6fc")
LINE = colors.HexColor("#e2e6ea")
WHITE = colors.white

# ── Fontes ────────────────────────────────────────────────────────────────────
F = "Helvetica"
FB = "Helvetica-Bold"
FI = "Helvetica-Oblique"

# ═══════════════════════════════════════════════════════════════════════════════
# Funções Auxiliares (Primitivas)
# ═══════════════════════════════════════════════════════════════════════════════

def box(c, x, y, w, h, title, fs=8, bar_h=15, color=BLUE, bg_color=PANEL):
    """Desenha as caixas principais com um cabeçalho colorido."""
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.5)
    c.setFillColor(bg_color)
    c.rect(x, y - h, w, h, fill=1, stroke=1)

    c.setFillColor(color)
    c.setStrokeColor(color)
    c.rect(x, y - bar_h, w, bar_h, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont(FB, fs)
    c.drawString(x + 5, y - bar_h + 4, title.upper())
    return y - bar_h

def softlines(c, x, y_top, w, h, lh=18, tag_margin=0, dashed=False):
    """Desenha as linhas horizontais para anotações."""
    n = int(h / lh)

    if tag_margin > 0:
        c.setStrokeColor(GRAY)
        c.setLineWidth(0.8)
        c.setDash(1, 0)
        c.line(x + tag_margin, y_top, x + tag_margin, y_top - (n * lh))

    if dashed:
        c.setDash(1, 3)
    else:
        c.setDash(1, 0)

    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)

    for i in range(1, n + 1):
        c.line(x + 5, y_top - i * lh, x + w - 5, y_top - i * lh)

    c.setDash(1, 0)

def cb(c, x, y, size=10):
    """Desenha uma única caixa de seleção (checkbox)."""
    c.setStrokeColor(GRAY_DARK)
    c.setLineWidth(0.7)
    c.setFillColor(WHITE) 
    c.rect(x, y, size, size, fill=1, stroke=1)

def draw_checkbox_group(c, start_x, y, count, spacing=12, size=10):
    """
    Função DRY: Desenha uma sequência horizontal de caixas de seleção.
    Retorna a posição x final logo após o grupo gerado.
    """
    px = start_x
    for _ in range(count):
        cb(c, px, y, size=size)
        px += spacing
    return px

def energy_bar(c, x, y, segments=5, seg_w=15, seg_h=10):
    """Desenha a barra de energia subdividida."""
    for i in range(segments):
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.7)
        c.setFillColor(WHITE)
        c.rect(x + i * (seg_w + 1), y, seg_w, seg_h, fill=1, stroke=1)

def draw_face(c, x, y, r, mood):
    """
    Desenha uma carinha vetorizada. moods: 
    'very_happy', 'happy', 'neutral', 'sad', 'very_sad'
    """
    c.setStrokeColor(GRAY_DARK)
    c.setLineWidth(0.7)
    c.setFillColor(WHITE)
    c.circle(x, y, r, fill=1, stroke=1)
    
    c.setFillColor(GRAY_DARK)
    c.setStrokeColor(GRAY_DARK)
    
    if mood == 'very_sad':
        c.setLineWidth(0.8)
        c.line(x - r*0.5, y + r*0.35, x - r*0.2, y + r*0.15)
        c.line(x - r*0.5, y - r*0.05, x - r*0.2, y + r*0.15)
        c.line(x + r*0.5, y + r*0.35, x + r*0.2, y + r*0.15)
        c.line(x + r*0.5, y - r*0.05, x + r*0.2, y + r*0.15)
    elif mood == 'happy':
        c.setLineWidth(0.8)
        c.arc(x - r*0.55, y + r*0.1, x - r*0.15, y + r*0.4, 0, 180)
        c.arc(x + r*0.15, y + r*0.1, x + r*0.55, y + r*0.4, 0, 180)
    else:
        c.circle(x - r*0.35, y + r*0.2, r*0.12, fill=1, stroke=0)
        c.circle(x + r*0.35, y + r*0.2, r*0.12, fill=1, stroke=0)
    
    c.setLineWidth(0.8)
    if mood == 'very_happy':
        c.wedge(x - r*0.5, y - r*0.6, x + r*0.5, y + r*0.1, 180, 180, fill=1, stroke=0)
    elif mood == 'happy':
        c.arc(x - r*0.5, y - r*0.4, x + r*0.5, y + r*0.1, 180, 180)
    elif mood == 'neutral':
        c.line(x - r*0.4, y - r*0.2, x + r*0.4, y - r*0.2)
    elif mood == 'sad':
        c.arc(x - r*0.5, y - r*0.5, x + r*0.5, y - r*0.1, 0, 180)
    elif mood == 'very_sad':
        c.arc(x - r*0.4, y - r*0.5, x + r*0.4, y - r*0.2, 0, 180)

# ═══════════════════════════════════════════════════════════════════════════════
# Construtores das Seções do PDF
# ═══════════════════════════════════════════════════════════════════════════════

def draw_header(c, cursor):
    """Monta o cabeçalho azul com metadados do dia."""
    y = cursor

    # ── Faixa azul de título ─────────────────────────────────────────────────
    title_bar_h = 24
    c.setFillColor(BLUE)
    c.rect(MARGIN, y - title_bar_h, CONTENT_W, title_bar_h, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont(FB, 14)
    c.drawString(MARGIN + 6, y - title_bar_h + 7, f"DIÁRIO DE BORDO — v{version}")

    # --- Área dos Números (Direita) ---
    c.setFont(FB, 10)
    
    label_dia = "DIA #"
    dia_x = MARGIN + CONTENT_W - 110
    c.setFillColor(WHITE)
    c.drawString(dia_x, y - title_bar_h + 8, label_dia)
    
    box_dia_x = dia_x + c.stringWidth(label_dia, FB, 10) + 4
    c.setFillColor(WHITE)
    c.rect(box_dia_x, y - title_bar_h + 5, 70, 14, fill=1, stroke=0)

    label_sem = "SEMANA #"
    sem_x = MARGIN + CONTENT_W - 220 
    c.setFillColor(WHITE)
    c.drawString(sem_x, y - title_bar_h + 8, label_sem)
    
    box_sem_x = sem_x + c.stringWidth(label_sem, FB, 10) + 4
    c.setFillColor(WHITE)
    c.rect(box_sem_x, y - title_bar_h + 5, 35, 14, fill=1, stroke=0)

    # ✨ Nova Feature: DATA no cabeçalho
    label_data = "DATA:"
    data_x = MARGIN + CONTENT_W - 350
    c.setFillColor(WHITE)
    c.drawString(data_x, y - title_bar_h + 8, label_data)
    
    box_data_x = data_x + c.stringWidth(label_data, FB, 10) + 4
    c.setFillColor(WHITE)
    # Crio uma caixinha um pouco maior para caber uma data no formato DD/MM/AAAA
    c.rect(box_data_x, y - title_bar_h + 5, 80, 14, fill=1, stroke=0)

    y -= title_bar_h

    # ── Linha de meta: HORÁRIOS | ENERGIA | SONO | HUMOR | 5S ──────
    meta_h = 18
    c.setFillColor(BLUE_LIGHT)
    c.rect(MARGIN, y - meta_h, CONTENT_W, meta_h, fill=1, stroke=0)
    
    my = y - meta_h + 5
    
    # 1. HORÁRIOS (Entrada e Saída) -> Agora assume a primeira posição à esquerda!
    hx_time = MARGIN + 6
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx_time, my, "ENTRADA:")
    hx_time += c.stringWidth("ENTRADA:", FB, 8) + 4
    c.setFont(F, 8)
    c.setFillColor(TEXT)
    c.drawString(hx_time, my, "___ : ___")

    hx_time += c.stringWidth("___ : ___", F, 8) + 12 # Espaço extra entre os horários
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx_time, my, "SAÍDA:")
    hx_time += c.stringWidth("SAÍDA:", FB, 8) + 4
    c.setFont(F, 8)
    c.setFillColor(TEXT)
    c.drawString(hx_time, my, "___ : ___")

    # 2. ENERGIA -> Empurrado para 22% da tela
    ex = MARGIN + CONTENT_W * 0.22
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(ex, my, "ENERGIA:")
    energy_bar(c, ex + c.stringWidth("ENERGIA:", FB, 8) + 4, my - 1, seg_w=14, seg_h=10)

    # 3. SONO -> Empurrado para 40% da tela
    sx = MARGIN + CONTENT_W * 0.40
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(sx, my, "SONO:")
    sx += c.stringWidth("SONO:", FB, 8) + 4
    c.setFillColor(WHITE)
    c.setStrokeColor(GRAY_DARK)
    c.setLineWidth(0.5)
    c.rect(sx, my - 2, 32, 11, fill=1, stroke=1)
    c.setFont(F, 8)
    c.setFillColor(TEXT)
    c.drawString(sx + 35, my, "h")

    # 4. HUMOR -> Empurrado para 55% da tela
    hx = MARGIN + CONTENT_W * 0.525
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx, my, "HUMOR:")
    hx += c.stringWidth("HUMOR:", FB, 8) + 12
    
    raio_rosto = 5.5
    moods = ['very_happy', 'happy', 'neutral', 'sad', 'very_sad']
    for mood in moods:
        draw_face(c, hx, my + 3, raio_rosto, mood)
        hx += 16

    # 5. 5S -> Empurrado para 72% da tela
    fx = MARGIN + CONTENT_W * 0.72
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(fx, my, "5S:")
    fx += c.stringWidth("5S:", FB, 8) + 6
    
    for label in ["OFF", "MESA", "COMPUTADOR", "CELULAR"]:
        cb(c, fx, my - 1, size=10)
        c.setFont(F, 8)
        c.setFillColor(TEXT)
        c.drawString(fx + 12, my, label)
        fx += c.stringWidth(label, F, 8) + 18 

    y -= meta_h

    # ── Linha de Inspiração ────────────────────────────────────────────────────
    int_h = 18
    c.setFillColor(colors.HexColor("#f5f8fa"))
    c.rect(MARGIN, y - int_h, CONTENT_W, int_h, fill=1, stroke=0)
    iy = y - int_h + 5
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    
    titulo_inspiracao = "INSPIRAÇÃO DO DIA:"
    c.drawString(MARGIN + 6, iy, titulo_inspiracao)
    
    inicio_linha = MARGIN + 6 + c.stringWidth(titulo_inspiracao, FB, 8) + 5
    
    c.setStrokeColor(LINE)
    c.line(inicio_linha, iy - 2, MARGIN + CONTENT_W - 6, iy - 2)
    
    return y - int_h

def draw_sections(c, cursor):
    """Monta o corpo do diário: Captura, Priorização e Notas."""
    GAP = 10
    COL_H = 360
    lw = (CONTENT_W - GAP) * 0.50
    rw = (CONTENT_W - GAP) * 0.50
    lx = MARGIN
    rx = MARGIN + lw + GAP

    yi_cap = box(
        c,
        lx,
        cursor,
        lw,
        COL_H,
        "1. Captura & Status (. A Fazer | / Em Curso | X Feito | -> Adiado)",
        fs=8,
    )
    c.setDash(2, 3)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.45)
    linhas_captura = int((COL_H - 15) / 18)
    for i in range(linhas_captura):
        yy = yi_cap - (i + 1) * 18
        c.setFont(F, 8)
        c.setFillColor(GRAY_DARK)
        c.drawString(lx + 5, yy + 3, "[   ]")
        c.line(lx + 22, yy, lx + lw - 5, yy)
    c.setDash()

    prio_h = 140
    yi_prio = box(
        c,
        rx,
        cursor,
        rw,
        prio_h,
        "2. Priorização & Foco de Ouro (80/20)",
        fs=8,
        color=ORANGE,
        bg_color=GRAY_LIGHT,
    )

    fo_x = rx + 5
    fo_y = yi_prio - 45
    fo_w = rw - 10
    
    # ── Tarefa 1: OURO 
    c.setFillColor(ORANGE_LIGHT)
    c.setStrokeColor(ORANGE)
    c.rect(fo_x, fo_y, fo_w, 40, fill=1, stroke=1)

    c.setFont(FB, 8)
    c.setFillColor(ORANGE)
    c.drawString(fo_x + 5, fo_y + 28, "1. OURO:")
    c.setStrokeColor(ORANGE)
    c.line(fo_x + 5, fo_y + 22, fo_x + fo_w - 5, fo_y + 22)

    c.setFont(FB, 7.5)
    c.drawString(fo_x + 5, fo_y + 8, "POMODOROS:")
    px = fo_x + c.stringWidth("POMODOROS:", FB, 7.5) + 12
    draw_checkbox_group(c, px, fo_y + 6, count=12)

    # ── Tarefa 2: Secundária
    c.setFont(FB, 8)
    c.setFillColor(GRAY_DARK)
    c.drawString(rx + 5, fo_y - 15, "2. Secundária:")
    c.setStrokeColor(LINE)
    c.line(rx + 5, fo_y - 20, rx + rw - 5, fo_y - 20)

    c.setFont(FB, 7.5)
    c.drawString(rx + 5, fo_y - 32, "POMODOROS:")
    px = rx + 5 + c.stringWidth("POMODOROS:", FB, 7.5) + 12
    draw_checkbox_group(c, px, fo_y - 34, count=9)

    # ── Tarefa 3: Secundária
    c.setFont(FB, 8)
    c.setFillColor(GRAY_DARK) 
    c.drawString(rx + 5, fo_y - 55, "3. Secundária:")
    c.setStrokeColor(LINE)
    c.line(rx + 5, fo_y - 60, rx + rw - 5, fo_y - 60)

    c.setFont(FB, 7.5)
    c.drawString(rx + 5, fo_y - 72, "POMODOROS:")
    px = rx + 5 + c.stringWidth("POMODOROS:", FB, 7.5) + 12
    draw_checkbox_group(c, px, fo_y - 74, count=6)

    notas_y = cursor - prio_h - GAP
    notas_h = COL_H - prio_h - GAP
    yi_n = box(
        c, rx, notas_y, rw, notas_h, "3. Notas Flexíveis & Fluxo", fs=8, color=BLUE_DARK
    )
    c.setFont(FI, 7)
    c.setFillColor(GRAY_DARK)
    c.drawString(rx + 5, yi_n - 12, "Tags (@)")
    c.drawString(rx + 60, yi_n - 12, "Anotações / Ideias / Bloqueios")

    softlines(c, rx, yi_n - 7, rw, notas_h - 20, lh=20, tag_margin=55)

    return cursor - COL_H - GAP

def draw_reflection(c, cursor):
    """Monta a seção final de metacognição."""
    refl_h = 80
    GAP = 10
    box(c, MARGIN, cursor, CONTENT_W, refl_h, "4. Fechamento — Metacognição", fs=8)
    inner_y = cursor - 15

    cells_w = CONTENT_W * 0.74
    cell_w = (cells_w - 10) / 3
    cell_h = refl_h - 18
    gap_c = 4

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

        softlines(c, cx, inner_y - 30, cell_w, cell_h - 32, lh=15, dashed=True)

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

    softlines(c, tmr_x, inner_y - 14, tmr_w, cell_h - 14, lh=18, dashed=True)

    return cursor - refl_h - GAP

def draw_habits_and_footer(c, cursor):
    """Monta a barra inferior de hábitos e a citação."""
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

    for label in ["Exercícios", "Devocional", "Leitura", "Estudos"]:
        cb(c, hx, hy - 1, size=10)
        c.setFont(F, 7.5)
        c.setFillColor(TEXT)
        c.drawString(hx + 11, hy, label)
        hx += c.stringWidth(label, F, 7.5) + 20

    # CAFÉ
    c.setFont(FB, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "CAFÉ:")
    hx += c.stringWidth("CAFÉ:", FB, 7.5) + 5
    hx = draw_checkbox_group(c, hx, hy - 1, count=8)

    hx += 12 # Espaço entre Café e Água
    
    # ÁGUA
    c.setFont(FB, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "ÁGUA:")
    hx += c.stringWidth("ÁGUA:", FB, 7.5) + 5
    hx = draw_checkbox_group(c, hx, hy - 1, count=16)

    hx += 12 # Espaço entre Água e Banheiro

    # BANHEIRO
    c.setFont(FB, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "BANHEIRO:")
    hx += c.stringWidth("BANHEIRO:", FB, 7.5) + 5
    hx = draw_checkbox_group(c, hx, hy - 1, count=10)

    cursor -= hab_h + 8

    quote = '"Sem reflexão, a produtividade é apenas um ciclo mecânico."'
    c.setFont(FI, 9)
    c.setFillColor(GRAY_DARK)
    qw = c.stringWidth(quote, FI, 9)
    c.drawString(MARGIN + CONTENT_W / 2 - qw / 2, cursor - 10, quote)

def draw_dot_grid(c):
    """Gera uma folha de fundo pontilhada."""
    c.showPage()
    c.setFillColor(GRAY)
    spacing = 5 * mm 

    for x in range(int(MARGIN), int(PAGE_W - MARGIN), int(spacing)):
        for y in range(int(MARGIN), int(PAGE_H - MARGIN), int(spacing)):
            c.circle(x, y, 0.4, fill=1, stroke=0)

# ═══════════════════════════════════════════════════════════════════════════════
# Motor de Geração
# ═══════════════════════════════════════════════════════════════════════════════

def gerar_pdf(pdf_path: str) -> None:
    """Orquestra as funções para desenhar as camadas do PDF."""
    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
    c.setTitle(f"Diário de Bordo Contemporâneo v{version}")

    cursor = PAGE_H - MARGIN
    cursor = draw_header(c, cursor)
    cursor -= 5
    cursor = draw_sections(c, cursor)
    cursor = draw_reflection(c, cursor)
    draw_habits_and_footer(c, cursor)

    draw_dot_grid(c)

    c.save()
    print(f"Sucesso! PDF gerado em: {os.path.abspath(pdf_path)}")

if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else f"diario_de_bordo_v{version}.pdf"
    try:
        gerar_pdf(output)
    except Exception as e:
        print(f"Ops! Erro ao gerar PDF: {e}", file=sys.stderr)
        sys.exit(1)