import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from backend import create_app, db
from backend.models import Usuario
from werkzeug.security import generate_password_hash

# Carregar variáveis de ambiente
load_dotenv()

# Criar a aplicação Flask
app = create_app()

def criar_usuarios_admin():
    """Cria usuários administradores para cada área"""
    usuarios_admin = [
        {
            'email': 'admin@delitrack.com',
            'senha': 'admin123',
            'nome': 'Administrador Geral',
            'tipo': 'gerente'
        },
        {
            'email': 'admin@garcom.com',
            'senha': 'admin123',
            'nome': 'Administrador Garçom',
            'tipo': 'garcom'
        },
        {
            'email': 'admin@cozinha.com',
            'senha': 'admin123',
            'nome': 'Administrador Cozinha',
            'tipo': 'cozinheiro'
        },
        {
            'email': 'admin@entrega.com',
            'senha': 'admin123',
            'nome': 'Administrador Entrega',
            'tipo': 'entregador'
        }
    ]
    
    for dados in usuarios_admin:
        # Verificar se o usuário já existe
        usuario = Usuario.query.filter_by(email=dados['email']).first()
        if not usuario:
            novo_usuario = Usuario(
                email=dados['email'],
                senha=generate_password_hash(dados['senha']),
                nome=dados['nome'],
                tipo=dados['tipo'],
                ativo=True
            )
            db.session.add(novo_usuario)
            print(f"Usuário {dados['nome']} criado com sucesso!")
            print(f"Email: {dados['email']}")
            print(f"Senha: {dados['senha']}")
            print("---")
    
    db.session.commit()
    print("Usuários administradores criados com sucesso!")

def inicializar_sistema():
    """Inicializa o sistema com as configurações necessárias"""
    print("Inicializando o sistema...")
    
    # Criar diretórios necessários
    diretorios = ['uploads', 'logs', 'temp']
    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            print(f"Diretório '{diretorio}' criado.")
    
    # Criar banco de dados e tabelas
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado.")
        
        # Criar usuários administradores
        criar_usuarios_admin()
    
    print("\nSistema inicializado com sucesso!")
    print("\nAcesse o sistema usando uma das seguintes contas:")
    print("Gerente: admin@delitrack.com / admin123")
    print("Garçom: admin@garcom.com / admin123")
    print("Cozinha: admin@cozinha.com / admin123")
    print("Entrega: admin@entrega.com / admin123")

if __name__ == '__main__':
    inicializar_sistema()
    app.run(debug=True) 