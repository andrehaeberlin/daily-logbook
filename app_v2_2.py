# file: app_v2_2.py
"""
Diário de Bordo Contemporâneo v2.2.0 — A4 Landscape
Atualização: Inversão dos blocos na Coluna 2. "Blocos do Dia" movido para cima e expandido (mais horários).
"Amanhã Começa Com" movido para o rodapé da coluna.
"""

import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

version = "2.2.0-A4"

# ── Configurações de Página ───────────────────────────────────────────────────
PAGE_W, PAGE_H = landscape(A4)
MARGIN = 8 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

# ── Paleta de Cores Coesas ────────────────────────────────────────────────────
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

# ── Tipografia ────────────────────────────────────────────────────────────────
F = "Helvetica"
FB = "Helvetica-Bold"
FI = "Helvetica-Oblique"

# ═══════════════════════════════════════════════════════════════════════════════
# Funções Auxiliares (Primitivas e Elementos Gráficos)
# ═══════════════════════════════════════════════════════════════════════════════

def box(c, x, y, w, h, title, fs=8, bar_h=15, color=BLUE, bg_color=PANEL):
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
    c.setStrokeColor(GRAY_DARK)
    c.setLineWidth(0.7)
    c.setFillColor(WHITE) 
    c.rect(x, y, size, size, fill=1, stroke=1)

def to_roman(n):
    vals = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out

def draw_checkbox_group(c, start_x, y, count, spacing=12, size=10, numbered=False):
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
    for i in range(segments):
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.7)
        c.setFillColor(WHITE)
        c.rect(x + i * (seg_w + 1), y, seg_w, seg_h, fill=1, stroke=1)

def draw_face(c, x, y, r, mood):
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
# Construtores de Camadas e Seções do PDF
# ═══════════════════════════════════════════════════════════════════════════════

def draw_header(c, cursor):
    y = cursor

    title_bar_h = 24
    c.setFillColor(BLUE)
    c.rect(MARGIN, y - title_bar_h, CONTENT_W, title_bar_h, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont(FB, 12)
    c.drawString(MARGIN + 6, y - title_bar_h + 7, f"DIÁRIO DE BORDO — v{version}")

    c.setFont(FB, 9)
    label_dia = "DIA #"
    dia_x = MARGIN + CONTENT_W - 100
    c.drawString(dia_x, y - title_bar_h + 8, label_dia)
    c.rect(dia_x + c.stringWidth(label_dia, FB, 9) + 4, y - title_bar_h + 5, 60, 14, fill=1, stroke=0)

    label_sem = "SEMANA #"
    sem_x = MARGIN + CONTENT_W - 200 
    c.drawString(sem_x, y - title_bar_h + 8, label_sem)
    c.rect(sem_x + c.stringWidth(label_sem, FB, 9) + 4, y - title_bar_h + 5, 30, 14, fill=1, stroke=0)

    label_data = "DATA:"
    data_x = MARGIN + CONTENT_W - 320
    c.drawString(data_x, y - title_bar_h + 8, label_data)
    c.rect(data_x + c.stringWidth(label_data, FB, 9) + 4, y - title_bar_h + 5, 75, 14, fill=1, stroke=0)

    y -= title_bar_h

    meta_h = 18
    c.setFillColor(BLUE_LIGHT)
    c.rect(MARGIN, y - meta_h, CONTENT_W, meta_h, fill=1, stroke=0)
    
    my = y - meta_h + 5
    
    hx_time = MARGIN + 6
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx_time, my, "ENTRADA:")
    hx_time += c.stringWidth("ENTRADA:", FB, 8) + 4
    c.setFont(F, 8)
    c.setFillColor(TEXT)
    c.drawString(hx_time, my, "___ : ___")

    hx_time += 55
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx_time, my, "SAÍDA:")
    hx_time += c.stringWidth("SAÍDA:", FB, 8) + 4
    c.setFont(F, 8)
    c.setFillColor(TEXT)
    c.drawString(hx_time, my, "___ : ___")

    ex = MARGIN + CONTENT_W * 0.28
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(ex, my, "ENERGIA:")
    energy_bar(c, ex + c.stringWidth("ENERGIA:", FB, 8) + 5, my - 1, seg_w=14, seg_h=10)

    sx = MARGIN + CONTENT_W * 0.52
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(sx, my, "SONO:")
    sx_box = sx + c.stringWidth("SONO:", FB, 8) + 5
    c.setFillColor(WHITE)
    c.setStrokeColor(GRAY_DARK)
    c.setLineWidth(0.5)
    c.rect(sx_box, my - 2, 28, 11, fill=1, stroke=1)
    c.setFont(F, 8)
    c.setFillColor(TEXT)
    c.drawString(sx_box + 32, my, "horas")

    hx = MARGIN + CONTENT_W * 0.74
    c.setFont(FB, 8)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx, my, "HUMOR:")
    hx += c.stringWidth("HUMOR:", FB, 8) + 10
    
    raio_rosto = 5.5
    for mood in ['very_happy', 'happy', 'neutral', 'sad', 'very_sad']:
        draw_face(c, hx, my + 3, raio_rosto, mood)
        hx += 15

    y -= meta_h

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
    c.setLineWidth(0.45)
    c.line(inicio_linha, iy - 2, MARGIN + CONTENT_W - 6, iy - 2)
    c.line(MARGIN + 6, iy - 15, MARGIN + CONTENT_W - 6, iy - 15)

    return y - int_h

