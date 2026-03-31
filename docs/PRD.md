# SUMÁRIO
1. [PRD — Product Requirements Document](#1-prd--product-requirements-document)\
    1.1 [Visão Geral](#-11-visão-geral)\
    1.2 [Problemas Principais](#-problemas-principais)
2. [Público Alvo](#2-público-alvo)\
    2.1[Perfis de usuário](#21-perfis-de-usuário)
3. [User Stories e Critérios de Aceite](#3-user-stories-e-critérios-de-aceite)
4. [Fluxo de IA](#4-fluxo-de-ia)\
    4.1[Dicionário](#41-dicionário)



# 1. PRD — Product Requirements Document
### 📌 1.1 Visão Geral

O sistema CADÊ é uma aplicação web AI-First voltada para a catalogação, recuperação e destinação de objetos perdidos no IFRN – Campus Parnamirim.

#### 🎯 Problemas Principais
| Problema | Impacto Atual |Como o CADÊ Resolve
|:--        |:--            | :-- 
Deslocamento desnecessário| Alunos e servidores precisam ir presencialmente à COAPAC apenas para verificar se seu item foi encontrado | Consulta remota e em tempo real de itens com status "Válido" ou "Armazenado", reduzindo deslocamentos improdutivos | 
Processo de devolução ineficiente | Dificuldade em validar a posse do item e rastrear quem retirou o quê |Formulário estruturado de reivindicação + registro auditável de entregas e comprovante digital |
Destinação inadequada de itens não reclamados | Itens esquecidos ocupam espaço físico sem critério claro de descarte ou doação | Monitoramento automático de prazo (30 dias) com alteração de status para "Disponível para Doação" e sistema de sorteio aleatório e auditável |
Falta de transparência e rastreabilidade | Não há histórico claro de movimentações, gerando dúvidas e conflitos | Log de auditoria imutável com todas as ações (cadastros, validações, alterações de status e entregas), filtrável por data e responsável |

# 2. Público Alvo

### 2.1 Perfis de usuário
Perfil de usuário são representações digitais que armazenam preferências, comportamentos e permissões de uma pessoa em um sistema, software ou rede.

a.  Usuário Comum (Aluno/Servidor do IFRN)
Característica |	Descrição
:-- | :--
Quem é | Estudantes regularmente matriculados e servidores (técnicos e docentes) do campus Parnamirim, autenticados via SUAP | 
Necessidades | • Encontrar rapidamente um item perdido<br> • Cadastrar um item achado de forma simples e guiada<br>• Acompanhar o status de suas solicitações e cadastros<br>• Participar de sorteios de doação de forma justa e transparente<br>• Receber orientações claras sobre entrega física na COAPAC |
Permissões no Sistema | • Autenticar-se via SUAP (OAuth2)<br>• Cadastrar itens encontrados com status inicial "Pendente"<br>• Editar ou cancelar seus próprios cadastros apenas enquanto status for "Pendente"<br>• Visualizar itens com status "Válido", "Armazenado" e "Disponível para Doação"<br>• Solicitar reivindicação de itens perdidos com formulário detalhado<br>• Manifestar interesse em itens para doação<br>• Visualizar comprovantes digitais de entregas relacionadas a si|
Perfil Técnico | Usuário com acesso a dispositivos móveis e/ou navegadores web; interface responsiva  e intuitiva; não exige conhecimento técnico avançado

b. Administrador (Equipe da COAPAC)

Característica | Descrição
:-- | :--
Quem é | Servidores responsáveis pela gestão do setor de Apoio Acadêmico (COAPAC)
Necessidades |• Validar ou rejeitar cadastros de itens encontrados (moderação de conteúdo)<br>• Gerenciar o inventário físico e digital com controle de status<br>• Processar reivindicações de posse com acesso a dados sensíveis<br>• Controlar prazos de guarda (30 dias) e destinação final (doação/descarte)<br>• Realizar sorteios com limite de 3 itens por usuário por sessão<br>• Gerar relatórios de auditoria para controle institucional|
Permissões no Sistema | • Todas as permissões do usuário comum<br>• Aprovar/rejeitar cadastros de itens (altera status para "Válido" ou rejeita)<br>• Editar ou excluir qualquer registro de item<br>• Validar ou rejeitar solicitações de reivindicação<br>• Confirmar entrega física no ponto de coleta<br>• Realizar sorteios de doação com seleção aleatória auditável<br>• Aplicar limite de 3 itens por usuário por "Sessão de Doações"<br>• Registrar retirada final com captura obrigatória de: matrícula do recebedor, identificação do admin logado, data/hora exata<br>• Acessar relatórios completos de auditoria com filtros avançados<br>• Visualizar dados sensíveis e imagens de documentos restritos
Perfil Técnico | Usuário com familiaridade com sistemas web institucionais; requer interface clara para operações frequentes de gestão

c. SUAP (Sistema Externo de Autenticação)

Característica | Descrição
:-- | :--  
Papel| Provedor de identidade institucional via OAuth2
Função no Sistema| • Garantir que apenas membros válidos da comunidade IFRN acessem o sistema<br>• Fornecer dados básicos do usuário (matrícula, nome, vínculo) para personalização e auditoria <br>• Assegurar integridade e segurança do processo de login

# 3. User Stories e Critérios de Aceite

**User Stories (Histórias de Usuário)** são descrições simples e curtas de uma funcionalidade, focadas na perspectiva do usuário final, geralmente seguindo o formato: 
```
"Como [tipo de usuário], eu quero [funcionalidade] para [benefício]".
```
Já os **Critérios de Aceite** são condições específicas que essa funcionalidade precisa atender para ser considerada concluída e aceita pelo Product Owner (PO), agindo como regras de negócio e limites de aceitação.

---

1. Autenticação Segura via SUAP: \
Como Aluno ou Servidor do IFRN, \
Eu quero autenticar-me no sistema utilizando minha conta institucional (SUAP), \
Para que eu possa acessar o sistema com segurança e sem necessidade de criar novas senhas. 

    | Criterios de aceite: |
    :--
    ✅ Dado que estou na página inicial, quando clico em "Entrar", então sou redirecionado para a página de OAuth2 do SUAP.
    ✅ Dado que autentiquei com sucesso, quando acesso o dashboard, então vejo meu nome e vínculo (Aluno/Servidor) exibidos no perfil.
    ✅ Dado que não estou autenticado, quando tento acessar uma URL interna (ex: /items), então sou redirecionado automaticamente para o login
    ✅ Dado que o token SUAP expirou, quando realizo uma ação sensível, então o sistema solicita reautenticação

2. Cadastro de Item Encontrado com Moderação\
Como Usuário Comum (Aluno/Servidor),\
Eu quero cadastrar um item que encontrei no campus preenchendo um formulário com campos obrigatórios,\
Para que o item seja registrado no inventário com status "Pendente" e eu possa entregá-lo na COAPAC para devolução ao dono. 

    | Critérios de Aceite |
    :--
    ✅ Dado que estou logado, quando acesso "Cadastrar Item", então vejo campos obrigatórios: Imagem, Categoria, Cor, Local de Encontro e Observações (opcional).
    ✅ Dado que preenchi todos os campos, quando submeto o formulário, então o item é salvo com status "Pendente" e não aparece na lista pública imediatamente.
    ✅ Dado que o cadastro foi realizado com sucesso, então recebo uma mensagem clara instruindo a entrega física do item na COAPAC para conclusão do processo.
    ✅ Dado que o item está com status "Pendente", quando acesso "Itens Cadastrados", então posso editar ou cancelar o próprio registro; após cancelamento, o status muda para "Cancelado".
    

3. Solicitação de Reivindicação de Item Perdido\
Como Usuário Comum que perdeu um objeto,\
Eu quero solicitar a reivindicação de um item listado como "Válido" ou "Armazenado" preenchendo um formulário detalhado,\
Para que eu possa provar minha posse com informações específicas e recuperar meu bem sem deslocamento.
    | Critérios de Aceite|
    :--
    ✅ Dado que visualizo um item na lista pública com status "Válido" ou "Armazenado", quando clico em "Reivindicar", então acesso um formulário com campos obrigatórios: descrição detalhada, data aproximada da perda, local específico e características não visíveis publicamente (ex: marca interna, arranhão, número de série).
    ✅ Dado que envio a solicitação com sucesso, quando o administrador acessa a fila de reivindicações, então ele vê os detalhes completos da prova de posse, incluindo dados sensíveis que não estão visíveis para usuários comuns (ex: foto do item ou documento, características específicas)
    ✅ Dado que enviei uma reivindicação, quando acompanho o status em "Minhas Solicitações", então vejo se foi "Aprovada", "Rejeitada" ou "Em Análise", com justificativa do administrador quando aplicável.

4. Registro de Entrega com Auditoria Imutável\
Como Administrador (COAPAC ou aluno bolsista),\
Eu quero registrar a entrega final de um item (devolução ao dono ou doação) capturando dados obrigatórios da transação,\
Para que haja controle físico do inventário, geração de comprovante digital e rastreabilidade total para auditoria futura.

    | Critérios de Aceite |
    :--
    ✅ Dado que vou registrar a entrega de um item, quando acesso a função "Registrar Retirada", então o sistema exige obrigatoriamente: (a) Matrícula SUAP ou identificação do recebedor, (b) Identificação automática do administrador logado, (c) Data e hora exata da transação (preenchidas automaticamente).
    ✅ Dado que confirmo a entrega, quando o sistema processa, então o status do item muda para "Entregue" ou "Doado" automaticamente.
    ✅ Dado que a transação foi concluída, quando verifico o log de auditoria, então o registro é criado como "apenas leitura", impedindo edição ou exclusão futura.
    ✅ Dado que a entrega foi registrada, quando o usuário recebe o comprovante, então ele pode visualizar/realizar download um comprovante digital da transação.

5. Sorteio para Itens Não Reclamados\
Como Administrador (COAPAC),\
Eu quero realizar um sorteio automático e aleatório entre usuários interessados em itens disponíveis para doação, respeitando o limite de 3 itens por sessão,\
Para que a destinação final de itens não reclamados após 30 dias seja transparente, equitativa e auditável. 


    | Critérios de Aceite |
    :--
    ✅ Dado que um item com status "Armazenado" atingiu 30 dias sem reivindicação aprovada, quando o sistema executa a rotina de monitoramento, então o status é alterado automaticamente para "Disponível para Doação".
    ✅ Dado que há usuários que manifestaram interesse no item, quando clico em "Realizar Sorteio", então o sistema seleciona um beneficiário de forma aleatória.
    ✅ Dado que um usuário já recebeu 3 itens em doações na mesma "Sessão de Doações", quando tento incluí-lo em um novo sorteio, então o sistema o exclui temporariamente da lista de elegíveis para garantir distribuição justa.
    ✅ Dado que o sorteio foi finalizado, quando visualizo o resultado, então o sistema: (a) registra o vencedor no log de auditoria, (b) atualiza o status do item para "Reservado para Doação", e (c) notifica o beneficiário para retirada na COAPAC.
    ✅ Dado que a sessão de doações foi encerrada pelo administrador, quando inicio uma nova sessão, então a contagem de itens recebidos por usuário é zerada, permitindo participação normal em sessões futuras.

# 4. Fluxo de IA


O prompt abaixo serve para validação de reinvidicações de item. Isto é, s sistema pré-analisa as descrições e fornece um parecer técnico estruturado com score de confiança, acelerando e padronizando a decisão.


```json
{
  "system_prompt": "Você é um assistente especializado em validação de posse de itens perdidos. Compare a descrição do item cadastrado com a reivindicação do usuário e identifique: (1) pontos de convergência, (2) inconsistências ou contradições, (3) score de confiança (0-100%). Responda em JSON estruturado para integração via Function Calling.",
  
  "few_shot_examples": [
    {
      "item_cadastrado": "Chaveiro preto com pingente de bola de futebol, encontrado no bloco B, perto da sala 12",
      "reivindicacao": "Perdi meu chaveiro preto com uma bolinha de futebol azul, deve ter caído perto da sala de informática do bloco B na terça-feira",
      "resposta_esperada": {
        "convergencias": ["cor preta", "pingente de bola de futebol", "localização bloco B"],
        "inconsistencias": ["cor da bola: cadastrado não especifica cor, usuário mencionou azul"],
        "score_confianca": 88,
        "recomendacao": "Alta probabilidade de posse legítima - sugerir validação com pergunta complementar sobre cor da bola"
      }
    }
  ],
  
  "function_calling": {
    "name": "registrar_parecer_ia",
    "parameters": {
      "id_item": "string",
      "id_reivindicacao": "string",
      "score_confianca": "number (0-100)",
      "convergencias": "array<string>",
      "inconsistencias": "array<string>",
      "recomendacao": "string",
      "perguntas_sugeridas": "array<string> (opcional)"
    }
  }
}
```

### 4.1 Dicionário

1. `system_prompt`: É a instrução de identidade + a tarefa que a inteligência artificial deve fazer.
2. `few_shot_examples`: O JSON mostra para a IA **um exemplo de caso real** (um chaveiro encontrado vs. um chaveiro perdido) e **ensina como ela deve "pensar"** para chegar ao score de 88%
3. `function_calling`: Define uma estrutura chamada _`registrar_parecer_ia`_. Em vez de a IA responder um texto longo, ela vai preencher esses campos (como *score_confianca* e *recomendacao*) 


Exemplo de tela de análise de reivindicações, após a resposta da IA:

```
┌─────────────────────────────────────────────────────────────────┐
│  REIVINDICAÇÕES PENDENTES                           [Filtros ▼] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📦 Item: Chaveiro Preto com Pingente                           │
│     Status: Armazenado | Data: 15/03/2026                       │
│                                                                 │
│  👤 Reivindicante: João Silva (Matrícula: 2023123456)           │
│     Data da Solicitação: 16/03/2026 14:30                       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🤖 PARECER DA IA                                       │   │
│  │  Score de Confiança: ████████████████░░ 88%             │   │
│  │                                                         │   │
│  │  ✅ Convergências:                                      │   │
│  │     • Cor preta do chaveiro                             │   │
│  │     • Pingente de bola de futebol                       │   │
│  │     • Localização Bloco B                               │   │
│  │     • Data coerente                                     │   │
│  │                                                         │   │
│  │  ⚠️ Inconsistências:                                    │   │
│  │     • Cor da bola não especificada no cadastro          │   │
│  │     • Arranhão não verificável                          │   │
│  │                                                         │   │
│  │  💡 Recomendação: Alta probabilidade - validar com      │   │
│  │     pergunta complementar sobre cor da bola             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [❌ REJEITAR]          [✅ APROVAR]          [❓ PEDIR MAIS INFO] │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```