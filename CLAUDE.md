# enem

Dashboard em Shiny for Python dos simulados do Enem que o Eduardo fez em 2023 (provas anteriores, edições de 2009 a 2020). Projeto pessoal, código e rótulos da UI em português.

## Rodar

```bash
pip install -r requirements.txt
shiny run --reload app.py   # a partir da raiz: os CSVs são lidos por caminho relativo
```

O README diz `cd src/data_analysis` e tem o título "FIPE": os dois estão errados (copiados de outro projeto). O link enem.stuaninauts.com do README não está no ar.

## Estrutura

- `app.py`: o app inteiro (UI + server). Duas abas:
  - "Acertos e melhoras" (`df_am`, prefixo `am`): acertos por área ou redação por edição, e comparação entre 1ª e 2ª tentativa da mesma prova.
  - "Conversão de conhecimento" (`df_cc`, prefixo `cc`): questões que sabia vs não sabia, e quantas errou em cada grupo.
- `examples/`: prints usados no README.
- `app2.py` e `tests.ipynb` estão no `.gitignore` (rascunhos locais, não versionados).

## Dados

`enem_acertos_melhoras.csv`, uma linha por edição (27 linhas, 25 com algum dado; `ENEM 2012 PPL` e `ENEM 2013 PPL` vazias):
- `linguagens`, `humanas`, `matematica`, `natureza`: acertos de 0 a 45. Quando há `melhora_*`, o valor é da 2ª tentativa.
- `redacao`: nota de 0 a 1000. `total`: soma das quatro áreas.
- `melhora_<area>`: 2ª tentativa menos a 1ª (1ª = `<area>` - `melhora_<area>`).

`enem_conversao_conhecimento.csv`, 23 linhas, só humanas, matemática e natureza (sem linguagens):
- `<area>_s`: questões que sabia; `<area>_s_e`: dessas, quantas errou.
- `<area>_ns`: questões que não sabia (chute); `<area>_ns_e`: dessas, quantas errou.
- `s + ns = 45`; acertos = `(s - s_e) + (ns - ns_e)`.
- `humanas_ns_{hist,geo,filo,socio}` e `natureza_ns_{quim,fis,bio}`: "não sabia" por disciplina (preenchido em parte; análise por disciplina é TODO no app).
- A ordem das linhas é a ordem em que as provas foram feitas: o modo "Cronológica por Resolução" reindexa os dois CSVs por ela.

Inconsistências conhecidas (não corrigir sem perguntar, são dados originais):
- `"ENEM 2017 PPL "` tem espaço no fim em `cc`, então não casa com `am` na ordem cronológica.
- Acertos calculados por `cc` divergem de `am` em humanas (2016/2, 2020 DIGITAL, 1 questão) e natureza (2010, 2017 LIBRAS, 2019, 2020 DIGITAL, 2017 PPL); em natureza 2019 e 2020 DIGITAL, `s + ns != 45`.

## Convenções

- Áreas usam as chaves de `dict_areas` (`linguagens`, `humanas`, `matematica`, `natureza`); colunas de `cc` são filtradas pelos 3 primeiros caracteres da área.
- Gráficos em Plotly via `shinywidgets` (`@render_plotly`).
- Texto: nunca usar travessão longo (em dash).
- Commit, push e PR só quando o Eduardo pedir; em dia útil, das 09h às 18h, nada no GitHub.
