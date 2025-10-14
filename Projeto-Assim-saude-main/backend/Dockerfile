# ==========================================
# Imagem base leve do Python 3.11
# ==========================================
FROM python:3.11-slim

# ==========================================
# Diretório de trabalho
# ==========================================
WORKDIR /app

# ==========================================
# Evita cache de .pyc e força logs imediatos
# ==========================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ==========================================
# Instala dependências do sistema
# Inclui libs para MySQL e PostgreSQL
# ==========================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd gcc libffi-dev libssl-dev \
    default-libmysqlclient-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# Copia e instala dependências Python
# ==========================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# Copia o restante do backend
# ==========================================
COPY . .

# ==========================================
# Exposição de porta e variáveis padrão
# Render define $PORT automaticamente
# ==========================================
EXPOSE 5000
ENV PORT=5000
ENV FLASK_ENV=development
ENV FLASK_DEBUG=True

# ==========================================
# Comando de inicialização:
# - Produção (Render): Gunicorn
# - Desenvolvimento (local): Flask dev server
# ==========================================
CMD ["sh", "-c", "\
  if [ \"$FLASK_ENV\" = 'production' ] || [ \"$RENDER\" = 'true' ]; then \
    echo 'Iniciando em produção com Gunicorn...'; \
    exec gunicorn --workers 3 --bind 0.0.0.0:${PORT} app:app; \
  else \
    echo 'Iniciando em modo desenvolvimento com Flask...'; \
    exec flask run --host=0.0.0.0 --port=${PORT}; \
  fi"]
