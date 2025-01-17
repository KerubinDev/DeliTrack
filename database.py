from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def configurar_banco(app):
    db.init_app(app)


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # garcom, cozinheiro, entregador, gerente
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    pedidos = db.relationship('Pedido', backref='garcom', lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    imagem_url = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)

    itens_pedido = db.relationship('ItemPedido', backref='produto', lazy=True)


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mesa = db.Column(db.Integer)
    status = db.Column(db.String(20), nullable=False)  # aguardando, preparando, pronto, entregue
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    garcom_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)

    def calcular_total(self):
        return sum(item.quantidade * item.produto.preco for item in self.itens)

    def to_dict(self):
        return {
            'id': self.id,
            'mesa': self.mesa,
            'status': self.status,
            'data_criacao': self.data_criacao.isoformat(),
            'garcom': self.garcom.nome,
            'itens': [item.to_dict() for item in self.itens],
            'total': self.calcular_total()
        }


class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, nullable=False)
    observacoes = db.Column(db.Text)
    
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'produto': self.produto.nome,
            'quantidade': self.quantidade,
            'observacoes': self.observacoes,
            'preco_unitario': self.produto.preco,
            'subtotal': self.quantidade * self.produto.preco
        }


def criar_usuario_admin():
    """Cria um usuário administrador se não existir"""
    admin = Usuario.query.filter_by(email='admin@restaurante.com').first()
    if not admin:
        admin = Usuario(
            nome='Administrador',
            email='admin@restaurante.com',
            tipo='gerente',
            ativo=True
        )
        admin.set_senha('admin123')
        db.session.add(admin)
        db.session.commit() 