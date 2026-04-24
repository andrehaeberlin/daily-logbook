"""
Diário de Bordo Contemporâneo v3 — A3 Landscape
Correções de layout para impressão:
  - Layout reestruturado: Notas flexíveis abaixo de Captura e Kanban.
  - Largura das colunas 1, 2, 3 e 4 aumentadas.
  - Altura das linhas para escrita aumentadas (lh maior).
  - Número de linhas da reflexão (item 5) reduzidas naturalmente pelo espaçamento.
"""

import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ── Página ────────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = landscape(A3)   # 420 x 297 mm  →  ~1190 x 842 pt
MARGIN    = 10 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

# ── Paleta ────────────────────────────────────────────────────────────────────
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
# Primitivas
# ═══════════════════════════════════════════════════════════════════════════════

def box(c, x, y, w, h, title, fs=7.5, bar_h=14, color=BLUE):
    """Caixa com barra de título colorida. Retorna y logo abaixo da barra."""
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.5)
    c.setFillColor(PANEL)
    c.rect(x, y - h, w, h, fill=1, stroke=1)
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.rect(x, y - bar_h, w, bar_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FB, fs)
    c.drawString(x + 5, y - bar_h + 3.5, title.upper())
    return y - bar_h


def hlines(c, x, y_top, w, n, lh=16, prefix=False, color=LINE):
    """n linhas horizontais tracejadas para escrita."""
    c.setDash(2, 3)
    c.setStrokeColor(color)
    c.setLineWidth(0.45)
    for i in range(n):
        yy = y_top - (i + 1) * lh
        if prefix:
            c.setFont(FB, 7.5)
            c.setFillColor(GRAY_DARK)
            c.drawString(x + 4, yy + 4, f"{i + 1}.")
        c.line(x + (20 if prefix else 5), yy, x + w - 5, yy)
    c.setDash()


def softlines(c, x, y_top, w, h, lh=16):
    """Linhas suaves para áreas de escrita livre."""
    c.setDash(1, 0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    n = int(h / lh)
    for i in range(1, n + 1):
        c.line(x + 5, y_top - i * lh, x + w - 5, y_top - i * lh)


def cb(c, x, y, size=8):
    """Checkbox quadrado."""
    c.setStrokeColor(GRAY_DARK)
    c.setLineWidth(0.7)
    c.setFillColor(WHITE)
    c.rect(x, y, size, size, fill=1, stroke=1)


def energy_bar(c, x, y, segments=5, seg_w=14, seg_h=9):
    """Barra de energia segmentada — preenche à caneta."""
    for i in range(segments):
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.7)
        c.setFillColor(WHITE)
        c.rect(x + i * (seg_w + 1), y, seg_w, seg_h, fill=1, stroke=1)


# ═══════════════════════════════════════════════════════════════════════════════
# Header  (altura total ~52 pt)
# ═══════════════════════════════════════════════════════════════════════════════

