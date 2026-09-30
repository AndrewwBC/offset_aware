# Auditoria semântica: Qwen/Qwen3.8-27B

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Visão comparativa em `audit/RELATORIO_AUDITORIA_SEMANTICA.md`.

**22.800 tuplas retidas** nos 6 runs; 300 julgadas. Estimativa de **18.675 válidas** sem correção e **20.437** opiniões reais sobre o hotel.

| Métrica (todas as tarefas e configurações) | % [IC 95%] |
|---|---:|
| Validade estrita | 81,9 [77–87] |
| Validade de domínio | 89,6 [86–94] |
| Fora do domínio (`A2`/`A3`) | 6,8 [3–10] |
| Sem opinião (`O1`/`O2`/`S1`) | 1,5 [0–3] |

## Por tarefa e configuração

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 5.494 | 50 | 4.725 | 86,0 [74–93] | 92,0 [81–97] | 2,0 [0–10] | 4,0 [1–13] | 4,0 [1–13] |
| SSA | `no_retry` | 5.089 | 50 | 4.377 | 86,0 [74–93] | 92,0 [81–97] | 0,0 [0–7] | 2,0 [0–10] | 0,0 [0–7] |
| SSA | `no_tags` | 655 | 50 | 432 | 66,0 [52–78] | 76,0 [63–86] | 2,0 [0–10] | 0,0 [0–7] | 0,0 [0–7] |
| ASQP | `full` | 5.774 | 50 | 4.504 | 78,0 [65–87] | 88,0 [76–94] | 6,0 [2–16] | 4,0 [1–13] | 2,0 [0–10] |
| ASQP | `no_retry` | 5.243 | 50 | 4.299 | 82,0 [69–90] | 90,0 [79–96] | 4,0 [1–13] | 6,0 [2–16] | 0,0 [0–7] |
| ASQP | `no_tags` | 545 | 50 | 338 | 62,0 [48–74] | 74,0 [60–84] | 0,0 [0–7] | 0,0 [0–7] | 0,0 [0–7] |
| **Total** | | **22.800** | **300** | **18.675** | **81,9 [77–87]** | **89,6 [86–94]** | **3,0 [1–5]** | **3,8 [1–6]** | **1,5 [0–3]** |

## Correção por campo

| Campo | SSA (%) | ASQP (%) |
|---|---:|---:|
| Aspecto correto | 87,7 [82–94] | 87,0 [81–93] |
| Expressão de opinião correta | 96,9 [94–100] | 95,6 [92–99] |
| Categoria correta | — | 96,2 [93–100] |
| Polaridade correta | 99,1 [97–100] | 100,0 [100–100] |
| Holder correto | 99,0 [97–100] | — |

## Erros (% estimado das tuplas retidas)

| Código | Significado | SSA (%) | ASQP (%) |
|---|---|---:|---:|
| `A1` | aspecto não é alvo | 5,0 | 1,2 |
| `A2` | lugar nomeado como aspecto | 1,1 | 4,8 |
| `A3` | entidade fora do domínio | 2,9 | 4,7 |
| `A4` | aspecto não pareado com a opinião | 3,3 | 2,3 |
| `O1` | sem avaliação | 1,0 | 0,0 |
| `S1` | expressão não avaliativa | 1,0 | 1,0 |
| `S2` | expressão incompleta | 1,1 | 0,2 |
| `S3` | expressão excessiva | 0,0 | 3,2 |
| `C1` | categoria errada | 0,0 | 3,8 |
| `P1` | polaridade errada | 0,9 | 0,0 |
| `H1` | holder errado | 1,0 | 0,0 |

## Triagem lexical (todas as tuplas do modelo)

Lugar nomeado como aspecto: 23 de 22.800 tuplas (0,1%). Termos mais frequentes: “rua do Louvre - Rue de Rivoli” (4), “Bairro Saint Germain” (4), “Catedral do Sacre Coeur” (4), “estação do Metrô Gare de Lyon” (4), “avenida principal de LV” (2), “estação Cambronne de metro” (2), “Cidade Luz” (1), “TOrre Eiffel” (1), “praça Vendome” (1).
Aspecto funcional ou intensificador: 77. Entorno genérico (aceito): 266.

## Limites

- Vereditos de juízes LLM; ver a seção 7 do guia antes de citar como avaliação humana.
- Runs com até 50 tuplas foram julgados por inteiro e aparecem como “censo”: não há erro amostral, mas há o erro dos juízes.
- Os percentuais agregados ponderam cada run pelas suas tuplas retidas.
