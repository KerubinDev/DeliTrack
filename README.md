# DeliTrack - Sistema de Gerenciamento de Pedidos e Entregas

O DeliTrack é um sistema web completo para gerenciamento de pedidos e entregas em restaurantes, desenvolvido com Flask e SQLAlchemy.

## Funcionalidades

- **Gerenciamento de Usuários**
  - Cadastro e autenticação de usuários
  - Diferentes níveis de acesso (garçom, chef, entregador, gerente)
  - Alteração de senha e recuperação por email

- **Gestão de Pedidos**
  - Criação e acompanhamento de pedidos
  - Interface específica para garçons
  - Painel de controle para a cozinha
  - Sistema de notificações em tempo real

- **Sistema de Entregas**
  - Rastreamento de entregadores em tempo real
  - Mapa interativo com rotas de entrega
  - Gestão de status das entregas
  - Cálculo de tempo estimado

- **Dashboard Gerencial**
  - Métricas em tempo real
  - Gráficos de desempenho
  - Relatórios personalizados
  - Gestão de usuários do sistema

## Tecnologias Utilizadas

- **Backend**
  - Python 3.8+
  - Flask 3.0.0
  - SQLAlchemy 2.0.23
  - Flask-Login para autenticação
  - Flask-Mail para envio de emails
  - Flask-Migrate para migrações do banco de dados

- **Frontend**
  - HTML5, CSS3, JavaScript
  - Bootstrap 4.5.2
  - jQuery 3.5.1
  - Leaflet.js para mapas
  - Chart.js para gráficos

- **Banco de Dados**
  - SQLite (desenvolvimento)
  - PostgreSQL (produção)

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/delitrack.git
   cd delitrack
   ```

2. Crie um ambiente virtual e ative-o:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. Inicialize o banco de dados:
   ```bash
   flask db upgrade
   ```

6. Execute o servidor de desenvolvimento:
   ```bash
   python run.py
   ```

## Estrutura do Projeto

```
delitrack/
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── auth.py
│   ├── config.py
│   ├── models.py
│   └── routes.py
├── frontend/
│   ├── dashboard.html
│   ├── cozinha.html
│   ├── garcom.html
│   └── entregadores.html
├── migrations/
│   ├── versions/
│   ├── alembic.ini
│   ├── env.py
│   └── script.py.mako
├── uploads/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## Configuração do Ambiente

1. **Variáveis de Ambiente**
   - `FLASK_APP`: Nome do módulo da aplicação
   - `FLASK_ENV`: Ambiente (development, production)
   - `SECRET_KEY`: Chave secreta para sessões
   - `DATABASE_URL`: URL do banco de dados
   - `MAIL_SERVER`: Servidor de email
   - `MAIL_PORT`: Porta do servidor de email
   - `MAIL_USERNAME`: Usuário do email
   - `MAIL_PASSWORD`: Senha do email

2. **Banco de Dados**
   - Desenvolvimento: SQLite
   - Produção: Configure `DATABASE_URL` para PostgreSQL

## Desenvolvimento

1. **Criar nova migração**:
   ```bash
   flask db migrate -m "descrição da migração"
   flask db upgrade
   ```

2. **Executar testes**:
   ```bash
   pytest
   ```

3. **Verificar cobertura de testes**:
   ```bash
   coverage run -m pytest
   coverage report
   ```

## Deployment

1. **Preparação**:
   - Configure as variáveis de ambiente de produção
   - Atualize o banco de dados
   - Colete arquivos estáticos

2. **Gunicorn**:
   ```bash
   gunicorn "backend.app:create_app()"
   ```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Para suporte, envie um email para suporte@delitrack.com ou abra uma issue no GitHub. 