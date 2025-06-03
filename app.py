from flask import Flask, jsonify
from src.utils.firebase import initialize_firebase
from src.routes.auth_routes import auth_bp
from src.routes.event_routes import event_bp

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase
initialize_firebase()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(event_bp, url_prefix='/api')

# Root route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to sprpsr backend!"})

if __name__ == '__main__':
    app.run(debug=True, port=8890) 