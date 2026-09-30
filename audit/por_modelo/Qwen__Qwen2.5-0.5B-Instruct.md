# Auditoria semântica: Qwen/Qwen2.5-0.5B-Instruct

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Visão comparativa em `audit/RELATORIO_AUDITORIA_SEMANTICA.md`.

**709 tuplas retidas** nos 6 runs; 200 julgadas. Estimativa de **164 válidas** sem correção e **458** opiniões reais sobre o hotel.

| Métrica (todas as tarefas e configurações) | % [IC 95%] |
|---|---:|
| Validade estrita | 23,3 [18–28] |
| Validade de domínio | 64,5 [59–70] |
| Fora do domínio (`A2`/`A3`) | 3,6 [1–6] |
| Sem opinião (`O1`/`O2`/`S1`) | 20,9 [16–26] |

## Por tarefa e configuração

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 219 | 50 | 48 | 22,0 [13–35] | 68,0 [54–79] | 2,0 [0–10] | 2,0 [0–10] | 16,0 [8–29] |
| SSA | `no_retry` | 195 | 50 | 27 | 14,0 [7–26] | 62,0 [48–74] | 2,0 [0–10] | 4,0 [1–13] | 28,0 [17–42] |
| SSA | `no_tags` | 0 | 0 | 0 | — | — | — | — | — |
| ASQP | `full` | 173 | 50 | 48 | 28,0 [17–42] | 62,0 [48–74] | 0,0 [0–7] | 0,0 [0–7] | 24,0 [14–37] |
| ASQP | `no_retry` | 122 | 50 | 41 | 34,0 [22–48] | 66,0 [52–78] | 0,0 [0–7] | 4,0 [1–13] | 14,0 [7–26] |
| ASQP | `no_tags` | 0 | 0 | 0 | — | — | — | — | — |
| **Total** | | **709** | **200** | **164** | **23,3 [18–28]** | **64,5 [59–70]** | **1,2 [0–3]** | **2,4 [1–4]** | **20,9 [16–26]** |

## Correção por campo

| Campo | SSA (%) | ASQP (%) |
|---|---:|---:|
| Aspecto correto | 74,9 [68–82] | 74,7 [68–82] |
| Expressão de opinião correta | 56,2 [48–65] | 57,3 [49–65] |
| Categoria correta | — | 81,2 [75–88] |
| Polaridade correta | 91,2 [86–96] | 88,8 [84–94] |
| Holder correto | 30,1 [22–38] | — |

## Erros (% estimado das tuplas retidas)

| Código | Significado | SSA (%) | ASQP (%) |
|---|---|---:|---:|
| `A1` | aspecto não é alvo | 17,2 | 20,0 |
| `A2` | lugar nomeado como aspecto | 2,0 | 0,0 |
| `A3` | entidade fora do domínio | 2,9 | 1,7 |
| `A4` | aspecto não pareado com a opinião | 2,9 | 3,7 |
| `O1` | sem avaliação | 2,9 | 2,0 |
| `S1` | expressão não avaliativa | 18,7 | 19,0 |
| `S2` | expressão incompleta | 22,1 | 22,8 |
| `C1` | categoria errada | 0,0 | 18,8 |
| `P1` | polaridade errada | 8,8 | 11,2 |
| `H1` | holder errado | 69,9 | 0,0 |

## Triagem lexical (todas as tuplas do modelo)

Lugar nomeado como aspecto: 0 de 709 tuplas (0,0%).
Aspecto funcional ou intensificador: 16. Entorno genérico (aceito): 14.

## Limites

- Vereditos de juízes LLM; ver a seção 7 do guia antes de citar como avaliação humana.
- Runs com até 50 tuplas foram julgados por inteiro e aparecem como “censo”: não há erro amostral, mas há o erro dos juízes.
- Os percentuais agregados ponderam cada run pelas suas tuplas retidas.
