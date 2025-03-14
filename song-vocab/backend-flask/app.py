from flask import Flask
from flask_cors import CORS
from routes import songs

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Register routes
songs.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, port=5000) 