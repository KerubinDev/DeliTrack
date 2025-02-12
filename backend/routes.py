"""
DeliTrack - Sistema de Gerenciamento de Pedidos e Entregas
Copyright (c) 2024 Kelvin Moraes
Email: kelvin.moraes117@gmail.com

Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo
sob os termos da GNU General Public License, conforme publicado pela
Free Software Foundation, seja a versão 3 da Licença, ou
(a seu critério) qualquer versão posterior.

Este programa é distribuído na esperança de que seja útil,
mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de
COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM DETERMINADO PROPÓSITO.
Veja a GNU General Public License para mais detalhes.

Você deve ter recebido uma cópia da GNU General Public License
junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.
"""

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
from werkzeug.utils import secure_filename
import os

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
        
    # Buscar pedidos pendentes e em preparação
    pedidos = Pedido.query.filter(
        Pedido.status.in_(['novo', 'preparando'])
    ).order_by(
        Pedido.data_criacao.desc()
    ).all()
    
    print(f"DEBUG - Total de pedidos encontrados: {len(pedidos)}")
    for pedido in pedidos:
        print(f"DEBUG - Pedido {pedido.id}: status={pedido.status}, tipo={pedido.tipo}")
    
    return render_template('cozinha.html', pedidos=pedidos)


@main.route('/entregador')
@login_required
def entregador():
    """Interface do entregador"""
    if current_user.tipo != 'entregador':
        return redirect(url_for('main.index'))
        
    # Buscar entregas pendentes e em andamento para este entregador
    entregas = Entrega.query.filter(
        Entrega.entregador_id == current_user.id,
        Entrega.status.in_(['pendente', 'em_rota'])
    ).order_by(Entrega.data_criacao.desc()).all()
    
    print(f"DEBUG - Entregador {current_user.id} tem {len(entregas)} entregas")
    for entrega in entregas:
        print(f"DEBUG - Entrega {entrega.id} para pedido {entrega.pedido_id} - status: {entrega.status}")
    
    return render_template('entregador.html', entregas=entregas)


