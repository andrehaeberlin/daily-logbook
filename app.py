"""
Diário de Bordo Contemporâneo v2 — A3 Landscape
Melhorias aplicadas:
  - Tracker de hábitos + barra de energia gráfica no header
  - Mini-kanban (A FAZER / EM CURSO / FEITO) no lugar da lista numerada
  - Contador de Pomodoros integrado ao Foco de Ouro
  - Seção reflexiva expandida com campo "Amanhã começa com:"
  - Rodapé simplificado (sem fórmula) para ganhar espaço
  - Campo Dia # no header

Dependência: pip install reportlab
Uso:         python app.py [caminho_saida.pdf]
"""

import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ── Paleta & tipografia ───────────────────────────────────────────────────────
PAGE_W, PAGE_H = landscape(A3)
MARGIN = 10 * mm

BLUE        = colors.HexColor("#2980b9")
BLUE_DARK   = colors.HexColor("#1a5276")
BLUE_LIGHT  = colors.HexColor("#ebf5fb")
ORANGE      = colors.HexColor("#e67e22")
ORANGE_LIGHT= colors.HexColor("#fef5ec")
GREEN       = colors.HexColor("#27ae60")
GREEN_LIGHT = colors.HexColor("#eafaf1")
GRAY        = colors.HexColor("#bdc3c7")
GRAY_DARK   = colors.HexColor("#7f8c8d")
PANEL       = colors.HexColor("#fcfcfc")
TEXT        = colors.HexColor("#2c3e50")
REFL        = colors.HexColor("#f4f9fd")
LINE_COLOR  = colors.HexColor("#e8e8e8")

CONTENT_W = PAGE_W - 2 * MARGIN
FONT      = "Helvetica"
FONT_B    = "Helvetica-Bold"
FONT_I    = "Helvetica-Oblique"


# ── Primitivas ────────────────────────────────────────────────────────────────

def section_box(c, x, y, w, h, title, title_size=8, color=BLUE):
    """Retângulo com header colorido. Retorna y logo abaixo do header."""
    bar_h = 15
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.5)
    c.setFillColor(PANEL)
    c.rect(x, y - h, w, h, fill=1, stroke=1)
    c.setFillColor(color)
    c.rect(x, y - bar_h, w, bar_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONT_B, title_size)
    c.drawString(x + 5, y - bar_h + 4, title.upper())
    return y - bar_h


def write_lines(c, x, y_top, w, n, line_h=14, prefix=False):
    """Linhas tracejadas para escrita manual."""
    c.setDash(2, 3)
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.4)
    for i in range(n):
        yy = y_top - (i + 1) * line_h
        if prefix:
            c.setFont(FONT_B, 7.5)
            c.setFillColor(GRAY_DARK)
            c.drawString(x + 3, yy + 3, f"{i + 1}.")
        c.line(x + (16 if prefix else 4), yy, x + w - 4, yy)
    c.setDash()


def note_lines(c, x, y_top, w, h, line_h=14):
    """Linhas suaves para área de escrita livre."""
    c.setDash(1, 0)
    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.5)
    for i in range(1, int(h / line_h) + 1):
        c.line(x + 4, y_top - i * line_h, x + w - 4, y_top - i * line_h)


def checkbox(c, x, y, size=7):
    """Desenha um checkbox quadrado."""
    c.setStrokeColor(GRAY_DARK)
    c.setLineWidth(0.6)
    c.setFillColor(colors.white)
    c.rect(x, y, size, size, fill=1, stroke=1)


