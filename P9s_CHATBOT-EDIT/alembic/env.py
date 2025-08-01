import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ให้ Python หา modules ในโปรเจกต์
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import settings
from services.database import Base

# โหลดการตั้งค่า Alembic
config = context.config
# override URL จาก settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# ตั้งค่า logging
fileConfig(config.config_file_name)

# metadata รวมจากโมเดลทั้งหมด
target_metadata = Base.metadata

def run_migrations_offline():
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
