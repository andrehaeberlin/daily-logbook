# file: app.py
"""
Diário de Bordo Contemporâneo — A4 Landscape
Correções de layout:
  - Tamanho de página alterado para A4 nativo.
  - Alturas de colunas (COL_TOP_H) e notas recalculadas para caberem nos ~595pt do A4.
  - Tamanhos de fontes e checkboxes mantidos/aumentados para garantir visibilidade
    real na impressão sem depender do redimensionamento da impressora.
"""

import os
import sys

from reportlab.lib import colors
# Importando o tamanho A4 no lugar do A3
from reportlab.lib.pagesizes import A4, landscape 
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# Definindo a versão dinâmica
version = "1.0-A4"

# ── Página ────────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = landscape(A4)   # 297 x 210 mm  →  ~842 x 595 pt
MARGIN    = 8 * mm               # Margem ligeiramente menor para aproveitar o espaço
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

def box(c, x, y, w, h, title, fs=8, bar_h=15, color=BLUE):
    """Caixa com barra de título colorida. Fontes levemente maiores para A4."""
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.5)
    c.setFillColor(PANEL)
    c.rect(x, y - h, w, h, fill=1, stroke=1)
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.rect(x, y - bar_h, w, bar_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FB, fs)
    c.drawString(x + 5, y - bar_h + 4, title.upper())
    return y - bar_h


def hlines(c, x, y_top, w, n, lh=18, prefix=False, color=LINE):
    """n linhas horizontais tracejadas para escrita."""
    c.setDash(2, 3)
    c.setStrokeColor(color)
    c.setLineWidth(0.45)
    for i in range(n):
        yy = y_top - (i + 1) * lh
        if prefix:
            c.setFont(FB, 8)
            c.setFillColor(GRAY_DARK)
            c.drawString(x + 4, yy + 4, f"{i + 1}.")
        c.line(x + (20 if prefix else 5), yy, x + w - 5, yy)
    c.setDash()


def softlines(c, x, y_top, w, h, lh=18):
    """Linhas suaves para áreas de escrita livre."""
    c.setDash(1, 0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    n = int(h / lh)
    for i in range(1, n + 1):
        c.line(x + 5, y_top - i * lh, x + w - 5, y_top - i * lh)


def cb(c, x, y, size=9):
    """Checkbox quadrado, ligeiramente maior para o A4."""
    c.setStrokeColor(GRAY_DARK)
    c.setLineWidth(0.7)
    c.setFillColor(WHITE)
    c.rect(x, y, size, size, fill=1, stroke=1)


def energy_bar(c, x, y, segments=5, seg_w=15, seg_h=10):
    """Barra de energia segmentada — preenche à caneta."""
    for i in range(segments):
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.7)
        c.setFillColor(WHITE)
        c.rect(x + i * (seg_w + 1), y, seg_w, seg_h, fill=1, stroke=1)


# ═══════════════════════════════════════════════════════════════════════════════
# Header
# ═══════════════════════════════════════════════════════════════════════════════

