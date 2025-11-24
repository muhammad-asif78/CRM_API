import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Load .env
from dotenv import load_dotenv
load_dotenv()

# Import your Base where models are defined
from app.core.database import Base  # SQLAlchemy Base
from app.models.user import User
from app.models.role import Role

# Alembic Config object
config = context.config

# Override sqlalchemy.url from .env
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Set up Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData here for 'autogenerate'
target_metadata = Base.metadata

# ---------------- Offline Migrations ---------------- #
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ---------------- Online Migrations ---------------- #
def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# ---------------- Run Migrations ---------------- #
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
