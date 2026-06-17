# Teste de Performance

## 1. Resumo Executivo das Métricas

O teste de carga executado com o `k6` seguiu um modelo de rampa progressiva com pico de até 30 usuários virtuais simultâneos (*Virtual Users - VUs*). Sob a ótica exclusiva dos limites configurados (*Thresholds*), o comportamento técnico bruto do servidor apresentou-se estável:

* **Taxa de Erro (`http_req_failed`):** **0%**. Não foram registradas falhas de conectividade na infraestrutura local ou erros internos de servidor (HTTP 5xx).
* **Tempo de Resposta (`http_req_duration`):** Os tempos de processamento individuais medidos pelo k6 ficaram extremamente baixos, oscilando predominantemente na faixa de **0.5ms a 3ms** por requisição.
* **Validação dos Critérios:** O requisito técnico de desempenho (`p95 < 500ms`) foi formalmente atendido.


---

## 2. Análise do Principal Gargalo: O Fenômeno do Redirecionamento (HTTP 302)

Ao auditar a massa de dados do arquivo JSON de telemetria, identificou-se um padrão idêntico e repetitivo em todas as iterações de cada ciclo de requisição efetuado pelas VUs:

```
[k6] GET http://127.0.0.1:8000/items/
  └── [Django] Retorna HTTP 302 (Found) + Header Location: /?next=/items/
        └── [k6] Segue Automaticamente -> GET http://127.0.0.1:8000/?next=/items/
              └── [Django] Retorna HTTP 200 (OK)
```

### Impactos Arquiteturais Deste Comportamento

1. **Duplicação Artificial da Carga:** Para cada clique simulado ou interação pretendida na listagem de itens, o ecossistema é forçado a processar **duas requisições HTTP** consecutivas em vez de uma. Sob cenários de escala real (ex: 5.000 usuários ativos), o volume no servidor saltará para 10.000 requisições, degradando precocemente o throughput.
2. **Desperdício Volumétrico de Recursos:** O tráfego de entrada e saída (`data_sent` / `data_received`) e a concorrência na tabela de sockets de rede duplicam de forma desnecessária, elevando o custo operacional da infraestrutura.
3. **Latência Mascarada (Efeito RTT):** No ambiente de loopback local (`127.0.0.1`), o impacto do redirecionamento é imperceptível (microsegundos). Contudo, em redes de produção em nuvem (AWS, GCP, etc.), o usuário sofrerá o impacto direto de dois *Round Trip Times (RTT)* completos na rede, gerando uma percepção de lentidão na interface (falso gargalo de front-end).

---

## 3. Diagnóstico de Causa Raiz

O redirecionamento explícito da rota `/items/` para a raiz com o parâmetro descritivo `?next=/items/` é o comportamento padrão gerado por mecanismos de controle de acesso do ecossistema Django (como o decorator `@login_required` ou classes de permissão do Django REST Framework).

O endpoint de Achados e Perdidos está interceptando os Usuários Virtuais antes que eles acessem a camada de dados. Como o script do k6 executa requisições anônimas (sem o envio prévio de cabeçalhos de sessão, cookies válidos ou tokens JWT), o Django barra o acesso à listagem e redireciona os clientes para a página de autenticação/home (que responde com HTTP 200). 

**Conclusão do Diagnóstico:** O teste atual avaliou com sucesso a capacidade do Django de redirecionar usuários não autenticados e renderizar a página inicial, mas **não testou** o gargalo do endpoint `/items/` (consultas ao banco de dados, serialização de objetos e paginação).

---

<br>

# Guia de Execução do Teste de Performance com Django e K6

---

## 🔧 Passo 1: Instalar o K6

Antes de executar o teste de performance, é necessário garantir que o K6 esteja instalado na máquina.

### Verificar se o K6 já está instalado

Abra o Git Bash e execute:

```bash
k6 version
```

Se o terminal retornar uma versão semelhante à exibida abaixo, a instalação já está concluída e você pode seguir para o próximo passo:

```text
k6 v0.49.0
```

---

### Instalação utilizando Chocolatey

Caso utilize o gerenciador de pacotes Chocolatey, execute o seguinte comando em um terminal com privilégios administrativos:

```bash
choco install k6
```

Após a instalação, feche e abra novamente o terminal e valide:

```bash
k6 version
```

---

### Instalação utilizando Winget

No PowerShell executado como administrador, execute:

```powershell
winget install k6.k6
```

Ao término da instalação, valide:

```bash
k6 version
```

---

### Instalação Manual

Caso prefira instalar manualmente:

1. Acesse a documentação oficial de instalação do K6:
   https://grafana.com/docs/k6/latest/set-up/install-k6/

2. Baixe a versão compatível com seu sistema operacional.

3. Extraia os arquivos e adicione o diretório que contém o executável `k6` às variáveis de ambiente do sistema.

4. Abra um novo terminal e execute:

```bash
k6 version
```

---

### Resultado Esperado

A instalação será considerada bem-sucedida quando o comando:

```bash
k6 version
```

retornar uma saída semelhante a:

```text
k6 v0.49.0
```

Somente após essa validação prossiga para a execução do teste de performance.

---



## 📊 Passo 2: Executar o K6 e Exportar o Relatório JSON

1. Abra uma **nova janela do Git Bash** (mantendo a janela do Django em execução).

2. Navegue até a pasta onde está localizado o arquivo `teste_performance.js` e execute o seguinte comando:

```bash
cd ~/projeto-final-grupo2-poliana-kaua-matheus/tests_suite/performance
```

```bash
k6 run --out json=relatorio_performance.json teste_performance.js
```

Ao término da execução, será gerado o arquivo:

```text
relatorio_performance.json
```

---

## 🏁 Passo 3: Validar os Resultados

Após o término do teste (aproximadamente 2 minutos), verifique se o arquivo `relatorio_performance.json` foi criado corretamente e analise o resumo exibido no terminal.

### Critérios de Aprovação

#### 1. Taxa de Erros

Localize a métrica:

```text
http_req_failed
```

O valor deve ser inferior a:

```text
1,00% (rate < 0.01)
```

#### 2. Tempo de Resposta (p95)

Localize a métrica:

```text
http_req_duration
```

Verifique o valor da coluna:

```text
p(95)
```

O resultado deve ser inferior a:

```text
500 ms
```


---

## Visão do Aluno

Ao realizar o teste, foi validada a regra de negócio que impede o acesso ao sistema por usuários não autenticados. Entretanto, não foi possível testar o endpoint principal de forma adequada, pois os usuários virtuais gerados pelo k6 não possuíam credenciais válidas (matrícula e senha do SUAP) para realizar a autenticação. Como consequência, as requisições foram redirecionadas para a página de login, impossibilitando a avaliação direta do desempenho do endpoint protegido.