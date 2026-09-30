# Guia de auditoria semântica das anotações geradas

## 1. Objetivo

A validação automática do pipeline só garante **forma**: JSON válido, esquema
correto e spans que batem exatamente com o texto. Ela não diz se a anotação
**faz sentido**. Esta auditoria mede quantas tuplas retidas são opiniões
plausíveis no domínio de hotelaria, isto é, informação que um **gestor ou dono de
hotel** usaria para entender o que o hóspede avaliou.

Pergunta central, para cada tupla:

> Um gestor de hotel, lendo esta tupla ao lado da frase, concordaria que ela
> registra uma avaliação do hóspede sobre algo do hotel ou da estadia, com
> alvo, expressão, categoria e polaridade coerentes?

A unidade de julgamento é **uma tupla**, lida no contexto da sua frase (com a
frase anterior e a seguinte, quando existirem). O julgamento é semântico: não se
compara com a anotação de referência.

## 2. O que é "domínio de hotel"

**Dentro do domínio**: tudo o que o hotel oferece, controla ou que caracteriza a
estadia. Exemplos: o hotel como um todo, quarto, cama, banheiro, chuveiro,
limpeza, ruído, ar-condicionado, Wi-Fi, piscina, estacionamento, café da manhã,
restaurante *do hotel*, funcionários, recepção, check-in, preço, diária, taxas,
custo-benefício e a **localização do hotel** (acesso, proximidade, segurança do
entorno *como atributo do hotel*).

**Fora do domínio**: entidades que o hotel não controla, avaliadas por si
mesmas. Exemplos:

- **nome** de rua, avenida, praça, bairro, cidade ou país usado como aspecto
  (“Rua Augusta”, “Lisboa”); o entorno genérico (“a rua”, “o bairro”) segue a
  regra da localização abaixo;
- monumento, museu, praia, igreja, parque ou atração turística (“Cristo
  Redentor”, “Torre de Belém”);
- outros estabelecimentos (restaurante vizinho, loja, shopping, companhia
  aérea), o clima, o trânsito ou a cidade;
- o próprio hóspede, acompanhantes e a viagem em geral (“nossas férias”,
  “meu marido”), exceto quando o texto os usa para avaliar o hotel;
- plataformas de reserva ou terceiros (Booking, agência), exceto quando a
  avaliação recai sobre a política do hotel.

**Regra da localização.** Distinga dois casos:

- **Lugar nomeado ou atração como aspecto → `A2`.** Em “Fica perto da Praça da
  Sé”, a opinião é sobre a **localização do hotel**. Se a tupla marca “Praça da
  Sé” como aspecto, o alvo está errado: para o gestor, a praça não é um
  atributo avaliável do hotel. O mesmo vale para “Rua Augusta”, “Torre Eiffel”,
  “Lisboa”, “Copacabana” e para atrações avaliadas por si mesmas (“o museu é
  lindo”). Em “vista para a Torre Eiffel”, o aspecto correto é “vista”.
- **Entorno genérico como atributo da localização → aceito.** Termos comuns que
  descrevem o entorno do hotel (“a rua é barulhenta”, “bairro seguro”, “perto
  da estação de metrô”, “longe do aeroporto”) informam o gestor sobre a
  localização. Não marque `A2`; avalie a categoria normalmente (`location`
  em ASQP, ou `structure` quando o ruído da rua é avaliado como isolamento do
  quarto).

## 3. Critérios por campo

Avalie cada campo independentemente e registre os códigos de erro (seção 4).

### 3.1 Existe opinião? (`O`)

Há uma avaliação real do hóspede sobre o alvo, e não apenas um fato,
uma descrição neutra, uma intenção, uma pergunta ou uma narração?

- “O quarto era enorme” → sim. “Fizemos check-in às 14h” → não.
- “Voltaremos com certeza” → sim, avaliação implícita do hotel (`general`).
- Descrição factual sem valor avaliativo (“o hotel tem 3 andares”) → não.

### 3.2 Aspecto (`A`)

- É o alvo do que foi avaliado?
- Está dentro do domínio de hotel (seção 2)?
- É um sintagma nominal que identifica o alvo, e não um artigo, intensificador,
  adjetivo avaliativo ou a oração inteira?

A pontuação colada ao final do termo (“localização,”) é um efeito da
tokenização por espaço em branco e **não é erro**.

### 3.3 Expressão de opinião (`S`)

