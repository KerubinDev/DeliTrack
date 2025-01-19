from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    """Modelo para usuários do sistema."""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    tipo = db.Column(db.String(20), nullable=False)  # garcom, chef, entregador, gerente
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class TokenRedefinicaoSenha(db.Model):
    """Modelo para tokens de redefinição de senha."""
    __tablename__ = 'tokens_redefinicao_senha'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    expiracao = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False)
    
    usuario = db.relationship('Usuario', backref=db.backref('tokens_redefinicao', lazy=True))
    
    @property
    def expirado(self):
        """Verifica se o token está expirado."""
        return datetime.utcnow() > self.expiracao


class Cliente(db.Model):
    """Modelo para clientes."""
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)


class ItemMenu(db.Model):
    """Modelo para itens do menu."""
    __tablename__ = 'itens_menu'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))
    disponivel = db.Column(db.Boolean, default=True)
    tempo_preparo = db.Column(db.Integer)  # em minutos


class Pedido(db.Model):
    """Modelo para pedidos."""
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # aguardando, em_preparo, pronto, entregue
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, onupdate=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime)
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)
    valor_total = db.Column(db.Float)


class ItemPedido(db.Model):
    """Modelo para itens de um pedido."""
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('itens_menu.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    observacao = db.Column(db.Text)
    valor_unitario = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    
    item = db.relationship('ItemMenu', backref=db.backref('pedidos', lazy=True))


class Entrega(db.Model):
    """Modelo para entregas."""
    __tablename__ = 'entregas'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    entregador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # pendente, em_rota, entregue
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_saida = db.Column(db.DateTime)
    data_entrega = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    
    pedido = db.relationship('Pedido', backref=db.backref('entrega', uselist=False))
    entregador = db.relationship('Usuario', backref=db.backref('entregas', lazy=True)) 