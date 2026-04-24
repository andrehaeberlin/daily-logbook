"""
Diário de Bordo Contemporâneo — A3 Landscape
Dependência: pip install reportlab
Uso:         python app.py [caminho_saida.pdf]
"""

import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ── Constantes de layout ──────────────────────────────────────────────────────
PAGE_W, PAGE_H = landscape(A3)   # ~1190 x 842 pt
MARGIN = 10 * mm
BLUE   = colors.HexColor("#2980b9")
LIGHT  = colors.HexColor("#ebf5fb")
GRAY   = colors.HexColor("#bdc3c7")
PANEL  = colors.HexColor("#fcfcfc")
TEXT   = colors.HexColor("#2c3e50")
LGRAY  = colors.HexColor("#7f8c8d")
REFL   = colors.HexColor("#f4f9fd")

CONTENT_W    = PAGE_W - 2 * MARGIN
FONT_REGULAR = "Helvetica"
FONT_BOLD    = "Helvetica-Bold"
FONT_ITALIC  = "Helvetica-Oblique"


# ── Helpers ───────────────────────────────────────────────────────────────────

def section_box(c: canvas.Canvas, x, y, w, h, title: str, title_size=8):
    """Desenha caixa com header azul. Retorna y do topo interno (abaixo do header)."""
    bar_h = 14
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.5)
    c.setFillColor(PANEL)
    c.rect(x, y - h, w, h, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.rect(x, y - bar_h, w, bar_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONT_BOLD, title_size)
    c.drawString(x + 4, y - bar_h + 3, title.upper())
    return y - bar_h


def draw_lines(c: canvas.Canvas, x, y_top, w, n, line_h=14, prefix=False):
    """Desenha n linhas tracejadas para escrita."""
    c.setDash(2, 3)
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.4)
    for i in range(n):
        yy = y_top - (i + 1) * line_h
        if prefix:
            c.setFont(FONT_BOLD, 8)
            c.setFillColor(TEXT)
            c.drawString(x + 3, yy + 3, f"{i + 1}.")
        c.line(x + (18 if prefix else 4), yy, x + w - 4, yy)
    c.setDash()


def draw_note_lines(c: canvas.Canvas, x, y_top, w, h, line_h=14):
    """Linhas horizontais leves para área de notas livres."""
    c.setDash(1, 0)
    c.setStrokeColor(colors.HexColor("#eeeeee"))
    c.setLineWidth(0.5)
    n = int(h / line_h)
    for i in range(1, n + 1):
        yy = y_top - i * line_h
        c.line(x + 4, yy, x + w - 4, yy)


# ── Gerador principal ─────────────────────────────────────────────────────────

