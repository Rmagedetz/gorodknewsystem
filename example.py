from flask import Flask, request, jsonify
import sql_connection

app = Flask(__name__)


@app.route('/tilda-webhook', methods=['POST'])
def handle_tilda_request():
    data = request.json or request.form

    # хз что будет в json-е
    sql_connection.Ankets.add_object(name=data['хз'],
                                     parent_main_name=data['хз'],
                                     parent_main_phone=data['хз'])

    return jsonify({"status": "success", "message": "Data received"}), 200


if __name__ == '__main__':
    app.run(port=5001, debug=True)
