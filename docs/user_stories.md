# User Stories e Critérios de Aceite

**User Stories (Histórias de Usuário)** são descrições simples e curtas de uma funcionalidade, focadas na perspectiva do usuário final, geralmente seguindo o formato: 
```
"Como [tipo de usuário], eu quero [funcionalidade] para [benefício]".
```
Já os **Critérios de Aceite** são condições específicas que essa funcionalidade precisa atender para ser considerada concluída e aceita pelo Product Owner (PO), agindo como regras de negócio e limites de aceitação.

**1. Autenticação Segura via SUAP:** \
Como usuário do sistema, \
Eu quero autenticar-me no sistema utilizando minha conta institucional (SUAP), \
Para que eu possa acessar o sistema com segurança e sem necessidade de criar novas senhas. 

| Criterios de aceite: |
:--
✅ Dado que estou na página inicial, quando clico em "Entrar", sou redirecionado para a página de OAuth2 do SUAP.
✅ Dado que autentiquei com sucesso, quando acesso o dashboard, então vejo meu nome e vínculo (Aluno/Servidor) exibidos no perfil.
✅ Dado que não estou autenticado, quando tento acessar uma URL interna (ex: /items), então sou redirecionado automaticamente para o login
✅ Dado que o token SUAP expirou, quando realizo uma ação sensível, então o sistema solicita reautenticação

---

**2. Cadastrar Item Encontrado**\
Como Usuário Comum,\
Eu quero cadastrar um item que encontrei no campus,\
Para que o item seja registrado no inventário com status "Pendente" e eu possa entregá-lo na COAPAC para devolução ao dono. 

    | Critérios de Aceite |
    :--
    ✅ Dado que estou logado, quando acesso "Cadastrar Item", vejo um formulário com campos obrigatórios: Imagem, Categoria, Cor, Descrição, Local de Encontro, Dados Sensíveis (checkbox).
    ✅ Dado que preenchi todos os campos, quando submeto o formulário, então o item é salvo com status "Pendente" e não aparece na lista pública imediatamente.
    ✅ Dado que o cadastro foi realizado com sucesso, então recebo uma mensagem clara instruindo a entrega física do item na COAPAC para conclusão do processo.
    ✅ Dado que o item está com status "Pendente", quando acesso "Itens Cadastrados", então posso editar ou cancelar o próprio registro; após cancelamento, o status muda para "Cancelado".
    
---

**3. Solicitação de Reivindicação de Item Perdido**\
Como Usuário Comum,\
Eu quero solicitar a reivindicação de um item listado como "Válido" ou "Armazenado" preenchendo um formulário,\
Para que eu possa provar minha posse com informações específicas do item.

| Critérios de Aceite|
:--
✅ Dado que visualizo um item na lista pública com status "Válido" ou "Armazenado", quando clico em "Reivindicar", então acesso um formulário com campos obrigatórios: motivo da reivindicação, data aproximada da perda, local da perda e características específicas (ex: marca interna, arranhão, número de série).
✅ Dado que envio a solicitação com sucesso, quando o administrador acessa a fila de reivindicações pendentes, ele vê os detalhes completos da prova de posse.
✅ Dado que enviei uma reivindicação, quando acompanho o status em "Minhas Solicitações", então vejo se foi "Aprovada", "Rejeitada" ou "Em Análise", com justificativa do administrador.

---

**4. Registro de Entrega (Reinvindicação)**\
Como Administrador,\
Eu quero registrar a entrega final de um item reivindicado,\
Para que haja controle físico do inventário e rastreabilidade.

| Critérios de Aceite |
:--
✅ Dado que vou registrar a entrega de um item reivindicado, o sistema automaticamente preenche os dados: (a) Matrícula SUAP ou identificação do recebedor, (b) Identificação automática do administrador logado, (c) Data e hora exata da transação .
✅ Dado que confirmo a entrega, quando o sistema processa, então o status do item muda para "Entregue" automaticamente.
✅ Dado que a transação foi concluída, quando verifico o log de auditoria, então o registro é criado como "apenas leitura", impedindo edição ou exclusão.
✅ Dado que a entrega foi registrada, quando o usuário recebe o comprovante, então ele pode visualizar/realizar download um comprovante digital da transação.

---

**5. Sorteiar itens para doação**\
Como administrador
Quero sortear itens
Para distribuir itens não reclamados


| Critérios de Aceite |
:--
✅ Dado que um item com status "Armazenado" atingiu 30 dias sem reivindicação aprovada, quando o sistema executa a rotina de monitoramento, então o status é alterado automaticamente para "Disponível para Doação".
✅ Dado que há usuários que manifestaram interesse no item, quando clico em "Sorteiar item", o sistema seleciona um beneficiário de forma aleatória.
✅ Dado que um usuário já recebeu 3 itens em doações na mesma "Sessão de Doações", então o sistema o exclui temporariamente da lista de elegíveis para garantir distribuição justa.
✅ Dado que o sorteio foi finalizado, quando visualizo o resultado, então o sistema: (a) registra o vencedor, (b) atualiza o status do item para "Sorteado Aguardando Entrega", e (c) notifica o beneficiário para retirada na COAPAC.
✅ Dado que a sessão de doações foi encerrada pelo administrador, quando inicio uma nova sessão, então a contagem de itens recebidos por usuário é zerada, permitindo participação normal em sessões futuras.