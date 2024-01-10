from flask import make_response
from flask import Flask, request, jsonify
from flask_cors import CORS


from .qna import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["CORS_HEADERS"] = "Content-Type"

@app.route('/chat', methods=['POST'])
def chat():
    user_question = request.json['question']
    ai_response = read(user_question)
    response = make_response(jsonify({'response': ai_response}), 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

    
