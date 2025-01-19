import pytest
from backend.app import create_app
from backend.models import db as _db


@pytest.fixture(scope='session')
def app():
    """Cria uma instância do app para toda a sessão de testes."""
    app = create_app('testing')
    
    # Outras configurações específicas para teste
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Criar contexto da aplicação
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    """Cria uma instância do banco de dados para toda a sessão de testes."""
    _db.app = app
    _db.create_all()
    
    yield _db
    
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """Cria uma nova sessão do banco de dados para cada teste."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove() 