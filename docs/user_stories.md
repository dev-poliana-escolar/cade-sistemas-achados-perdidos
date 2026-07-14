# 👥 User Stories e Critérios de Aceite (Atualizado com Novo MER e Domínio)

Este documento descreve as histórias de usuário e os critérios de aceite baseados na especificação técnica do sistema **CADÊ**, alinhados ao Modelo de Entidade-Relacionamento (MER), Diagrama de Classes e Diagrama de Domínio do projeto.

---

## 🔑 US01 - Autenticação Segura (SUAP e Contingência Administrativa)
Como **Usuário** (Comum ou Administrador),  
eu quero **me autenticar utilizando minha conta institucional do SUAP ou via credenciais locais nativas (apenas Administradores)**,  
para **garantir acesso contínuo ao sistema mesmo em cenários de indisponibilidade de serviços externos**.

### 📋 Critérios de Aceite (BDD)
* **Login padrão via SUAP (Fluxo Discente/Servidor):**
  * **Dado que** sou um usuário comum ou administrador acessando a tela de login,
  * **quando** seleciono a opção de autenticação institucional e entro com sucesso via OAuth2 do SUAP,
  * **então** o sistema cria/atualiza o registro na tabela `USUARIO` e estabelece a sessão padrão.
* **Mecanismo de Contingência/Login Nativo (Apenas Administrador):**
  * **Dado que** o sistema do SUAP está instável ou indisponível por motivos técnicos,
  * **quando** um usuário com perfil `Administrador` acessa a tela de login nativa segura e insere seu usuário e senha local pré-cadastrados na base,
  * **então** o sistema valida as credenciais criptografadas internamente, ignora a validação do SUAP e concede acesso total ao painel administrativo da COAPAC.
* **Bloqueio de Login Nativo para Usuários Comuns:**
  * **Dado que** sou um usuário com perfil `comum`,
  * **quando** tento forçar o login inserindo credenciais na tela de autenticação interna/nativa,
  * **então** o sistema nega o acesso imediatamente e exibe uma mensagem orientando o uso exclusivo do botão do SUAP.
* **Restrição de Acesso a URLs Protegidas:**
  * **Dado que** não possuo nenhuma sessão ativa (seja via SUAP ou nativa),
  * **quando** tento acessar rotas internas ou administrativas,
  * **então** sou redirecionado de volta para a tela de seleção de login.

---

## 📦 US02 - Registro de Reportes (Encontrado e Perdido) e Controle de Estoque
Como **Usuário** (Comum ou Administrador),  
eu quero **cadastrar um reporte de item encontrado ou perdido**,  
para **que a COAPAC possa centralizar o inventário e possibilitar o cruzamento de dados**.

### 📋 Critérios de Aceite (BDD)
* **Cadastro de Reporte de Item Encontrado:**
  * **Dado que** encontrei um objeto no campus e estou autenticado,
  * **quando** preencho o formulário de reporte marcando o tipo como `'encontrado'`, inserindo `categoria_id`, `cor_id`, `descricao`, `local` e anexando uma imagem,
  * **então** o sistema:
    1. Cria um registro na tabela `ITEM` com `status` inicial definido como `'aguardando_entrega'`.
    2. Cria um registro na tabela `REPORTE` com `tipo = 'encontrado'`, vinculando-o ao `ITEM` recém-criado e ao meu `USUARIO`.
* **Cadastro de Reporte de Item Perdido:**
  * **Dado que** perdi um objeto pessoal no campus e estou autenticado,
  * **quando** preencho o formulário de reporte marcando o tipo como `'perdido'`, informando a `categoria_id`, `cor_id`, `descricao` detalhada, `local` aproximado da perda e a data do ocorrido,
  * **então** o sistema cria um registro na tabela `REPORTE` com `tipo = 'perdido'` vinculado ao meu `USUARIO`, deixando a chave estrangeira do `ITEM` como nula (`NULL`), já que o objeto físico ainda não foi recuperado pelo sistema.
* **Validação Física do Estoque pelo Administrador:**
  * **Dado que** o item de um reporte encontrado foi entregue fisicamente à COAPAC,
  * **quando** o Administrador altera o status do item correspondente para `'no_estoque'`,
  * **então** o sistema preenche o campo `data_entrega_estoque` com o timestamp atual e grava a transação na tabela `LOG_AUDITORIA`.
* **Privacidade e Segurança de Dados Sensíveis:**
  * **Dado que** o criador do reporte marcou o item com restrição de visibilidade,
  * **quando** um usuário comum faz uma busca na listagem pública do sistema,
  * **então** os campos de observações profundas e fotos aproximadas permanecem ocultos, visíveis apenas para o perfil `Administrador`.

---

