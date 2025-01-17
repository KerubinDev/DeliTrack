from flask import Flask, render_template, redirect, url_for, request, flash
from database import configurar_banco, Usuario
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

def criar_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurante.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    
    # Inicializa o banco de dados
    configurar_banco(app)
    
    # Configura o Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Rotas
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            senha = request.form.get('senha')
            
            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario and check_password_hash(usuario.senha_hash, senha):
                login_user(usuario)
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('dashboard'))
            
            flash('Email ou senha inválidos', 'error')
        
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def dashboard():
        if current_user.tipo == 'garcom':
            return render_template('garcom/pedidos.html')
        elif current_user.tipo == 'cozinheiro':
            return render_template('cozinha/painel.html')
        elif current_user.tipo == 'entregador':
            return render_template('entregador/painel.html')
        elif current_user.tipo == 'gerente':
            return render_template('gerente/dashboard.html')
        
        return redirect(url_for('login'))
    
    return app


app = criar_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')