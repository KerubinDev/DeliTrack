from flask_sqlalchemy import SQLAlchemy
import os

# Inicializa o objeto SQLAlchemy
db = SQLAlchemy()


def configurar_banco(app):
    """Configura o banco de dados SQLite"""
    # Define o caminho do arquivo do banco de dados
    diretorio_base = os.path.abspath(os.path.dirname(__file__))
    
    # Configurações do SQLAlchemy
    app.config.update(
        # URI do banco SQLite
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(diretorio_base, "restaurante.db")}',
        # Desativa o track modifications para melhor performance
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # Chave secreta para sessões
        SECRET_KEY='chave_super_secreta_mude_em_producao'
    )
    
    # Inicializa o banco de dados com a aplicação
    db.init_app(app)
    
    # Cria todas as tabelas se não existirem
    with app.app_context():
        db.create_all()
        criar_dados_iniciais()


def criar_dados_iniciais():
    """Cria dados iniciais para teste se o banco estiver vazio"""
    from models import Usuario, Produto
    
    # Cria usuário administrador se não existir
    if not Usuario.query.filter_by(email='admin@restaurante.com').first():
        admin = Usuario(
            nome='Administrador',
            email='admin@restaurante.com',
            tipo='gerente',
            ativo=True
        )
        admin.definir_senha('admin123')
        db.session.add(admin)
    
    # Cria alguns produtos de exemplo se não existirem
    if not Produto.query.first():
        produtos = [
            {
                'nome': 'X-Burger',
                'descricao': 'Hambúrguer com queijo e salada',
                'preco': 25.90,
                'categoria': 'prato_principal',
                'tempo_preparo': 15
            },
            {
                'nome': 'Refrigerante',
                'descricao': 'Lata 350ml',
                'preco': 6.90,
                'categoria': 'bebida',
                'tempo_preparo': 1
            },
            {
                'nome': 'Salada Caesar',
                'descricao': 'Alface, croutons, parmesão e molho caesar',
                'preco': 28.90,
                'categoria': 'entrada',
                'tempo_preparo': 10
            }
        ]
        
        for produto_dados in produtos:
            produto = Produto(**produto_dados)
            db.session.add(produto)
    
    # Commit das alterações
    db.session.commit() 