from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/tilda-webhook', methods=['POST'])
def handle_tilda_request():
    data = request.json  # или request.form
    # Здесь ваша логика:
    print(f"Получены данные: {data}")
    # Сохранение в базу данных, отправка email, интеграция с CRM...
    return jsonify({"status": "success", "message": "Data received"}), 200


if __name__ == '__main__':
    app.run(debug=True)
