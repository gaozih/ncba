from flask import current_app
from alembic import context
from models import *

def run_migrations():
    """Run migrations in 'online' mode."""
    
    with current_app.app_context():
        config = context.config
        
        config.set_main_option(
            'sqlalchemy.url',
            current_app.config.get('SQLALCHEMY_DATABASE_URI')
        )
        
        with current_app.db.engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=current_app.db.metadata
            )
            
            with context.begin_transaction():
                context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations() 