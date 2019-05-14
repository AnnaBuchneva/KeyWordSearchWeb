from sqlalchemy import create_engine, MetaData, Table, Column, String, pool
from scripts.data import get_path_above


class DataBase:
    def __init__(self):
        path_to_db = get_path_above('resources/users.db')
        self.engine = create_engine('sqlite:///{}'.format(path_to_db), echo=False, poolclass=pool.SingletonThreadPool)
        self.metadata = MetaData(self.engine)
        self.connection = self.engine.connect()
        self.users = Table('users', self.metadata, autoload=True)

    def __del__(self):
        self.connection.close()

    def create_table(self):
        self.users = Table('users', self.metadata,
                      Column('username', String, primary_key=True),
                      Column('password', String)
                      )
        self.metadata.create_all(self.engine)

    def create_user(self, username, password):
        if not self.get_user(username):
            self.connection.execute(self.users.insert(), username=username, password=password)
        else:
            self.connection.execute(self.users.update(self.users.c.username == username), password=password)

    def get_user(self, username):
        result = self.users.select(self.users.c.username == username).execute().first()
        return result
