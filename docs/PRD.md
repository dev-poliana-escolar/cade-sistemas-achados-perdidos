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

O CADÊ é um sistema de achados e perdidos que permite aos usuários o registro de itens encontrados e a solicitação para recuperação de itens perdidos. Além disso, o sistema realiza intermediação de doações em formato de sorteio. Diante disso, administradores validam itens, analisam solicitações e conduzem doações.

#### 🎯 Problemas Principais
| Problema | Impacto Atual |Como o CADÊ Resolve
|:--        |:--            | :-- 
Deslocamento desnecessário| Alunos e servidores precisam ir presencialmente à COAPAC apenas para verificar se seu item foi encontrado | Consulta remota de itens com status "Válido" ou "Armazenado", reduzindo deslocamentos. | 
Processo de devolução ineficiente | Dificuldade em validar a posse do item e rastrear quem retirou o quê |Formulário estruturado de reivindicação + registro auditável de entregas como comprovante digital |
Destinação inadequada de itens não reclamados | Itens esquecidos ocupam espaço físico sem critério claro de descarte ou doação | Monitoramento automático de prazo (30 dias) com alteração de status para "Disponível para Doação" e sistema de sorteio aleatório e auditável |
Falta de transparência e rastreabilidade | Não há histórico claro de movimentações, gerando dúvidas e conflitos | Log de auditoria imutável com todas as ações (cadastros, validações, alterações de status e entregas), filtrável por data e responsável |

# 2. Público Alvo

### 2.1 Perfis de usuário
Perfil de usuário são representações digitais que armazenam preferências, comportamentos e permissões de uma pessoa em um sistema, software ou rede.

a.  Usuário Comum (Aluno/Servidor do IFRN)
Característica |	Descrição
:-- | :--
Quem é | Estudantes regularmente matriculados e servidores (técnicos e docentes) do campus Parnamirim, autenticados via SUAP | 
Necessidades | • Encontrar rapidamente um item perdido<br> • Cadastrar um item encontrado de forma simples <br>• Acompanhar o status de suas solicitações e cadastros<br>• Participar de sorteios de doação de forma justa e transparente<br>• Receber orientações claras sobre entrega física na COAPAC |
Permissões no Sistema | • Autenticar-se via SUAP (OAuth2)<br>• Cadastrar itens encontrados com status inicial "Pendente"<br>• Editar ou cancelar seus próprios cadastros, enquanto status for "Pendente"<br>• Visualizar itens com status "Válido", "Armazenado" e "Disponível para Doação"<br>• Solicitar reivindicação de itens perdidos com formulário <br>• Manifestar interesse em itens para doação<br>• Visualizar comprovantes digitais de entregas relacionadas a ele|
Perfil Técnico | Usuário com acesso a dispositivos móveis e/ou navegadores web; interface responsiva  e intuitiva; não exige conhecimento técnico avançado

b. Administrador (Equipe da COAPAC)

Característica | Descrição
:-- | :--
Quem é | Servidores responsáveis pela gestão do setor de Apoio Acadêmico (COAPAC)
Necessidades |• Validar ou rejeitar cadastros de itens encontrados (moderação de conteúdo)<br>• Gerenciar o inventário físico e digital com controle de status<br>• Processar reivindicações de posse. Ocasional acesso a dados sensíveis<br>• Controlar prazos de guarda (30 dias) e destinação final (doação/descarte)<br>• Conduzir sessão de sorteios |
Permissões no Sistema | • Todas as permissões do usuário comum<br>• Aprovar/rejeitar cadastros de itens (altera status para "Válido" ou rejeita)<br>• Editar ou excluir qualquer registro de item<br>• Validar ou rejeitar solicitações de reivindicação<br>• Confirmar entrega física no ponto de coleta<br>• Realizar sorteios de doação com seleção aleatória auditável <br>• Acessar relatórios completos de auditoria com filtros <br>• Visualizar dados sensíveis e imagens de documentos restritos
Perfil Técnico | Usuário com familiaridade com sistemas web institucionais; requer interface clara para operações frequentes de gestão

c. SUAP (Sistema Externo de Autenticação)

Característica | Descrição
:-- | :--  
Papel| Provedor de identidade institucional via OAuth2
Função no Sistema| • Garantir que apenas membros válidos da comunidade IFRN acessem o sistema<br>• Fornecer dados básicos do usuário (matrícula, nome, vínculo) para personalização e auditoria <br>• Assegurar integridade e segurança do processo de login

---

# 3. User Stories e Critérios de Aceite

Acesse a especificação: [User Stories e critérios de aceite](user_storys.md)

---
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