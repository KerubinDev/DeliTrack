import os
import sys

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import create_app, db
from backend.models import Usuario
from werkzeug.security import generate_password_hash

def criar_admin():
    """Cria o usuário administrador inicial."""
    app = create_app()
    
    with app.app_context():
        # Verifica se já existe um admin
        admin = Usuario.query.filter_by(email='admin@delitrack.com').first()
        
        if admin:
            print('Usuário administrador já existe!')
            print('Email: admin@delitrack.com')
            return
        
        # Cria o usuário admin
        admin = Usuario(
            nome='Administrador',
            email='admin@delitrack.com',
            senha_hash=generate_password_hash('admin123'),
            tipo='gerente',
            ativo=True
        )
        
        # Adiciona ao banco de dados
        db.session.add(admin)
        db.session.commit()
        
        print('Usuário administrador criado com sucesso!')
        print('Email: admin@delitrack.com')
        print('Senha: admin123')

if __name__ == '__main__':
    criar_admin() 