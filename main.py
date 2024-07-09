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


# Addition user data base
def add_user(cur, first_name, last_name, email, numbers=None):

    try:
        cur.execute("""
                INSERT INTO users(first_name, last_name, email) VALUES (%s, %s, %s)
                RETURNING user_id;
                """, (first_name, last_name, email))
        user_id = cur.fetchone()[0]

        if numbers is not None:
            if not isinstance(numbers, tuple):
                numbers = (numbers,)
            for item in numbers:
                cur.execute("""
                            INSERT INTO phones(number, user_id) VALUES (%s, %s)
                            """, (item, user_id))

        cur.execute("""
                    SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u
                    LEFT JOIN phones p ON p.user_id = u.user_id
                    WHERE u.user_id = %s
                    """, (user_id, ))

        # Create of understandable data output
        new_cur = tuple()
        for item in set(cur.fetchall()):
            new_cur += item

        print("Addition user: ", tuple(dict.fromkeys(new_cur)))

    except psycopg2.errors.CheckViolation as e:
        print(f"Error when adding a user: {e}")

    except psycopg2.errors.StringDataRightTruncation as e:
        print(f"Error when adding a user: {e}")


# Addition phone data base
def add_phone(cur, number, user_id):

    try:
        cur.execute("""
            INSERT INTO phones(number, user_id) VALUES (%s, %s) 
            RETURNING phone_id, number, user_id;
            """, (number, user_id))

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
            cur.execute("""
                    SELECT phone_id FROM phones
                    WHERE user_id = %s
                    """, (user_id, ))

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
                cur.execute("""
                        UPDATE phones SET number=%s
                        WHERE phone_id=%s
                        """, (item[0], item[1]))

        cur.execute("""
            SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
            LEFT JOIN phones p ON p.user_id = u.user_id         
            WHERE u.user_id = %s
            """, (user_id, ))

        # Create of understandable data output
        new_cur = tuple()
        for item in set(cur.fetchall()):
            new_cur += item

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
        cur.execute("""
                    SELECT * FROM phones
                    WHERE phone_id = %s 
                    """, (phone_id, ))
        print("Data that was deleted of phones: ", cur.fetchone())

        cur.execute("""
                DELETE FROM phones WHERE phone_id = %s
                """, (phone_id, ))

    except psycopg2.errors.InFailedSqlTransaction as e:
        print(f"Error when updating user data: {e}")


# Delete an existing user
def delete_user(cur, user_id):

    try:
        cur.execute("""
                    SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                    LEFT JOIN phones p ON p.user_id = u.user_id         
                    WHERE u.user_id = %s
                    """, (user_id, ))

        new_cur = tuple()
        for item in set(cur.fetchall()):
            new_cur += item

        print("Data that was deleted about user: ", tuple(dict.fromkeys(new_cur)))

        cur.execute("""
               DELETE FROM phones WHERE user_id = %s
               """, (user_id, ))

        cur.execute("""
                   DELETE FROM users WHERE user_id = %s
                   """, (user_id, ))

    except psycopg2.errors.InFailedSqlTransaction as e:
        print(f"Error when updating user data: {e}")


# User search by user data
def search_user(cur, first_name='%', last_name='%', email='%', number='%'):

    try:

        cur.execute("""
                SELECT DISTINCT u.user_id, first_name, last_name, email, number FROM users u  
                LEFT JOIN phones p ON p.user_id = u.user_id         
                WHERE first_name LIKE (%s) 
                    AND last_name LIKE (%s) 
                    AND email LIKE (%s) 
                    AND (number LIKE (%s) OR number LIKE (null)) 
                """, (first_name, last_name, email, number))

        # Create of understandable data output
        users_dict = dict()
        for item in set(cur.fetchall()):
            if item[0] in users_dict.keys():
                users_dict[item[0]] += (item[4], )
            else:
                users_dict[item[0]] = item

        if len(users_dict) != 0:
            print("Found users: ")
            for item in sorted(users_dict.items()):
                print(item[1])
            print()
        else:
            print("Incorrect value entered or there is no user with this value")

    except psycopg2.errors.InFailedSqlTransaction as e:
        print(f"Error when updating user data: {e}")


if __name__ == '__main__':

    with psycopg2.connect(database='database_from_python', user='postgres', password='1324') as curs:

        curs = curs.cursor()

        create_tables(curs)
        add_user(curs, 'Jason', 'Baker', 'ker@gmail.com', ('89777777777', '89666666666'))
        add_user(curs, 'Jerry', 'Baker', 'ge352@mail.ru', '89444444444')
        add_user(curs, 'Jerry', 'Baker', 'cat@yandex.ru')
        add_user(curs, 'Scott', 'Wilson', 'cat@yandex.ru')
        add_phone(curs, '+79010101010', 1)
        # update_data_user(curs, 2, "Jon", numbers=('81593609777', '82598946777'))
        # update_data_user(curs, 2, "Jon", "Adams", None, '89900000009')
        # delete_phone(curs, 2)
        # delete_user(curs, 1)
        # search_user(curs, 'Jason', 'Baker')
        # search_user(curs, last_name='Baker')

        # Error checking
        # add_user(curs, 'Ray ', 'Kroc', 'makyandex.ru')
        # add_phone(curs, '901010101', 1)
        # update_data_user(curs, 99, numbers='8111111009')
        # delete_phone(curs, 999)
        # delete_user(curs, 999)
        # search_user(curs, 'Jerry', 'Baker', number='89444444444')

        curs.close()
