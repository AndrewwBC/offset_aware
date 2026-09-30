# Auditoria semântica: Qwen/Qwen2.5-1.5B-Instruct

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Visão comparativa em `audit/RELATORIO_AUDITORIA_SEMANTICA.md`.

**5.274 tuplas retidas** nos 6 runs; 200 julgadas. Estimativa de **1.528 válidas** sem correção e **2.932** opiniões reais sobre o hotel.

| Métrica (todas as tarefas e configurações) | % [IC 95%] |
|---|---:|
| Validade estrita | 29,0 [22–36] |
| Validade de domínio | 55,6 [48–63] |
| Fora do domínio (`A2`/`A3`) | 8,1 [4–12] |
| Sem opinião (`O1`/`O2`/`S1`) | 30,1 [23–37] |

## Por tarefa e configuração

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 1.760 | 50 | 387 | 22,0 [13–35] | 62,0 [48–74] | 0,0 [0–7] | 2,0 [0–10] | 28,0 [17–42] |
| SSA | `no_retry` | 853 | 50 | 290 | 34,0 [22–48] | 58,0 [44–71] | 6,0 [2–16] | 4,0 [1–13] | 26,0 [16–40] |
| SSA | `no_tags` | 0 | 0 | 0 | — | — | — | — | — |
| ASQP | `full` | 1.869 | 50 | 598 | 32,0 [21–46] | 50,0 [37–63] | 2,0 [0–10] | 12,0 [6–24] | 34,0 [22–48] |
| ASQP | `no_retry` | 792 | 50 | 253 | 32,0 [21–46] | 52,0 [39–65] | 4,0 [1–13] | 2,0 [0–10] | 30,0 [19–44] |
| ASQP | `no_tags` | 0 | 0 | 0 | — | — | — | — | — |
| **Total** | | **5.274** | **200** | **1.528** | **29,0 [22–36]** | **55,6 [48–63]** | **2,3 [0–4]** | **5,9 [2–9]** | **30,1 [23–37]** |

## Correção por campo

| Campo | SSA (%) | ASQP (%) |
|---|---:|---:|
| Aspecto correto | 71,3 [62–81] | 62,2 [52–72] |
| Expressão de opinião correta | 43,2 [33–53] | 55,2 [45–66] |
| Categoria correta | — | 92,0 [88–96] |
| Polaridade correta | 92,7 [88–98] | 94,0 [89–99] |
| Holder correto | 88,0 [81–95] | — |

## Erros (% estimado das tuplas retidas)

| Código | Significado | SSA (%) | ASQP (%) |
|---|---|---:|---:|
| `A1` | aspecto não é alvo | 17,4 | 20,8 |
| `A2` | lugar nomeado como aspecto | 2,0 | 2,6 |
| `A3` | entidade fora do domínio | 2,7 | 9,0 |
| `A4` | aspecto não pareado com a opinião | 6,7 | 5,4 |
| `O1` | sem avaliação | 7,3 | 9,4 |
| `S1` | expressão não avaliativa | 20,0 | 26,0 |
| `S2` | expressão incompleta | 28,1 | 9,2 |
| `S3` | expressão excessiva | 1,3 | 2,8 |
| `C1` | categoria errada | 0,0 | 8,0 |
| `P1` | polaridade errada | 7,3 | 6,0 |
| `H1` | holder errado | 12,0 | 0,0 |

## Triagem lexical (todas as tuplas do modelo)

Lugar nomeado como aspecto: 6 de 5.274 tuplas (0,1%). Termos mais frequentes: “Catedral do Sacre Coeur, maravilhosa” (2), “Mercado Municipal e a Casa Mario Quintana” (1), “bairro Daumesnil” (1), “Estação de Trem Gare du Nord (para outros países” (1), “Shopping Total” (1).
Aspecto funcional ou intensificador: 163. Entorno genérico (aceito): 71.

## Limites

- Vereditos de juízes LLM; ver a seção 7 do guia antes de citar como avaliação humana.
- Runs com até 50 tuplas foram julgados por inteiro e aparecem como “censo”: não há erro amostral, mas há o erro dos juízes.
- Os percentuais agregados ponderam cada run pelas suas tuplas retidas.
