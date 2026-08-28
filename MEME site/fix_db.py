from sqlalchemy import create_engine, text

# Paste the External Database URL copied from the Connect button here
DATABASE_URL = "postgresql://memefiy_user:mT5T7LhfeOVS6GRsQq1MJcXlmUo0Z4VN@dpg-da6jdqv10e5c73bu41t0-a.oregon-postgres.render.com/memefiy"

engine = create_engine(DATABASE_URL)


with engine.connect() as connection:
    connection.execute(text("ALTER TABLE post DROP COLUMN created_user;"))
    connection.commit()
    print("Column 'created_user' deleted successfully!")