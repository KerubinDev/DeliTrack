from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, jsonify
)
from flask_login import login_required, current_user
from datetime import datetime
from .models import (
    Usuario, Cliente, Pedido, ItemPedido, Entrega, ItemMenu, db
)

# Blueprint para organizar as rotas
bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def index():
    """Rota principal que redireciona baseado no tipo de usuário."""
    if current_user.tipo == 'garcom':
        return redirect(url_for('main.tela_garcom'))
    elif current_user.tipo == 'chef':
        return redirect(url_for('main.tela_cozinha'))
    elif current_user.tipo == 'entregador':
        return redirect(url_for('main.tela_entregador'))
    elif current_user.tipo == 'gerente':
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@bp.route('/garcom')
@login_required
def tela_garcom():
    """Tela do garçom para gerenciar pedidos."""
    if current_user.tipo != 'garcom':
        flash('Acesso não autorizado')
        return redirect(url_for('main.index'))
    
    clientes = Cliente.query.all()
    itens_menu = ItemMenu.query.all()
    pedidos_ativos = Pedido.query.filter(
        Pedido.status.in_(['aguardando', 'em_preparo'])
    ).all()
    
    return render_template(
        'garcom/index.html',
        clientes=clientes,
        itens_menu=itens_menu,
        pedidos_ativos=pedidos_ativos
    )


@bp.route('/cozinha')
@login_required
def tela_cozinha():
    """Tela da cozinha para gerenciar preparo dos pedidos."""
    if current_user.tipo != 'chef':
        flash('Acesso não autorizado')
        return redirect(url_for('main.index'))
    
    pedidos = Pedido.query.filter(
        Pedido.status.in_(['aguardando', 'em_preparo'])
    ).order_by(Pedido.data_criacao).all()
    
    return render_template('cozinha/index.html', pedidos=pedidos)


@bp.route('/entregador')
@login_required
def tela_entregador():
    """Tela do entregador para gerenciar entregas."""
    if current_user.tipo != 'entregador':
        flash('Acesso não autorizado')
        return redirect(url_for('main.index'))
    
    entregas_pendentes = Entrega.query.filter_by(
        entregador_id=current_user.id,
        status='pendente'
    ).all()
    
    entregas_hoje = Entrega.query.filter(
        Entrega.entregador_id == current_user.id,
        Entrega.data_entrega >= datetime.today().date()
    ).all()
    
    return render_template(
        'entregador/index.html',
        entregas_pendentes=entregas_pendentes,
        entregas_hoje=entregas_hoje
    )


@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard para gerenciamento geral."""
    if current_user.tipo != 'gerente':
        flash('Acesso não autorizado')
        return redirect(url_for('main.index'))
    
    pedidos_andamento = Pedido.query.filter(
        Pedido.status != 'entregue'
    ).count()
    
    entregas_concluidas = Entrega.query.filter_by(
        status='entregue'
    ).count()
    
    usuarios = Usuario.query.all()
    
    return render_template(
        'dashboard/index.html',
        pedidos_andamento=pedidos_andamento,
        entregas_concluidas=entregas_concluidas,
        usuarios=usuarios
    )


# APIs para atualização em tempo real

@bp.route('/api/pedido/novo', methods=['POST'])
@login_required
def criar_pedido():
    """API para criar novo pedido."""
    if current_user.tipo != 'garcom':
        return jsonify({'erro': 'Não autorizado'}), 403
    
    dados = request.get_json()
    
    try:
        novo_pedido = Pedido(
            cliente_id=dados['cliente_id'],
            status='aguardando',
            observacoes=dados.get('observacoes', ''),
            data_criacao=datetime.now()
        )
        db.session.add(novo_pedido)
        db.session.flush()
        
        for item in dados['itens']:
            item_pedido = ItemPedido(
                pedido_id=novo_pedido.id,
                item=item['item'],
                quantidade=item['quantidade'],
                observacao=item.get('observacao', '')
            )
            db.session.add(item_pedido)
        
        db.session.commit()
        return jsonify({'mensagem': 'Pedido criado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400


@bp.route('/api/pedido/<int:pedido_id>/status', methods=['PUT'])
@login_required
def atualizar_status_pedido(pedido_id):
    """API para atualizar status do pedido."""
    if current_user.tipo not in ['chef', 'entregador']:
        return jsonify({'erro': 'Não autorizado'}), 403
    
    pedido = Pedido.query.get_or_404(pedido_id)
    dados = request.get_json()
    
    try:
        pedido.status = dados['status']
        db.session.commit()
        return jsonify({'mensagem': 'Status atualizado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400


@bp.route('/api/entrega/nova', methods=['POST'])
@login_required
def criar_entrega():
    """API para criar nova entrega."""
    if current_user.tipo != 'chef':
        return jsonify({'erro': 'Não autorizado'}), 403
    
    dados = request.get_json()
    
    try:
        nova_entrega = Entrega(
            pedido_id=dados['pedido_id'],
            entregador_id=dados['entregador_id'],
            status='pendente'
        )
        db.session.add(nova_entrega)
        db.session.commit()
        return jsonify({'mensagem': 'Entrega criada com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400
