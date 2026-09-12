# Guia de anotação SSA

## 1. Definição da tarefa

A tarefa produz tuplas `(holder, aspect, sentiment, polarity)`. O holder é quem
manifesta a avaliação sobre o aspecto. Cada aspecto deve ser relacionado ao seu
holder direto; a mesma expressão pode avaliar vários aspectos.

## 2. O que deve ser anotado

Identifique o emissor da opinião, o alvo, a expressão avaliativa e a polaridade.
Não classifique automaticamente qualquer sujeito gramatical como holder: ele
precisa ser a entidade que manifesta a avaliação.

“Eu achei o quarto, a recepção e o café da manhã organizados e limpos.” Produza
tuplas separadas para `quarto`, `recepção` e `café da manhã`, com holder `Eu` e
expressão `organizados e limpos`.

## 3. Critérios para holder

- Manifestação explícita: “Eu amei este hotel” → holder `Eu`.
- Grupo nominal explícito: “Meu marido adorou o café da manhã” → holder `Meu
  marido`.
- Sujeito implícito na flexão de um verbo avaliativo: “Adorei o serviço” → o
  verbo `Adorei` pode representar o holder implícito e a expressão.
- Pronome pessoal que identifica o experienciador: “A recepcionista me acusou de
  roubo” → holder `me`, quando essa for a convenção aplicável à opinião anotada.

Use holder nulo como `{"term":"null","token_ids":[]}` quando nenhum emissor
estiver expresso na mesma relação de opinião. Não transporte um holder de uma
frase anterior: em “Eu cheguei ao hotel na terça. O hotel é muito bonito”, a
opinião da segunda frase usa holder nulo.

## 4. Cuidados

- Mantenha relação direta entre holder, aspecto e expressão.
- Não associe um sujeito distante a uma opinião apenas por aparecer antes.
- Em coordenações, gere uma tupla para cada aspecto.
- Não confunda o alvo criticado com quem emite a crítica.
- Aspect e sentiment devem ser spans mínimos e semanticamente completos.
- Inclua negação na expressão quando ela alterar a polaridade.

