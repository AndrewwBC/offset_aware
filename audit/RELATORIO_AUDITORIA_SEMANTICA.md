# Relatório da auditoria semântica

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Configuração auditada: `full`.
Amostra: 800 tuplas sorteadas uniformemente, 100 por run (semente 20260930), 784 itens únicos julgados. Segunda passada da regra de localização em 107 itens.
Percentuais sobre as tuplas retidas, com IC de 95% (Wilson por run; estimativa estratificada ponderada pelas tuplas retidas nos totais).

**Válidas**: corretas em todos os campos. **No domínio**: opinião real sobre o hotel, talvez com algum campo a corrigir. **Fora do domínio**: aspecto é lugar nomeado ou monumento (`A2`) ou outra entidade fora do hotel (`A3`).

## Tabela por modelo

| Modelo | Retidas | Válidas (%) | No domínio (%) | Fora do domínio (%) | Válidas estimadas |
|---|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B | 173 | 29,0 [21–39] | 58,0 [48–67] | 1,0 [0–5] | 50 |
| Qwen2.5-1.5B | 1.869 | 29,0 [21–39] | 50,0 [40–60] | 10,0 [6–17] | 542 |
| Qwen2.5-3B | 2.132 | 41,0 [32–51] | 60,0 [50–69] | 2,0 [1–7] | 874 |
| Qwen2.5-7B | 2.642 | 55,0 [45–64] | 79,0 [70–86] | 1,0 [0–5] | 1.453 |
| Gemma 3 4B | 1.707 | 39,0 [30–49] | 63,0 [53–72] | 1,0 [0–5] | 666 |
| Gemma 3 12B | 5.755 | 65,0 [55–74] | 77,0 [68–84] | 4,0 [2–10] | 3.741 |
| Qwen3.8-27B | 5.774 | 81,0 [72–87] | 89,0 [81–94] | 6,0 [3–12] | 4.677 |
| Gemma 4 31B | 6.423 | 84,0 [76–90] | 91,0 [84–95] | 3,0 [1–8] | 5.395 |
| **Todos** | **26.475** | **65,7 [62–69]** | **78,9 [76–82]** | **3,9 [2–6]** | **17.398** |

No total, das 26.475 tuplas retidas, 65,7 [62–69]% são válidas e 78,9 [76–82]% estão no domínio. Fora do domínio: 3,9 [2–6]%, dos quais lugar nomeado ou monumento como aspecto (`A2`): 2,2 [1–3]%. Sem opinião: 9,6 [8–11]%.

## Correção por campo

| Campo | Corretos (%) |
|---|---:|
| Aspecto correto | 80,3 [77–83] |
| Expressão de opinião correta | 85,9 [84–88] |
| Categoria correta | 95,7 [94–97] |
| Polaridade correta | 97,7 [97–99] |

## Códigos de erro na amostra

| Código | Ocorrências |
|---|---:|
| `A1` | 119 |
| `S1` | 114 |
| `C1` | 57 |
| `S2` | 53 |
| `A4` | 47 |
| `P1` | 33 |
| `O1` | 22 |
| `A3` | 15 |
| `A2` | 13 |
| `S3` | 12 |

## Concordância e triagem lexical

78 itens julgados duas vezes: concordância bruta no veredito de 93,6%, kappa de Cohen (3 classes) de 0,89. Os juízes são o mesmo modelo, então isso mede consistência, não validade.

Triagem determinística sobre todas as 26.475 tuplas (seção 8 do guia): 66 (0,2%) têm lugar nomeado como aspecto. Mais frequentes: “Torre Eiffel” (6), “avenida principal de LV” (4), “Bairro Saint Germain” (4), “Catedral do Sacre Coeur” (3), “estação do Metrô Gare de Lyon” (3), “bairro Daumesnil” (3), “Jardim de Luxembourg” (3), “estação Cambronne de metro” (2), “TOrre Eiffel” (2), “praça da Bastille” (2). Contagem por run em `semantic_audit_runs.csv`.

## Limites

- Vereditos de juízes LLM seguindo o guia, não de anotadores humanos; revise uma subamostra (seção 7 do guia) antes de citar como avaliação humana.
- Com 100 tuplas por run, cada célula tem margem de cerca de ±10 pontos percentuais.
- As taxas medem precisão das tuplas retidas, não cobertura.