- A expressão carrega a avaliação (“sujo”, “não vale o preço”, “longe de tudo”)?
- Inclui a negação quando ela muda o sentido?
- Não é só um intensificador (“muito”), só o aspecto repetido, nem um trecho
  sem nenhum valor avaliativo?

Spans um pouco maiores ou menores que o ideal, mas que ainda contêm a
avaliação, são aceitáveis (`S3` só vale para spans claramente excessivos, como
uma oração inteira ou várias opiniões juntas).

### 3.4 Categoria (`C`, apenas ASQP)

Categorias permitidas: `general`, `structure`, `service`, `location`, `price`
e `others`. Use as definições de `prompts/asqp_annotation_guide.md`: limpeza e
comida são `service`; quarto, conforto e comodidades são `structure`; “o hotel
fica perto do metrô” é `location`. Marque `C1` quando outra categoria for
claramente mais adequada. Na dúvida entre duas categorias aceitáveis, não
marque erro.

### 3.5 Polaridade (`P`)

`POS`, `NEG` ou `NEU` compatível com a expressão **no contexto**, considerando
negação, ironia e contraste (“não podia ser melhor” é `POS`).

### 3.6 Holder (`H`, apenas SSA)

O holder é quem emite a opinião. `null` é correto quando nenhum emissor está
expresso na mesma relação de opinião. Marque `H1` quando o holder for o alvo, uma
entidade que não opina ou um sujeito distante.

## 4. Códigos de erro

| Código | Campo | Significado | Gravidade |
|---|---|---|---|
| `O1` | opinião | Não há avaliação: fato, narração, pergunta ou intenção | invalida |
| `O2` | opinião | Tupla alucinada: a relação aspecto–opinião não existe no texto | invalida |
| `A1` | aspecto | Não é alvo: palavra funcional, avaliativa ou oração inteira | invalida |
| `A2` | aspecto | Lugar nomeado ou atração como aspecto: nome de rua, bairro ou cidade, monumento (seção 2) | invalida |
| `A3` | aspecto | Entidade fora do domínio: outro estabelecimento, hóspede, clima, viagem, plataforma | invalida |
| `A4` | aspecto | Aspecto do domínio, mas não é o alvo desta opinião (pareamento errado) | parcial |
| `S1` | expressão | A expressão não é avaliativa ou não se refere ao aspecto | invalida |
| `S2` | expressão | Falta a negação ou o complemento que muda o sentido, ou é só um intensificador | parcial |
| `S3` | expressão | Span claramente excessivo: oração inteira ou várias opiniões juntas | parcial |
| `C1` | categoria | Categoria errada (ASQP) | parcial |
| `P1` | polaridade | Polaridade errada | parcial |
| `H1` | holder | Holder errado (SSA) | parcial |
| `D1` | tupla | Duplicata semântica de outra tupla do mesmo trecho | parcial |

## 5. Veredito

Aplique na ordem:

1. Se houver qualquer código **invalida** → **`INVALIDA`**. A tupla não é uma
   opinião útil sobre o hotel.
2. Senão, se houver algum código **parcial** → **`PARCIAL`**. É uma opinião de
   domínio real, mas precisa de correção em algum campo.
3. Senão → **`VALIDA`**.

Métricas reportadas:

- **Validade estrita** = `VALIDA / total`: tuplas utilizáveis sem correção.
- **Validade de domínio** = `(VALIDA + PARCIAL) / total`: tuplas que registram
  uma opinião real sobre o hotel, ainda que com algum campo errado.
- **Taxa de fora do domínio** = tuplas com `A2` ou `A3` / total. Responde
  diretamente “o nome da rua ou o monumento faz sentido para o dono do hotel?”.
- Taxas por campo: aspecto, expressão, categoria, polaridade e holder corretos.

Cada taxa vem com intervalo de confiança de Wilson de 95%.
**Tuplas válidas estimadas** = taxa × tuplas retidas do run.

## 6. Exemplos

