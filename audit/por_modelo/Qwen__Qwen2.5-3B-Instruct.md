# Auditoria semântica: Qwen/Qwen2.5-3B-Instruct

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Visão comparativa em `audit/RELATORIO_AUDITORIA_SEMANTICA.md`.

**5.450 tuplas retidas** nos 6 runs; 206 julgadas. Estimativa de **1.704 válidas** sem correção e **3.618** opiniões reais sobre o hotel.

| Métrica (todas as tarefas e configurações) | % [IC 95%] |
|---|---:|
| Validade estrita | 31,3 [25–38] |
| Validade de domínio | 66,4 [59–74] |
| Fora do domínio (`A2`/`A3`) | 3,2 [1–6] |
| Sem opinião (`O1`/`O2`/`S1`) | 19,9 [14–26] |

## Por tarefa e configuração

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 1.909 | 50 | 229 | 12,0 [6–24] | 70,0 [56–81] | 4,0 [1–13] | 0,0 [0–7] | 16,0 [8–29] |
| SSA | `no_retry` | 674 | 50 | 148 | 22,0 [13–35] | 74,0 [60–84] | 2,0 [0–10] | 6,0 [2–16] | 10,0 [4–21] |
| SSA | `no_tags` | 2 | 2 | 2 | 100,0 (censo) | 100,0 (censo) | 0,0 (censo) | 0,0 (censo) | 0,0 (censo) |
| ASQP | `full` | 2.132 | 50 | 768 | 36,0 [24–50] | 54,0 [40–67] | 2,0 [0–10] | 0,0 [0–7] | 32,0 [21–46] |
| ASQP | `no_retry` | 729 | 50 | 554 | 76,0 [63–86] | 86,0 [74–93] | 0,0 [0–7] | 0,0 [0–7] | 4,0 [1–13] |
| ASQP | `no_tags` | 4 | 4 | 3 | 75,0 (censo) | 75,0 (censo) | 0,0 (censo) | 0,0 (censo) | 0,0 (censo) |
| **Total** | | **5.450** | **206** | **1.704** | **31,3 [25–38]** | **66,4 [59–74]** | **2,4 [0–5]** | **0,7 [0–2]** | **19,9 [14–26]** |

## Correção por campo

| Campo | SSA (%) | ASQP (%) |
|---|---:|---:|
| Aspecto correto | 74,1 [65–84] | 75,6 [66–85] |
| Expressão de opinião correta | 73,7 [64–83] | 65,2 [55–76] |
| Categoria correta | — | 95,0 [90–100] |
| Polaridade correta | 91,6 [85–98] | 91,1 [84–98] |
| Holder correto | 39,0 [29–49] | — |

## Erros (% estimado das tuplas retidas)

| Código | Significado | SSA (%) | ASQP (%) |
|---|---|---:|---:|
| `A1` | aspecto não é alvo | 12,9 | 17,5 |
| `A2` | lugar nomeado como aspecto | 3,5 | 1,5 |
| `A3` | entidade fora do domínio | 1,6 | 0,0 |
| `A4` | aspecto não pareado com a opinião | 7,9 | 5,5 |
| `O1` | sem avaliação | 0,5 | 2,5 |
| `S1` | expressão não avaliativa | 13,9 | 22,3 |
| `S2` | expressão incompleta | 9,9 | 9,9 |
| `S3` | expressão excessiva | 2,0 | 0,0 |
| `C1` | categoria errada | 0,0 | 5,0 |
| `P1` | polaridade errada | 8,4 | 8,9 |
| `H1` | holder errado | 61,0 | 0,0 |

## Triagem lexical (todas as tuplas do modelo)

Lugar nomeado como aspecto: 6 de 5.450 tuplas (0,1%). Termos mais frequentes: “Torre Eifel” (2), “Mercado Publico” (1), “Torre Eiffel, exatamente em frente a uma estação do metro, a dois passos da Rue Passy” (1), “estação do metrô da Union Square” (1), “Jardim de Luxembourg” (1).
Aspecto funcional ou intensificador: 127. Entorno genérico (aceito): 57.

## Limites

- Vereditos de juízes LLM; ver a seção 7 do guia antes de citar como avaliação humana.
- Runs com até 50 tuplas foram julgados por inteiro e aparecem como “censo”: não há erro amostral, mas há o erro dos juízes.
- Os percentuais agregados ponderam cada run pelas suas tuplas retidas.
