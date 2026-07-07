# file: app.py
"""
Diário de Bordo Contemporâneo v1.2.3 — A4 Landscape
Atualizações (v1.2.3):
  - Pomodoros numerados com algarismos romanos (I, II, III...) acima das caixas.
  - Inspiração do Dia com duas linhas.
Atualizações anteriores (v1.2.2):
Atualizações (calibradas com 9 folhas reais de uso, 07/05–08/06/26):
  - Layout em 3 colunas: Captura | Priorização | Bloqueios+Fechamento.
  - Nova Feature: RECORRENTES/PENDENTES DA SEMANA com marcadores S-T-Q-Q-S
    (elimina recópia diária de itens como "Facul" e "IR").
  - Nova Feature: campos EST/REAL no Ouro e Prata + seção CALIBRAÇÃO
    (fator real÷estimado, integra com o Calibrador).
  - Nova Feature: prefixo YYMMDD- pré-impresso na linha do Ouro.
  - Nova Feature: BLOQUEIOS & IMPEDIMENTOS em destaque (uso real observado).
  - Nova Feature: BLOCOS DO DIA (timeboxing) e escala "DIA NO ALVO?" (1-5).
  - "AMANHÃ COMEÇA COM" promovido para a coluna central, em destaque.
  - Fechamento enxuto (2 perguntas + escala): dado de uso mostrou abandono
    do fechamento longo.
  - Removidos: 5S, CAFÉ, ÁGUA, BANHEIRO (zero/quase zero uso observado).
  - Mantidos: frase do dia no rodapé, Inspiração, Bronze e Cobre.
"""

import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

version = "1.2.3-A4"

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

def to_roman(n):
    """Converte inteiro (1-20) para algarismo romano."""
    vals = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out

def draw_checkbox_group(c, start_x, y, count, spacing=12, size=10, numbered=False):
    """
    Função DRY: Desenha uma sequência horizontal de caixas de seleção.
    Se numbered=True, desenha algarismos romanos (I, II, III...) acima
    de cada caixa para facilitar a contagem de pomodoros.
    Retorna a posição x final logo após o grupo gerado.
    """
    px = start_x
    for i in range(count):
        if numbered:
            num = to_roman(i + 1)
            c.setFont(F, 4)
            c.setFillColor(GRAY_DARK)
            nw = c.stringWidth(num, F, 4)
            c.drawString(px + (size - nw) / 2, y + size + 1.5, num)
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

    # DATA no cabeçalho
    label_data = "DATA:"
    data_x = MARGIN + CONTENT_W - 350
    c.setFillColor(WHITE)
    c.drawString(data_x, y - title_bar_h + 8, label_data)
    
    box_data_x = data_x + c.stringWidth(label_data, FB, 10) + 4
    c.setFillColor(WHITE)
    c.rect(box_data_x, y - title_bar_h + 5, 80, 14, fill=1, stroke=0)

    y -= title_bar_h

    # ── Linha de meta: HORÁRIOS | ENERGIA | SONO | HUMOR | 5S ──────
    meta_h = 18
    c.setFillColor(BLUE_LIGHT)
    c.rect(MARGIN, y - meta_h, CONTENT_W, meta_h, fill=1, stroke=0)
    
    my = y - meta_h + 5
    
    # 1. HORÁRIOS
    hx_time = MARGIN + 6
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx_time, my, "ENTRADA:")
    hx_time += c.stringWidth("ENTRADA:", FB, 8) + 4
    c.setFont(F, 8)
    c.setFillColor(TEXT)
    c.drawString(hx_time, my, "___ : ___")

    hx_time += c.stringWidth("___ : ___", F, 8) + 12
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx_time, my, "SAÍDA:")
    hx_time += c.stringWidth("SAÍDA:", FB, 8) + 4
    c.setFont(F, 8)
    c.setFillColor(TEXT)
    c.drawString(hx_time, my, "___ : ___")

    # 2. ENERGIA
    ex = MARGIN + CONTENT_W * 0.22
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(ex, my, "ENERGIA:")
    energy_bar(c, ex + c.stringWidth("ENERGIA:", FB, 8) + 4, my - 1, seg_w=14, seg_h=10)

    # 3. SONO
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

    # 4. HUMOR
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

    y -= meta_h

    # ── Linha de Inspiração ────────────────────────────────────────────────────
    int_h = 32
    c.setFillColor(colors.HexColor("#f5f8fa"))
    c.rect(MARGIN, y - int_h, CONTENT_W, int_h, fill=1, stroke=0)
    iy = y - 13
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)

    titulo_inspiracao = "INSPIRAÇÃO DO DIA:"
    c.drawString(MARGIN + 6, iy, titulo_inspiracao)

    inicio_linha = MARGIN + 6 + c.stringWidth(titulo_inspiracao, FB, 8) + 5

    c.setStrokeColor(LINE)
    c.line(inicio_linha, iy - 2, MARGIN + CONTENT_W - 6, iy - 2)
    # Segunda linha (largura total)
    c.line(MARGIN + 6, iy - 15, MARGIN + CONTENT_W - 6, iy - 15)

    return y - int_h

