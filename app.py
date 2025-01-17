from flask import Flask
from database import configurar_banco, Usuario
from flask_login import LoginManager
import routes

def criar_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurante.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True  # Habilitando o modo debug
    
    # Inicializa o banco de dados
    configurar_banco(app)
    
    # Configura o Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Corrigido para usar o blueprint
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Registra as rotas
    routes.init_app(app)
    
    return app


app = criar_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 