def energy_bar(c, x, y, value=0, max_val=5, bar_w=60, bar_h=8):
    """Barra gráfica de energia para preencher à caneta."""
    seg_w = bar_w / max_val
    for i in range(max_val):
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.6)
        c.setFillColor(colors.white)
        c.rect(x + i * seg_w, y, seg_w - 1, bar_h, fill=1, stroke=1)
    # label
    c.setFont(FONT, 6.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(x + bar_w + 3, y + 1, "↑ preencha")


# ── Seções ────────────────────────────────────────────────────────────────────

def draw_header(c, cursor):
    """Retorna novo cursor após o header."""
    # Título + Dia #
    c.setFillColor(BLUE)
    c.setFont(FONT_B, 19)
    c.drawString(MARGIN, cursor - 17, "DIÁRIO DE BORDO CONTEMPORÂNEO")

    c.setFont(FONT_B, 10)
    c.setFillColor(GRAY_DARK)
    dia_label = "DIA #"
    dw = c.stringWidth(dia_label, FONT_B, 10)
    c.drawString(MARGIN + CONTENT_W - 80, cursor - 17, dia_label)
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.8)
    c.line(MARGIN + CONTENT_W - 80 + dw + 2, cursor - 14,
           MARGIN + CONTENT_W - 80 + dw + 42, cursor - 14)

    cursor -= 22
    c.setStrokeColor(BLUE)
    c.setLineWidth(2)
    c.line(MARGIN, cursor, MARGIN + CONTENT_W, cursor)
    cursor -= 3

    # Linha de meta-info: DATA | ENERGIA (barra) | HIGIENE DIGITAL
    col_w = CONTENT_W / 3
    y_meta = cursor - 13

    # DATA
    c.setFont(FONT_B, 8)
    c.setFillColor(TEXT)
    c.drawString(MARGIN + 4, y_meta, "DATA:")
    c.setFont(FONT, 8)
    c.drawString(MARGIN + 4 + c.stringWidth("DATA:", FONT_B, 8) + 3, y_meta,
                 "____/____/_______")

    # ENERGIA — barra gráfica
    e_x = MARGIN + col_w + 4
    c.setFont(FONT_B, 8)
    c.setFillColor(TEXT)
    c.drawString(e_x, y_meta, "ENERGIA:")
    energy_bar(c, e_x + c.stringWidth("ENERGIA:", FONT_B, 8) + 4,
               y_meta - 1, bar_w=55, bar_h=8)

    # HIGIENE DIGITAL — checkboxes
    hx = MARGIN + 2 * col_w + 4
    c.setFont(FONT_B, 8)
    c.setFillColor(TEXT)
    c.drawString(hx, y_meta, "HIGIENE DIGITAL:")
    habits_inline = ["OFF", "MESA LIMPA", "HIDRATAÇÃO"]
    hx2 = hx + c.stringWidth("HIGIENE DIGITAL:", FONT_B, 8) + 4
    for h_label in habits_inline:
        checkbox(c, hx2, y_meta - 1)
        c.setFont(FONT, 7.5)
        c.setFillColor(TEXT)
        c.drawString(hx2 + 9, y_meta, h_label)
        hx2 += c.stringWidth(h_label, FONT, 7.5) + 18

    # Linha separadora
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.3)
    c.line(MARGIN, cursor - 18, MARGIN + CONTENT_W, cursor - 18)
    cursor -= 22

    # Tracker de hábitos diários
    habits = ["Exercício", "Leitura", "Sem redes sociais", "8h sono"]
    hx = MARGIN + 4
    c.setFont(FONT_B, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, cursor - 10, "HÁBITOS:")
    hx += c.stringWidth("HÁBITOS:", FONT_B, 7.5) + 8
    for h in habits:
        checkbox(c, hx, cursor - 12)
        c.setFont(FONT, 7.5)
        c.setFillColor(TEXT)
        c.drawString(hx + 9, cursor - 10, h)
        hx += c.stringWidth(h, FONT, 7.5) + 20

    # Água
    c.setFont(FONT_B, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, cursor - 10, "ÁGUA:")
    hx += c.stringWidth("ÁGUA:", FONT_B, 7.5) + 4
    for _ in range(8):
        checkbox(c, hx, cursor - 12, size=6)
        hx += 10

    cursor -= 18
    c.setStrokeColor(colors.HexColor("#ecf0f1"))
    c.setLineWidth(1)
    c.line(MARGIN, cursor, MARGIN + CONTENT_W, cursor)
    cursor -= 4

    return cursor


