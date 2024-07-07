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
def add_user(cur, first_name, last_name, email, numbers=None):

    cur.execute(f"""

        INSERT INTO users(first_name, last_name, email) VALUES ('{first_name}', '{last_name}', '{email}')
        RETURNING user_id;
        """)
    user_id = cur.fetchone()[0]

    if numbers is not None:
        if not isinstance(numbers, tuple):
            numbers = (numbers,)
        for item in numbers:
            cur.execute(f"""
                    INSERT INTO phones(number, user_id) VALUES ('{item}',{user_id})
                    """)

    cur.execute(f"""
            SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u
            LEFT JOIN phones p ON p.user_id = u.user_id
            WHERE u.user_id = {user_id}
            """)

    new_cur = tuple()
    for item in set(cur.fetchall()):
        new_cur += item

    conn.commit()
    print("Addition user: ", tuple(dict.fromkeys(new_cur)))


# Addition phone data base
def add_phone(cur, number, user_id):

    cur.execute(f"""
        INSERT INTO phones(number, user_id) VALUES ('{number}',{user_id}) 
        RETURNING phone_id, number, user_id;
        """)

    conn.commit()
    print("Addition phone:", cur.fetchone())


# Change information about user
def update_data_user(cur, user_id, first_name=None, last_name=None, email=None, numbers=None):

    if first_name is not None:
        cur.execute("""
                UPDATE users SET first_name=%s
                WHERE user_id=%s
                """, (first_name, user_id))

    if last_name is not None:
        cur.execute("""
                UPDATE users SET last_name=%s
                WHERE user_id=%s
                """, (last_name, user_id))

    if email is not None:
        cur.execute("""
                UPDATE users SET email=%s
                WHERE user_id=%s
                """, (email, user_id))

    if numbers is not None:
        cur.execute(f"""
                SELECT phone_id FROM phones
                WHERE user_id = {user_id}
                """)

        all_phones_user = tuple()
        for item in set(cur.fetchall()):
            all_phones_user += item
        all_phones_user = tuple(sorted(all_phones_user))

        if not isinstance(numbers, tuple):
            numbers = (numbers,)
        for item in zip(numbers, all_phones_user):
            cur.execute(f"""
                    UPDATE phones SET number=%s
                    WHERE phone_id=%s
                    """, (item[0], item[1]))

    cur.execute(f"""
        SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
        LEFT JOIN phones p ON p.user_id = u.user_id         
        WHERE u.user_id = {user_id}
        """)

    new_cur = tuple()
    for item in set(cur.fetchall()):
        new_cur += item

    conn.commit()
    print("Update user data: ", tuple(dict.fromkeys(new_cur)))


# Delete the phone of an existing user
def delete_phone(cur, phone_id):

    cur.execute(f"""
            SELECT * FROM phones
            WHERE phone_id = {phone_id}
            """)
    print("Data that was deleted of phones: ", cur.fetchone())

    cur.execute(f"""
        DELETE FROM phones WHERE phone_id = {phone_id}
        """)

    conn.commit()


# Delete an existing user
def delete_user(cur, user_id):

    cur.execute(f"""
            SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
            LEFT JOIN phones p ON p.user_id = u.user_id         
            WHERE u.user_id = {user_id}
            """)

    new_cur = tuple()
    for item in set(cur.fetchall()):
        new_cur += item

    print("Data that was deleted about user: ", tuple(dict.fromkeys(new_cur)))

    cur.execute(f"""
        DELETE FROM phones WHERE user_id = {user_id}
        """)

    cur.execute(f"""
            DELETE FROM users WHERE user_id = {user_id}
            """)

    conn.commit()


# User search by user data
def search_user(cur, first_name=None, last_name=None, email=None, number=None):

    if first_name is not None:
        cur.execute(f"""
                SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                LEFT JOIN phones p ON p.user_id = u.user_id         
                WHERE u.user_id = (SELECT user_id FROM users WHERE first_name = '{first_name}')
                """)
    if last_name is not None:
        cur.execute(f"""
                SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                LEFT JOIN phones p ON p.user_id = u.user_id         
                WHERE u.user_id = (SELECT user_id FROM users WHERE last_name = '{last_name}')
                """)
    if email is not None:
        cur.execute(f"""
                SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                LEFT JOIN phones p ON p.user_id = u.user_id         
                WHERE u.user_id = (SELECT user_id FROM users WHERE email = '{email}')
                """)
    if number is not None:
        cur.execute(f"""
                SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                LEFT JOIN phones p ON p.user_id = u.user_id         
                WHERE u.user_id=(SELECT user_id FROM phones WHERE number='{number}')
                """)

    new_cur = tuple()
    for item in set(cur.fetchall()):
        new_cur += item

    if len(tuple(dict.fromkeys(new_cur))) != 0:
        print("Found user: ", tuple(dict.fromkeys(new_cur)))
    else:
        print("Incorrect value entered or there is no user with this value")


if __name__ == '__main__':

    conn = psycopg2.connect(database='database_from_python', user='postgres', password='1324')
    with conn.cursor() as curs:

        # create_tables(curs)
        # add_user(curs, 'Jason', 'Miller', 'ker@gmail.com',('89766978867', '89764658867'))
        # add_user(curs, 'Jerry ', 'Baker', 'ge352@mail.ru', '89656978867')
        # add_user(curs, 'Ja', 'M', 'k@gm.com')
        # add_user(curs, 'Js', 'Ml', 'er@gm.com', '89656979990')
        # add_phone(curs, '+79106343610', 1)
        # add_phone(curs, '89146343610', 1)
        # add_phone(curs, '+79777343610', 2)
        # update_data_user(curs, 1, "Jon", None, None, ('81593609777', '82598946777'))
        # delete_phone(curs,2)
        # delete_user(curs, 1)
         search_user(curs,  number='82598946777')

    conn.close()
