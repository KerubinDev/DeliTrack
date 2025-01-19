"""
Modelos do banco de dados
"""
from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário pelo ID"""
    return Usuario.query.get(int(user_id))

class Usuario(UserMixin, db.Model):
    """Modelo de usuário"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    tipo = db.Column(db.String(20), nullable=False)  # gerente, garcom, cozinheiro, entregador
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    pedidos_criados = db.relationship('Pedido', backref='criador', lazy=True,
                                    foreign_keys='Pedido.criador_id')
    entregas = db.relationship('Pedido', backref='entregador', lazy=True,
                             foreign_keys='Pedido.entregador_id')

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


class Produto(db.Model):
    """Modelo de produto"""
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))
    imagem = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    itens_pedido = db.relationship('ItemPedido', backref='produto', lazy=True)


class Pedido(db.Model):
    """Modelo de pedido"""
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), default='local')  # local ou entrega
    numero_mesa = db.Column(db.Integer, nullable=True)
    nome_cliente = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='novo')  # novo, preparando, pronto, entregue, cancelado
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campos para entrega
    endereco_entrega = db.Column(db.String(200), nullable=True)
    complemento_entrega = db.Column(db.String(100), nullable=True)
    bairro_entrega = db.Column(db.String(100), nullable=True)
    telefone_entrega = db.Column(db.String(20), nullable=True)
    ponto_referencia = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Relacionamentos
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    entregador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade='all, delete-orphan')
    
    @property
    def valor_total(self):
        """Calcula o valor total do pedido"""
        return sum(item.subtotal for item in self.itens)


class ItemPedido(db.Model):
    """Modelo de item do pedido"""
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False)
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    
    @property
    def subtotal(self):
        """Calcula o subtotal do item"""
        return self.quantidade * self.valor_unitario


class Entrega(db.Model):
    """Modelo para entregas"""
    __tablename__ = 'entregas'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='pendente')  # pendente, em_rota, entregue
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_saida = db.Column(db.DateTime)
    data_entrega = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    entregador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    pedido = db.relationship('Pedido', backref=db.backref('entrega', uselist=False))
    entregador = db.relationship('Usuario', backref=db.backref('entregas_realizadas', lazy=True)) 