@main.route('/dashboard')
@login_required
def dashboard():
    print("DEBUG - Iniciando rota do dashboard")  # Debug
    
    # Verifica se o usuário é gerente
    if current_user.tipo != 'gerente':
        print(f"DEBUG - Acesso negado para usuário tipo {current_user.tipo}")  # Debug
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('main.index'))
    
    print("DEBUG - Usuário autorizado, calculando métricas")  # Debug
    
    # Obtém as métricas das últimas 24 horas
    agora = datetime.now()
    inicio = agora - timedelta(days=1)
    
    # Métricas básicas
    metricas = {
        'total_pedidos': 0,  # Inicializa com zero
        'valor_total': 0,    # Inicializa com zero
        'pedidos_preparando': 0,
        'pedidos_novos': 0,
        'pedidos_prontos': 0,
        'pedidos_entregues': 0,
        'pedidos_cancelados': 0,
        'labels_horas': [],
        'pedidos_por_hora': []
    }
    
    try:
        # Total de pedidos finalizados
        metricas['total_pedidos'] = Pedido.query.filter(
            Pedido.data_criacao >= inicio,
            Pedido.status.in_(['pronto', 'entregue'])
        ).count()
        print(f"DEBUG - Total de pedidos: {metricas['total_pedidos']}")  # Debug
        
        # Valor total dos pedidos finalizados
        valor_total = db.session.query(
            func.sum(Pedido.valor_total)
        ).filter(
            Pedido.data_criacao >= inicio,
            Pedido.status.in_(['pronto', 'entregue'])
        ).scalar()
        metricas['valor_total'] = valor_total if valor_total else 0
        print(f"DEBUG - Valor total: {metricas['valor_total']}")  # Debug
        
        # Contagem por status
        metricas['pedidos_preparando'] = Pedido.query.filter_by(status='preparando').count()
        metricas['pedidos_novos'] = Pedido.query.filter_by(status='novo').count()
        metricas['pedidos_prontos'] = Pedido.query.filter_by(status='pronto').count()
        metricas['pedidos_entregues'] = Pedido.query.filter_by(status='entregue').count()
        metricas['pedidos_cancelados'] = Pedido.query.filter_by(status='cancelado').count()
        
        print(f"DEBUG - Status dos pedidos: novo={metricas['pedidos_novos']}, "
              f"preparando={metricas['pedidos_preparando']}, "
              f"pronto={metricas['pedidos_prontos']}, "
              f"entregue={metricas['pedidos_entregues']}, "
              f"cancelado={metricas['pedidos_cancelados']}")  # Debug
        
        # Gera dados para o gráfico de pedidos por hora
        for hora in range(24):
            hora_inicio = agora - timedelta(hours=24-hora)
            hora_fim = agora - timedelta(hours=23-hora)
            
            pedidos = Pedido.query.filter(
                Pedido.data_criacao >= hora_inicio,
                Pedido.data_criacao < hora_fim,
                Pedido.status.in_(['pronto', 'entregue'])
            ).count()
            
            metricas['labels_horas'].append(hora_inicio.strftime('%H:00'))
            metricas['pedidos_por_hora'].append(pedidos)
        
        print(f"DEBUG - Dados do gráfico gerados: {len(metricas['pedidos_por_hora'])} horas")  # Debug
        
    except Exception as e:
        print(f"ERRO - Falha ao calcular métricas: {str(e)}")  # Debug de erro
        flash('Erro ao carregar métricas.', 'danger')
        metricas = {
            'total_pedidos': 0,
            'valor_total': 0,
            'pedidos_preparando': 0,
            'pedidos_novos': 0,
            'pedidos_prontos': 0,
            'pedidos_entregues': 0,
            'pedidos_cancelados': 0,
            'labels_horas': [],
            'pedidos_por_hora': []
        }
    
    # Obtém usuários e produtos para as tabelas
    try:
        usuarios = Usuario.query.all()
        produtos = Produto.query.all()
        print(f"DEBUG - Usuários: {len(usuarios)}, Produtos: {len(produtos)}")  # Debug
    except Exception as e:
        print(f"ERRO - Falha ao carregar usuários/produtos: {str(e)}")  # Debug de erro
        usuarios = []
        produtos = []
        flash('Erro ao carregar dados de usuários e produtos.', 'danger')
    
    print("DEBUG - Renderizando template do dashboard")  # Debug
    return render_template('dashboard.html',
                         metricas=metricas,
                         usuarios=usuarios,
                         produtos=produtos)


@main.route('/welcome')
@login_required
def welcome():
    """Rota para a tela de boas-vindas"""
    return render_template('welcome.html')


# APIs para atualização em tempo real

