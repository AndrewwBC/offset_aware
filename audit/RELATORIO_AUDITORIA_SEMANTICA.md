# Relatório da auditoria semântica

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Configuração auditada: `full`.
Amostra: 1.600 tuplas sorteadas uniformemente, 100 por run (semente 20260930), 1.572 itens únicos julgados. Segunda passada da regra de localização em 107 itens.
Percentuais sobre as tuplas retidas, com IC de 95% (Wilson por run; estimativa estratificada ponderada pelas tuplas retidas nos totais).

**Válidas**: corretas em todos os campos. **No domínio**: opinião real sobre o hotel, talvez com algum campo a corrigir. **Fora do domínio**: aspecto é lugar nomeado ou monumento (`A2`) ou outra entidade fora do hotel (`A3`).

## Tabela por modelo

| Modelo | SSA: retidas | SSA: válidas (%) | SSA: no domínio (%) | SSA: fora do domínio (%) | ASQP: retidas | ASQP: válidas (%) | ASQP: no domínio (%) | ASQP: fora do domínio (%) | Válidas estimadas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B | 219 | 16,0 [10–24] | 63,0 [53–72] | 2,0 [1–7] | 173 | 29,0 [21–39] | 58,0 [48–67] | 1,0 [0–5] | 85 |
| Qwen2.5-1.5B | 1.760 | 23,0 [16–32] | 59,0 [49–68] | 3,0 [1–8] | 1.869 | 29,0 [21–39] | 50,0 [40–60] | 10,0 [6–17] | 947 |
| Qwen2.5-3B | 1.909 | 17,0 [11–26] | 67,0 [57–75] | 5,0 [2–11] | 2.132 | 41,0 [32–51] | 60,0 [50–69] | 2,0 [1–7] | 1.199 |
| Qwen2.5-7B | 2.546 | 52,0 [42–62] | 81,0 [72–87] | 4,0 [2–10] | 2.642 | 55,0 [45–64] | 79,0 [70–86] | 1,0 [0–5] | 2.777 |
| Gemma 3 4B | 1.969 | 63,0 [53–72] | 79,0 [70–86] | 3,0 [1–8] | 1.707 | 39,0 [30–49] | 63,0 [53–72] | 1,0 [0–5] | 1.906 |
| Gemma 3 12B | 5.790 | 61,0 [51–70] | 76,0 [67–83] | 12,0 [7–20] | 5.755 | 65,0 [55–74] | 77,0 [68–84] | 4,0 [2–10] | 7.273 |
| Qwen3.8-27B | 5.494 | 85,0 [77–91] | 92,0 [85–96] | 7,0 [3–14] | 5.774 | 81,0 [72–87] | 89,0 [81–94] | 6,0 [3–12] | 9.347 |
| Gemma 4 31B | 6.340 | 74,0 [65–82] | 86,0 [78–91] | 8,0 [4–15] | 6.423 | 84,0 [76–90] | 91,0 [84–95] | 3,0 [1–8] | 10.087 |
| **Todos** | **26.027** | **62,3 [59–66]** | **80,6 [78–84]** | **7,3 [5–10]** | **26.475** | **65,7 [62–69]** | **78,9 [76–82]** | **3,9 [2–6]** | **33.621** |

No total, das 52.502 tuplas retidas, 64,0 [62–67]% são válidas e 79,8 [78–82]% estão no domínio. Fora do domínio: 5,6 [4–7]%, dos quais lugar nomeado ou monumento como aspecto (`A2`): 2,4 [1–3]%. Sem opinião: 8,7 [7–10]%.

## Correção por campo

| Campo | SSA (%) | ASQP (%) |
|---|---:|---:|
| Aspecto correto | 81,3 [78–84] | 80,3 [77–83] |
| Expressão de opinião correta | 87,0 [85–89] | 85,9 [84–88] |
| Categoria correta | — | 95,7 [94–97] |
| Polaridade correta | 98,1 [97–99] | 97,7 [97–99] |
| Holder correto | 86,3 [84–89] | — |

## Códigos de erro na amostra

| Código | Ocorrências |
|---|---:|
| `A1` | 200 |
| `S1` | 197 |
| `H1` | 195 |
| `S2` | 121 |
| `A4` | 90 |
| `P1` | 64 |
| `C1` | 57 |
| `A3` | 42 |
| `O1` | 42 |
| `A2` | 30 |
| `S3` | 24 |

## Concordância e triagem lexical

157 itens julgados duas vezes: concordância bruta no veredito de 95,5%, kappa de Cohen (3 classes) de 0,92. Os juízes são o mesmo modelo, então isso mede consistência, não validade.

Triagem determinística sobre todas as 52.502 tuplas (seção 8 do guia): 108 (0,2%) têm lugar nomeado como aspecto. Mais frequentes: “Torre Eiffel” (12), “Bairro Saint Germain” (7), “Catedral do Sacre Coeur” (6), “avenida principal de LV” (5), “bairro Daumesnil” (5), “estação do Metrô Gare de Lyon” (4), “praça da Bastille” (4), “praça Vendome” (4), “Catedral do Sacre Coeur, maravilhosa” (4), “praça de Vendome 1 quarteirão” (4). Contagem por run em `semantic_audit_runs.csv`.

## Limites

- Vereditos de juízes LLM seguindo o guia, não de anotadores humanos; revise uma subamostra (seção 7 do guia) antes de citar como avaliação humana.
- Com 100 tuplas por run, cada célula tem margem de cerca de ±10 pontos percentuais.
- As taxas medem precisão das tuplas retidas, não cobertura.
