from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.core.db import Base
from app.core.config import settings

# Import all models to ensure they are registered with Base.metadata
from app.models.users import User
from app.models.destination import Destination
from app.models.category import Category
from app.models.tour import Tour
from app.models.tour_itinerary_day import TourItineraryDay
from app.models.departure import Departure
from app.models.guide_assignment import GuideAssignment
from app.models.booking import Booking
from app.models.booking_traveler import BookingTraveler
from app.models.attendance import Attendance
from app.models.payment import Payment    

config = context.config

# Dynamically set the database URL from settings, escaping % for ConfigParser
db_url_for_alembic = settings.DATABASE_URL
if db_url_for_alembic and db_url_for_alembic.startswith("postgresql+asyncpg://"):
    db_url_for_alembic = db_url_for_alembic.replace("postgresql+asyncpg://", "postgresql://", 1)

config.set_main_option("sqlalchemy.url", db_url_for_alembic.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

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
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = engine_from_config(
        configuration,
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
