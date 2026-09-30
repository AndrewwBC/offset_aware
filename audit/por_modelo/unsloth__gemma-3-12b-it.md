# Auditoria semântica: unsloth/gemma-3-12b-it

Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Visão comparativa em `audit/RELATORIO_AUDITORIA_SEMANTICA.md`.

**17.699 tuplas retidas** nos 6 runs; 300 julgadas. Estimativa de **11.537 válidas** sem correção e **13.847** opiniões reais sobre o hotel.

| Métrica (todas as tarefas e configurações) | % [IC 95%] |
|---|---:|
| Validade estrita | 65,2 [58–72] |
| Validade de domínio | 78,2 [72–84] |
| Fora do domínio (`A2`/`A3`) | 7,6 [4–11] |
| Sem opinião (`O1`/`O2`/`S1`) | 7,3 [4–11] |

## Por tarefa e configuração

| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SSA | `full` | 5.790 | 50 | 4.053 | 70,0 [56–81] | 82,0 [69–90] | 8,0 [3–19] | 4,0 [1–13] | 2,0 [0–10] |
| SSA | `no_retry` | 2.963 | 50 | 2.015 | 68,0 [54–79] | 80,0 [67–89] | 2,0 [0–10] | 4,0 [1–13] | 12,0 [6–24] |
| SSA | `no_tags` | 82 | 50 | 52 | 64,0 [50–76] | 72,0 [58–83] | 0,0 [0–7] | 0,0 [0–7] | 6,0 [2–16] |
| ASQP | `full` | 5.755 | 50 | 3.568 | 62,0 [48–74] | 72,0 [58–83] | 2,0 [0–10] | 4,0 [1–13] | 10,0 [4–21] |
| ASQP | `no_retry` | 3.008 | 50 | 1.805 | 60,0 [46–72] | 82,0 [69–90] | 2,0 [0–10] | 2,0 [0–10] | 8,0 [3–19] |
| ASQP | `no_tags` | 101 | 50 | 44 | 44,0 [31–58] | 58,0 [44–71] | 0,0 [0–7] | 4,0 [1–13] | 4,0 [1–13] |
| **Total** | | **17.699** | **300** | **11.537** | **65,2 [58–72]** | **78,2 [72–84]** | **3,9 [1–7]** | **3,6 [1–6]** | **7,3 [4–11]** |

## Correção por campo

| Campo | SSA (%) | ASQP (%) |
|---|---:|---:|
| Aspecto correto | 81,3 [73–89] | 81,2 [73–89] |
| Expressão de opinião correta | 88,0 [82–94] | 83,4 [76–91] |
| Categoria correta | — | 95,2 [92–98] |
| Polaridade correta | 97,3 [94–100] | 94,7 [90–99] |
| Holder correto | 97,3 [94–100] | — |

## Erros (% estimado das tuplas retidas)

| Código | Significado | SSA (%) | ASQP (%) |
|---|---|---:|---:|
| `A1` | aspecto não é alvo | 4,2 | 11,5 |
| `A2` | lugar nomeado como aspecto | 5,9 | 2,0 |
| `A3` | entidade fora do domínio | 4,0 | 3,3 |
| `A4` | aspecto não pareado com a opinião | 4,6 | 2,0 |
| `O1` | sem avaliação | 2,7 | 2,0 |
| `S1` | expressão não avaliativa | 2,7 | 7,2 |
| `S2` | expressão incompleta | 4,0 | 5,3 |
| `S3` | expressão excessiva | 2,6 | 2,0 |
| `C1` | categoria errada | 0,0 | 4,8 |
| `P1` | polaridade errada | 2,7 | 5,3 |
| `H1` | holder errado | 2,7 | 0,0 |

## Triagem lexical (todas as tuplas do modelo)

Lugar nomeado como aspecto: 64 de 17.699 tuplas (0,4%). Termos mais frequentes: “Torre Eiffel” (13), “praça Vendome” (4), “praça de Vendome 1 quarteirão” (3), “Torre Eifel” (3), “praça da Bastille” (3), “estação do Metrô Gare de Lyon” (3), “Rua do Comércio” (2), “avenida principal de LV” (2), “estação de metrô CADET” (2), “Bairro Saint Germain” (2).
Aspecto funcional ou intensificador: 56. Entorno genérico (aceito): 243.

## Limites

- Vereditos de juízes LLM; ver a seção 7 do guia antes de citar como avaliação humana.
- Runs com até 50 tuplas foram julgados por inteiro e aparecem como “censo”: não há erro amostral, mas há o erro dos juízes.
- Os percentuais agregados ponderam cada run pelas suas tuplas retidas.
