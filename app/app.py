from flask import Flask, Blueprint
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from routes.usuarios import usuarios # Importa el Blueprint

app = Flask(__name__)
app.secret_key = 'chistosa'

# Configuración de CSRF y LoginManager
csrf = CSRFProtect(app)

# Registro de Blueprints
app.register_blueprint(usuarios)

# Rutas principales
# @app.route("/")
# def index():
#     return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
