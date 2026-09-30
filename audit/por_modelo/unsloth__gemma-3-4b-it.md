# Auditoria semântica: unsloth/gemma-3-4b-it

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Visão comparativa em `audit/RELATORIO_AUDITORIA_SEMANTICA.md`.

**5.403 tuplas retidas** nos 6 runs; 223 julgadas. Estimativa de **3.098 válidas** sem correção e **4.158** opiniões reais sobre o hotel.

| Métrica (todas as tarefas e configurações) | % [IC 95%] |
|---|---:|
| Validade estrita | 57,3 [50–64] |
| Validade de domínio | 77,0 [71–83] |
| Fora do domínio (`A2`/`A3`) | 3,1 [1–6] |
| Sem opinião (`O1`/`O2`/`S1`) | 9,5 [6–13] |

## Por tarefa e configuração

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 1.969 | 50 | 1.300 | 66,0 [52–78] | 82,0 [69–90] | 2,0 [0–10] | 4,0 [1–13] | 2,0 [0–10] |
| SSA | `no_retry` | 938 | 50 | 638 | 68,0 [54–79] | 80,0 [67–89] | 0,0 [0–7] | 2,0 [0–10] | 14,0 [7–26] |
| SSA | `no_tags` | 10 | 10 | 7 | 70,0 (censo) | 90,0 (censo) | 0,0 (censo) | 0,0 (censo) | 0,0 (censo) |
| ASQP | `full` | 1.707 | 50 | 751 | 44,0 [31–58] | 70,0 [56–81] | 0,0 [0–7] | 0,0 [0–7] | 12,0 [6–24] |
| ASQP | `no_retry` | 766 | 50 | 398 | 52,0 [39–65] | 76,0 [63–86] | 2,0 [0–10] | 2,0 [0–10] | 18,0 [10–31] |
| ASQP | `no_tags` | 13 | 13 | 4 | 30,8 (censo) | 53,8 (censo) | 7,7 (censo) | 0,0 (censo) | 15,4 (censo) |
| **Total** | | **5.403** | **223** | **3.098** | **57,3 [50–64]** | **77,0 [71–83]** | **1,0 [0–3]** | **2,1 [0–4]** | **9,5 [6–13]** |

## Correção por campo

| Campo | SSA (%) | ASQP (%) |
|---|---:|---:|
| Aspecto correto | 84,0 [76–92] | 73,0 [64–82] |
| Expressão de opinião correta | 86,1 [79–93] | 77,6 [69–86] |
| Categoria correta | — | 88,1 [82–95] |
| Polaridade correta | 96,6 [93–100] | 96,0 [92–100] |
| Holder correto | 95,4 [91–100] | — |

## Erros (% estimado das tuplas retidas)

| Código | Significado | SSA (%) | ASQP (%) |
|---|---|---:|---:|
| `A1` | aspecto não é alvo | 9,4 | 16,5 |
| `A2` | lugar nomeado como aspecto | 1,4 | 0,7 |
| `A3` | entidade fora do domínio | 3,3 | 0,6 |
| `A4` | aspecto não pareado com a opinião | 2,0 | 9,2 |
| `O1` | sem avaliação | 4,6 | 4,5 |
| `S1` | expressão não avaliativa | 1,3 | 9,9 |
| `S2` | expressão incompleta | 8,1 | 8,6 |
| `C1` | categoria errada | 0,0 | 11,9 |
| `P1` | polaridade errada | 3,4 | 4,0 |
| `H1` | holder errado | 4,6 | 0,0 |

## Triagem lexical (todas as tuplas do modelo)

Lugar nomeado como aspecto: 4 de 5.403 tuplas (0,1%). Termos mais frequentes: “Mercado Publico” (1), “Bairro Saint Germain” (1), “Cidade Luz de” (1), “praça Vendome” (1).
Aspecto funcional ou intensificador: 168. Entorno genérico (aceito): 44.

## Limites

- Vereditos de juízes LLM; ver a seção 7 do guia antes de citar como avaliação humana.
- Runs com até 50 tuplas foram julgados por inteiro e aparecem como “censo”: não há erro amostral, mas há o erro dos juízes.
- Os percentuais agregados ponderam cada run pelas suas tuplas retidas.
