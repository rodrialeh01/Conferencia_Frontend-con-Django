from controllers.ventascontroller import BlueprintVenta
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

app.register_blueprint(BlueprintVenta)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)