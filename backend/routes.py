from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, jsonify
)
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func
from werkzeug.security import generate_password_hash
from .models import (
    Usuario, Pedido, ItemPedido, Entrega, Produto, db
)

# Blueprint para organizar as rotas
main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():
    """Rota principal - redireciona para a interface adequada"""
    if current_user.tipo == 'gerente':
        return redirect(url_for('main.dashboard'))
    elif current_user.tipo == 'garcom':
        return redirect(url_for('main.garcom'))
    elif current_user.tipo == 'cozinheiro':
        return redirect(url_for('main.cozinha'))
    elif current_user.tipo == 'entregador':
        return redirect(url_for('main.entregador'))
    return redirect(url_for('main.dashboard'))


@main.route('/garcom')
@login_required
def garcom():
    """Interface do garçom"""
    if current_user.tipo != 'garcom':
        return redirect(url_for('main.index'))
        
    produtos = Produto.query.filter_by(ativo=True).all()
    pedidos_ativos = Pedido.query.filter(
        Pedido.status.in_(['novo', 'preparando'])
    ).order_by(Pedido.data_criacao.desc()).all()
    
    return render_template('garcom.html',
                         produtos=produtos,
                         pedidos_ativos=pedidos_ativos)


@main.route('/cozinha')
@login_required
def cozinha():
    """Interface da cozinha"""
    if current_user.tipo != 'cozinheiro':
        return redirect(url_for('main.index'))
        
    pedidos = Pedido.query.filter(
        Pedido.status.in_(['novo', 'preparando'])
    ).order_by(Pedido.data_criacao).all()
    
    return render_template('cozinha.html', pedidos=pedidos)


@main.route('/entregador')
@login_required
def entregador():
    """Interface do entregador"""
    if current_user.tipo != 'entregador':
        return redirect(url_for('main.index'))
        
    entregas_pendentes = Entrega.query.filter_by(
        entregador_id=current_user.id,
        status='pendente'
    ).order_by(Entrega.data_criacao.desc()).all()
    
    return render_template('entregador.html',
                         entregas_pendentes=entregas_pendentes)