## 🤖 US03 - Geração de Parecer de Inteligência Artificial por Demanda do Administrador
Como **Administrador**,  
eu quero **solicitar que a IA compare um reporte de perda com os itens físicos em estoque**,  
para **obter um laudo automatizado de confiabilidade que auxilie no processo de validação e devolução**.

### 📋 Critérios de Aceite (BDD)
* **Gatilho Manual de Análise por um Administrador:**
  * **Dado que** estou visualizando a fila de reportes do tipo `'perdido'`,
  * **quando** seleciono um reporte de perda específico e clico na ação "Gerar Parecer IA",
  * **então** o sistema envia os dados textuais do reporte e as características dos itens que estão atualmente `'no_estoque'` para o provedor de IA.
* **Retorno Estruturado e Persistência do Parecer:**
  * **Dado que** a API de IA processou a requisição usando as regras de inferência,
  * **quando** o sistema recebe a resposta através de Function Calling,
  * **então** ele cria um registro imutável na tabela `PARECER_IA` salvando o `score_confianca` (0 a 100), as `convergencias` (JSON), as `inconsistencias` (JSON) e a `recomendacao` explícita gerada.
* **Criação da Fila de Homologação:**
  * **Dado que** o parecer da IA foi armazenado com sucesso,
  * **quando** o processo é concluído,
  * **então** o sistema gera automaticamente uma entrada na tabela `ANALISE` com `status = 'pendente'`, unindo o `REPORTE` de perda, o `ITEM` físico candidato avaliado e o `PARECER_IA` emitido.

---

## 🧾 US04 - Homologação de Análise, Devolução e Auditoria
Como **Administrador**,  
eu quero **avaliar a análise de correspondência apoiado pelo laudo da IA**,  
para **aprovar a devolução do item físico e registrar o evento de forma auditável e imutável**.

### 📋 Critérios de Aceite (BDD)
* **Aprovação da Devolução:**
  * **Dado que** estou revisando uma `ANALISE` na fila,
  * **quando** clico em "Aprovar" e preencho a justificativa,
  * **então** o sistema:
    1. Atualiza o status da `ANALISE` para `'aprovado'`.
    2. Altera o status do `ITEM` correspondente para `'entregue'`.
* **Registro de Auditoria Imutável (JSONB):**
  * **Dado que** a transação de aprovação foi submetida,
  * **quando** o banco de dados processa a atualização do item e da análise,
  * **então** um sinal interno do Django intercepta a ação e persiste um registro na tabela `LOG_AUDITORIA` contendo o ID do administrador, a ação realizada, além dos estados `dados_anteriores` e `dados_novos` em formato JSON.
* **Prevenção de Fraude:**
  * **Dado que** um registro de `LOG_AUDITORIA` foi gerado,
  * **quando** qualquer usuário tenta editar ou deletar a linha do log,
  * **então** o sistema recusa a operação (registro estritamente read-only).

---

## 🎁 US05 - Disponibilização para Doação, Adesão de Interesse e Sorteio
Como **Administrador**,  
eu quero **disponibilizar itens que ultrapassaram o prazo de guarda legal para doação em sorteio público**,  
para **dar um destino social aos objetos não reclamados de forma transparente**.

### 📋 Critérios de Aceite (BDD)
* **Transição Temporal Automatizada:**
  * **Dado que** um `ITEM` com status `'no_estoque'` completou 30 dias de armazenamento sem nenhuma análise aprovada,
  * **quando** a rotina diária de monitoramento é executada,
  * **então** o status do item é automaticamente alterado para `'disponivel_para_doacao'`.
* **Manifestação de Interesse do Usuário:**
  * **Dado que** o item está marcado como disponível para doação,
  * **quando** um usuário comum clica em "Manifestar Interesse",
  * **então** o sistema cria um registro na tabela `INTERESSE_SORTEIO` associando o usuário, o item e a data atual de inscrição.
* **Sorteio Justo e Limite de Recebimento:**
  * **Dado que** o Administrador executa a rotina de sorteio para o item,
  * **quando** o algoritmo de seleção aleatória seleciona um ganhador,
  * **então** o sistema valida se o usuário sorteado já recebeu menos de 3 doações em um período ativo de sorteios; se atingiu o limite, ele é ignorado e um novo sorteio ocorre.
* **Concretização e Registro de Doação:**
  * **Dado que** o vencedor elegível foi validado,
  * **quando** o sorteio é concluído,
  * **então** o sistema:
    1. Cria um registro na tabela `DOACAO` definindo `tipo_doacao = 'sorteio'` e vinculando o ganhador em `usuario_receptor_id`.
    2. Atualiza o status do `ITEM` para `'doado'`.
    3. Registra a saída final na tabela `LOG_AUDITORIA`.