def draw_header(c, cursor):
    y = cursor

    # ── Faixa azul de título ─────────────────────────────────────────────────
    title_bar_h = 22
    c.setFillColor(BLUE)
    c.rect(MARGIN, y - title_bar_h, CONTENT_W, title_bar_h, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont(FB, 13)
    c.drawString(MARGIN + 6, y - title_bar_h + 6, "DIÁRIO DE BORDO CONTEMPORÂNEO")

    # DIA # à direita
    c.setFont(FB, 9)
    label = "DIA #"
    lw = c.stringWidth(label, FB, 9)
    c.drawString(MARGIN + CONTENT_W - 90, y - title_bar_h + 6, label)
    c.setStrokeColor(WHITE)
    c.setLineWidth(0.8)
    c.line(MARGIN + CONTENT_W - 90 + lw + 3, y - title_bar_h + 8,
           MARGIN + CONTENT_W - 6,            y - title_bar_h + 8)

    y -= title_bar_h

    # ── Linha de meta: DATA | ENERGIA | HIGIENE ──────────────────────────────
    meta_h = 16
    c.setFillColor(BLUE_LIGHT)
    c.rect(MARGIN, y - meta_h, CONTENT_W, meta_h, fill=1, stroke=0)

    # DATA
    mx = MARGIN + 6
    my = y - meta_h + 4
    c.setFont(FB, 7.5)
    c.setFillColor(BLUE_DARK)
    c.drawString(mx, my, "DATA:")
    mx += c.stringWidth("DATA:", FB, 7.5) + 4
    c.setFont(F, 7.5)
    c.setFillColor(TEXT)
    c.drawString(mx, my, "____/____/_______")

    # ENERGIA
    ex = MARGIN + CONTENT_W * 0.25
    c.setFont(FB, 7.5)
    c.setFillColor(BLUE_DARK)
    c.drawString(ex, my, "ENERGIA:")
    energy_bar(c, ex + c.stringWidth("ENERGIA:", FB, 7.5) + 4,
               my - 1, seg_w=12, seg_h=8)

    # HIGIENE DIGITAL
    hx = MARGIN + CONTENT_W * 0.52
    c.setFont(FB, 7.5)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx, my, "HIGIENE DIGITAL:")
    hx += c.stringWidth("HIGIENE DIGITAL:", FB, 7.5) + 6
    for label in ["OFF", "MESA LIMPA", "HIDRATAÇÃO"]:
        cb(c, hx, my - 1, size=8)
        c.setFont(F, 7.5)
        c.setFillColor(TEXT)
        c.drawString(hx + 10, my, label)
        hx += c.stringWidth(label, F, 7.5) + 22

    y -= meta_h

    # ── Linha de hábitos ──────────────────────────────────────────────────────
    hab_h = 14
    c.setFillColor(colors.HexColor("#f5f8fa"))
    c.rect(MARGIN, y - hab_h, CONTENT_W, hab_h, fill=1, stroke=0)
    # borda inferior
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.4)
    c.line(MARGIN, y - hab_h, MARGIN + CONTENT_W, y - hab_h)

    hx = MARGIN + 6
    hy = y - hab_h + 3
    c.setFont(FB, 7)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "HÁBITOS:")
    hx += c.stringWidth("HÁBITOS:", FB, 7) + 8

    for label in ["Exercício", "Leitura", "Sem redes sociais", "8h sono"]:
        cb(c, hx, hy - 1, size=7)
        c.setFont(F, 7)
        c.setFillColor(TEXT)
        c.drawString(hx + 9, hy, label)
        hx += c.stringWidth(label, F, 7) + 20

    c.setFont(FB, 7)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "ÁGUA:")
    hx += c.stringWidth("ÁGUA:", FB, 7) + 5
    for _ in range(8):
        cb(c, hx, hy - 1, size=7)
        hx += 11

    y -= hab_h
    return y


# ═══════════════════════════════════════════════════════════════════════════════
# Seções Intermediárias (Itens 1, 2, 3 e 4)
# ═══════════════════════════════════════════════════════════════════════════════

