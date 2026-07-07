# CLAUDE.md

Guidance for Claude Code when working in this repository.

## O que é este projeto

Gerador de PDF do **Diário de Bordo Contemporâneo**: uma folha de planejamento diário em A4 paisagem, feita para ser impressa e preenchida à mão. A página 1 é o formulário do dia; a página 2 é uma grade pontilhada (verso). Único requisito: `reportlab`.

```bash
pip install reportlab
python app_v3.py [saida.pdf]   # sem argumento: diario_de_bordo_v<versão>.pdf
```

## Estrutura e convenções

- **Um arquivo por versão** (`app_v0.py`, `app_v1.py`, `app_v2_2.py`, `app_v3.py`). Uma nova versão é um **arquivo novo** copiado da anterior — as versões antigas não são editadas nem removidas; servem de histórico comparável.
- Cada arquivo tem:
  - Docstring de módulo com o **changelog da versão** (em português, citando a motivação).
  - Constante `version = "X.Y.Z-A4"` usada no título do PDF e no nome do arquivo de saída.
  - As mesmas primitivas de desenho: `box`, `softlines`, `cb`, `draw_checkbox_group`, `energy_bar`, `draw_face`, `to_roman`. Reutilize-as; não crie variantes novas sem necessidade.
  - Orquestração em `gerar_pdf()`: `draw_header` → `draw_sections` → `draw_habits_and_footer` → `draw_dot_grid`.
- **Coordenadas**: origem do ReportLab é o canto inferior esquerdo; o código desenha de cima para baixo com um `cursor` decrescente. Constantes de página: `PAGE_W/PAGE_H` (A4 paisagem), `MARGIN = 8*mm`, `CONTENT_W`.
- Corpo em 3 colunas dentro de `draw_sections` com `COL_H = 426`; as alturas dos blocos de cada coluna devem somar `COL_H` (com `GAP = 10` entre eles) — ao mudar a altura de um bloco, recalcule os demais da coluna.
- **Idioma**: todos os rótulos do formulário, comentários e changelogs são em **português (pt-BR)**. Fontes Helvetica embutidas (sem fontes externas).

## Processo de evolução (importante)

As versões são **calibradas com folhas reais preenchidas**: o usuário imprime, usa por dias/semanas, fotografa a folha e as mudanças derivam da observação de uso (seções ignoradas são removidas; adaptações manuscritas viram campos). Ao propor uma nova versão:

1. Baseie-se na versão mais recente (hoje: `app_v3.py`).
2. Justifique cada mudança com evidência de uso no changelog.
3. Gere o PDF, renderize a página 1 como imagem e **inspecione visualmente** (sem sobreposições, colunas fechando em `COL_H`, rodapé dentro da página) antes de commitar.

## Verificação

```bash
python app_vN.py /tmp/teste.pdf   # deve sair com código 0 e imprimir "Sucesso!"
```

Para inspeção visual, renderize com `pypdfium2` (ou `pdftoppm`) e confira o layout. Não há testes automatizados.

## Git

- Commits com mensagens `feat:`/`fix:` descritivas, em inglês, citando a versão.
- Não editar versões antigas; mudanças de layout entram sempre como versão nova.
