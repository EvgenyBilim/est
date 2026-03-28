from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, make_url

from src.infra.models.base import Base
from src.settings import Settings

target_metadata = Base.metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# в случае тестов скрипт запускается внутри питона и средствами alembic внутрь прокидывается контекст,
# который уже содержит url
if config.cmd_opts is not None and hasattr(config.cmd_opts, "pg_url"):
    URL = config.cmd_opts.pg_url
else:

    class DbSettings(Settings):
        class Config:
            env_file = "local.env"

    URL = make_url(str(DbSettings().postgres_dsn)).set(drivername="postgresql+psycopg")


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(URL)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
