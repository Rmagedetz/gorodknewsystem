import streamlit as st
from flask import Flask, request, jsonify
import threading
import socket

# -----------------------------
#  FLASK-ПРИЛОЖЕНИЕ (вебхук)
# -----------------------------

app = Flask(__name__)


@app.route('/tilda-webhook', methods=['POST'])
def handle_tilda_request():
    data = request.json or request.form
    print(f"[WEBHOOK] Получены данные: {data}")

    # Здесь можно добавить INSERT в MySQL
    # save_to_db(data)

    return jsonify({"status": "success", "message": "Data received"}), 200


def run_flask():
    """Запуск Flask в отдельном потоке."""
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)


# Запускаем Flask асинхронно
threading.Thread(target=run_flask, daemon=True).start()

# -----------------------------
#  STREAMLIT ИНТЕРФЕЙС
# -----------------------------

st.title("Настройки интеграции Tilda → MySQL")

# Получаем локальный IP
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

FLASK_PORT = 5001
webhook_url = f"http://{local_ip}:{FLASK_PORT}/tilda-webhook"

st.subheader("Ваш Webhook URL для вставки в Tilda:")
st.code(webhook_url)

st.info("Скопируйте этот URL и вставьте в настройки формы → 'Custom webhook'.")

st.write("---")
st.write("Flask-сервер запущен в фоновом режиме и готов принимать данные.")
