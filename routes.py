from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from database import db, Usuario, Produto, Pedido, ItemPedido
from werkzeug.security import check_password_hash

bp = Blueprint('main', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha_hash, senha):
            login_user(usuario)
            return redirect(url_for('main.dashboard'))
        
        flash('Email ou senha inválidos', 'error')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/')
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
    
    return redirect(url_for('main.login'))

@bp.route('/api/produto/<int:produto_id>')
@login_required
def get_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    return {
        'id': produto.id,
        'nome': produto.nome,
        'preco': produto.preco,
        'descricao': produto.descricao
    }

@bp.route('/api/pedidos', methods=['POST'])
@login_required
def criar_pedido():
    if current_user.tipo != 'garcom':
        return {'success': False, 'error': 'Não autorizado'}, 403
    
    data = request.get_json()
    
    pedido = Pedido(
        mesa=data['mesa'],
        status='aguardando',
        garcom_id=current_user.id
    )
    db.session.add(pedido)
    
    for item in data['itens']:
        item_pedido = ItemPedido(
            pedido=pedido,
            produto_id=item['produto_id'],
            quantidade=item['quantidade']
        )
        db.session.add(item_pedido)
    
    db.session.commit()
    return {'success': True, 'pedido_id': pedido.id}

@bp.route('/api/pedidos/atualizacoes')
@login_required
def get_atualizacoes():
    pedidos_aguardando = Pedido.query.filter_by(status='aguardando').all()
    pedidos_preparando = Pedido.query.filter_by(status='preparando').all()
    pedidos_prontos = Pedido.query.filter_by(status='pronto').all()
    
    return {
        'aguardando': [p.to_dict() for p in pedidos_aguardando],
        'preparando': [p.to_dict() for p in pedidos_preparando],
        'prontos': [p.to_dict() for p in pedidos_prontos]
    }

@bp.route('/api/pedidos/<int:pedido_id>/iniciar', methods=['POST'])
@login_required
def iniciar_pedido(pedido_id):
    if current_user.tipo != 'cozinheiro':
        return {'success': False, 'error': 'Não autorizado'}, 403
    
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.status = 'preparando'
    db.session.commit()
    
    return {'success': True}

@bp.route('/api/pedidos/<int:pedido_id>/pronto', methods=['POST'])
@login_required
def finalizar_pedido(pedido_id):
    if current_user.tipo != 'cozinheiro':
        return {'success': False, 'error': 'Não autorizado'}, 403
    
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.status = 'pronto'
    db.session.commit()
    
    return {'success': True}

@bp.route('/api/entregas/status')
@login_required
def get_status_entregas():
    if current_user.tipo != 'entregador':
        return {'success': False, 'error': 'Não autorizado'}, 403
    
    return {
        'prontos': [],  # Implementar lógica de pedidos prontos
        'andamento': []  # Implementar lógica de entregas em andamento
    }

@bp.route('/api/dashboard/metricas')
@login_required
def get_metricas_dashboard():
    if current_user.tipo != 'gerente':
        return {'success': False, 'error': 'Não autorizado'}, 403
    
    # Implementar lógica de métricas do dashboard
    return {
        'metricas': {},
        'graficos': {
            'vendas': {'labels': [], 'valores': []},
            'produtos': {'labels': [], 'valores': []}
        },
        'entregas': [],
        'desempenho': []
    }

def init_app(app):
    app.register_blueprint(bp)