def draw_header(c, cursor):
    y = cursor

    # ── Faixa azul de título ─────────────────────────────────────────────────
    title_bar_h = 24
    c.setFillColor(BLUE)
    c.rect(MARGIN, y - title_bar_h, CONTENT_W, title_bar_h, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont(FB, 14)
    c.drawString(MARGIN + 6, y - title_bar_h + 7, "DIÁRIO DE BORDO")

    # DIA # à direita
    c.setFont(FB, 10)
    label = "DIA #"
    lw = c.stringWidth(label, FB, 10)
    c.drawString(MARGIN + CONTENT_W - 90, y - title_bar_h + 7, label)
    c.setStrokeColor(WHITE)
    c.setLineWidth(0.8)
    c.line(MARGIN + CONTENT_W - 90 + lw + 3, y - title_bar_h + 9,
           MARGIN + CONTENT_W - 6,            y - title_bar_h + 9)

    y -= title_bar_h

    # ── Linha de meta: DATA | ENERGIA | HIGIENE ──────────────────────────────
    meta_h = 18
    c.setFillColor(BLUE_LIGHT)
    c.rect(MARGIN, y - meta_h, CONTENT_W, meta_h, fill=1, stroke=0)

    # DATA
    mx = MARGIN + 6
    my = y - meta_h + 5
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(mx, my, "DATA:")
    mx += c.stringWidth("DATA:", FB, 8) + 4
    c.setFont(F, 8)
    c.setFillColor(TEXT)
    c.drawString(mx, my, "____/____/_______")

    # ENERGIA
    ex = MARGIN + CONTENT_W * 0.25
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(ex, my, "ENERGIA:")
    energy_bar(c, ex + c.stringWidth("ENERGIA:", FB, 8) + 4,
               my - 1, seg_w=14, seg_h=10)

    # HIGIENE DIGITAL
    hx = MARGIN + CONTENT_W * 0.52
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx, my, "HIGIENE DIGITAL:")
    hx += c.stringWidth("HIGIENE DIGITAL:", FB, 8) + 6
    for label in ["OFF", "MESA LIMPA", "HIDRATAÇÃO"]:
        cb(c, hx, my - 1, size=9)
        c.setFont(F, 8)
        c.setFillColor(TEXT)
        c.drawString(hx + 12, my, label)
        hx += c.stringWidth(label, F, 8) + 24

    y -= meta_h

    # ── Linha de hábitos ──────────────────────────────────────────────────────
    hab_h = 16
    c.setFillColor(colors.HexColor("#f5f8fa"))
    c.rect(MARGIN, y - hab_h, CONTENT_W, hab_h, fill=1, stroke=0)
    
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.4)
    c.line(MARGIN, y - hab_h, MARGIN + CONTENT_W, y - hab_h)

    hx = MARGIN + 6
    hy = y - hab_h + 4
    c.setFont(FB, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "HÁBITOS:")
    hx += c.stringWidth("HÁBITOS:", FB, 7.5) + 8

    for label in ["Exercício", "Leitura", "Estudos", "h sono"]:
        cb(c, hx, hy - 1, size=8)
        c.setFont(F, 7.5)
        c.setFillColor(TEXT)
        c.drawString(hx + 11, hy, label)
        hx += c.stringWidth(label, F, 7.5) + 22

    c.setFont(FB, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "ÁGUA:")
    hx += c.stringWidth("ÁGUA:", FB, 7.5) + 5
    for _ in range(8):
        cb(c, hx, hy - 1, size=8)
        hx += 12

    y -= hab_h
    return y


# ═══════════════════════════════════════════════════════════════════════════════
# Seções Intermediárias (Itens 1, 2, 3 e 4)
# ═══════════════════════════════════════════════════════════════════════════════

def draw_sections(c, cursor):
    GAP       = 10
    # Reduzimos a altura total das colunas superiores para caber no A4
    COL_TOP_H = 190 

    lw = (CONTENT_W - GAP) * 0.42
    rw = (CONTENT_W - GAP) * 0.58

    lx = MARGIN
    rx = MARGIN + lw + GAP

    # ── Coluna A: Captura ─────────────────────────────────────────────────────
    cap_h = 75
    yi = box(c, lx, cursor, lw, cap_h, "1. Captura  —  GTD / Caixa de Entrada", fs=8)
    hlines(c, lx, yi, lw, 3, lh=18) 

    # ── Coluna A: Priorização ─────────────────────────────────────────────────
    prio_top  = cursor - cap_h - GAP
    prio_h    = COL_TOP_H - cap_h - GAP
    yi2 = box(c, lx, prio_top, lw, prio_h, "2. Priorização  —  Ivy Lee / 80-20", fs=8)
    hlines(c, lx, yi2, lw, 3, lh=18, prefix=True)

    # Foco de Ouro + Pomodoros
    fo_h  = 45
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
    c.setFont(FB, 7.5)
    c.setFillColor(ORANGE)
    c.drawString(fo_x + 5, fo_y + 19, "POMODOROS:")
    px = fo_x + 5 + c.stringWidth("POMODOROS:", FB, 7.5) + 5
    for g in range(3):
        for _ in range(4):
            cb(c, px, fo_y + 18, size=8)
            px += 11
        px += 5

    c.setFont(F, 7)
    c.setFillColor(GRAY_DARK)
    half = fo_w / 2
    c.drawString(fo_x + 5,        fo_y + 5, "Sessão 1: ______________")
    c.drawString(fo_x + 5 + half, fo_y + 5, "Sessão 2: ______________")

    # ── Coluna B: Kanban ──────────────────────────────────────────────────────
    yi_k = box(c, rx, cursor, rw, COL_TOP_H, "3. Kanban do Dia", fs=8, color=BLUE_DARK)

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
        c.setFont(FB, 7.5)
        tw = c.stringWidth(lbl, FB, 7.5)
        c.drawString(kx + (kw - tw) / 2, k_top - 10, lbl)

        # linhas internas 
        c.setDash(1, 3)
        c.setStrokeColor(fg)
        c.setLineWidth(0.3)
        lines_n = int((kh - 14) / 20)
        for j in range(lines_n):
            yy = k_top - 14 - (j + 1) * 20
            c.line(kx + 4, yy, kx + kw - 4, yy)
        c.setDash()

    # ── Item 4: Notas Flexíveis ───────────────────────────────────────────────
    notas_y = cursor - COL_TOP_H - GAP
    notas_h = 110 # Altura recalculada para o A4

    yi_n = box(c, MARGIN, notas_y, CONTENT_W, notas_h, "4. Fluxo de Trabalho & Notas Flexíveis", fs=8)
    
    softlines(c, MARGIN, yi_n, CONTENT_W, notas_h - 16, lh=18) 
    
    c.setFont(FI, 7)
    c.setFillColor(GRAY_DARK)
    c.drawRightString(MARGIN + CONTENT_W - 5, notas_y - notas_h + 5,
                      "Ideias, bloqueios e insights do dia.")

    return notas_y - notas_h - GAP


