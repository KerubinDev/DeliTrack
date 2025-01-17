from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from database import db


class Usuario(UserMixin, db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _senha_hash = db.Column(db.String(128), nullable=False)
    tipo = db.Column(
        db.Enum('garcom', 'chef', 'entregador', 'gerente', name='tipos_usuario'),
        nullable=False
    )
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    pedidos_criados = db.relationship(
        'Pedido',
        backref='garcom',
        lazy=True,
        foreign_keys='Pedido.garcom_id'
    )
    
    def definir_senha(self, senha):
        """Define a senha criptografada do usuário"""
        self._senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self._senha_hash, senha)


class Produto(db.Model):
    """Modelo para produtos do cardápio"""
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    categoria = db.Column(
        db.Enum('entrada', 'prato_principal', 'sobremesa', 'bebida', 
                name='categorias_produto'),
        nullable=False
    )
    tempo_preparo = db.Column(db.Integer)  # em minutos
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    itens_pedido = db.relationship('ItemPedido', backref='produto', lazy=True)


class Pedido(db.Model):
    """Modelo para pedidos"""
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    mesa = db.Column(db.String(10))
    status = db.Column(
        db.Enum(
            'aguardando',
            'preparando',
            'pronto_entrega',
            'em_entrega',
            'entregue',
            'cancelado',
            name='status_pedido'
        ),
        nullable=False,
        default='aguardando'
    )
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    data_atualizacao = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )
    
    # Chaves estrangeiras
    garcom_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=False
    )
    entregador_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=True
    )
    
    # Relacionamentos
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)
    entregador = db.relationship(
        'Usuario',
        foreign_keys=[entregador_id],
        backref='pedidos_entregues'
    )
    
    @property
    def valor_total(self):
        """Calcula o valor total do pedido"""
        return sum(item.subtotal for item in self.itens)
    
    @property
    def tempo_estimado(self):
        """Calcula o tempo estimado de preparo do pedido"""
        return max(
            (item.produto.tempo_preparo * item.quantidade 
             for item in self.itens),
            default=0
        )


class ItemPedido(db.Model):
    """Modelo para itens de um pedido"""
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    observacoes = db.Column(db.Text)
    
    # Chaves estrangeiras
    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey('pedidos.id'),
        nullable=False
    )
    produto_id = db.Column(
        db.Integer,
        db.ForeignKey('produtos.id'),
        nullable=False
    )
    
    @property
    def subtotal(self):
        """Calcula o subtotal do item"""
        return self.quantidade * self.preco_unitario