| Frase (trecho) | Tupla | Veredito |
|---|---|---|
| “A localização é excelente, perto de tudo.” | (location, localização, excelente, POS) | `VALIDA` |
| “Fica a 5 min da Torre de Belém, ótimo.” | (location, Torre de Belém, ótimo, POS) | `INVALIDA` `A2` |
| “Fica a 5 min da Torre de Belém, ótimo.” | (location, Fica, ótimo, POS) | `PARCIAL` `A4`: o alvo é o hotel ou a localização, e o termo não o identifica bem |
| “Lisboa é linda.” | (general, Lisboa, linda, POS) | `INVALIDA` `A2` |
| “O bairro é muito seguro.” | (location, bairro, muito seguro, POS) | `VALIDA`: entorno genérico como atributo da localização |
| “Jantamos num restaurante ao lado, péssimo.” | (service, restaurante, péssimo, NEG) | `INVALIDA` `A3` |
| “O quarto não era limpo.” | (service, quarto, limpo, POS) | `PARCIAL` `S2` `P1` |
| “O café da manhã era variado.” | (structure, café da manhã, variado, POS) | `PARCIAL` `C1` |
| “Chegamos às 22h.” | (general, 22h, Chegamos, NEU) | `INVALIDA` `O1` |
| “Muito bom o atendimento.” | (service, atendimento, Muito, POS) | `PARCIAL` `S2` |
| “Meu marido adorou o café.” (SSA) | (holder=café, café, adorou, POS) | `PARCIAL` `H1` |

## 7. Procedimento

1. **Amostra.** `scripts/semantic_audit_sample.py` sorteia, com semente fixa,
   até 50 tuplas por run (modelo × tarefa × configuração), uniformemente e sem
   reposição; runs com menos de 50 tuplas entram inteiros. Tuplas idênticas em
   runs diferentes (mesmo documento, spans, rótulos) são julgadas uma única vez
   e o veredito é propagado. A amostra contém texto original e é gravada fora do
   repositório (`private_runs/`, ignorado pelo git).
2. **Julgamento.** Para cada item, registre uma linha JSONL:
   `{"item_id": ..., "verdict": "VALIDA|PARCIAL|INVALIDA", "codes": [...],
   "note": "..."}`. A nota é curta e **não copia texto original** além dos termos
   já anotados. Não consulte o modelo que gerou a tupla nem a anotação de
   referência.
3. **Concordância.** Cerca de 10% dos itens são julgados por dois juízes sem que
   eles saibam disso. Reporte concordância bruta e kappa de Cohen sobre o
   veredito de três classes. Kappa < 0,6 indica que o guia precisa ser refinado
   antes de confiar nas taxas.
4. **Segunda passada de domínio.** Todos os itens marcados com `A2` ou `A3` são
   revistos por um único revisor, que decide apenas se o código se mantém
   (`keep`) ou se o aspecto é entorno genérico aceito pela regra da localização
   (`drop`, com `C1` quando a categoria ASQP não for `location`). As decisões
   ficam em `ood_decisions.jsonl`, ao lado da amostra, e o relatório as aplica
   sobre os julgamentos originais, que são preservados.
5. **Relatório.** `scripts/semantic_audit_report.py` junta vereditos e amostra e
   produz as taxas por run, por modelo × configuração e por tarefa, além da
   triagem lexical completa (seção 8).
6. **Revisão humana.** Se os juízes forem LLMs, pelo menos uma subamostra
   (sugestão: 100 itens estratificados por veredito) deve ser revisada por um
   anotador humano, e a concordância humano × LLM deve ser reportada com os
   resultados.

## 8. Triagem lexical sobre todas as tuplas

Além da amostra, o relatório aplica a **todas** as tuplas retidas um filtro
determinístico com três sinais:

- **lugar nomeado**: aspecto iniciado por marcador geográfico (rua, av.,
  avenida, praça, largo, travessa, museu, igreja, catedral, torre, ponte,
  castelo, mosteiro, praia, parque, estação, aeroporto, bairro, cidade e
  similares) seguido de nome próprio (“Rua Augusta”, “Torre Eiffel”). É um limite
  inferior para `A2`, porque nomes sem marcador (“Lisboa”) só aparecem no
  julgamento;
- **entorno genérico**: marcador sem nome próprio (“rua”, “bairro”, “estação
  de metrô”). Aceito pela regra da localização e reportado só como contexto;
- **aspecto funcional**: aspecto que é só palavra funcional ou
  intensificador. É um limite inferior para `A1`.

O filtro não substitui o julgamento, mas cobre 100% das tuplas.

## 9. Limites

- A amostra estima taxas por run com margem de cerca de ±14 pontos
  percentuais; agregados por modelo e configuração são mais precisos.
- A validade é julgada tupla a tupla. Esta auditoria **não** mede cobertura: não
  mede opiniões que o modelo deixou de extrair.
- Juízes LLM podem ser sistematicamente lenientes ou rigorosos. A revisão
  humana da seção 7 é necessária antes de citar as taxas como avaliação humana.
