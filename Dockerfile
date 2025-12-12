# Dockerfile
FROM python:3.11-slim

# Неинтерактивный режим для apt
ENV DEBIAN_FRONTEND=noninteractive

# Рабочая директория
WORKDIR /app

# Ставим системные зависимости (по минимуму) и очищаем кеш
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt /app/

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY . /app

# Streamlit будет слушать порт 8000
EXPOSE 8000

# Настройки сервера Streamlit
ENV STREAMLIT_SERVER_PORT=8000
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Команда запуска:
# 1) создаём каталог .streamlit
# 2) если переменная STREAMLIT_SECRETS задана — пишем её содержимое в /app/.streamlit/secrets.toml
# 3) запускаем Streamlit
CMD sh -c '\
  mkdir -p /app/.streamlit && \
  if [ -n "$STREAMLIT_SECRETS" ]; then \
    printf "%s" "$STREAMLIT_SECRETS" > /app/.streamlit/secrets.toml; \
  fi && \
  streamlit run main.py \
'