@main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard gerencial"""
    if current_user.tipo != 'gerente':
        return redirect(url_for('main.index'))
        
    pedidos = Pedido.query.order_by(Pedido.data_criacao.desc()).limit(10).all()
    usuarios = Usuario.query.all()
    
    stats = {
        'total_pedidos': Pedido.query.count(),
        'pedidos_hoje': Pedido.query.filter(Pedido.data_criacao >= datetime.today()).count(),
        'usuarios_ativos': Usuario.query.filter_by(ativo=True).count(),
        'valor_total': sum(p.valor_total for p in Pedido.query.all())
    }
    
    return render_template('dashboard.html', 
                         pedidos=pedidos,
                         usuarios=usuarios,
                         stats=stats)


# APIs para atualização em tempo real

@main.route('/api/pedido/novo', methods=['POST'])
@login_required
def criar_pedido():
    """API para criar novo pedido"""
    if current_user.tipo != 'garcom':
        return jsonify({'erro': 'Não autorizado'}), 403
    
    dados = request.get_json()
    
    try:
        novo_pedido = Pedido(
            numero_mesa=dados['numero_mesa'],
            status='novo',
            observacoes=dados.get('observacoes', ''),
            criador_id=current_user.id
        )
        db.session.add(novo_pedido)
        db.session.flush()
        
        for item in dados['itens']:
            produto = Produto.query.get(item['produto_id'])
            if not produto:
                raise ValueError(f"Produto {item['produto_id']} não encontrado")
                
            item_pedido = ItemPedido(
                pedido_id=novo_pedido.id,
                produto_id=produto.id,
                quantidade=item['quantidade'],
                valor_unitario=produto.preco,
                observacoes=item.get('observacoes', '')
            )
            db.session.add(item_pedido)
        
        db.session.commit()
        return jsonify({'mensagem': 'Pedido criado com sucesso', 'id': novo_pedido.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400


@main.route('/api/pedido/<int:pedido_id>/status', methods=['PUT'])
@login_required
def atualizar_status_pedido(pedido_id):
    """API para atualizar status do pedido"""
    if current_user.tipo not in ['cozinheiro', 'entregador', 'garcom']:
        return jsonify({'erro': 'Não autorizado'}), 403
    
    pedido = Pedido.query.get_or_404(pedido_id)
    dados = request.get_json()
    novo_status = dados['status']
    
    # Validar transições de status permitidas
    status_permitidos = {
        'garcom': ['cancelado'],
        'cozinheiro': ['preparando', 'pronto'],
        'entregador': ['entregue']
    }
    
    if novo_status not in status_permitidos[current_user.tipo]:
        return jsonify({'erro': 'Transição de status não permitida'}), 400
    
    try:
        pedido.status = novo_status
        db.session.commit()
        return jsonify({'mensagem': 'Status atualizado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400


@main.route('/api/entrega/nova', methods=['POST'])
@login_required
def criar_entrega():
    """API para criar nova entrega"""
    if current_user.tipo != 'cozinheiro':
        return jsonify({'erro': 'Não autorizado'}), 403
    
    dados = request.get_json()
    
    try:
        pedido = Pedido.query.get_or_404(dados['pedido_id'])
        if pedido.status != 'pronto':
            return jsonify({'erro': 'Pedido não está pronto para entrega'}), 400
        
        nova_entrega = Entrega(
            pedido_id=pedido.id,
            entregador_id=dados['entregador_id'],
            status='pendente'
        )
        db.session.add(nova_entrega)
        pedido.status = 'entregue'
        db.session.commit()
        return jsonify({'mensagem': 'Entrega criada com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400


@main.route('/api/entrega/<int:entrega_id>/status', methods=['PUT'])
@login_required
def atualizar_status_entrega(entrega_id):
    """API para atualizar status da entrega"""
    if current_user.tipo != 'entregador':
        return jsonify({'erro': 'Não autorizado'}), 403
    
    entrega = Entrega.query.get_or_404(entrega_id)
    dados = request.get_json()
    
    try:
        entrega.status = dados['status']
        if dados['status'] == 'em_rota':
            entrega.data_saida = datetime.now()
        elif dados['status'] == 'entregue':
            entrega.data_entrega = datetime.now()
            entrega.pedido.status = 'entregue'
        
        db.session.commit()
        return jsonify({'mensagem': 'Status atualizado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400


# APIs para gerenciamento de usuários
@main.route('/api/usuario/novo', methods=['POST'])
@login_required
def criar_usuario():
    """API para criar novo usuário"""
    if current_user.tipo != 'gerente':
        return jsonify({'erro': 'Não autorizado'}), 403
    
    dados = request.get_json()
    
    try:
        # Verificar se email já existe
        if Usuario.query.filter_by(email=dados['email']).first():
            return jsonify({'erro': 'Email já cadastrado'}), 400
            
        novo_usuario = Usuario(
            nome=dados['nome'],
            email=dados['email'],
            tipo=dados['tipo'],
            ativo=True
        )
        novo_usuario.set_senha(dados['senha'])
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Usuário criado com sucesso',
            'id': novo_usuario.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400

@main.route('/api/usuario/<int:usuario_id>', methods=['PUT'])
@login_required
def atualizar_usuario(usuario_id):
    """API para atualizar usuário"""
    if current_user.tipo != 'gerente':
        return jsonify({'erro': 'Não autorizado'}), 403
    
    usuario = Usuario.query.get_or_404(usuario_id)
    dados = request.get_json()
    
    try:
        if 'nome' in dados:
            usuario.nome = dados['nome']
        if 'email' in dados and dados['email'] != usuario.email:
            if Usuario.query.filter_by(email=dados['email']).first():
                return jsonify({'erro': 'Email já cadastrado'}), 400
            usuario.email = dados['email']
        if 'tipo' in dados:
            usuario.tipo = dados['tipo']
        if 'senha' in dados:
            usuario.set_senha(dados['senha'])
        if 'ativo' in dados:
            usuario.ativo = dados['ativo']
            
        db.session.commit()
        return jsonify({'mensagem': 'Usuário atualizado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400

@main.route('/api/usuario/<int:usuario_id>', methods=['DELETE'])
@login_required
def deletar_usuario(usuario_id):
    """API para deletar usuário"""
    if current_user.tipo != 'gerente':
        return jsonify({'erro': 'Não autorizado'}), 403
    
    if usuario_id == current_user.id:
        return jsonify({'erro': 'Não é possível deletar o próprio usuário'}), 400
        
    usuario = Usuario.query.get_or_404(usuario_id)
    
    try:
        usuario.ativo = False  # Soft delete
        db.session.commit()
        return jsonify({'mensagem': 'Usuário desativado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400

# APIs para métricas do dashboard
@main.route('/api/dashboard/metricas')
@login_required
def obter_metricas():
    """API para obter métricas do dashboard"""
    if current_user.tipo != 'gerente':
        return jsonify({'erro': 'Não autorizado'}), 403
    
    periodo = request.args.get('periodo', 'hoje')
    data_inicio = request.args.get('dataInicio')
    data_fim = request.args.get('dataFim')
    
    # Definir período de análise
    hoje = date.today()
    if periodo == 'hoje':
        data_inicio = hoje
        data_fim = hoje + timedelta(days=1)
    elif periodo == 'semana':
        data_inicio = hoje - timedelta(days=7)
        data_fim = hoje + timedelta(days=1)
    elif periodo == 'mes':
        data_inicio = hoje.replace(day=1)
        data_fim = hoje + timedelta(days=1)
    elif periodo == 'personalizado':
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date() + timedelta(days=1)
        except:
            return jsonify({'erro': 'Datas inválidas'}), 400
    
    # Calcular métricas
    try:
        pedidos = Pedido.query.filter(
            Pedido.data_criacao >= data_inicio,
            Pedido.data_criacao < data_fim
        )
        
        metricas = {
            'total_pedidos': pedidos.count(),
            'valor_total': sum(p.valor_total for p in pedidos.all()),
            'pedidos_por_status': {
                status: pedidos.filter_by(status=status).count()
                for status in ['novo', 'preparando', 'pronto', 'entregue', 'cancelado']
            },
            'pedidos_por_hora': db.session.query(
                func.date_part('hour', Pedido.data_criacao),
                func.count(Pedido.id)
            ).filter(
                Pedido.data_criacao >= data_inicio,
                Pedido.data_criacao < data_fim
            ).group_by(
                func.date_part('hour', Pedido.data_criacao)
            ).all()
        }
        
        return jsonify(metricas)
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 400
