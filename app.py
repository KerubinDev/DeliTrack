from flask import Flask
from database import configurar_banco
from routes import app as routes_app
from flask_login import LoginManager

def criar_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    
    # Configura o banco de dados
    configurar_banco(app)
    
    # Registra as rotas
    app.register_blueprint(routes_app)
    
    # Configura o Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    return app


if __name__ == '__main__':
    app = criar_app()
    app.run(debug=True) 