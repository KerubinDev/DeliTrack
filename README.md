# DeliTrack - Sistema de Gerenciamento de Pedidos e Entregas

Sistema web completo para gerenciamento de pedidos e entregas em restaurantes, desenvolvido com Flask e SQLAlchemy.

## Funcionalidades

- Gestão de usuários (garçons, cozinheiros, entregadores, gerentes)
- Sistema de pedidos com acompanhamento em tempo real
- Gestão de entregas com rastreamento
- Dashboard gerencial com métricas e relatórios
- Sistema de notificações
- Interface responsiva e moderna

## Tecnologias

- Python 3.12+
- Flask (Framework web)
- SQLAlchemy (ORM)
- SQLite (Desenvolvimento)
- PostgreSQL (Produção)
- Bootstrap 4 (Frontend)
- JavaScript (Interatividade)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/delitrack.git
cd delitrack
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
# Windows (PowerShell)
copy .env.example .env
# Linux/Mac
cp .env.example .env
```

4. Edite o arquivo `.env` com suas configurações

5. Inicialize o banco de dados:
```bash
flask db upgrade
```

6. Crie o usuário administrador:
```bash
python scripts/criar_admin.py
```

## Executando o Sistema

1. Desenvolvimento:
```bash
python run.py
```

2. Produção:
```bash
gunicorn "backend:create_app()"
```

O sistema estará disponível em `http://localhost:5000`

## Credenciais Iniciais

- Email: admin@delitrack.com
- Senha: admin123

**Importante**: Altere a senha do administrador após o primeiro login.

## Estrutura do Projeto

```
delitrack/
├── backend/           # Código backend
│   ├── models.py     # Modelos do banco de dados
│   ├── routes.py     # Rotas da aplicação
│   ├── auth.py       # Sistema de autenticação
│   └── config.py     # Configurações
├── templates/         # Templates HTML
│   ├── auth/         # Templates de autenticação
│   └── email/        # Templates de email
├── static/           # Arquivos estáticos
├── migrations/       # Migrações do banco
├── scripts/          # Scripts utilitários
└── uploads/          # Arquivos enviados
```

## Configuração do Ambiente

### Variáveis de Ambiente (.env)

```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta

# Banco de dados
DATABASE_URL=sqlite:///delitrack.db

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha
MAIL_DEFAULT_SENDER=seu-email@gmail.com

# Uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

## Desenvolvimento

1. Criar novas migrações:
```bash
flask db migrate -m "Descrição da migração"
```

2. Aplicar migrações:
```bash
flask db upgrade
```

3. Executar testes:
```bash
python -m pytest
```

## Produção

1. Configure o PostgreSQL
2. Atualize DATABASE_URL no .env
3. Configure um servidor web (nginx/apache)
4. Use gunicorn como servidor WSGI
5. Configure SSL/TLS para HTTPS

## Suporte

Em caso de dúvidas ou problemas:
- Abra uma issue no GitHub
- Envie um email para suporte@delitrack.com

## Licença

Este projeto está licenciado sob a MIT License. 