def draw_sections(c, cursor):
    GAP = 10
    COL_H = 426
    
    w1 = (CONTENT_W - 2 * GAP) * 0.34
    w2 = (CONTENT_W - 2 * GAP) * 0.38
    w3 = (CONTENT_W - 2 * GAP) * 0.28
    
    x1 = MARGIN
    x2 = x1 + w1 + GAP
    x3 = x2 + w2 + GAP

    # ═════════ COLUNA 1: CAPTURA DO DIA & RECORRENTES DA SEMANA ═════════
    cap_h = 280
    yi_cap = box(
        c, x1, cursor, w1, cap_h,
        "1. Captura do Dia (. A Fazer | / Em Curso | X Feito | -> Adiado)",
        fs=7.5
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
        "Recorrentes / Pendentes da Semana (Matriz de Produtividade)",
        fs=7.5, color=GREEN
    )
    
    day_x0 = x1 + w1 - 105
    c.setFont(FB, 7)
    c.setFillColor(GRAY_DARK)
    for k, d in enumerate(["S", "T", "Q", "Q", "S"]):
        c.drawString(day_x0 + k * 20 + 2, yi_rec - 9, d)
        
    ry = yi_rec - 24
    for _ in range(5):
        c.setStrokeColor(LINE)
        c.setLineWidth(0.45)
        c.setDash(2, 3)
        c.line(x1 + 5, ry, day_x0 - 5, ry)
        c.setDash()
        for k in range(5):
            cb(c, day_x0 + k * 20, ry - 2, size=10)
        ry -= 20

    # ═════════ COLUNA 2: PRIORIZAÇÃO (MÉTODO MATRIZ OURO) + BLOCOS ═════════
    prio_h = 182
    yi_prio = box(
        c, x2, cursor, w2, prio_h,
        "2. Priorização & Foco de Ouro (Princípio de Pareto 80/20)",
        fs=7.5, color=ORANGE, bg_color=GRAY_LIGHT
    )

    fo_x = x2 + 5
    fo_y = yi_prio - 46
    fo_w = w2 - 10

    c.setFillColor(ORANGE_LIGHT)
    c.setStrokeColor(ORANGE)
    c.rect(fo_x, fo_y, fo_w, 42, fill=1, stroke=1)

    c.setFont(FB, 8)
    c.setFillColor(ORANGE)
    c.drawString(fo_x + 5, fo_y + 30, "1. OURO:")
    
    pref_x = fo_x + 5 + c.stringWidth("1. OURO:", FB, 8) + 4
    c.setFont(F, 7.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(pref_x, fo_y + 30, "YYMMDD-")
    
    linha_start = pref_x + c.stringWidth("YYMMDD-", F, 7.5) + 3
    linha_fim = fo_x + fo_w - 10 
    c.setStrokeColor(ORANGE)
    c.setLineWidth(0.5)
    c.line(linha_start, fo_y + 28, linha_fim, fo_y + 28)

    c.setFont(FB, 7)
    c.setFillColor(ORANGE)
    c.drawString(fo_x + 5, fo_y + 8, "POMODOROS:")
    px = fo_x + c.stringWidth("POMODOROS:", FB, 7) + 8
    draw_checkbox_group(c, px, fo_y + 6, count=12, numbered=True)

    def prio_task(num, nome, py, n_pomo):
        c.setFont(FB, 8)
        c.setFillColor(TEXT)
        label_str = f"{num}. {nome}:"
        c.drawString(x2 + 5, py, label_str)
        
        txt_w = c.stringWidth(label_str, FB, 8)
        linha_start = x2 + 5 + txt_w + 5
        linha_fim = x2 + w2 - 10
        
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(linha_start, py - 1, linha_fim, py - 1)
            
        c.setFont(FB, 7)
        c.setFillColor(GRAY_DARK)
        c.drawString(x2 + 5, py - 15, "POMODOROS:")
        px2 = x2 + 5 + c.stringWidth("POMODOROS:", FB, 7) + 8
        draw_checkbox_group(c, px2, py - 17, count=n_pomo, numbered=True)

    prio_task(2, "PRATA", fo_y - 14, 8)
    prio_task(3, "BRONZE", fo_y - 48, 6)
    prio_task(4, "COBRE", fo_y - 82, 4)

    # ── Blocos Horários (Timeboxing) logo após a Priorização
    tmr_h = 48
    blk_y = cursor - prio_h - GAP
    blk_h = COL_H - prio_h - tmr_h - 2 * GAP
    yi_blk = box(c, x2, blk_y, w2, blk_h, "Blocos do Dia (Timeboxing & Ritmo)", fs=7, color=BLUE_DARK)
    
    # Aumentando os períodos para aproveitar bem a altura do bloco
    periodos = [
        "08-09h:", "09-10h:", "10-11h:", "11-12h:", 
        "13-14h:", "14-15h:", "15-16h:", "16-17h:", "17-18h:"
    ]
    lh_blk = (blk_h - 18) / len(periodos)
    by = yi_blk - 14
    for p in periodos:
        c.setFont(FB, 7)
        c.setFillColor(GRAY_DARK)
        c.drawString(x2 + 5, by, p)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.45)
        c.setDash(2, 3)
        c.line(x2 + 42, by - 1, x2 + w2 - 5, by - 1)
        c.setDash()
        by -= lh_blk

    # ── Amanhã Começa Com (Movido para o fundo)
    tmr_y = blk_y - blk_h - GAP
    c.setFillColor(BLUE_LIGHT)
    c.setStrokeColor(BLUE_DARK)
    c.setLineWidth(1.0)
    c.rect(x2, tmr_y - tmr_h, w2, tmr_h, fill=1, stroke=1)
    c.setFillColor(BLUE_DARK)
    c.rect(x2, tmr_y - 14, w2, 14, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FB, 7.5)
    c.drawString(x2 + 5, tmr_y - 10, "★ AMANHÃ COMEÇA COM: (Decida agora, blinde sua rotina)")
    
    c.setStrokeColor(LINE)
    c.setLineWidth(0.45)
    c.setDash(2, 3)
    c.line(x2 + 5, tmr_y - 35, x2 + w2 - 5, tmr_y - 35)
    c.setDash()

    # ═════════ COLUNA 3: BLOQUEIOS, NOTAS E METACOGNIÇÃO ENXUTA ═════════
    blq_h = 120
    yi_blq = box(c, x3, cursor, w3, blq_h, "3. Bloqueios & Impedimentos (Atrito)", fs=7.5, color=ORANGE)
    c.setFont(FI, 6.5)
    c.setFillColor(GRAY_DARK)
    c.drawString(x3 + 5, yi_blq - 11, "Dependências externas, travamentos de rede e infra:")
    softlines(c, x3, yi_blq - 8, w3, blq_h - 26, lh=18)

    not_y = cursor - blq_h - GAP
    not_h = 138
    yi_not = box(c, x3, not_y, w3, not_h, "Notas Flexíveis & Fluxo (Tags @)", fs=7.5, color=BLUE_DARK)
    softlines(c, x3, yi_not - 2, w3, not_h - 18, lh=18, tag_margin=42)

    fch_y = not_y - not_h - GAP
    fch_h = COL_H - blq_h - not_h - 2 * GAP
    yi_fch = box(c, x3, fch_y, w3, fch_h, "4. Fechamento Rápido (2 minutos)", fs=7.5)

    fy = yi_fch - 12
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
    
    fy -= 28
    c.setFont(FB, 7)
    c.setFillColor(BLUE_DARK)
    c.drawString(x3 + 5, fy, "DIA NO ALVO?")
    dx = x3 + 5 + c.stringWidth("DIA NO ALVO?", FB, 7) + 8
    for n in ["1", "2", "3", "4", "5"]:
        c.setFont(F, 7.5)
        c.setFillColor(TEXT)
        c.drawString(dx, fy, n)
        cb(c, dx + 7, fy - 2, size=10)
        dx += 22

    return cursor - COL_H - GAP