def draw_columns(c, cursor):
    """Captura, Kanban+Pomodoro e Notas. Retorna novo cursor."""
    col_area_h = 188
    left_w  = CONTENT_W * 0.30
    mid_w   = CONTENT_W * 0.30
    right_w = CONTENT_W * 0.37
    gap     = CONTENT_W * 0.015

    mid_x   = MARGIN + left_w + gap
    right_x = mid_x + mid_w + gap

    # ── Coluna A: Captura GTD ──────────────────────────────────────────────
    cap_h = 75
    y_cap = section_box(c, MARGIN, cursor, left_w, cap_h,
                        "1. Captura (GTD — Caixa de Entrada)")
    write_lines(c, MARGIN, y_cap, left_w, 6, line_h=13)

    # ── Priorização Ivy Lee abaixo da captura ──────────────────────────────
    ivy_h = col_area_h - cap_h - 4
    y_ivy = section_box(c, MARGIN, cursor - cap_h - 4,
                        left_w, ivy_h,
                        "2. Priorização (Ivy Lee / 80-20)")
    write_lines(c, MARGIN, y_ivy, left_w, 6, line_h=13, prefix=True)

    # Foco de Ouro + Pomodoros
    focus_y = cursor - cap_h - 4 - ivy_h + 4
    focus_h = 44
    c.setStrokeColor(ORANGE)
    c.setLineWidth(1.5)
    c.setFillColor(ORANGE_LIGHT)
    c.rect(MARGIN + 4, focus_y, left_w - 8, focus_h, fill=1, stroke=1)

    c.setFont(FONT_B, 7.5)
    c.setFillColor(ORANGE)
    c.drawString(MARGIN + 8, focus_y + focus_h - 10,
                 "FOCO DE OURO (Trabalho Profundo):")
    c.setStrokeColor(ORANGE)
    c.setLineWidth(0.8)
    c.line(MARGIN + 8, focus_y + focus_h - 14,
           MARGIN + left_w - 8, focus_y + focus_h - 14)

    # Pomodoros
    c.setFont(FONT_B, 7)
    c.setFillColor(ORANGE)
    c.drawString(MARGIN + 8, focus_y + 22, "POMODOROS:")
    px = MARGIN + 8 + c.stringWidth("POMODOROS:", FONT_B, 7) + 5
    for group in range(3):
        for _ in range(4):
            checkbox(c, px, focus_y + 20, size=6)
            px += 9
        px += 4  # espaço entre grupos

    c.setFont(FONT, 7)
    c.setFillColor(GRAY_DARK)
    c.drawString(MARGIN + 8, focus_y + 9, "Sessão 1: ________________")
    c.drawString(MARGIN + 8 + (left_w - 8) / 2, focus_y + 9,
                 "Sessão 2: ________________")

    # ── Coluna B: Mini-Kanban ──────────────────────────────────────────────
    y_kan = section_box(c, mid_x, cursor, mid_w, col_area_h,
                        "3. Kanban do Dia", color=BLUE_DARK)

    kan_cols = [
        ("A FAZER",  BLUE_LIGHT,  BLUE),
        ("EM CURSO", ORANGE_LIGHT, ORANGE),
        ("FEITO",    GREEN_LIGHT,  GREEN),
    ]
    k_col_w = (mid_w - 10) / 3
    k_col_h = col_area_h - 20

    for i, (label, bg, fg) in enumerate(kan_cols):
        kx = mid_x + 4 + i * (k_col_w + 1)
        ky_top = y_kan - 4

        # fundo da coluna
        c.setFillColor(bg)
        c.setStrokeColor(fg)
        c.setLineWidth(0.8)
        c.rect(kx, ky_top - k_col_h, k_col_w, k_col_h, fill=1, stroke=1)

        # label da coluna
        c.setFillColor(fg)
        c.setFont(FONT_B, 7)
        tw = c.stringWidth(label, FONT_B, 7)
        c.drawString(kx + (k_col_w - tw) / 2, ky_top - 11, label)

        # linhas internas
        c.setDash(2, 3)
        c.setStrokeColor(fg)
        c.setLineWidth(0.3)
        for j in range(1, int(k_col_h / 16)):
            yy = ky_top - 16 - j * 16
            c.line(kx + 3, yy, kx + k_col_w - 3, yy)
        c.setDash()

    # ── Coluna C: Notas Flexíveis ──────────────────────────────────────────
    y_notes = section_box(c, right_x, cursor, right_w, col_area_h,
                          "4. Fluxo de Trabalho & Notas Flexíveis")
    note_lines(c, right_x, y_notes, right_w, col_area_h - 15, line_h=14)
    c.setFont(FONT_I, 6.5)
    c.setFillColor(GRAY_DARK)
    c.drawRightString(right_x + right_w - 5,
                      cursor - col_area_h + 5,
                      "Capture ideias, bloqueios e insights.")

    return cursor - col_area_h - 8


