from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import (
    LoginManager, 
    login_required, 
    current_user, 
    login_user, 
    logout_user
)
from datetime import datetime
from models import Usuario, Pedido, ItemPedido, Produto
from database import db


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def carregar_usuario(id_usuario):
    """Carrega o usuário pelo ID para o Flask-Login"""
    return Usuario.query.get(int(id_usuario))


# Rotas de Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para autenticação de usuários"""
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            return redirect(url_for(f'painel_{usuario.tipo}'))
            
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Rota para logout de usuários"""
    logout_user()
    return redirect(url_for('login'))


# Rotas para Garçons
@app.route('/garcom/pedidos', methods=['GET', 'POST'])
@login_required
def painel_garcom():
    """Painel principal do garçom"""
    if current_user.tipo != 'garcom':
        return redirect(url_for('login'))
    
    return render_template('garcom/pedidos.html')


@app.route('/garcom/novo-pedido', methods=['POST'])
@login_required
def criar_pedido():
    """Rota para criar novo pedido"""
    if current_user.tipo != 'garcom':
        return jsonify({'erro': 'Acesso não autorizado'}), 403
    
    dados = request.get_json()
    novo_pedido = Pedido(
        mesa=dados['mesa'],
        status='aguardando',
        garcom_id=current_user.id
    )
    db.session.add(novo_pedido)
    db.session.commit()
    
    return jsonify({'mensagem': 'Pedido criado com sucesso'})


# Rotas para Cozinha
@app.route('/cozinha')
@login_required
def painel_cozinha():
    """Painel principal da cozinha"""
    if current_user.tipo != 'chef':
        return redirect(url_for('login'))
    
    pedidos = Pedido.query.filter(
        Pedido.status.in_(['aguardando', 'preparando'])
    ).order_by(Pedido.data_criacao).all()
    
    return render_template('cozinha/painel.html', pedidos=pedidos)


# Rotas para Entregadores
@app.route('/entregador')
@login_required
def painel_entregador():
    """Painel principal do entregador"""
    if current_user.tipo != 'entregador':
        return redirect(url_for('login'))
    
    pedidos = Pedido.query.filter_by(
        status='pronto_entrega'
    ).order_by(Pedido.data_criacao).all()
    
    return render_template('entregador/painel.html', pedidos=pedidos)


# Rotas para Gerentes
@app.route('/gerente')
@login_required
def painel_gerente():
    """Painel principal do gerente"""
    if current_user.tipo != 'gerente':
        return redirect(url_for('login'))
    
    return render_template('gerente/dashboard.html')


@app.route('/gerente/relatorios')
@login_required
def relatorios():
    """Rota para geração de relatórios"""
    if current_user.tipo != 'gerente':
        return redirect(url_for('login'))
    
    return render_template('gerente/relatorios.html')


# API endpoints para atualização em tempo real
@app.route('/api/atualizar-status', methods=['POST'])
@login_required
def atualizar_status():
    """Endpoint para atualização de status dos pedidos"""
    dados = request.get_json()
    pedido = Pedido.query.get(dados['pedido_id'])
    
    if not pedido:
        return jsonify({'erro': 'Pedido não encontrado'}), 404
        
    pedido.status = dados['novo_status']
    pedido.data_atualizacao = datetime.now()
    db.session.commit()
    
    return jsonify({'mensagem': 'Status atualizado com sucesso'})


if __name__ == '__main__':
    app.run(debug=True)