def draw_sections(c, cursor):
    """Monta o corpo em 3 colunas: Captura | Priorização | Bloqueios+Fechamento."""
    GAP = 10
    COL_H = 426
    w1 = (CONTENT_W - 2 * GAP) * 0.34
    w2 = (CONTENT_W - 2 * GAP) * 0.38
    w3 = (CONTENT_W - 2 * GAP) * 0.28
    x1 = MARGIN
    x2 = x1 + w1 + GAP
    x3 = x2 + w2 + GAP

    # ═══ COLUNA 1: CAPTURA DO DIA + RECORRENTES ═══════════════════════════════
    cap_h = 280
    yi_cap = box(
        c, x1, cursor, w1, cap_h,
        "1. Captura do Dia (. A Fazer | / Em Curso | X Feito | -> Adiado)",
        fs=7,
    )
    c.setDash(2, 3)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.45)
    for i in range(int((cap_h - 15) / 18)):
        yy = yi_cap - (i + 1) * 18
        c.setFont(F, 8)
        c.setFillColor(GRAY_DARK)
        c.drawString(x1 + 5, yy + 3, "[   ]")
        c.line(x1 + 22, yy, x1 + w1 - 5, yy)
    c.setDash()

    rec_y = cursor - cap_h - GAP
    rec_h = COL_H - cap_h - GAP
    yi_rec = box(
        c, x1, rec_y, w1, rec_h,
        "Recorrentes / Pendentes da Semana (não recopiar!)",
        fs=7, color=GREEN,
    )
    # Cabeçalho dos dias (S T Q Q S)
    day_x0 = x1 + w1 - 108
    c.setFont(FB, 6)
    c.setFillColor(GRAY_DARK)
    for k, d in enumerate(["S", "T", "Q", "Q", "S"]):
        c.drawString(day_x0 + k * 21 + 3, yi_rec - 9, d)
    ry = yi_rec - 24
    for _ in range(5):
        c.setStrokeColor(LINE)
        c.setLineWidth(0.45)
        c.setDash(2, 3)
        c.line(x1 + 5, ry, day_x0 - 6, ry)
        c.setDash()
        for k in range(5):
            cb(c, day_x0 + k * 21, ry - 2, size=10)
        ry -= 21

    # ═══ COLUNA 2: PRIORIZAÇÃO + CALIBRAÇÃO + AMANHÃ + BLOCOS ═════════════════
    prio_h = 182
    yi_prio = box(
        c, x2, cursor, w2, prio_h,
        "2. Priorização & Foco de Ouro (80/20)",
        fs=8, color=ORANGE, bg_color=GRAY_LIGHT,
    )

    fo_x = x2 + 5
    fo_y = yi_prio - 48
    fo_w = w2 - 10

    def est_real(px_right, py):
        c.setFont(F, 6)
        c.setFillColor(GRAY_DARK)
        c.drawString(px_right - 70, py, "EST ___  REAL ___")

    # ── Tarefa 1: OURO (destacada, prefixo YYMMDD- pré-impresso) ──────────────
    c.setFillColor(ORANGE_LIGHT)
    c.setStrokeColor(ORANGE)
    c.rect(fo_x, fo_y, fo_w, 46, fill=1, stroke=1)

    c.setFont(FB, 8)
    c.setFillColor(ORANGE)
    c.drawString(fo_x + 5, fo_y + 34, "1. OURO:")
    pref_x = fo_x + 5 + c.stringWidth("1. OURO:", FB, 8) + 4
    c.setFont(F, 7)
    c.setFillColor(GRAY_DARK)
    c.drawString(pref_x, fo_y + 34, "______-")
    c.setStrokeColor(ORANGE)
    c.line(pref_x + 26, fo_y + 31, fo_x + fo_w - 75, fo_y + 31)
    est_real(fo_x + fo_w, fo_y + 34)

    c.setFont(FB, 7.5)
    c.setFillColor(ORANGE)
    c.drawString(fo_x + 5, fo_y + 8, "POMODOROS:")
    px = fo_x + c.stringWidth("POMODOROS:", FB, 7.5) + 12
    draw_checkbox_group(c, px, fo_y + 6, count=12, numbered=True)

    def prio_task(num, nome, py, n_pomo, com_est=False):
        c.setFont(FB, 8)
        c.setFillColor(GRAY_DARK)
        c.drawString(x2 + 5, py, f"{num}. {nome}:")
        c.setStrokeColor(LINE)
        fim = x2 + w2 - (80 if com_est else 10)
        c.line(x2 + 5, py - 5, fim, py - 5)
        if com_est:
            est_real(x2 + w2, py)
        c.setFont(FB, 7.5)
        c.drawString(x2 + 5, py - 18, "POMODOROS:")
        px2 = x2 + 5 + c.stringWidth("POMODOROS:", FB, 7.5) + 12
        draw_checkbox_group(c, px2, py - 20, count=n_pomo, numbered=True)

    prio_task(2, "PRATA", fo_y - 12, 8, com_est=True)
    prio_task(3, "BRONZE", fo_y - 49, 6)
    prio_task(4, "COBRE", fo_y - 86, 4)

    # ── Calibração ────────────────────────────────────────────────────────────
    cal_y = cursor - prio_h - GAP
    cal_h = 42
    yi_cal = box(c, x2, cal_y, w2, cal_h, "Calibração (real ÷ estimado)", fs=7,
                 color=GREEN)
    c.setFont(FB, 8)
    c.setFillColor(TEXT)
    c.drawString(x2 + 5, yi_cal - 16, "FATOR DO DIA: ________")
    c.drawString(x2 + w2 * 0.45, yi_cal - 16, "FATOR ACUMULADO (semana): ________")

    # ── Amanhã começa com (promovido, em destaque) ────────────────────────────
    tmr_y = cal_y - cal_h - GAP
    tmr_h = 48
    c.setFillColor(BLUE_LIGHT)
    c.setStrokeColor(BLUE_DARK)
    c.setLineWidth(1.2)
    c.rect(x2, tmr_y - tmr_h, w2, tmr_h, fill=1, stroke=1)
    c.setFillColor(BLUE_DARK)
    c.rect(x2, tmr_y - 15, w2, 15, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FB, 8)
    c.drawString(x2 + 5, tmr_y - 11, "★ AMANHÃ COMEÇA COM: (decida AGORA, antes de sair)")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.45)
    c.setDash(2, 3)
    c.line(x2 + 5, tmr_y - 38, x2 + w2 - 5, tmr_y - 38)
    c.setDash()

    # ── Blocos do dia ─────────────────────────────────────────────────────────
    blk_y = tmr_y - tmr_h - GAP
    blk_h = COL_H - prio_h - cal_h - tmr_h - 3 * GAP
    yi_blk = box(c, x2, blk_y, w2, blk_h, "Blocos do Dia (timeboxing)", fs=7,
                 color=BLUE_DARK)
    periodos = ["08-10h:", "10-12h:", "13-15h:", "15-17h:", "17-18h:"]
    lh_blk = (blk_h - 22) / len(periodos)
    by = yi_blk - 16
    for p in periodos:
        c.setFont(FB, 7)
        c.setFillColor(GRAY_DARK)
        c.drawString(x2 + 5, by, p)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.45)
        c.setDash(2, 3)
        c.line(x2 + 40, by - 2, x2 + w2 - 5, by - 2)
        c.setDash()
        by -= lh_blk

    # ═══ COLUNA 3: BLOQUEIOS + NOTAS + FECHAMENTO ═════════════════════════════
    blq_h = 120
    yi_blq = box(c, x3, cursor, w3, blq_h, "3. Bloqueios & Impedimentos", fs=8,
                 color=ORANGE)
    c.setFont(FI, 6.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(x3 + 5, yi_blq - 11, "O que travou o trabalho? (rede, dependências, espera)")
    softlines(c, x3, yi_blq - 8, w3, blq_h - 28, lh=18)

    not_y = cursor - blq_h - GAP
    not_h = 138
    yi_not = box(c, x3, not_y, w3, not_h, "Notas / Ideias (tags @)", fs=8,
                 color=BLUE_DARK)
    softlines(c, x3, yi_not - 2, w3, not_h - 20, lh=18, tag_margin=45)

    # ── Fechamento enxuto (2 min) ─────────────────────────────────────────────
    fch_y = not_y - not_h - GAP
    fch_h = COL_H - blq_h - not_h - 2 * GAP
    yi_fch = box(c, x3, fch_y, w3, fch_h, "4. Fechamento (2 min)", fs=8)

    fy = yi_fch - 13
    c.setFont(FB, 7)
    c.setFillColor(BLUE_DARK)
    c.drawString(x3 + 5, fy, "O QUE FUNCIONOU?")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.45)
    c.setDash(2, 3)
    c.line(x3 + 5, fy - 14, x3 + w3 - 5, fy - 14)
    c.line(x3 + 5, fy - 28, x3 + w3 - 5, fy - 28)
    fy -= 42
    c.setDash()
    c.setFont(FB, 7)
    c.setFillColor(BLUE_DARK)
    c.drawString(x3 + 5, fy, "AJUSTE PARA AMANHÃ:")
    c.setDash(2, 3)
    c.line(x3 + 5, fy - 14, x3 + w3 - 5, fy - 14)
    c.setDash()
    fy -= 30
    c.setFont(FB, 7)
    c.setFillColor(BLUE_DARK)
    c.drawString(x3 + 5, fy, "DIA NO ALVO?")
    dx = x3 + 5 + c.stringWidth("DIA NO ALVO?", FB, 7) + 8
    for n in ["1", "2", "3", "4", "5"]:
        c.setFont(F, 7)
        c.setFillColor(TEXT)
        c.drawString(dx, fy, n)
        cb(c, dx + 7, fy - 2, size=10)
        dx += 27

    return cursor - COL_H - GAP

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

    # POMODOROS TOTAIS DO DIA
    hx += 14
    c.setFont(FB, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(hx, hy, "POMODOROS TOTAIS DO DIA:")
    hx += c.stringWidth("POMODOROS TOTAIS DO DIA:", FB, 7.5) + 5
    hx = draw_checkbox_group(c, hx, hy - 1, count=14, numbered=True)

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