# Guia de anotação ASQP

## 1. Definição da tarefa

A tarefa ASQP produz quádruplas `(category, aspect, sentiment, polarity)`. Cada
quádrupla representa uma opinião completa sobre uma característica do hotel ou
da estadia. Extraia todas as opiniões expressas no trecho. Não crie uma
quádrupla apenas porque uma entidade foi mencionada: deve existir uma avaliação
associada a ela.

## 2. Categoria

`category` é uma classe semântica; `aspect` é o trecho textual avaliado. Não
troque um pelo outro. O JSON deste projeto aceita exatamente seis categorias:

- `general`: avaliação global do hotel, da hospedagem, da experiência ou do
  estabelecimento. Use somente quando a opinião não estiver limitada a uma
  característica mais específica.
- `structure`: elementos físicos e instalações, como quarto, banheiro, cama,
  elevador, ar-condicionado, mobiliário, isolamento acústico, conforto e
  comodidades.
- `service`: atendimento, funcionários, recepção, limpeza, café da manhã,
  comida e demais serviços prestados.
- `location`: posição geográfica, acesso, bairro, proximidade de transporte,
  atrações, comércio ou restaurantes.
- `price`: preço, diária, taxas, custo, economia e relação custo-benefício.
- `others`: use apenas quando nenhuma das cinco categorias anteriores for
  adequada. Não use como saída automática para casos difíceis.

Conceitos ontológicos mais específicos devem ser normalizados para esse esquema:
`room`, `comfort` e `amenities` pertencem a `structure`; `food` e `cleanliness`
pertencem a `service`. `location`, `price` e `general` permanecem nas categorias
homônimas.

Critérios de desempate:

1. Classifique pelo atributo efetivamente avaliado, não apenas pelo substantivo
   mais próximo.
2. Prefira uma categoria específica a `general`. Em “O hotel fica perto do
   metrô”, `hotel` é o aspecto textual, mas a categoria é `location`.
3. Em “O hotel é excelente”, use `general`; em “O quarto é excelente”, use
   `structure`.
4. Limpeza e alimentação são `service`, mesmo quando ocorrem dentro do quarto.
5. Uma menção a dinheiro só é `price` quando existe uma avaliação de custo,
   preço, taxa ou valor.

## 3. Aspecto

`aspect` é o menor trecho explícito que identifica o alvo da opinião. Normalmente
é um substantivo ou sintagma nominal: `localização`, `café da manhã`, `quarto`,
`relação custo-benefício`. Não marque determinantes isolados (`o`, `a`),
intensificadores, adjetivos avaliativos ou a frase inteira como aspecto.

Quando a mesma expressão avalia aspectos coordenados, produza uma quádrupla para
cada aspecto e reutilize a expressão. Em “O quarto e o banheiro eram amplos”,
produza uma quádrupla para `quarto` e outra para `banheiro`, ambas com a
expressão `amplos`.

## 4. Expressão de opinião

`sentiment` é o menor trecho que contém a avaliação completa do aspecto. Pode
ser adjetivo, verbo ou sintagma. Inclua negação, modificadores ou complementos
quando eles mudarem a avaliação: `não vale`, `muito confortável`, `longe de
tudo`. Não selecione apenas o intensificador (`muito`, `bem`, `tão`) quando ele
não expressar a opinião sozinho.

Não use o próprio aspecto como expressão, salvo quando a palavra realmente
funcionar como predicado avaliativo no contexto. Evite spans excessivos que
incluam o aspecto ou a oração inteira sem necessidade.

Use `sentiment.type="explicit"` quando a avaliação estiver lexicalizada no
trecho. Use `implicit` somente quando o trecho selecionado requer inferência
contextual para adquirir valor avaliativo.

## 5. Polaridade

Use exatamente `POS`, `NEG` ou `NEU`: `POS` para avaliação favorável, `NEG`
para desfavorável e `NEU` para avaliação verdadeiramente neutra ou descritiva.
Interprete a composição completa. “Não era bom” é `NEG`; “não podia ser melhor”
é `POS`. Em frases com contraste, não transfira a polaridade de uma oração para
outra.

## 6. Múltiplas opiniões e ausência de opinião

Crie uma quádrupla para cada par aspecto–expressão distinto. A mesma expressão
pode ser compartilhada por vários aspectos, e um aspecto pode receber avaliações
diferentes. Não una opiniões de polaridades distintas em uma única quádrupla.

Se não houver alvo explícito e expressão avaliativa associável, retorne
`{"annotations":[]}`. Não fabrique um aspecto para evitar uma lista vazia.

## 7. Exemplos

- “A localização é excelente, perto de tudo.” →
  `(location, localização, excelente, POS)`
- “O quarto era amplo e confortável.” →
  `(structure, quarto, amplo e confortável, POS)`
- “O café da manhã era variado, mas a diária não valia o preço.” →
  `(service, café da manhã, variado, POS)` e
  `(price, diária, não valia o preço, NEG)`
- “O hotel é bonito, mas os funcionários foram grosseiros.” →
  `(general, hotel, bonito, POS)` e
  `(service, funcionários, grosseiros, NEG)`

## 8. Verificação antes de responder

Para cada quádrupla, confirme:

1. Há uma avaliação real?
2. O aspecto é um alvo textual, e não uma palavra funcional ou avaliativa?
3. A expressão contém a avaliação completa, incluindo negação relevante?
4. A categoria pertence às seis permitidas e é a mais específica?
5. A polaridade é compatível com a expressão no contexto?
6. Todos os aspectos distintos receberam quádruplas separadas?