def draw_habits_and_footer(c, cursor):
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
    c.drawString(hx, hy, "HÁBITOS NOBRES:")
    hx += c.stringWidth("HÁBITOS NOBRES:", FB, 7.5) + 8

    for label in ["Exercícios", "Devocional", "Leitura", "Estudos"]:
        cb(c, hx, hy - 1, size=10)
        c.setFont(F, 7.5)
        c.setFillColor(TEXT)
        c.drawString(hx + 12, hy, label)
        hx += c.stringWidth(label, F, 7.5) + 18

    hx += 10
    c.setFont(FB, 7.5)
    c.setFillColor(BLUE_DARK)
    c.drawString(hx, hy, "POMODOROS TOTAIS DO DIA:")
    hx += c.stringWidth("POMODOROS TOTAIS DO DIA:", FB, 7.5) + 6
    hx = draw_checkbox_group(c, hx, hy - 1, count=14, numbered=True)

    cursor -= hab_h + 8

    quote = '"Sem reflexão, a produtividade é apenas um ciclo mecânico."'
    c.setFont(FI, 8.5)
    c.setFillColor(GRAY_DARK)
    qw = c.stringWidth(quote, FI, 8.5)
    c.drawString(MARGIN + CONTENT_W / 2 - qw / 2, cursor - 10, quote)

def draw_dot_grid(c):
    c.showPage()
    c.setFillColor(GRAY)
    spacing = 5 * mm 

    for x in range(int(MARGIN), int(PAGE_W - MARGIN), int(spacing)):
        for y in range(int(MARGIN), int(PAGE_H - MARGIN), int(spacing)):
            c.circle(x, y, 0.4, fill=1, stroke=0)

# ═══════════════════════════════════════════════════════════════════════════════
# Motor de Execução e Orquestração
# ═══════════════════════════════════════════════════════════════════════════════

def gerar_pdf(pdf_path: str) -> None:
    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
    c.setTitle(f"Diário de Bordo Contemporâneo v{version}")

    cursor = PAGE_H - MARGIN
    cursor = draw_header(c, cursor)
    cursor -= 5
    cursor = draw_sections(c, cursor)
    draw_habits_and_footer(c, cursor)

    draw_dot_grid(c)
    c.save()

if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else f"diario_de_bordo_v{version}.pdf"
    gerar_pdf(output)