@main.route('/api/pedido/novo', methods=['POST'])
@login_required
def criar_pedido():
    """Cria um novo pedido"""
    if current_user.tipo != 'garcom':
        return jsonify({'erro': 'Acesso não autorizado'}), 403
        
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({'erro': 'Dados inválidos'}), 400
            
        print(f"DEBUG - Dados recebidos: {dados}")
        
        pedido = Pedido(
            tipo=dados['tipo_pedido'],
            nome_cliente=dados.get('nome_cliente', ''),  # Nome do cliente opcional
            observacoes=dados.get('observacoes', ''),
            criador_id=current_user.id,
            status='novo'  # Garantir que o status inicial seja 'novo'
        )
        
        if dados['tipo_pedido'] == 'local':
            if not dados.get('numero_mesa'):
                return jsonify({'erro': 'Número da mesa é obrigatório para pedidos locais'}), 400
            pedido.numero_mesa = dados['numero_mesa']
        else:
            # Validações para pedido de entrega
            if not dados.get('nome_cliente'):
                return jsonify({'erro': 'Nome do cliente é obrigatório para entregas'}), 400
                
            if not dados.get('endereco'):
                return jsonify({'erro': 'Endereço é obrigatório para entregas'}), 400
                
            endereco = dados['endereco']
            pedido.endereco_entrega = endereco['logradouro']
            pedido.complemento_entrega = endereco.get('complemento', '')
            pedido.bairro_entrega = endereco['bairro']
            pedido.telefone_entrega = endereco['telefone']
            pedido.ponto_referencia = endereco.get('ponto_referencia', '')
            if 'coordenadas' in endereco and endereco['coordenadas']:
                pedido.latitude = endereco['coordenadas']['latitude']
                pedido.longitude = endereco['coordenadas']['longitude']
        
        if not dados.get('itens'):
            return jsonify({'erro': 'Pedido deve ter pelo menos um item'}), 400
            
        for item_dados in dados['itens']:
            produto = Produto.query.get(item_dados['produto_id'])
            if not produto:
                return jsonify({'erro': f'Produto {item_dados["produto_id"]} não encontrado'}), 404
                
            item = ItemPedido(
                produto_id=item_dados['produto_id'],
                quantidade=item_dados['quantidade'],
                valor_unitario=produto.preco,
                observacoes=item_dados.get('observacoes', '')
            )
            pedido.itens.append(item)
        
        print(f"DEBUG - Pedido criado: id={pedido.id}, tipo={pedido.tipo}, status={pedido.status}")
        
        db.session.add(pedido)
        db.session.commit()
        
        print(f"DEBUG - Pedido salvo com sucesso: id={pedido.id}")
        
        return jsonify({
            'mensagem': 'Pedido criado com sucesso!',
            'id': pedido.id
        })
        
    except KeyError as e:
        print(f"DEBUG - Erro de campo obrigatório: {str(e)}")
        return jsonify({'erro': f'Campo obrigatório ausente: {str(e)}'}), 400
    except Exception as e:
        print(f"DEBUG - Erro ao criar pedido: {str(e)}")
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


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
        
        # Se o pedido for marcado como pronto e for do tipo entrega,
        # criar automaticamente uma entrega
        if novo_status == 'pronto' and pedido.tipo == 'entrega':
            # Buscar um entregador disponível
            entregador = Usuario.query.filter_by(
                tipo='entregador',
                ativo=True
            ).first()
            
            if entregador:
                nova_entrega = Entrega(
                    pedido_id=pedido.id,
                    entregador_id=entregador.id,
                    status='pendente'
                )
                db.session.add(nova_entrega)
                print(f"DEBUG - Criando entrega para pedido {pedido.id} com entregador {entregador.id}")
            else:
                print("DEBUG - Nenhum entregador disponível encontrado")
        
        db.session.commit()
        return jsonify({'mensagem': 'Status atualizado com sucesso'})
    
    except Exception as e:
        print(f"DEBUG - Erro ao atualizar status: {str(e)}")
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
        # Base query para o período selecionado
        pedidos_base = Pedido.query.filter(
            Pedido.data_criacao >= data_inicio,
            Pedido.data_criacao < data_fim
        )
        
        # Pedidos locais finalizados (status 'pronto')
        pedidos_local_finalizados = pedidos_base.filter(
            Pedido.tipo == 'local',
            Pedido.status == 'pronto'
        )
        
        # Pedidos de entrega finalizados (status 'entregue')
        pedidos_entrega_finalizados = pedidos_base.filter(
            Pedido.tipo == 'entrega',
            Pedido.status == 'entregue'
        )
        
        # Combinar os pedidos finalizados
        pedidos_finalizados = pedidos_local_finalizados.union(
            pedidos_entrega_finalizados
        ).all()
        
        metricas = {
            'total_pedidos': pedidos_base.count(),
            'pedidos_finalizados': len(pedidos_finalizados),
            'valor_total': sum(p.valor_total for p in pedidos_finalizados),
            'pedidos_por_status': {
                'novo': pedidos_base.filter_by(status='novo').count(),
                'preparando': pedidos_base.filter_by(status='preparando').count(),
                'pronto': pedidos_local_finalizados.count(),
                'entregue': pedidos_entrega_finalizados.count(),
                'cancelado': pedidos_base.filter_by(status='cancelado').count()
            },
            'pedidos_por_tipo': {
                'local': pedidos_base.filter_by(tipo='local').count(),
                'entrega': pedidos_base.filter_by(tipo='entrega').count()
            },
            'pedidos_por_hora': db.session.query(
                func.date_part('hour', Pedido.data_criacao),
                func.count(Pedido.id)
            ).filter(
                Pedido.data_criacao >= data_inicio,
                Pedido.data_criacao < data_fim,
                Pedido.id.in_([p.id for p in pedidos_finalizados])
            ).group_by(
                func.date_part('hour', Pedido.data_criacao)
            ).all()
        }
        
        return jsonify(metricas)
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@main.route('/api/produto/novo', methods=['POST'])
@login_required
def criar_produto():
    """Cria um novo produto"""
    if current_user.tipo != 'gerente':
        return jsonify({'erro': 'Acesso não autorizado'}), 403
        
    nome = request.form['nome']
    descricao = request.form['descricao']
    preco = float(request.form['preco'])
    categoria = request.form['categoria']
    ativo = request.form['ativo'].lower() == 'true'
    
    produto = Produto(
        nome=nome,
        descricao=descricao,
        preco=preco,
        categoria=categoria,
        ativo=ativo
    )
    
    if 'imagem' in request.files:
        arquivo = request.files['imagem']
        if arquivo and arquivo.filename:
            nome_arquivo = secure_filename(arquivo.filename)
            caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo)
            arquivo.save(caminho)
            produto.imagem = f'/uploads/{nome_arquivo}'
    
    db.session.add(produto)
    db.session.commit()
    
    return jsonify({'mensagem': 'Produto criado com sucesso!'})

