# Auditoria semântica: google/gemma-4-31B-it

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Visão comparativa em `audit/RELATORIO_AUDITORIA_SEMANTICA.md`.

**25.371 tuplas retidas** nos 6 runs; 300 julgadas. Estimativa de **19.367 válidas** sem correção e **22.467** opiniões reais sobre o hotel.

| Métrica (todas as tarefas e configurações) | % [IC 95%] |
|---|---:|
| Validade estrita | 76,3 [71–82] |
| Validade de domínio | 88,6 [85–92] |
| Fora do domínio (`A2`/`A3`) | 4,1 [2–7] |
| Sem opinião (`O1`/`O2`/`S1`) | 0,7 [0–2] |

## Por tarefa e configuração

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 6.340 | 50 | 4.311 | 68,0 [54–79] | 84,0 [71–92] | 0,0 [0–7] | 10,0 [4–21] | 0,0 [0–7] |
| SSA | `no_retry` | 5.375 | 50 | 3.655 | 68,0 [54–79] | 86,0 [74–93] | 2,0 [0–10] | 4,0 [1–13] | 0,0 [0–7] |
| SSA | `no_tags` | 1.077 | 50 | 775 | 72,0 [58–83] | 80,0 [67–89] | 2,0 [0–10] | 4,0 [1–13] | 2,0 [0–10] |
| ASQP | `full` | 6.423 | 50 | 5.652 | 88,0 [76–94] | 94,0 [84–98] | 0,0 [0–7] | 0,0 [0–7] | 2,0 [0–10] |
| ASQP | `no_retry` | 5.228 | 50 | 4.287 | 82,0 [69–90] | 94,0 [84–98] | 0,0 [0–7] | 0,0 [0–7] | 0,0 [0–7] |
| ASQP | `no_tags` | 928 | 50 | 687 | 74,0 [60–84] | 76,0 [63–86] | 2,0 [0–10] | 0,0 [0–7] | 4,0 [1–13] |
| **Total** | | **25.371** | **300** | **19.367** | **76,3 [71–82]** | **88,6 [85–92]** | **0,6 [0–1]** | **3,5 [1–6]** | **0,7 [0–2]** |

## Correção por campo

| Campo | SSA (%) | ASQP (%) |
|---|---:|---:|
| Aspecto correto | 82,0 [75–89] | 87,6 [82–93] |
| Expressão de opinião correta | 99,8 [100–100] | 98,7 [97–100] |
| Categoria correta | — | 98,1 [96–100] |
| Polaridade correta | 99,0 [97–100] | 100,0 [100–100] |
| Holder correto | 83,2 [76–90] | — |

## Erros (% estimado das tuplas retidas)

| Código | Significado | SSA (%) | ASQP (%) |
|---|---|---:|---:|
| `A1` | aspecto não é alvo | 8,4 | 5,9 |
| `A2` | lugar nomeado como aspecto | 1,0 | 0,1 |
| `A3` | entidade fora do domínio | 7,0 | 0,0 |
| `A4` | aspecto não pareado com a opinião | 2,7 | 6,3 |
| `O1` | sem avaliação | 0,2 | 0,1 |
| `S1` | expressão não avaliativa | 0,0 | 1,2 |
| `C1` | categoria errada | 0,0 | 1,9 |
| `P1` | polaridade errada | 1,0 | 0,0 |
| `H1` | holder errado | 16,8 | 0,0 |

## Triagem lexical (todas as tuplas do modelo)

Lugar nomeado como aspecto: 34 de 25.371 tuplas (0,1%). Termos mais frequentes: “praça de Vendome” (4), “praça da Bastille” (4), “Catedral do Sacre Coeur” (4), “mercado dos Enfants Rouge” (4), “praça Vendome” (4), “Bairro Saint Germain” (3), “avenida principal de LV” (2), “aeroporto internacional e Strip” (2), “estação Gare Du Norte” (2), “TOrre Eiffel” (2).
Aspecto funcional ou intensificador: 126. Entorno genérico (aceito): 321.

## Limites

- Vereditos de juízes LLM; ver a seção 7 do guia antes de citar como avaliação humana.
- Runs com até 50 tuplas foram julgados por inteiro e aparecem como “censo”: não há erro amostral, mas há o erro dos juízes.
- Os percentuais agregados ponderam cada run pelas suas tuplas retidas.