def draw_reflection(c, cursor):
    """Seção reflexiva expandida. Retorna novo cursor."""
    refl_h = 110
    section_box(c, MARGIN, cursor, CONTENT_W, refl_h,
                "5. Registro Reflexivo (Metacognição de Encerramento)")
    inner_y = cursor - 15

    # 3 células reflexivas
    cells = [
        ("FASE DESCRITIVA",        "O QUE aconteceu? (fatos e cronologia)"),
        ("FASE INTERPRETATIVA",    "POR QUÊ aconteceu? (causa e efeito)"),
        ("FASE CRÍTICA / SISTÊMICA","APRENDIZADO: O que mudo amanhã?"),
    ]
    cell_w = (CONTENT_W * 0.74 - 8) / 3
    cell_h = refl_h - 20

    for i, (title, subtitle) in enumerate(cells):
        cx = MARGIN + 2 + i * (cell_w + 4)
        c.setFillColor(REFL)
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.6)
        c.rect(cx, inner_y - cell_h, cell_w, cell_h, fill=1, stroke=1)

        c.setFont(FONT_B, 7.5)
        c.setFillColor(BLUE)
        tw = c.stringWidth(title, FONT_B, 7.5)
        c.drawString(cx + (cell_w - tw) / 2, inner_y - 11, title)

        c.setFont(FONT_I, 6.5)
        c.setFillColor(GRAY_DARK)
        c.drawString(cx + 4, inner_y - 21, subtitle)

        c.setStrokeColor(GRAY)
        c.setLineWidth(0.3)
        c.line(cx + 4, inner_y - 24, cx + cell_w - 4, inner_y - 24)

        note_lines(c, cx, inner_y - 26, cell_w, cell_h - 28, line_h=13)

    # Campo "Amanhã começa com:" — coluna direita da reflexão
    tmr_x = MARGIN + 2 + 3 * (cell_w + 4) + 4
    tmr_w = CONTENT_W - (tmr_x - MARGIN) - 2
    tmr_h = refl_h - 20

    c.setFillColor(BLUE_LIGHT)
    c.setStrokeColor(BLUE)
    c.setLineWidth(1)
    c.rect(tmr_x, inner_y - tmr_h, tmr_w, tmr_h, fill=1, stroke=1)

    c.setFont(FONT_B, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(tmr_x + 5, inner_y - 12, "AMANHÃ COMEÇA COM:")

    c.setFont(FONT_I, 7)
    c.setFillColor(GRAY_DARK)
    c.drawString(tmr_x + 5, inner_y - 22,
                 "A tarefa mais importante do dia seguinte:")

    c.setStrokeColor(BLUE)
    c.setLineWidth(0.8)
    c.line(tmr_x + 5, inner_y - 26, tmr_x + tmr_w - 5, inner_y - 26)

    note_lines(c, tmr_x, inner_y - 28, tmr_w, tmr_h - 30, line_h=14)

    return cursor - refl_h - 6


def draw_footer(c, cursor):
    """Rodapé minimalista com citação."""
    c.setStrokeColor(colors.HexColor("#ecf0f1"))
    c.setLineWidth(1)
    c.line(MARGIN, cursor, MARGIN + CONTENT_W, cursor)

    quote = ('"A organização é o andaime externo da função executiva. '
             'Sem reflexão, a produtividade é apenas um ciclo mecânico."')
    c.setFont(FONT_I, 7.5)
    c.setFillColor(GRAY_DARK)
    qw = c.stringWidth(quote, FONT_I, 7.5)
    cx = MARGIN + CONTENT_W / 2
    c.drawString(cx - qw / 2, cursor - 12, quote)


# ── Entry point ───────────────────────────────────────────────────────────────

def gerar_pdf(pdf_path: str) -> None:
    c = canvas.Canvas(pdf_path, pagesize=landscape(A3))
    c.setTitle("Diário de Bordo Contemporâneo v2")

    cursor = PAGE_H - MARGIN
    cursor = draw_header(c, cursor)
    cursor = draw_columns(c, cursor)
    cursor = draw_reflection(c, cursor)
    draw_footer(c, cursor)

    c.save()
    print(f"PDF gerado com sucesso: {os.path.abspath(pdf_path)}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "diario_de_bordo_v2_A3.pdf"
    try:
        gerar_pdf(output)
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}", file=sys.stderr)
        sys.exit(1)