# daily-logbook

Gerador de PDF do **Diário de Bordo Contemporâneo** — uma folha A4 paisagem para planejamento e registro do dia, feita para imprimir e preencher à mão. A página 1 traz o formulário (captura de tarefas, priorização Ouro/Prata/Bronze/Cobre, timeboxing, bloqueios, notas e fechamento); a página 2 é uma grade pontilhada para usar como verso.

## Uso

Requer Python 3 e [reportlab](https://pypi.org/project/reportlab/):

```bash
pip install reportlab
python app_v3.py             # gera diario_de_bordo_v3.0.0-A4.pdf
python app_v3.py saida.pdf   # ou escolha o nome do arquivo
```

**Impressão:** A4 paisagem, tamanho real (100%, sem "ajustar à página"), frente e verso pelo lado menor para ter a grade pontilhada no verso.

## Seções da folha (v3.0.0)

- **Cabeçalho** — data, semana, dia da semana (SEG–DOM), entrada/saída, energia, sono, humor e inspiração do dia (2 linhas).
- **1. Captura do Dia** — lista rápida com status: `.` a fazer, `/` em curso, `X` feito, `->` adiado.
- **Recorrentes / Pendentes da Semana** — itens que se repetem, com marcadores S-T-Q-Q-S (sem recopiar todo dia).
- **2. Priorização & Foco de Ouro (80/20)** — Ouro (ID + REF + 8 pomodoros), Prata, Bronze e Cobre (ID + pomodoros).
- **Blocos do Dia** — timeboxing hora a hora (08h–18h).
- **★ Amanhã Começa Com** — decida a primeira tarefa de amanhã antes de sair.
- **3. Bloqueios & Impedimentos** — o que travou o trabalho.
- **Notas Flexíveis & Fluxo** — anotações livres com coluna de tags `@`.
- **4. Fechamento Rápido (2 min)** — o que funcionou, ajuste para amanhã, "dia no alvo?" (1–5).
- **Rodapé** — hábitos nobres (Exercícios, Devocional, Leitura, Estudos) e pomodoros totais do dia.

## Histórico de versões

As versões são calibradas com folhas reais preenchidas: o que não é usado sai, e adaptações manuscritas viram campos.

| Arquivo | Versão | Destaques |
|---|---|---|
| `app_v0.py` | v1.1.13 | 2 colunas; Ouro/Prata/Bronze/Cobre; Mood Tracker; 5S, Café/Água/Banheiro; Metacognição completa |
| `app_v1.py` | v1.2.3 | 3 colunas (calibrada com 9 folhas reais); Recorrentes da Semana; EST/REAL + Calibração; Bloqueios; Blocos do Dia; fechamento enxuto; removidos 5S/Café/Água/Banheiro |
| `app_v2_2.py` | v2.2.0 | Blocos do Dia horários e expandidos; "Amanhã Começa Com" no rodapé da coluna; sem EST/REAL/Calibração |
| `app_v3.py` | **v3.0.0** | Calibrada com folha real de uso: seletor de dia da semana (SEG–DOM) no cabeçalho; campos ID + REF nas prioridades (códigos tipo `WTDMF-2730`); pomodoros reduzidos (8/6/6/4) |
