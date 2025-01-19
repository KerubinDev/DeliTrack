from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, jsonify
)
from flask_login import login_required, current_user
from datetime import datetime, date
from sqlalchemy import func
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
        flash('Acesso não autorizado', 'danger')
        return redirect(url_for('main.index'))
    
    clientes = Cliente.query.all()
    itens_menu = ItemMenu.query.all()
    pedidos_ativos = Pedido.query.filter(
        Pedido.status.in_(['aguardando', 'em_preparo'])
    ).order_by(Pedido.data_criacao.desc()).all()
    
    return render_template(
        'garcom.html',
        clientes=clientes,
        itens_menu=itens_menu,
        pedidos_ativos=pedidos_ativos
    )


@bp.route('/cozinha')
@login_required
def tela_cozinha():
    """Tela da cozinha para gerenciar preparo dos pedidos."""
    if current_user.tipo != 'chef':
        flash('Acesso não autorizado', 'danger')
        return redirect(url_for('main.index'))
    
    pedidos = Pedido.query.filter(
        Pedido.status.in_(['aguardando', 'em_preparo'])
    ).order_by(Pedido.data_criacao).all()
    
    return render_template('cozinha.html', pedidos=pedidos)


@bp.route('/entregador')
@login_required
def tela_entregador():
    """Tela do entregador para gerenciar entregas."""
    if current_user.tipo != 'entregador':
        flash('Acesso não autorizado', 'danger')
        return redirect(url_for('main.index'))
    
    entregas_pendentes = Entrega.query.filter_by(
        entregador_id=current_user.id,
        status='pendente'
    ).order_by(Entrega.data_criacao.desc()).all()
    
    entregas_hoje = Entrega.query.filter(
        Entrega.entregador_id == current_user.id,
        Entrega.data_entrega >= date.today()
    ).order_by(Entrega.data_criacao.desc()).all()
    
    return render_template(
        'entregador.html',
        entregas_pendentes=entregas_pendentes,
        entregas_hoje=entregas_hoje
    )


@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard para gerenciamento geral."""
    if current_user.tipo != 'gerente':
        flash('Acesso não autorizado', 'danger')
        return redirect(url_for('main.index'))
    
    # Métricas gerais
    hoje = date.today()
    pedidos_hoje = Pedido.query.filter(
        func.date(Pedido.data_criacao) == hoje
    ).count()
    
    pedidos_andamento = Pedido.query.filter(
        Pedido.status.in_(['aguardando', 'em_preparo'])
    ).count()
    
    entregas_concluidas = Entrega.query.filter(
        func.date(Entrega.data_entrega) == hoje,
        Entrega.status == 'entregue'
    ).count()
    
    faturamento_hoje = db.session.query(
        func.sum(Pedido.valor_total)
    ).filter(
        func.date(Pedido.data_criacao) == hoje,
        Pedido.status != 'cancelado'
    ).scalar() or 0
    
    # Dados para gráficos
    pedidos_por_status = db.session.query(
        Pedido.status, func.count(Pedido.id)
    ).group_by(Pedido.status).all()
    
    return render_template(
        'dashboard.html',
        pedidos_hoje=pedidos_hoje,
        pedidos_andamento=pedidos_andamento,
        entregas_concluidas=entregas_concluidas,
        faturamento_hoje=faturamento_hoje,
        pedidos_por_status=dict(pedidos_por_status)
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
        
        valor_total = 0
        for item in dados['itens']:
            item_menu = ItemMenu.query.get(item['item_id'])
            if not item_menu:
                raise ValueError(f"Item {item['item_id']} não encontrado")
                
            valor_item = item_menu.preco * item['quantidade']
            valor_total += valor_item
            
            item_pedido = ItemPedido(
                pedido_id=novo_pedido.id,
                item_id=item['item_id'],
                quantidade=item['quantidade'],
                valor_unitario=item_menu.preco,
                valor_total=valor_item,
                observacao=item.get('observacao', '')
            )
            db.session.add(item_pedido)
        
        novo_pedido.valor_total = valor_total
        db.session.commit()
        return jsonify({'mensagem': 'Pedido criado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400


@bp.route('/api/pedido/<int:pedido_id>/status', methods=['PUT'])
@login_required
def atualizar_status_pedido(pedido_id):
    """API para atualizar status do pedido."""
    if current_user.tipo not in ['chef', 'entregador', 'garcom']:
        return jsonify({'erro': 'Não autorizado'}), 403
    
    pedido = Pedido.query.get_or_404(pedido_id)
    dados = request.get_json()
    novo_status = dados['status']
    
    # Validar transições de status permitidas
    status_permitidos = {
        'garcom': ['cancelado'],
        'chef': ['em_preparo', 'pronto'],
        'entregador': ['em_entrega', 'entregue']
    }
    
    if novo_status not in status_permitidos[current_user.tipo]:
        return jsonify({'erro': 'Transição de status não permitida'}), 400
    
    try:
        pedido.status = novo_status
        if novo_status == 'entregue':
            pedido.data_conclusao = datetime.now()
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
        pedido = Pedido.query.get_or_404(dados['pedido_id'])
        if pedido.status != 'pronto':
            return jsonify({'erro': 'Pedido não está pronto para entrega'}), 400
        
        nova_entrega = Entrega(
            pedido_id=dados['pedido_id'],
            entregador_id=dados['entregador_id'],
            status='pendente',
            data_criacao=datetime.now()
        )
        db.session.add(nova_entrega)
        pedido.status = 'em_entrega'
        db.session.commit()
        return jsonify({'mensagem': 'Entrega criada com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400


@bp.route('/api/entrega/<int:entrega_id>/status', methods=['PUT'])
@login_required
def atualizar_status_entrega(entrega_id):
    """API para atualizar status da entrega."""
    if current_user.tipo != 'entregador':
        return jsonify({'erro': 'Não autorizado'}), 403
    
    entrega = Entrega.query.get_or_404(entrega_id)
    dados = request.get_json()
    
    try:
        entrega.status = dados['status']
        if dados['status'] == 'entregue':
            entrega.data_entrega = datetime.now()
            entrega.pedido.status = 'entregue'
            entrega.pedido.data_conclusao = datetime.now()
        db.session.commit()
        return jsonify({'mensagem': 'Status atualizado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400
