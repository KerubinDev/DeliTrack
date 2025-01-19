import os
import sys
from pathlib import Path

def inicializar_sistema():
    """Inicializa todo o sistema automaticamente"""
    
    print("🚀 Iniciando DeliTrack...")
    
    # 1. Criar arquivo .env se não existir
    if not os.path.exists('.env'):
        print("📝 Criando arquivo .env...")
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("""FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=chave-super-secreta-123
DATABASE_URL=sqlite:///delitrack.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha
MAIL_DEFAULT_SENDER=seu-email@gmail.com
MAX_CONTENT_LENGTH=16777216""")
    
    # 2. Criar diretórios necessários
    print("📁 Criando diretórios...")
    Path('uploads').mkdir(exist_ok=True)
    Path('migrations').mkdir(exist_ok=True)
    
    # 3. Instalar dependências
    print("📦 Instalando dependências...")
    os.system('pip install -r requirements.txt')
    
    # 4. Inicializar banco de dados e criar admin
    print("🗄️ Configurando banco de dados...")
    from backend import create_app, db
    from backend.models import Usuario
    from werkzeug.security import generate_password_hash
    
    app = create_app()
    
    with app.app_context():
        # Criar tabelas
        db.create_all()
        
        # Criar admin se não existir
        admin = Usuario.query.filter_by(email='admin@delitrack.com').first()
        if not admin:
            admin = Usuario(
                nome='Administrador',
                email='admin@delitrack.com',
                senha_hash=generate_password_hash('admin123'),
                tipo='gerente',
                ativo=True
            )
            db.session.add(admin)
            db.session.commit()
            print("👤 Usuário admin criado!")
            print("📧 Email: admin@delitrack.com")
            print("🔑 Senha: admin123")
    
    # 5. Iniciar o servidor
    print("\n✨ Sistema inicializado com sucesso!")
    print("🌐 Acessar: http://localhost:5000")
    print("📧 Login: admin@delitrack.com")
    print("🔑 Senha: admin123\n")
    
    print("🚀 Iniciando servidor...")
    app.run(debug=True)

if __name__ == '__main__':
    inicializar_sistema() 