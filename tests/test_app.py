import os
import tempfile
import pytest
from backend.app import create_app
from backend.models import db, Usuario, Cliente, ItemMenu, Pedido, ItemPedido, Entrega


@pytest.fixture
def app():
    """Cria uma instância do app para testes."""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.create_all()
        yield app
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Cria um cliente de teste."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Cria um runner de comandos CLI."""
    return app.test_cli_runner()


def test_pagina_inicial(client):
    """Testa se a página inicial redireciona para login quando não autenticado."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_login_invalido(client):
    """Testa tentativa de login com credenciais inválidas."""
    response = client.post('/auth/login', data={
        'email': 'naoexiste@email.com',
        'senha': 'senhaerrada'
    })
    assert b'Email n\xc3\xa3o cadastrado' in response.data


def test_criar_usuario(app):
    """Testa a criação de um novo usuário."""
    with app.app_context():
        usuario = Usuario(
            nome='Teste',
            email='teste@email.com',
            tipo='garcom'
        )
        usuario.set_senha('senha123')
        db.session.add(usuario)
        db.session.commit()
        
        assert Usuario.query.filter_by(email='teste@email.com').first() is not None


def test_criar_pedido(app):
    """Testa a criação de um novo pedido."""
    with app.app_context():
        # Criar cliente
        cliente = Cliente(
            nome='Cliente Teste',
            telefone='11999999999',
            endereco='Rua Teste, 123'
        )
        db.session.add(cliente)
        
        # Criar item do menu
        item = ItemMenu(
            nome='Item Teste',
            preco=10.0,
            categoria='Teste'
        )
        db.session.add(item)
        
        db.session.commit()
        
        # Criar pedido
        pedido = Pedido(
            cliente_id=cliente.id,
            status='aguardando',
            valor_total=10.0
        )
        db.session.add(pedido)
        db.session.commit()
        
        # Adicionar item ao pedido
        item_pedido = ItemPedido(
            pedido_id=pedido.id,
            item_menu_id=item.id,
            quantidade=1,
            preco_unitario=item.preco
        )
        db.session.add(item_pedido)
        db.session.commit()
        
        assert Pedido.query.get(pedido.id) is not None
        assert len(pedido.itens) == 1


def test_fluxo_pedido(app):
    """Testa o fluxo completo de um pedido."""
    with app.app_context():
        # Criar usuários
        garcom = Usuario(nome='Garçom', email='garcom@email.com', tipo='garcom')
        chef = Usuario(nome='Chef', email='chef@email.com', tipo='chef')
        entregador = Usuario(nome='Entregador', email='entregador@email.com', tipo='entregador')
        
        for usuario in [garcom, chef, entregador]:
            usuario.set_senha('senha123')
            db.session.add(usuario)
        
        # Criar cliente e item do menu
        cliente = Cliente(nome='Cliente', telefone='11999999999', endereco='Rua Teste, 123')
        item = ItemMenu(nome='Item', preco=10.0, categoria='Teste')
        
        db.session.add_all([cliente, item])
        db.session.commit()
        
        # Criar pedido
        pedido = Pedido(
            cliente_id=cliente.id,
            status='aguardando',
            valor_total=10.0
        )
        db.session.add(pedido)
        db.session.commit()
        
        # Adicionar item ao pedido
        item_pedido = ItemPedido(
            pedido_id=pedido.id,
            item_menu_id=item.id,
            quantidade=1,
            preco_unitario=item.preco
        )
        db.session.add(item_pedido)
        db.session.commit()
        
        # Atualizar status do pedido
        pedido.status = 'em_preparo'
        db.session.commit()
        assert pedido.status == 'em_preparo'
        
        pedido.status = 'pronto'
        db.session.commit()
        assert pedido.status == 'pronto'
        
        # Criar entrega
        entrega = Entrega(
            pedido_id=pedido.id,
            entregador_id=entregador.id,
            status='pendente'
        )
        db.session.add(entrega)
        db.session.commit()
        
        # Atualizar status da entrega
        entrega.status = 'em_rota'
        db.session.commit()
        assert entrega.status == 'em_rota'
        
        entrega.status = 'entregue'
        db.session.commit()
        assert entrega.status == 'entregue'
        
        # Verificar status final do pedido
        pedido.status = 'entregue'
        db.session.commit()
        assert pedido.status == 'entregue' 