def draw_sections(c, cursor):
    GAP       = 12
    COL_TOP_H = 260 # Altura das colunas superiores (1, 2 e 3)

    # Agora temos apenas 2 colunas superiores para acomodar (1, 2) e (3). 
    # Dessa forma elas ficam muito mais largas.
    lw = (CONTENT_W - GAP) * 0.42 # 42% para Captura e Priorização
    rw = (CONTENT_W - GAP) * 0.58 # 58% para o Kanban

    lx = MARGIN
    rx = MARGIN + lw + GAP

    # ── Coluna A: Captura ─────────────────────────────────────────────────────
    cap_h = 100
    yi = box(c, lx, cursor, lw, cap_h, "1. Captura  —  GTD / Caixa de Entrada", fs=7.5)
    # Espaçamento de linha aumentado de 15 para 20
    hlines(c, lx, yi, lw, 4, lh=20) 

    # ── Coluna A: Priorização ─────────────────────────────────────────────────
    prio_top  = cursor - cap_h - GAP
    prio_h    = COL_TOP_H - cap_h - GAP
    yi2 = box(c, lx, prio_top, lw, prio_h, "2. Priorização  —  Ivy Lee / 80-20", fs=7.5)
    # Espaçamento de linha aumentado de 15 para 22
    hlines(c, lx, yi2, lw, 4, lh=22, prefix=True)

    # Foco de Ouro + Pomodoros (rodapé da caixa de priorização)
    fo_h  = 50
    fo_y  = cursor - COL_TOP_H + 4
    fo_x  = lx + 5
    fo_w  = lw - 10

    c.setFillColor(ORANGE_LIGHT)
    c.setStrokeColor(ORANGE)
    c.setLineWidth(1.2)
    c.rect(fo_x, fo_y, fo_w, fo_h, fill=1, stroke=1)

    c.setFont(FB, 8)
    c.setFillColor(ORANGE)
    c.drawString(fo_x + 5, fo_y + fo_h - 11, "FOCO DE OURO  (Trabalho Profundo)")
    c.setStrokeColor(ORANGE)
    c.setLineWidth(0.8)
    c.line(fo_x + 5, fo_y + fo_h - 15, fo_x + fo_w - 5, fo_y + fo_h - 15)

    # Pomodoros
    c.setFont(FB, 7)
    c.setFillColor(ORANGE)
    c.drawString(fo_x + 5, fo_y + 28, "POMODOROS:")
    px = fo_x + 5 + c.stringWidth("POMODOROS:", FB, 7) + 5
    for g in range(3):
        for _ in range(4):
            cb(c, px, fo_y + 26, size=7)
            px += 10
        px += 5

    c.setFont(F, 7)
    c.setFillColor(GRAY_DARK)
    half = fo_w / 2
    c.drawString(fo_x + 5,        fo_y + 14, "Sessão 1: ______________")
    c.drawString(fo_x + 5 + half, fo_y + 14, "Sessão 2: ______________")

    # ── Coluna B: Kanban ──────────────────────────────────────────────────────
    yi_k = box(c, rx, cursor, rw, COL_TOP_H, "3. Kanban do Dia", fs=7.5, color=BLUE_DARK)

    kan_data = [
        ("A FAZER",  BLUE_LIGHT,   BLUE),
        ("EM CURSO", ORANGE_LIGHT, ORANGE),
        ("FEITO",    GREEN_LIGHT,  GREEN),
    ]
    kw    = (rw - 10) / 3
    kh    = COL_TOP_H - 22
    k_top = yi_k - 4

    for i, (lbl, bg, fg) in enumerate(kan_data):
        kx = rx + 4 + i * (kw + 1)

        c.setFillColor(bg)
        c.setStrokeColor(fg)
        c.setLineWidth(0.8)
        c.rect(kx, k_top - kh, kw, kh, fill=1, stroke=1)

        # header da raia
        c.setFillColor(fg)
        c.rect(kx, k_top - 13, kw, 13, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(FB, 7)
        tw = c.stringWidth(lbl, FB, 7)
        c.drawString(kx + (kw - tw) / 2, k_top - 10, lbl)

        # linhas internas - Espaçamento aumentado para lh=24 (era 18)
        c.setDash(1, 3)
        c.setStrokeColor(fg)
        c.setLineWidth(0.3)
        lines_n = int((kh - 14) / 24)
        for j in range(lines_n):
            yy = k_top - 14 - (j + 1) * 24
            c.line(kx + 4, yy, kx + kw - 4, yy)
        c.setDash()

    # ── Item 4: Notas Flexíveis ───────────────────────────────────────────────
    # Abaixo das colunas superiores, pegando 100% da largura
    notas_y = cursor - COL_TOP_H - GAP
    notas_h = 160

    yi_n = box(c, MARGIN, notas_y, CONTENT_W, notas_h, "4. Fluxo de Trabalho & Notas Flexíveis", fs=7.5)
    
    # Altura da linha (lh) aumentada para 22 (era 16)
    softlines(c, MARGIN, yi_n, CONTENT_W, notas_h - 16, lh=22) 
    
    c.setFont(FI, 6.5)
    c.setFillColor(GRAY_DARK)
    c.drawRightString(MARGIN + CONTENT_W - 5, notas_y - notas_h + 5,
                      "Ideias, bloqueios e insights do dia.")

    return notas_y - notas_h - GAP


# ═══════════════════════════════════════════════════════════════════════════════
# Reflexão  (seção final)
# ═══════════════════════════════════════════════════════════════════════════════

def draw_reflection(c, cursor):
    # Altura disponível até o rodapé (~20 pt)
    available = cursor - MARGIN - 20
    refl_h    = available

    box(c, MARGIN, cursor, CONTENT_W, refl_h,
        "5. Registro Reflexivo  —  Metacognição de Encerramento", fs=7.5)
    inner_y = cursor - 14

    # Proporções: 3 células reflexivas (75%) + "Amanhã" (25%)
    cells_w  = CONTENT_W * 0.74
    cell_w   = (cells_w - 10) / 3
    cell_h   = refl_h - 18
    gap_c    = 4

    cells = [
        ("FASE DESCRITIVA",         "O QUE aconteceu? (fatos e cronologia)"),
        ("FASE INTERPRETATIVA",     "POR QUÊ aconteceu? (causa e efeito)"),
        ("FASE CRÍTICA / SISTÊMICA","APRENDIZADO: O que mudo amanhã?"),
    ]

    for i, (title, subtitle) in enumerate(cells):
        cx = MARGIN + 4 + i * (cell_w + gap_c)

        c.setFillColor(REFL)
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.6)
        c.rect(cx, inner_y - cell_h, cell_w, cell_h, fill=1, stroke=1)

        # mini-header da célula
        c.setFillColor(BLUE)
        c.rect(cx, inner_y - 13, cell_w, 13, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(FB, 7.5)
        tw = c.stringWidth(title, FB, 7.5)
        c.drawString(cx + (cell_w - tw) / 2, inner_y - 10, title)

        c.setFont(FI, 6.5)
        c.setFillColor(GRAY_DARK)
        c.drawString(cx + 5, inner_y - 22, subtitle)

        c.setStrokeColor(GRAY)
        c.setLineWidth(0.3)
        c.line(cx + 5, inner_y - 25, cx + cell_w - 5, inner_y - 25)

        # Espaçamento muito maior (lh=26, era 16). 
        # Isso diminui drasticamente a quantidade de linhas!
        softlines(c, cx, inner_y - 27, cell_w, cell_h - 29, lh=26)

    # ── "Amanhã começa com:" ──────────────────────────────────────────────────
    tmr_x = MARGIN + 4 + 3 * (cell_w + gap_c) + 2
    tmr_w = CONTENT_W - (tmr_x - MARGIN) - 4
    tmr_h = cell_h

    c.setFillColor(BLUE_LIGHT)
    c.setStrokeColor(BLUE_DARK)
    c.setLineWidth(1.2)
    c.rect(tmr_x, inner_y - tmr_h, tmr_w, tmr_h, fill=1, stroke=1)

    # mini-header
    c.setFillColor(BLUE_DARK)
    c.rect(tmr_x, inner_y - 13, tmr_w, 13, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FB, 7.5)
    c.drawString(tmr_x + 5, inner_y - 10, "AMANHÃ COMEÇA COM:")

    c.setFont(FI, 7)
    c.setFillColor(GRAY_DARK)
    c.drawString(tmr_x + 5, inner_y - 22, "Tarefa mais importante do próximo dia:")

    c.setStrokeColor(BLUE)
    c.setLineWidth(0.8)
    c.line(tmr_x + 5, inner_y - 26, tmr_x + tmr_w - 5, inner_y - 26)

    # Mesma redução de linhas aqui (lh=26)
    softlines(c, tmr_x, inner_y - 28, tmr_w, tmr_h - 30, lh=26)

    return cursor - refl_h - 4


# ═══════════════════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════════════════

def draw_footer(c, cursor):
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, cursor, MARGIN + CONTENT_W, cursor)

    quote = ('"Sem reflexão, a produtividade é apenas um ciclo mecânico."')
    c.setFont(FI, 7)
    c.setFillColor(GRAY_DARK)
    qw = c.stringWidth(quote, FI, 7)
    c.drawString(MARGIN + CONTENT_W / 2 - qw / 2, cursor - 12, quote)


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def gerar_pdf(pdf_path: str) -> None:
    c = canvas.Canvas(pdf_path, pagesize=landscape(A3))
    c.setTitle("Diário de Bordo Contemporâneo v3")

    cursor = PAGE_H - MARGIN
    cursor = draw_header(c, cursor)
    cursor -= 5                        # respiração entre header e seções
    cursor = draw_sections(c, cursor)
    cursor = draw_reflection(c, cursor)
    draw_footer(c, cursor)

    c.save()
    print(f"PDF gerado com sucesso: {os.path.abspath(pdf_path)}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "diario_de_bordo_v3_A3_novo.pdf"
    try:
        gerar_pdf(output)
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}", file=sys.stderr)
        sys.exit(1)