from flask import Flask
from database import configurar_banco, Usuario
from flask_login import LoginManager

def criar_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurante.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    
    # Inicializa o banco de dados
    configurar_banco(app)
    
    # Importa e registra as rotas
    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Configura o Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Corrigido para usar o endpoint do blueprint
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    return app


app = criar_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 