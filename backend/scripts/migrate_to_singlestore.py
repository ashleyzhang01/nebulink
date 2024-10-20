import csv
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.database import Base

# Create engines for both local and SingleStore databases
local_engine = create_engine("sqlite:///./sql_app.db")  # Adjust this to your local database URL
singlestore_engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)

def export_table(table_name, local_engine, singlestore_engine):
    # Export data from local database
    with local_engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table_name}"))
        data = result.fetchall()
        columns = result.keys()

    # Import data into SingleStore
    with singlestore_engine.connect() as conn:
        for row in data:
            placeholders = ', '.join(['%s'] * len(row))
            columns_string = ', '.join(columns)
            sql = f"INSERT INTO {table_name} ({columns_string}) VALUES ({placeholders})"
            conn.execute(text(sql), row)
        conn.commit()

def main():
    # Create tables in SingleStore
    Base.metadata.create_all(singlestore_engine)

    # Export and import each table
    for table in Base.metadata.tables:
        print(f"Migrating table: {table}")
        try:
            export_table(table, local_engine, singlestore_engine)
            print(f"Successfully migrated table: {table}")
        except Exception as e:
            print(f"Error migrating table {table}: {str(e)}")

if __name__ == "__main__":
    main()