import psycopg2


# Create tables data base
def create_tables():

    cur.execute("""
            DROP TABLE phones;
            DROP TABLE users;
            """)

    cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id SERIAL PRIMARY KEY,
                first_name  varchar(50) NOT NULL,
                last_name varchar(50) NOT NULL,
                email varchar(50) NOT NULL,
                CHECK (email LIKE '%@%.%')
            )
            """)

    cur.execute("""
            CREATE TABLE IF NOT EXISTS phones(
                phone_id SERIAL PRIMARY KEY,
                number char(12) NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                CHECK (number LIKE '+7%' OR number LIKE '8%')
            )
            """)

    conn.commit()


# Addition user data base
def addition_user(user_id, first_name, last_name, email):
    cur.execute(f"""
        INSERT INTO users VALUES ({user_id}, '{first_name}', '{last_name}', '{email}') 
        RETURNING user_id, first_name, last_name, email;
        """)
    conn.commit()
    print("Addition user:", cur.fetchone())


# Addition phone data base
def addition_phone(phone_id, number, user_id):

    cur.execute(f"""
        INSERT INTO phones VALUES ({phone_id},'{number}',{user_id}) 
        RETURNING phone_id, number, user_id;
        """)

    conn.commit()
    print("Addition phone:", cur.fetchone())


# Change information about user
def update_data_user(user_id, first_name, last_name, email):

    if first_name != 0:
        cur.execute(f"""
                UPDATE users SET first_name=%s
                WHERE user_id=%s
                """, (f"{first_name}", f"{user_id}"))

    if last_name != 0:
        cur.execute(f"""
                UPDATE users SET last_name=%s
                WHERE user_id=%s
                """, (f"{last_name}", f"{user_id}"))

    if email != 0:
        cur.execute(f"""
                UPDATE users SET email=%s
                WHERE user_id=%s
                """, (f"{email}", f"{user_id}"))

    cur.execute(f"""
        SELECT * FROM users;
        """)

    conn.commit()
    print("Update user data: ", cur.fetchone())


# Delete the phone of an existing user
def delete_phone(phone_id):

    cur.execute(f"""
            SELECT * FROM phones
            WHERE phone_id = {phone_id}
            """)
    print("Data that was deleted of phones: " ,cur.fetchone())

    cur.execute(f"""
        DELETE FROM phones WHERE phone_id = {phone_id}
        """)

    conn.commit()


# Delete an existing user
def delete_user(user_id):

    cur.execute(f"""
            SELECT * FROM users
            WHERE user_id = {user_id}
            """)
    print("Data that was deleted about user: ",cur.fetchone())

    cur.execute(f"""
                SELECT * FROM phones
                WHERE user_id = {user_id}
                """)
    print("The phones that was deleted: ",cur.fetchall())

    cur.execute(f"""
        DELETE FROM phones WHERE user_id = {user_id}
        """)

    cur.execute(f"""
            DELETE FROM users WHERE user_id = {user_id}
            """)

    conn.commit()


# User search by user data
def search_user(key, value):

    status = True

    if 'first_name' == key:
        cur.execute(f"""
                SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                LEFT JOIN phones p ON p.user_id = u.user_id         
                WHERE u.user_id = (SELECT user_id FROM users WHERE first_name = '{value}')
                """)
    elif 'last_name' == key:
        cur.execute(f"""
                SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                LEFT JOIN phones p ON p.user_id = u.user_id         
                WHERE u.user_id = (SELECT user_id FROM users WHERE last_name = '{value}')
                """)
    elif 'email' == key:
        cur.execute(f"""
                SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                LEFT JOIN phones p ON p.user_id = u.user_id         
                WHERE u.user_id = (SELECT user_id FROM users WHERE email = '{value}')
                """)
    elif 'number' == key:
        cur.execute(f"""
                SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                LEFT JOIN phones p ON p.user_id = u.user_id         
                WHERE u.user_id=(SELECT user_id FROM phones WHERE number='{value}')
                """)
    else:
        print("Incorrect key: ", key)
        print("Correct key: first_name, last_name, email or number")
        status = False

    if status:
        new_cur = tuple()
        for item in set(cur.fetchall()):
            new_cur += item

        if len(tuple(dict.fromkeys(new_cur))) != 0:
            print("Found user: ", tuple(dict.fromkeys(new_cur)))
        else:
            print("Incorrect value entered or there is no user with this value")


if __name__ == '__main__':

    conn = psycopg2.connect(database='database_from_python', user='postgres', password='1324')
    with conn.cursor() as cur:

        create_tables()
        addition_user(1, 'Jason', 'Miller', 'ker@gmail.com')
        addition_phone(1, '+79106343610', 1)
        addition_phone(2, '89146343610', 1)
        #addition_phone(3, '+79777343610', 1)
        #update_data_user(1, "Jen", 0, 0)
        #delete_phone(1)
        #delete_user(1)
        #search_user('number', '89106343610')

    conn.close()
