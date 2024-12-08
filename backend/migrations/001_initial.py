"""Initial migration

Peewee-migrate migration file

"""

def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    
    # Drop tables if they exist (for clean migration)
    migrator.sql('DROP TABLE IF EXISTS message CASCADE')
    migrator.sql('DROP TABLE IF EXISTS personalad CASCADE')
    migrator.sql('DROP TABLE IF EXISTS "user" CASCADE')

    # Create User table
    migrator.sql('''
        CREATE TABLE "user" (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            profile_picture VARCHAR(255),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            last_location_update TIMESTAMP
        )
    ''')

    # Add unique constraints
    migrator.sql('CREATE UNIQUE INDEX user_username_key ON "user" (username)')
    migrator.sql('CREATE UNIQUE INDEX user_email_key ON "user" (email)')

    # Create PersonalAd table
    migrator.sql('''
        CREATE TABLE personalad (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES "user" (id) ON DELETE CASCADE
        )
    ''')

    # Create Message table
    migrator.sql('''
        CREATE TABLE message (
            id SERIAL PRIMARY KEY,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN NOT NULL DEFAULT FALSE,
            read_at TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES "user" (id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES "user" (id) ON DELETE CASCADE
        )
    ''')

    # Create indexes
    migrator.sql('CREATE INDEX idx_personalad_user_id ON personalad (user_id)')
    migrator.sql('CREATE INDEX idx_personalad_is_active ON personalad (is_active)')
    migrator.sql('CREATE INDEX idx_message_sender_id ON message (sender_id)')
    migrator.sql('CREATE INDEX idx_message_receiver_id ON message (receiver_id)')
    migrator.sql('CREATE INDEX idx_message_is_read ON message (is_read)')


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    
    migrator.sql('DROP TABLE IF EXISTS message CASCADE')
    migrator.sql('DROP TABLE IF EXISTS personalad CASCADE')
    migrator.sql('DROP TABLE IF EXISTS "user" CASCADE')
