import sqlite3

from database import Databases


def main():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    users_db = Databases().get_users_db()
    for user in users:
        if users_db.get_user(user[0]) is None:
            users_db.add_user(user[0])
            email = None if user[1] == 'None' else user[1]
            users_db.set_email(user[0], email)
            print('Added {} with {}'.format(user[0], email))
        else:
            print('User {} exists'.format(user[0]))


if __name__ == "__main__":
    main()
