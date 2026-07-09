import http from 'k6/http';
import { check, sleep } from 'k6';

// 1. Configurações do Teste (Estágios e Regras)
export const options = {
  stages: [
    { duration: '30s', target: 15 }, // 1. Ramp-up: sobe gradativamente de 0 para 15 usuários em 30 segundos
    { duration: '1m', target: 15 },  // 2. Carga Constante: mantém 15 usuários batendo no Django por 1 minuto
    { duration: '30s', target: 30 },  // 3. Pico: Sobe para 30 usuários rapidamente em 30 segundos para estressar o sistema
  ],
  thresholds: {
    // REQUISITO: p95 deve ser menor que 500ms (95% das requisições precisam responder abaixo de 500ms)
    http_req_duration: ['p(95)<500'],
    // REQUISITO: A taxa de erro de requisições falhas deve ser menor que 1% (0.01)
    http_req_failed: ['rate<0.01'],
  },
};

// 2. Ação que cada usuário simulado vai fazer
export default function () {
  // ATENÇÃO: Altere para a URL exata do seu endpoint de Achados e Perdidos
  // Exemplo: 'http://127.0.0.1:8000/api/itens/' ou '/itens/perdidos/'
  const URL_DO_DJANGO = 'http://127.0.0.1:8000/items/';

  // Faz a requisição GET no endpoint principal
  const response = http.get(URL_DO_DJANGO);

  // Verifica se o Django está respondendo com Status 200 (Sucesso)
  check(response, {
    'status igual a 200': (r) => r.status === 200,
  });

  // Aguarda 1 segundo antes do usuário fazer uma nova requisição
  // Isso impede que um único usuário derrube o servidor sozinho e simula acessos reais
  sleep(1);
}