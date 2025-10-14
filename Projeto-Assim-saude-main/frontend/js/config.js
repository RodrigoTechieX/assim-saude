// Configuração da URL base da API do backend
// Quando rodar via Docker, o nome do serviço "backend" é resolvido automaticamente via DNS interno do Docker.
// Fora do Docker (em desenvolvimento local), use "localhost".

const API_URL = window.location.hostname === "localhost"
  ? "http://localhost:5000/api"
  : "http://backend:5000/api";

export { API_URL };
