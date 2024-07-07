import psycopg2


# Create tables data base
def create_tables(cur):

    cur.execute("""
            DROP TABLE IF EXISTS phones;
            DROP TABLE IF EXISTS users;
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

    try:
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

        # Create of understandable data output
        new_cur = tuple()
        for item in set(cur.fetchall()):
            new_cur += item

        conn.commit()
        print("Addition user: ", tuple(dict.fromkeys(new_cur)))

    except psycopg2.errors.CheckViolation as e:
        print(f"Error when adding a user: {e}")

    except psycopg2.errors.StringDataRightTruncation as e:
        print(f"Error when adding a user: {e}")


# Addition phone data base
def add_phone(cur, number, user_id):

    try:
        cur.execute(f"""
            INSERT INTO phones(number, user_id) VALUES ('{number}',{user_id}) 
            RETURNING phone_id, number, user_id;
            """)

        conn.commit()
        print("Addition phone:", cur.fetchone())

    except psycopg2.errors.CheckViolation as e:
        print(f"Error when adding a phone: {e}")

    except psycopg2.errors.StringDataRightTruncation as e:
        print(f"Error when adding a phone: {e}")

    except psycopg2.errors.ForeignKeyViolation as e:
        print(f"Error when adding a phone: {e}")

    except psycopg2.errors.InFailedSqlTransaction as e:
        print(f"Error when updating user data: {e}")


# Change information about user
def update_data_user(cur, user_id, first_name=None, last_name=None, email=None, numbers=None):

    try:
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

            # Updating phone numbers
            """
            all_phones_user - stores the ID of all the user's phones  
            numbers - the tuple with the new phones
            """
            all_phones_user = tuple()
            for item in set(cur.fetchall()):
                all_phones_user += item
            all_phones_user = tuple(sorted(all_phones_user))

            if len(all_phones_user) < len(numbers):
                print(f"There are more phones than there are in the database."
                      f"No {len(numbers)-len(all_phones_user)} phones were added.")

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

        # Create of understandable data output
        new_cur = tuple()
        for item in set(cur.fetchall()):
            new_cur += item

        conn.commit()
        print("Update user data: ", tuple(dict.fromkeys(new_cur)))

    except psycopg2.errors.CheckViolation as e:
        print(f"Error when updating user data: {e}")

    except psycopg2.errors.StringDataRightTruncation as e:
        print(f"Error when updating user data: {e}")

    except psycopg2.errors.ForeignKeyViolation as e:
        print(f"Error when updating user data: {e}")

    except psycopg2.errors.InFailedSqlTransaction as e:
        print(f"Error when updating user data: {e}")


# Delete the phone of an existing user
def delete_phone(cur, phone_id):
    try:
        cur.execute(f"""
                    SELECT * FROM phones
                    WHERE phone_id = {phone_id}
                    """)
        print("Data that was deleted of phones: ", cur.fetchone())

        cur.execute(f"""
                DELETE FROM phones WHERE phone_id = {phone_id}
                """)

        conn.commit()

    except psycopg2.errors.InFailedSqlTransaction as e:
        print(f"Error when updating user data: {e}")


# Delete an existing user
def delete_user(cur, user_id):

    try:
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

    except psycopg2.errors.InFailedSqlTransaction as e:
        print(f"Error when updating user data: {e}")


# User search by user data
def search_user(cur, first_name=None, last_name=None, email=None, number=None):

    try:
        # result_search - stores tuples with query results (user_id)
        result_search = list()
        if first_name is not None:
            cur.execute(f"""
                        SELECT user_id FROM users 
                        WHERE first_name = '{first_name}'
                        """)
            result_search.append(set(cur.fetchall()))

        if last_name is not None:
            cur.execute(f"""
                        SELECT user_id FROM users 
                        WHERE last_name = '{last_name}'
                        """)
            result_search.append(set(cur.fetchall()))

        if email is not None:
            cur.execute(f"""
                        SELECT user_id FROM users 
                        WHERE email = '{email}'
                        """)
            result_search.append(set(cur.fetchall()))

        if number is not None:
            cur.execute(f"""
                        SELECT user_id FROM phones 
                        WHERE number='{number}'
                        """)
            result_search.append(set(cur.fetchall()))

        # Search for the user index by intersecting tuples from the query
        user_id = result_search[0]
        for item in result_search[1:]:
            user_id &= item

        if len(user_id) == 1:
            user_id = list(user_id)[0][0]

            cur.execute(f"""
                        SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                        LEFT JOIN phones p ON p.user_id = u.user_id         
                        WHERE u.user_id = {user_id}
                        """)

            # Create of understandable data output
            new_cur = tuple()
            for item in set(cur.fetchall()):
                new_cur += item

            if len(tuple(dict.fromkeys(new_cur))) != 0:
                print("Found user: ", tuple(dict.fromkeys(new_cur)))
            else:
                print("Incorrect value entered or there is no user with this value")
        else:
            print("More than one user has this data. Add another search parameter.")

    except psycopg2.errors.InFailedSqlTransaction as e:
        print(f"Error when updating user data: {e}")


if __name__ == '__main__':

    conn = psycopg2.connect(database='database_from_python', user='postgres', password='1324')
    with conn.cursor() as curs:

        create_tables(curs)
        add_user(curs, 'Jason', 'Baker', 'ker@gmail.com', ('89777777777', '89666666666'))
        add_user(curs, 'Jerry', 'Baker', 'ge352@mail.ru', '89444444444')
        add_user(curs, 'Jerry', 'Baker', 'cat@yandex.ru')
        add_user(curs, 'Scott', 'Wilson', 'cat@yandex.ru')
        add_phone(curs, '+79010101010', 1)
        # update_data_user(curs, 2, "Jon", numbers=('81593609777', '82598946777'))
        # update_data_user(curs, 2, "Jon", "Adams", None, '89900000009')
        # delete_phone(curs,2)
        # delete_user(curs, 1)
        # search_user(curs,  number='82598946777')

        # Error checking
        # add_user(curs, 'Ray ', 'Kroc', 'makyandex.ru')
        # add_phone(curs, '901010101', 1)
        # update_data_user(curs, 99, numbers='8111111009')
        # delete_phone(curs, 999)
        # delete_user(curs, 999)
        # search_user(curs, 'Jerry', 'Baker', number='89444444444')

    conn.close()