# ═══════════════════════════════════════════════════════════════════════════════
# Reflexão
# ═══════════════════════════════════════════════════════════════════════════════

def draw_reflection(c, cursor):
    available = cursor - MARGIN - 20
    refl_h    = available

    box(c, MARGIN, cursor, CONTENT_W, refl_h,
        "5. Registro Reflexivo  —  Metacognição de Encerramento", fs=8)
    inner_y = cursor - 15

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
        c.setLineWidth(0.3)
        c.line(cx + 5, inner_y - 28, cx + cell_w - 5, inner_y - 28)

        softlines(c, cx, inner_y - 30, cell_w, cell_h - 32, lh=18)

    # ── "Amanhã começa com:" ──────────────────────────────────────────────────
    tmr_x = MARGIN + 4 + 3 * (cell_w + gap_c) + 2
    tmr_w = CONTENT_W - (tmr_x - MARGIN) - 4
    tmr_h = cell_h

    c.setFillColor(BLUE_LIGHT)
    c.setStrokeColor(BLUE_DARK)
    c.setLineWidth(1.2)
    c.rect(tmr_x, inner_y - tmr_h, tmr_w, tmr_h, fill=1, stroke=1)

    c.setFillColor(BLUE_DARK)
    c.rect(tmr_x, inner_y - 14, tmr_w, 14, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FB, 8)
    c.drawString(tmr_x + 5, inner_y - 10, "AMANHÃ COMEÇA COM:")

    c.setFont(FI, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(tmr_x + 5, inner_y - 24, "Tarefa prioritária:")

    c.setStrokeColor(BLUE)
    c.setLineWidth(0.8)
    c.line(tmr_x + 5, inner_y - 28, tmr_x + tmr_w - 5, inner_y - 28)

    softlines(c, tmr_x, inner_y - 30, tmr_w, tmr_h - 32, lh=18)

    return cursor - refl_h - 4


# ═══════════════════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════════════════

def draw_footer(c, cursor):
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, cursor, MARGIN + CONTENT_W, cursor)

    quote = ('"Sem reflexão, a produtividade é apenas um ciclo mecânico."')
    c.setFont(FI, 8)
    c.setFillColor(GRAY_DARK)
    qw = c.stringWidth(quote, FI, 8)
    c.drawString(MARGIN + CONTENT_W / 2 - qw / 2, cursor - 12, quote)


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def gerar_pdf(pdf_path: str) -> None:
    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
    
    c.setTitle(f"Diário de Bordo Contemporâneo v{version}")

    cursor = PAGE_H - MARGIN
    cursor = draw_header(c, cursor)
    cursor -= 5                        
    cursor = draw_sections(c, cursor)
    cursor = draw_reflection(c, cursor)
    draw_footer(c, cursor)

    c.save()
    print(f"PDF gerado com sucesso: {os.path.abspath(pdf_path)}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else f"diario_de_bordo_v{version}.pdf"
    try:
        gerar_pdf(output)
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}", file=sys.stderr)
        sys.exit(1)