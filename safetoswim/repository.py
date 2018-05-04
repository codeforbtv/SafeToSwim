from abc import ABCMeta
import psycopg2


class Repository(metaclass=ABCMeta):
    sample_table = '''CREATE TABLE samples
    (
        id SERIAL PRIMARY KEY,
        submitter text,
        name text,
        location text,
        latitude float,
        longitude float,
        imageLocation text,
        date date,
        time time
    )
    '''

    def __init__(self):
        pass

    def create_tables(self):
        raise NotImplementedError()

    def add_sample(self, submitter, image_location, date, time, name=None, location=None, latitude=None, longitude=None):
        raise NotImplementedError

    def get_sample(self, id):
        pass

    def drop_tables(self):
        raise NotImplementedError()

class PostgresRepository(Repository):
    def __init__(self):
        super(PostgresRepository, self).__init__()


    def create_tables(self):
        return self.execute_command(Repository.sample_table)

    def execute_command(self, command, select=False):
        ret_val = True
        try:
            conn = psycopg2.connect("host='localhost' dbname='SafeToSwim' user='stos' password='algalBl00m'")
            cur = conn.cursor()
            cur.execute(command)
            if select:
                ret_val = cur.fetchall()
        except Exception as ex:
            print(ex)
            ret_val = False
        finally:
            if conn is not None:
                conn.commit()
                conn.close()

        return ret_val


    def add_sample(self, submitter, image_location, date, time, name=None, location=None, latitude=None, longitude=None):
        command = f'INSERT INTO samples(submitter, name, location, latitude, longitude, imageLocation, date, time)' \
                  f' VALUES (\'{submitter}\', \'{name}\', \'{location}\', 0.0, 0.0, \'{image_location}\', ' \
                  f'\'{date}\', \'{time}\') RETURNING Id'
        ret_val = self.execute_command(command, select=True)
        return ret_val[0][0]

    def get_sample(self, id):
        command = f'select * from samples where id = {id}'
        ret_val = self.execute_command(command, select=True)
        return ret_val

    def drop_tables(self):
        return self.execute_command('DROP TABLE IF EXISTS samples')