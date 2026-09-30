# Relatório da auditoria semântica

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`.
Amostra: 1944 tuplas sorteadas (até 50 por run, semente 20260930), 1817 itens únicos julgados. Segunda passada da regra de localização: 141 itens revisados (57 passaram a entorno aceito).
Percentuais com IC de 95%: Wilson por run; estimativa estratificada ponderada pelas tuplas retidas nos agregados.

**Validade estrita**: tupla correta em todos os campos. **Validade de domínio**: opinião real sobre o hotel, talvez com algum campo a corrigir. **Fora do domínio**: aspecto é rua, monumento, cidade, outro estabelecimento etc. (`A2`/`A3`).

## Visão geral

| Recorte | Tuplas retidas | Validade estrita (%) | Validade de domínio (%) | Fora do domínio (%) | Sem opinião (%) |
|---|---:|---:|---:|---:|---:|
| Todos os runs | 90.306 | 66,8 [64–69] | 82,0 [80–84] | 5,5 [4–7] | 6,5 [5–8] |
| SSA | 45.225 | 65,0 [61–69] | 82,6 [80–86] | 6,3 [4–8] | 5,7 [4–7] |
| ASQP | 45.081 | 68,6 [65–72] | 81,3 [78–84] | 4,7 [3–6] | 7,3 [6–9] |
| `full` | 52.502 | 63,7 [60–67] | 79,8 [77–83] | 6,2 [4–8] | 8,0 [6–10] |
| `no_retry` | 34.372 | 71,4 [68–75] | 85,8 [83–89] | 4,6 [3–7] | 4,6 [3–6] |
| `no_tags` | 3.432 | 68,7 [63–75] | 76,3 [71–82] | 3,0 [1–5] | 2,0 [0–4] |

## Resumo por modelo (todas as tarefas e configurações)

Detalhes de cada modelo em `audit/por_modelo/`.

| Modelo | Tuplas retidas | Amostradas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Fora do domínio (%) | Sem opinião (%) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B-Instruct | 709 | 200 | 164 | 23,3 [18–28] | 64,5 [59–70] | 3,6 [1–6] | 20,9 [16–26] |
| Qwen2.5-1.5B-Instruct | 5.274 | 200 | 1.528 | 29,0 [22–36] | 55,6 [48–63] | 8,1 [4–12] | 30,1 [23–37] |
| Qwen2.5-3B-Instruct | 5.450 | 206 | 1.704 | 31,3 [25–38] | 66,4 [59–74] | 3,2 [1–6] | 19,9 [14–26] |
| Qwen2.5-7B-Instruct | 7.600 | 215 | 4.272 | 56,2 [49–63] | 80,2 [74–86] | 3,2 [1–6] | 9,1 [5–13] |
| Qwen3.8-27B | 22.800 | 300 | 18.675 | 81,9 [77–87] | 89,6 [86–94] | 6,8 [3–10] | 1,5 [0–3] |
| gemma-4-31B-it | 25.371 | 300 | 19.367 | 76,3 [71–82] | 88,6 [85–92] | 4,1 [2–7] | 0,7 [0–2] |
| gemma-3-12b-it | 17.699 | 300 | 11.537 | 65,2 [58–72] | 78,2 [72–84] | 7,6 [4–11] | 7,3 [4–11] |
| gemma-3-4b-it | 5.403 | 223 | 3.098 | 57,3 [50–64] | 77,0 [71–83] | 3,1 [1–6] | 9,5 [6–13] |

## Tabela por modelo

Uma tabela por modelo: linhas por tarefa e configuração, IC de 95% entre colchetes, “censo” quando o run foi julgado por inteiro. O total pondera cada run pelas suas tuplas retidas.

### Qwen/Qwen2.5-0.5B-Instruct

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 219 | 50 | 48 | 22,0 [13–35] | 68,0 [54–79] | 2,0 [0–10] | 2,0 [0–10] | 16,0 [8–29] |
| SSA | `no_retry` | 195 | 50 | 27 | 14,0 [7–26] | 62,0 [48–74] | 2,0 [0–10] | 4,0 [1–13] | 28,0 [17–42] |
| SSA | `no_tags` | 0 | 0 | 0 | — | — | — | — | — |
| ASQP | `full` | 173 | 50 | 48 | 28,0 [17–42] | 62,0 [48–74] | 0,0 [0–7] | 0,0 [0–7] | 24,0 [14–37] |
| ASQP | `no_retry` | 122 | 50 | 41 | 34,0 [22–48] | 66,0 [52–78] | 0,0 [0–7] | 4,0 [1–13] | 14,0 [7–26] |
| ASQP | `no_tags` | 0 | 0 | 0 | — | — | — | — | — |
| **Total** | | **709** | **200** | **164** | **23,3 [18–28]** | **64,5 [59–70]** | **1,2 [0–3]** | **2,4 [1–4]** | **20,9 [16–26]** |

### Qwen/Qwen2.5-1.5B-Instruct

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 1.760 | 50 | 387 | 22,0 [13–35] | 62,0 [48–74] | 0,0 [0–7] | 2,0 [0–10] | 28,0 [17–42] |
| SSA | `no_retry` | 853 | 50 | 290 | 34,0 [22–48] | 58,0 [44–71] | 6,0 [2–16] | 4,0 [1–13] | 26,0 [16–40] |
| SSA | `no_tags` | 0 | 0 | 0 | — | — | — | — | — |
| ASQP | `full` | 1.869 | 50 | 598 | 32,0 [21–46] | 50,0 [37–63] | 2,0 [0–10] | 12,0 [6–24] | 34,0 [22–48] |
| ASQP | `no_retry` | 792 | 50 | 253 | 32,0 [21–46] | 52,0 [39–65] | 4,0 [1–13] | 2,0 [0–10] | 30,0 [19–44] |
| ASQP | `no_tags` | 0 | 0 | 0 | — | — | — | — | — |
| **Total** | | **5.274** | **200** | **1.528** | **29,0 [22–36]** | **55,6 [48–63]** | **2,3 [0–4]** | **5,9 [2–9]** | **30,1 [23–37]** |

### Qwen/Qwen2.5-3B-Instruct

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 1.909 | 50 | 229 | 12,0 [6–24] | 70,0 [56–81] | 4,0 [1–13] | 0,0 [0–7] | 16,0 [8–29] |
| SSA | `no_retry` | 674 | 50 | 148 | 22,0 [13–35] | 74,0 [60–84] | 2,0 [0–10] | 6,0 [2–16] | 10,0 [4–21] |
| SSA | `no_tags` | 2 | 2 | 2 | 100,0 (censo) | 100,0 (censo) | 0,0 (censo) | 0,0 (censo) | 0,0 (censo) |
| ASQP | `full` | 2.132 | 50 | 768 | 36,0 [24–50] | 54,0 [40–67] | 2,0 [0–10] | 0,0 [0–7] | 32,0 [21–46] |
| ASQP | `no_retry` | 729 | 50 | 554 | 76,0 [63–86] | 86,0 [74–93] | 0,0 [0–7] | 0,0 [0–7] | 4,0 [1–13] |
| ASQP | `no_tags` | 4 | 4 | 3 | 75,0 (censo) | 75,0 (censo) | 0,0 (censo) | 0,0 (censo) | 0,0 (censo) |
| **Total** | | **5.450** | **206** | **1.704** | **31,3 [25–38]** | **66,4 [59–74]** | **2,4 [0–5]** | **0,7 [0–2]** | **19,9 [14–26]** |

### Qwen/Qwen2.5-7B-Instruct

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 2.546 | 50 | 1.069 | 42,0 [29–56] | 74,0 [60–84] | 2,0 [0–10] | 2,0 [0–10] | 18,0 [10–31] |
| SSA | `no_retry` | 1.278 | 50 | 869 | 68,0 [54–79] | 92,0 [81–97] | 0,0 [0–7] | 0,0 [0–7] | 4,0 [1–13] |
| SSA | `no_tags` | 7 | 7 | 5 | 71,4 (censo) | 71,4 (censo) | 0,0 (censo) | 0,0 (censo) | 0,0 (censo) |
| ASQP | `full` | 2.642 | 50 | 1.427 | 54,0 [40–67] | 78,0 [65–87] | 2,0 [0–10] | 0,0 [0–7] | 6,0 [2–16] |
| ASQP | `no_retry` | 1.119 | 50 | 895 | 80,0 [67–89] | 86,0 [74–93] | 2,0 [0–10] | 6,0 [2–16] | 2,0 [0–10] |
| ASQP | `no_tags` | 8 | 8 | 7 | 87,5 (censo) | 100,0 (censo) | 0,0 (censo) | 0,0 (censo) | 0,0 (censo) |
| **Total** | | **7.600** | **215** | **4.272** | **56,2 [49–63]** | **80,2 [74–86]** | **1,7 [0–4]** | **1,6 [0–3]** | **9,1 [5–13]** |

### Qwen/Qwen3.8-27B

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 5.494 | 50 | 4.725 | 86,0 [74–93] | 92,0 [81–97] | 2,0 [0–10] | 4,0 [1–13] | 4,0 [1–13] |
| SSA | `no_retry` | 5.089 | 50 | 4.377 | 86,0 [74–93] | 92,0 [81–97] | 0,0 [0–7] | 2,0 [0–10] | 0,0 [0–7] |
| SSA | `no_tags` | 655 | 50 | 432 | 66,0 [52–78] | 76,0 [63–86] | 2,0 [0–10] | 0,0 [0–7] | 0,0 [0–7] |
| ASQP | `full` | 5.774 | 50 | 4.504 | 78,0 [65–87] | 88,0 [76–94] | 6,0 [2–16] | 4,0 [1–13] | 2,0 [0–10] |
| ASQP | `no_retry` | 5.243 | 50 | 4.299 | 82,0 [69–90] | 90,0 [79–96] | 4,0 [1–13] | 6,0 [2–16] | 0,0 [0–7] |
| ASQP | `no_tags` | 545 | 50 | 338 | 62,0 [48–74] | 74,0 [60–84] | 0,0 [0–7] | 0,0 [0–7] | 0,0 [0–7] |
| **Total** | | **22.800** | **300** | **18.675** | **81,9 [77–87]** | **89,6 [86–94]** | **3,0 [1–5]** | **3,8 [1–6]** | **1,5 [0–3]** |

### google/gemma-4-31B-it

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 6.340 | 50 | 4.311 | 68,0 [54–79] | 84,0 [71–92] | 0,0 [0–7] | 10,0 [4–21] | 0,0 [0–7] |
| SSA | `no_retry` | 5.375 | 50 | 3.655 | 68,0 [54–79] | 86,0 [74–93] | 2,0 [0–10] | 4,0 [1–13] | 0,0 [0–7] |
| SSA | `no_tags` | 1.077 | 50 | 775 | 72,0 [58–83] | 80,0 [67–89] | 2,0 [0–10] | 4,0 [1–13] | 2,0 [0–10] |
| ASQP | `full` | 6.423 | 50 | 5.652 | 88,0 [76–94] | 94,0 [84–98] | 0,0 [0–7] | 0,0 [0–7] | 2,0 [0–10] |
| ASQP | `no_retry` | 5.228 | 50 | 4.287 | 82,0 [69–90] | 94,0 [84–98] | 0,0 [0–7] | 0,0 [0–7] | 0,0 [0–7] |
| ASQP | `no_tags` | 928 | 50 | 687 | 74,0 [60–84] | 76,0 [63–86] | 2,0 [0–10] | 0,0 [0–7] | 4,0 [1–13] |
| **Total** | | **25.371** | **300** | **19.367** | **76,3 [71–82]** | **88,6 [85–92]** | **0,6 [0–1]** | **3,5 [1–6]** | **0,7 [0–2]** |

### unsloth/gemma-3-12b-it

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 5.790 | 50 | 4.053 | 70,0 [56–81] | 82,0 [69–90] | 8,0 [3–19] | 4,0 [1–13] | 2,0 [0–10] |
| SSA | `no_retry` | 2.963 | 50 | 2.015 | 68,0 [54–79] | 80,0 [67–89] | 2,0 [0–10] | 4,0 [1–13] | 12,0 [6–24] |
| SSA | `no_tags` | 82 | 50 | 52 | 64,0 [50–76] | 72,0 [58–83] | 0,0 [0–7] | 0,0 [0–7] | 6,0 [2–16] |
| ASQP | `full` | 5.755 | 50 | 3.568 | 62,0 [48–74] | 72,0 [58–83] | 2,0 [0–10] | 4,0 [1–13] | 10,0 [4–21] |
| ASQP | `no_retry` | 3.008 | 50 | 1.805 | 60,0 [46–72] | 82,0 [69–90] | 2,0 [0–10] | 2,0 [0–10] | 8,0 [3–19] |
| ASQP | `no_tags` | 101 | 50 | 44 | 44,0 [31–58] | 58,0 [44–71] | 0,0 [0–7] | 4,0 [1–13] | 4,0 [1–13] |
| **Total** | | **17.699** | **300** | **11.537** | **65,2 [58–72]** | **78,2 [72–84]** | **3,9 [1–7]** | **3,6 [1–6]** | **7,3 [4–11]** |

### unsloth/gemma-3-4b-it

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 1.969 | 50 | 1.300 | 66,0 [52–78] | 82,0 [69–90] | 2,0 [0–10] | 4,0 [1–13] | 2,0 [0–10] |
| SSA | `no_retry` | 938 | 50 | 638 | 68,0 [54–79] | 80,0 [67–89] | 0,0 [0–7] | 2,0 [0–10] | 14,0 [7–26] |
| SSA | `no_tags` | 10 | 10 | 7 | 70,0 (censo) | 90,0 (censo) | 0,0 (censo) | 0,0 (censo) | 0,0 (censo) |
| ASQP | `full` | 1.707 | 50 | 751 | 44,0 [31–58] | 70,0 [56–81] | 0,0 [0–7] | 0,0 [0–7] | 12,0 [6–24] |
| ASQP | `no_retry` | 766 | 50 | 398 | 52,0 [39–65] | 76,0 [63–86] | 2,0 [0–10] | 2,0 [0–10] | 18,0 [10–31] |
| ASQP | `no_tags` | 13 | 13 | 4 | 30,8 (censo) | 53,8 (censo) | 7,7 (censo) | 0,0 (censo) | 15,4 (censo) |
| **Total** | | **5.403** | **223** | **3.098** | **57,3 [50–64]** | **77,0 [71–83]** | **1,0 [0–3]** | **2,1 [0–4]** | **9,5 [6–13]** |

## Erros por modelo (% estimado das tuplas retidas)

| Modelo | `A1` | `A2` | `A3` | `A4` | `O1` | `O2` | `S1` | `S2` | `S3` | `C1` | `P1` | `H1` | `D1` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B-Instruct | 18,3 | 1,2 | 2,4 | 3,2 | 2,6 | 0,0 | 18,8 | 22,4 | 0,0 | 7,8 | 9,8 | 40,8 | 0,0 |
| Qwen2.5-1.5B-Instruct | 19,1 | 2,3 | 5,9 | 6,0 | 8,4 | 0,0 | 23,0 | 18,6 | 2,1 | 4,0 | 6,6 | 5,9 | 0,0 |
| Qwen2.5-3B-Instruct | 15,3 | 2,4 | 0,7 | 6,6 | 1,6 | 0,0 | 18,3 | 9,9 | 0,9 | 2,6 | 8,7 | 28,9 | 0,0 |
| Qwen2.5-7B-Instruct | 8,2 | 1,7 | 1,6 | 5,1 | 4,0 | 0,0 | 5,0 | 2,7 | 4,7 | 3,8 | 3,8 | 13,1 | 0,0 |
| Qwen3.8-27B | 3,1 | 3,0 | 3,8 | 2,8 | 0,5 | 0,0 | 1,0 | 0,7 | 1,6 | 1,9 | 0,4 | 0,5 | 0,0 |
| gemma-4-31B-it | 7,1 | 0,6 | 3,5 | 4,5 | 0,2 | 0,0 | 0,6 | 0,0 | 0,0 | 0,9 | 0,5 | 8,5 | 0,0 |
| gemma-3-12b-it | 7,9 | 3,9 | 3,6 | 3,3 | 2,4 | 0,0 | 5,0 | 4,7 | 2,3 | 2,4 | 4,0 | 1,3 | 0,0 |
| gemma-3-4b-it | 12,6 | 1,0 | 2,1 | 5,3 | 4,6 | 0,0 | 5,3 | 8,3 | 0,0 | 5,5 | 3,7 | 2,5 | 0,0 |

Percentuais sobre todas as tuplas do modelo (SSA + ASQP). `H1` só existe em SSA e `C1` só em ASQP; a taxa por tarefa está em `audit/por_modelo/`. Uma tupla pode ter mais de um código.

## Por modelo e configuração (SSA + ASQP)

| Modelo | Config | Tuplas retidas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Fora do domínio (%) |
|---|---|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B-Instruct | `full` | 392 | 96 | 24,6 [17–32] | 65,4 [57–73] | 2,2 [0–5] |
| Qwen2.5-0.5B-Instruct | `no_retry` | 317 | 68 | 21,7 [15–28] | 63,5 [55–72] | 5,2 [1–9] |
| Qwen2.5-0.5B-Instruct | `no_tags` | 0 | 0 | — | — | — |
| Qwen2.5-1.5B-Instruct | `full` | 3.629 | 985 | 27,2 [19–36] | 55,8 [46–65] | 8,2 [3–13] |
| Qwen2.5-1.5B-Instruct | `no_retry` | 1.645 | 543 | 33,0 [24–42] | 55,1 [46–65] | 8,1 [3–13] |
| Qwen2.5-1.5B-Instruct | `no_tags` | 0 | 0 | — | — | — |
| Qwen2.5-3B-Instruct | `full` | 4.041 | 997 | 24,7 [17–33] | 61,6 [52–71] | 2,9 [0–6] |
| Qwen2.5-3B-Instruct | `no_retry` | 1.403 | 702 | 50,1 [42–58] | 80,2 [73–88] | 3,8 [0–7] |
| Qwen2.5-3B-Instruct | `no_tags` | 6 | 5 | 83,3 [83–83] | 83,3 [83–83] | 0,0 [0–0] |
| Qwen2.5-7B-Instruct | `full` | 5.188 | 2.496 | 48,1 [38–58] | 76,0 [68–84] | 3,0 [0–6] |
| Qwen2.5-7B-Instruct | `no_retry` | 2.397 | 1.764 | 73,6 [65–82] | 89,2 [83–95] | 3,7 [0–7] |
| Qwen2.5-7B-Instruct | `no_tags` | 15 | 12 | 80,0 [80–80] | 86,7 [87–87] | 0,0 [0–0] |
| Qwen3.8-27B | `full` | 11.268 | 9.229 | 81,9 [74–89] | 90,0 [84–96] | 8,0 [3–13] |
| Qwen3.8-27B | `no_retry` | 10.332 | 8.676 | 84,0 [77–91] | 91,0 [85–97] | 6,1 [1–11] |
| Qwen3.8-27B | `no_tags` | 1.200 | 770 | 64,2 [55–73] | 75,1 [67–83] | 1,1 [0–3] |
| gemma-4-31B-it | `full` | 12.763 | 9.963 | 78,1 [70–86] | 89,0 [83–95] | 5,0 [1–9] |
| gemma-4-31B-it | `no_retry` | 10.603 | 7.942 | 74,9 [67–83] | 89,9 [84–96] | 3,0 [0–6] |
| gemma-4-31B-it | `no_tags` | 2.005 | 1.462 | 72,9 [64–81] | 78,1 [70–86] | 4,1 [0–8] |
| gemma-3-12b-it | `full` | 11.545 | 7.621 | 66,0 [57–75] | 77,0 [69–85] | 9,0 [3–15] |
| gemma-3-12b-it | `no_retry` | 5.971 | 3.820 | 64,0 [55–73] | 81,0 [73–89] | 5,0 [1–9] |
| gemma-3-12b-it | `no_tags` | 183 | 96 | 53,0 [46–60] | 64,3 [58–71] | 2,2 [0–4] |
| gemma-3-4b-it | `full` | 3.676 | 2.051 | 55,8 [46–65] | 76,4 [68–85] | 3,2 [0–7] |
| gemma-3-4b-it | `no_retry` | 1.704 | 1.036 | 60,8 [52–70] | 78,2 [70–86] | 2,9 [0–6] |
| gemma-3-4b-it | `no_tags` | 23 | 11 | 47,8 [48–48] | 69,6 [70–70] | 4,3 [4–4] |

## Correção por campo (todos os runs, estratificado)

| Campo | SSA (%) | ASQP (%) |
|---|---:|---:|
| Aspecto correto | 82,8 [80–86] | 82,3 [79–85] |
| Expressão de opinião correta | 89,0 [87–91] | 88,0 [86–90] |
| Categoria correta | — | 95,4 [94–97] |
| Polaridade correta | 97,4 [96–98] | 97,5 [96–99] |
| Holder correto | 87,2 [85–90] | — |
| Aspecto geográfico (`A2`) | 2,2 [1–3] | 2,1 [1–3] |

## Frequência dos códigos de erro na amostra

| Código | Ocorrências |
|---|---:|
| `A1` | 245 |
| `H1` | 198 |
| `S1` | 145 |
| `S2` | 136 |
| `A4` | 85 |
| `P1` | 77 |
| `C1` | 73 |
| `O1` | 59 |
| `A3` | 52 |
| `A2` | 35 |
| `S3` | 23 |

## Concordância entre juízes

184 itens julgados duas vezes. Concordância bruta no veredito: 93,5%; kappa de Cohen (3 classes): 0,89.
Concordância na marcação de fora do domínio: 98,4%.

## Triagem lexical sobre todas as tuplas

Limite inferior determinístico (seção 8 do guia): lugar nomeado como aspecto (marcador geográfico + nome próprio), entorno genérico (aceito) e aspecto que é só palavra funcional ou intensificador.

| Modelo | Config | Tarefa | Tuplas | Lugar nomeado (`A2`) | Entorno genérico (aceito) | Aspecto funcional (`A1`) |
|---|---|---|---:|---:|---:|---:|
| Qwen2.5-0.5B-Instruct | `full` | ssa | 219 | 0 (0,0%) | 6 (2,7%) | 6 (2,7%) |
| Qwen2.5-0.5B-Instruct | `full` | asqp | 173 | 0 (0,0%) | 1 (0,6%) | 3 (1,7%) |
| Qwen2.5-0.5B-Instruct | `no_retry` | ssa | 195 | 0 (0,0%) | 6 (3,1%) | 4 (2,1%) |
| Qwen2.5-0.5B-Instruct | `no_retry` | asqp | 122 | 0 (0,0%) | 1 (0,8%) | 3 (2,5%) |
| Qwen2.5-1.5B-Instruct | `full` | ssa | 1.760 | 2 (0,1%) | 28 (1,6%) | 90 (5,1%) |
| Qwen2.5-1.5B-Instruct | `full` | asqp | 1.869 | 4 (0,2%) | 23 (1,2%) | 60 (3,2%) |
| Qwen2.5-1.5B-Instruct | `no_retry` | ssa | 853 | 0 (0,0%) | 10 (1,2%) | 7 (0,8%) |
| Qwen2.5-1.5B-Instruct | `no_retry` | asqp | 792 | 0 (0,0%) | 10 (1,3%) | 6 (0,8%) |
| Qwen2.5-3B-Instruct | `full` | ssa | 1.909 | 0 (0,0%) | 15 (0,8%) | 52 (2,7%) |
| Qwen2.5-3B-Instruct | `full` | asqp | 2.132 | 5 (0,2%) | 26 (1,2%) | 73 (3,4%) |
| Qwen2.5-3B-Instruct | `no_retry` | ssa | 674 | 0 (0,0%) | 4 (0,6%) | 1 (0,1%) |
| Qwen2.5-3B-Instruct | `no_retry` | asqp | 729 | 1 (0,1%) | 12 (1,6%) | 1 (0,1%) |
| Qwen2.5-3B-Instruct | `no_tags` | ssa | 2 | 0 (0,0%) | 0 (0,0%) | 0 (0,0%) |
| Qwen2.5-3B-Instruct | `no_tags` | asqp | 4 | 0 (0,0%) | 0 (0,0%) | 0 (0,0%) |
| Qwen2.5-7B-Instruct | `full` | ssa | 2.546 | 6 (0,2%) | 23 (0,9%) | 41 (1,6%) |
| Qwen2.5-7B-Instruct | `full` | asqp | 2.642 | 9 (0,3%) | 33 (1,2%) | 34 (1,3%) |
| Qwen2.5-7B-Instruct | `no_retry` | ssa | 1.278 | 0 (0,0%) | 8 (0,6%) | 5 (0,4%) |
| Qwen2.5-7B-Instruct | `no_retry` | asqp | 1.119 | 1 (0,1%) | 14 (1,3%) | 1 (0,1%) |
| Qwen2.5-7B-Instruct | `no_tags` | ssa | 7 | 0 (0,0%) | 0 (0,0%) | 0 (0,0%) |
| Qwen2.5-7B-Instruct | `no_tags` | asqp | 8 | 0 (0,0%) | 0 (0,0%) | 0 (0,0%) |
| Qwen3.8-27B | `full` | ssa | 5.494 | 4 (0,1%) | 50 (0,9%) | 23 (0,4%) |
| Qwen3.8-27B | `full` | asqp | 5.774 | 8 (0,1%) | 84 (1,5%) | 15 (0,3%) |
| Qwen3.8-27B | `no_retry` | ssa | 5.089 | 5 (0,1%) | 48 (0,9%) | 19 (0,4%) |
| Qwen3.8-27B | `no_retry` | asqp | 5.243 | 6 (0,1%) | 74 (1,4%) | 14 (0,3%) |
| Qwen3.8-27B | `no_tags` | ssa | 655 | 0 (0,0%) | 6 (0,9%) | 3 (0,5%) |
| Qwen3.8-27B | `no_tags` | asqp | 545 | 0 (0,0%) | 4 (0,7%) | 3 (0,6%) |
| gemma-4-31B-it | `full` | ssa | 6.340 | 6 (0,1%) | 78 (1,2%) | 39 (0,6%) |
| gemma-4-31B-it | `full` | asqp | 6.423 | 11 (0,2%) | 93 (1,4%) | 25 (0,4%) |
| gemma-4-31B-it | `no_retry` | ssa | 5.375 | 7 (0,1%) | 64 (1,2%) | 31 (0,6%) |
| gemma-4-31B-it | `no_retry` | asqp | 5.228 | 9 (0,2%) | 72 (1,4%) | 18 (0,3%) |
| gemma-4-31B-it | `no_tags` | ssa | 1.077 | 0 (0,0%) | 7 (0,6%) | 8 (0,7%) |
| gemma-4-31B-it | `no_tags` | asqp | 928 | 1 (0,1%) | 7 (0,8%) | 5 (0,5%) |
| gemma-3-12b-it | `full` | ssa | 5.790 | 21 (0,4%) | 79 (1,4%) | 15 (0,3%) |
| gemma-3-12b-it | `full` | asqp | 5.755 | 29 (0,5%) | 88 (1,5%) | 26 (0,5%) |
| gemma-3-12b-it | `no_retry` | ssa | 2.963 | 6 (0,2%) | 33 (1,1%) | 5 (0,2%) |
| gemma-3-12b-it | `no_retry` | asqp | 3.008 | 8 (0,3%) | 41 (1,4%) | 8 (0,3%) |
| gemma-3-12b-it | `no_tags` | ssa | 82 | 0 (0,0%) | 1 (1,2%) | 1 (1,2%) |
| gemma-3-12b-it | `no_tags` | asqp | 101 | 0 (0,0%) | 1 (1,0%) | 1 (1,0%) |
| gemma-3-4b-it | `full` | ssa | 1.969 | 3 (0,2%) | 15 (0,8%) | 60 (3,0%) |
| gemma-3-4b-it | `full` | asqp | 1.707 | 0 (0,0%) | 17 (1,0%) | 99 (5,8%) |
| gemma-3-4b-it | `no_retry` | ssa | 938 | 1 (0,1%) | 7 (0,7%) | 5 (0,5%) |
| gemma-3-4b-it | `no_retry` | asqp | 766 | 0 (0,0%) | 5 (0,7%) | 4 (0,5%) |
| gemma-3-4b-it | `no_tags` | ssa | 10 | 0 (0,0%) | 0 (0,0%) | 0 (0,0%) |
| gemma-3-4b-it | `no_tags` | asqp | 13 | 0 (0,0%) | 0 (0,0%) | 0 (0,0%) |

Total: 153 de 90.306 tuplas (0,2%) têm um lugar nomeado como aspecto. Termos mais frequentes (gerados pelos modelos): “Torre Eiffel” (13), “Bairro Saint Germain” (11), “Catedral do Sacre Coeur” (10), “praça Vendome” (10), “estação do Metrô Gare de Lyon” (8), “avenida principal de LV” (7), “praça da Bastille” (7), “praça de Vendome 1 quarteirão” (6), “rua do Louvre - Rue de Rivoli” (5), “mercado dos Enfants Rouge” (5), “bairro Daumesnil” (5), “Torre Eifel” (5), “praça de Vendome” (4), “Rua do Comércio” (4), “Catedral do Sacre Coeur, maravilhosa” (4).

## Limites

- Os vereditos foram emitidos por juízes LLM seguindo o guia; antes de citar estas taxas como avaliação humana, revise uma subamostra conforme a seção 7 do guia.
- As taxas medem precisão semântica das tuplas retidas, não cobertura.
- Runs com até 50 tuplas foram julgados por inteiro: o intervalo degenerado (ex.: [83–83]) indica censo, sem erro amostral, mas ainda sujeito ao erro dos juízes. Runs pequenos têm pouca informação; ver `semantic_audit_runs.csv`.
