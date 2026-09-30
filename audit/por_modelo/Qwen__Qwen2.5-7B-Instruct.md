# Auditoria semântica: Qwen/Qwen2.5-7B-Instruct

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Visão comparativa em `audit/RELATORIO_AUDITORIA_SEMANTICA.md`.

**7.600 tuplas retidas** nos 6 runs; 215 julgadas. Estimativa de **4.272 válidas** sem correção e **6.096** opiniões reais sobre o hotel.

| Métrica (todas as tarefas e configurações) | % [IC 95%] |
|---|---:|
| Validade estrita | 56,2 [49–63] |
| Validade de domínio | 80,2 [74–86] |
| Fora do domínio (`A2`/`A3`) | 3,2 [1–6] |
| Sem opinião (`O1`/`O2`/`S1`) | 9,1 [5–13] |

## Por tarefa e configuração

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 2.546 | 50 | 1.069 | 42,0 [29–56] | 74,0 [60–84] | 2,0 [0–10] | 2,0 [0–10] | 18,0 [10–31] |
| SSA | `no_retry` | 1.278 | 50 | 869 | 68,0 [54–79] | 92,0 [81–97] | 0,0 [0–7] | 0,0 [0–7] | 4,0 [1–13] |
| SSA | `no_tags` | 7 | 7 | 5 | 71,4 (censo) | 71,4 (censo) | 0,0 (censo) | 0,0 (censo) | 0,0 (censo) |
| ASQP | `full` | 2.642 | 50 | 1.427 | 54,0 [40–67] | 78,0 [65–87] | 2,0 [0–10] | 0,0 [0–7] | 6,0 [2–16] |
| ASQP | `no_retry` | 1.119 | 50 | 895 | 80,0 [67–89] | 86,0 [74–93] | 2,0 [0–10] | 6,0 [2–16] | 2,0 [0–10] |
| ASQP | `no_tags` | 8 | 8 | 7 | 87,5 (censo) | 100,0 (censo) | 0,0 (censo) | 0,0 (censo) | 0,0 (censo) |
| **Total** | | **7.600** | **215** | **4.272** | **56,2 [49–63]** | **80,2 [74–86]** | **1,7 [0–4]** | **1,6 [0–3]** | **9,1 [5–13]** |

## Correção por campo

| Campo | SSA (%) | ASQP (%) |
|---|---:|---:|
| Aspecto correto | 88,0 [81–95] | 79,0 [70–88] |
| Expressão de opinião correta | 79,4 [71–88] | 89,0 [82–96] |
| Categoria correta | — | 92,4 [87–98] |
| Polaridade correta | 95,3 [91–100] | 97,2 [93–100] |
| Holder correto | 74,1 [65–83] | — |

## Erros (% estimado das tuplas retidas)

| Código | Significado | SSA (%) | ASQP (%) |
|---|---|---:|---:|
| `A1` | aspecto não é alvo | 5,4 | 11,0 |
| `A2` | lugar nomeado como aspecto | 1,3 | 2,0 |
| `A3` | entidade fora do domínio | 1,3 | 1,8 |
| `A4` | aspecto não pareado com a opinião | 4,0 | 6,2 |
| `O1` | sem avaliação | 6,7 | 1,4 |
| `S1` | expressão não avaliativa | 6,6 | 3,4 |
| `S2` | expressão incompleta | 4,0 | 1,4 |
| `S3` | expressão excessiva | 4,7 | 4,8 |
| `C1` | categoria errada | 0,0 | 7,6 |
| `P1` | polaridade errada | 4,7 | 2,8 |
| `H1` | holder errado | 25,9 | 0,0 |

## Triagem lexical (todas as tuplas do modelo)

Lugar nomeado como aspecto: 16 de 7.600 tuplas (0,2%). Termos mais frequentes: “praça de Vendome 1 quarteirão” (3), “Catedral do Sacre Coeur, maravilhosa” (2), “bairro Daumesnil” (2), “Rua do Comércio” (1), “avenida principal de LV” (1), “Bairro Saint Germain” (1), “estação de metrô Cambronne que dá acesso aos principais pontos turísticos (estações” (1), “Jardim de Luxembourg” (1), “estação do Metrô Gare de Lyon que te leva aos 4 cantos de” (1), “torre Eiffel” (1).
Aspecto funcional ou intensificador: 81. Entorno genérico (aceito): 78.

## Limites

- Vereditos de juízes LLM; ver a seção 7 do guia antes de citar como avaliação humana.
- Runs com até 50 tuplas foram julgados por inteiro e aparecem como “censo”: não há erro amostral, mas há o erro dos juízes.
- Os percentuais agregados ponderam cada run pelas suas tuplas retidas.
