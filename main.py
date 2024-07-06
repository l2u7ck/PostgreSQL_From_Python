import psycopg2


# Create tables data base
def create_tables(cur):

    cur.execute("""
                DROP TABLE phones;
                DROP TABLE users;
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    user_id SERIAL PRIMARY KEY,
                    first_name  varchar(50) NOT NULL,
                    last_name varchar(50) NOT NULL,
                    email varchar(50) NOT NULL
                )
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS phones(
                    phone_id SERIAL PRIMARY KEY,
                    number char(12) NOT NULL,
                    user_id INTEGER NOT NULL REFERENCES users(user_id)
                )
                """)

    conn.commit()
def addition_user(cur):
    

conn = psycopg2.connect(database='database_from_python', user='postgres', password='1324')
with conn.cursor() as curs:
    create_tables(curs)
conn.close()