def gerar_pdf(pdf_path: str) -> None:
    c = canvas.Canvas(pdf_path, pagesize=landscape(A3))
    c.setTitle("Diário de Bordo Contemporâneo")

    cursor = PAGE_H - MARGIN

    # ── 1. Header ────────────────────────────────────────────────────────────
    c.setFillColor(BLUE)
    c.setFont(FONT_BOLD, 20)
    c.drawString(MARGIN, cursor - 18, "DIÁRIO DE BORDO CONTEMPORÂNEO")

    cursor -= 24
    c.setStrokeColor(BLUE)
    c.setLineWidth(2)
    c.line(MARGIN, cursor, MARGIN + CONTENT_W, cursor)
    cursor -= 4

    col_w = CONTENT_W / 3
    meta = [
        ("DATA: ",           "____/____/_______"),
        ("ENERGIA: ",        "[ 1 ]  [ 2 ]  [ 3 ]  [ 4 ]  [ 5 ]"),
        ("HIGIENE DIGITAL: ","[ ] OFF   [ ] MESA LIMPA   [ ] HIDRATAÇÃO"),
    ]
    for i, (label, value) in enumerate(meta):
        cx = MARGIN + i * col_w
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(TEXT)
        c.drawString(cx + 4, cursor - 12, label)
        lw = c.stringWidth(label, FONT_BOLD, 8)
        c.setFont(FONT_REGULAR, 8)
        c.drawString(cx + 4 + lw, cursor - 12, value)
        c.setStrokeColor(GRAY)
        c.setLineWidth(0.4)
        c.line(cx + 4, cursor - 16, cx + col_w - 4, cursor - 16)

    cursor -= 22

    # ── 2. Colunas principais ─────────────────────────────────────────────────
    col_area_h = 195
    left_w  = CONTENT_W * 0.48
    right_w = CONTENT_W * 0.50
    right_x = MARGIN + left_w + CONTENT_W * 0.02

    # Coluna esquerda — Captura
    cap_h = 82
    y_inner = section_box(c, MARGIN, cursor, left_w, cap_h,
                          "1. Captura (Caixa de Entrada / GTD)")
    draw_lines(c, MARGIN, y_inner, left_w, 9, line_h=13)

    # Coluna esquerda — Priorização
    prio_h = col_area_h - cap_h - 4
    y_inner2 = section_box(c, MARGIN, cursor - cap_h - 4,
                           left_w, prio_h,
                           "2. Priorização de Impacto (Ivy Lee / 80-20)")
    draw_lines(c, MARGIN, y_inner2, left_w, 6, line_h=13, prefix=True)

    # Foco de Ouro
    focus_y = cursor - cap_h - 4 - prio_h + 4
    focus_h = 32
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.5)
    c.setFillColor(LIGHT)
    c.rect(MARGIN + 4, focus_y, left_w - 8, focus_h, fill=1, stroke=1)
    c.setFont(FONT_BOLD, 8)
    c.setFillColor(BLUE)
    c.drawString(MARGIN + 8, focus_y + focus_h - 11,
                 "FOCO DE OURO (Trabalho Profundo):")
    c.setStrokeColor(BLUE)
    c.setLineWidth(1)
    c.line(MARGIN + 8, focus_y + 8, MARGIN + left_w - 8, focus_y + 8)

    # Coluna direita — Notas
    notes_h = col_area_h
    y_notes = section_box(c, right_x, cursor, right_w, notes_h,
                          "3. Fluxo de Trabalho & Notas Flexíveis")
    draw_note_lines(c, right_x, y_notes, right_w, notes_h - 14, line_h=14)
    c.setFont(FONT_ITALIC, 7)
    c.setFillColor(LGRAY)
    c.drawRightString(right_x + right_w - 6,
                      cursor - notes_h + 6,
                      "Capture ideias, bloqueios e sucessos momentâneos.")

    cursor -= col_area_h + 8

    # ── 3. Registro Reflexivo ─────────────────────────────────────────────────
    refl_h = 95
    section_box(c, MARGIN, cursor, CONTENT_W, refl_h,
                "4. Registro Reflexivo (Metacognição de Encerramento)")
    refl_title_y = cursor - 14   # abaixo do header

    cells = [
        ("FASE DESCRITIVA",        "O QUE aconteceu hoje? (Fatos e cronologia)"),
        ("FASE INTERPRETATIVA",    "POR QUÊ aconteceu? (Análise de causa e efeito)"),
        ("FASE CRÍTICA / SISTÊMICA", "APRENDIZADO: O que mudo amanhã?"),
    ]
    cell_w = (CONTENT_W - 12) / 3
    cell_h = refl_h - 18

    for i, (title, subtitle) in enumerate(cells):
        cx    = MARGIN + 2 + i * (cell_w + 4)
        cy_top = refl_title_y - 2

        c.setFillColor(REFL)
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.6)
        c.rect(cx, cy_top - cell_h, cell_w, cell_h, fill=1, stroke=1)

        c.setFont(FONT_BOLD, 7.5)
        c.setFillColor(BLUE)
        tw = c.stringWidth(title, FONT_BOLD, 7.5)
        c.drawString(cx + (cell_w - tw) / 2, cy_top - 12, title)

        c.setFont(FONT_ITALIC, 7)
        c.setFillColor(LGRAY)
        c.drawString(cx + 4, cy_top - 23, subtitle)

        c.setStrokeColor(GRAY)
        c.setLineWidth(0.4)
        c.line(cx + 4, cy_top - 26, cx + cell_w - 4, cy_top - 26)

        draw_note_lines(c, cx, cy_top - 28, cell_w, cell_h - 30, line_h=13)

    cursor -= refl_h + 8

    # ── 4. Footer ─────────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor("#ecf0f1"))
    c.setLineWidth(1)
    c.line(MARGIN, cursor, MARGIN + CONTENT_W, cursor)
    cursor -= 4

    # Fórmula com expoente manual
    formula = "Tempo de Execução = Tempo Inicial  ×  (N.º de Repetições)"
    center_x = MARGIN + CONTENT_W / 2
    c.setFont(FONT_ITALIC, 10)
    c.setFillColor(colors.HexColor("#34495e"))
    fw = c.stringWidth(formula, FONT_ITALIC, 10)
    base_x = center_x - fw / 2
    c.drawString(base_x, cursor - 12, formula)
    # expoente
    c.setFont(FONT_ITALIC, 6)
    c.drawString(base_x + fw + 1, cursor - 8, "-Taxa de Aprendizado")

    # Citação
    quote = ('"A organização é o andaime externo da função executiva. '
             'Sem reflexão, a produtividade é apenas um ciclo mecânico."')
    c.setFont(FONT_ITALIC, 7.5)
    c.setFillColor(colors.HexColor("#95a5a6"))
    qw = c.stringWidth(quote, FONT_ITALIC, 7.5)
    c.drawString(center_x - qw / 2, cursor - 24, quote)

    c.save()
    print(f"PDF gerado com sucesso: {os.path.abspath(pdf_path)}")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "diario_de_bordo_mestre_A3.pdf"
    try:
        gerar_pdf(output)
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}", file=sys.stderr)
        sys.exit(1)