from backend import create_app, db
from backend.models import Usuario

def criar_admin():
    """Cria o usuário administrador inicial."""
    app = create_app()
    
    with app.app_context():
        # Verificar se já existe um usuário admin
        admin = Usuario.query.filter_by(email='admin@delitrack.com').first()
        
        if not admin:
            admin = Usuario(
                nome='Administrador',
                email='admin@delitrack.com',
                tipo='gerente',
                ativo=True
            )
            admin.set_senha('admin123')
            
            db.session.add(admin)
            db.session.commit()
            print('Usuário administrador criado com sucesso!')
            print('Email: admin@delitrack.com')
            print('Senha: admin123')
        else:
            print('Usuário administrador já existe!')

if __name__ == '__main__':
    criar_admin() 