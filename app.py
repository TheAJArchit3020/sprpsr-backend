from flask import Flask, jsonify
from src.utils.firebase import initialize_firebase
from src.routes.auth_routes import auth_bp
from src.routes.event_routes import event_bp
from src.routes.user_routes import user_bp
from src.routes.event_request_routes import event_request_bp
from src.routes.chat_routes import chat_bp
from src.config.swagger import init_swagger
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

initialize_firebase()
spec = init_swagger(app)

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(event_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(event_request_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')


@app.route('/', methods=['GET'])
def home():
    """
    Welcome endpoint
    ---
    tags:
      - General
    responses:
      200:
        description: Welcome message
        schema:
          type: object
          properties:
            message:
              type: string
              example: Welcome to sprpsr backend!
    """
    return jsonify({"message": "Welcome to sprpsr backend!"})

if __name__ == '__main__':
    app.run(debug=True, port=8890) 