@main.route('/api/produto/<int:id>', methods=['PUT'])
@login_required
def atualizar_produto(id):
    """Atualiza um produto existente"""
    if current_user.tipo != 'gerente':
        return jsonify({'erro': 'Acesso não autorizado'}), 403
        
    produto = Produto.query.get_or_404(id)
    
    produto.nome = request.form['nome']
    produto.descricao = request.form['descricao']
    produto.preco = float(request.form['preco'])
    produto.categoria = request.form['categoria']
    produto.ativo = request.form['ativo'].lower() == 'true'
    
    if 'imagem' in request.files:
        arquivo = request.files['imagem']
        if arquivo and arquivo.filename:
            # Remove imagem antiga se existir
            if produto.imagem:
                caminho_antigo = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    os.path.basename(produto.imagem)
                )
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)
            
            nome_arquivo = secure_filename(arquivo.filename)
            caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo)
            arquivo.save(caminho)
            produto.imagem = f'/uploads/{nome_arquivo}'
    
    db.session.commit()
    
    return jsonify({'mensagem': 'Produto atualizado com sucesso!'})

@main.route('/api/produto/<int:id>', methods=['DELETE'])
@login_required
def deletar_produto(id):
    """Deleta um produto"""
    if current_user.tipo != 'gerente':
        return jsonify({'erro': 'Acesso não autorizado'}), 403
        
    produto = Produto.query.get_or_404(id)
    
    # Remove imagem se existir
    if produto.imagem:
        caminho = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            os.path.basename(produto.imagem)
        )
        if os.path.exists(caminho):
            os.remove(caminho)
    
    db.session.delete(produto)
    db.session.commit()
    
    return jsonify({'mensagem': 'Produto deletado com sucesso!'})

@main.route('/api/produto/<int:id>', methods=['GET'])
def obter_produto(id):
    """Obtém os detalhes de um produto"""
    produto = Produto.query.get_or_404(id)
    return jsonify({
        'id': produto.id,
        'nome': produto.nome,
        'descricao': produto.descricao,
        'preco': produto.preco,
        'categoria': produto.categoria,
        'imagem': produto.imagem,
        'ativo': produto.ativo
    })
