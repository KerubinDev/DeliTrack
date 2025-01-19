from __future__ import with_statement

import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Adicionar o diretório pai ao path para importar a aplicação
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar os modelos e configurações
from backend.models import db
from backend.config import config as app_config
from backend.app import create_app

# Obter a URL do banco de dados da configuração da aplicação
app = create_app()
config = context.config

# Interpretar o arquivo de configuração para logging
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

config.set_main_option(
    'sqlalchemy.url',
    str(app.config.get('SQLALCHEMY_DATABASE_URI'))
)
target_metadata = db.metadata

# Outras configurações que você pode querer ajustar
# config.set_main_option('sqlalchemy.url', 'driver://user:pass@localhost/dbname')


def run_migrations_offline():
    """Executa migrações em modo 'offline'.

    Isso configura o contexto com apenas uma URL
    e não um Engine, embora um Engine seja aceitável
    aqui também. Por skipping, várias configurações de
    Engine são ignoradas aqui, incluindo 'poolclass' e 'pool_size'.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Executa migrações em modo 'online'.

    Neste cenário, precisamos criar um Engine
    e associá-lo com o contexto.

    """
    # Configurações para a conexão do banco de dados
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Comparar tipos na geração de migrações
            compare_type=True,
            # Comparar server defaults na geração de migrações
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 