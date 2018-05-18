import os
from string import Template
from abc import ABCMeta, abstractmethod
import psycopg2
import sqlite3


class Repository(metaclass=ABCMeta):
    sample_table_templ = Template('''CREATE TABLE samples
        (
            id $id_pre PRIMARY KEY $id_post,
            submitter text,
            name text,
            location text,
            latitude float,
            longitude float,
            imageLocation text,
            date date,
            time time
        )
        ''')

    add_sample_templ = Template('INSERT INTO samples (submitter, name, location, latitude, longitude, imageLocation, '
                                'date, time) VALUES (\'$submitter\', \'$name\', \'$location\', $latitude, $longitude, '
                                '\'$image_location\', \'$date\', \'$time\') $returning')

    def __init__(self):
        pass

    @abstractmethod
    def create_tables(self):
        raise NotImplementedError()

    @abstractmethod
    def add_sample(self, submitter, image_location, date, time, name=None, location=None, latitude=None, longitude=None):
        raise NotImplementedError()

    @abstractmethod
    def get_sample(self, id):
        pass

    @abstractmethod
    def drop_tables(self):
        raise NotImplementedError()


class SqliteRepository(Repository):
    def __init__(self, db_file):
        self.db_file = db_file
        # if the file doesn't exist, we will need to create the tables in the new file
        if not os.path.isfile(self.db_file):
            self.create_tables()

    def create_tables(self):
        sample_table = Repository.sample_table_templ.substitute(id_pre='INTEGER', id_post='AUTOINCREMENT')
        return self.execute_command(sample_table)

    def add_sample(self, submitter, image_location, date, time, name='', location='', latitude=0.0, longitude=0.0):
        command = Repository.add_sample_templ.substitute(
            submitter=submitter, name=name, location=location, latitude=latitude, longitude=longitude,
            image_location=image_location, date=date, time=time, returning='')
        ret_val = self.execute_command(command)
        return ret_val

    def get_sample(self, id):
        command = f'select * from samples where id = {id}'
        ret_val = self.execute_command(command, select=True)
        return ret_val

    def drop_tables(self):
        return self.execute_command('DROP TABLE IF EXISTS samples')

    def execute_command(self, command, select=False):
        ret_val = True
        try:
            conn = sqlite3.connect(self.db_file)
            cur = conn.cursor()
            cur.execute(command)
            if select:
                ret_val = cur.fetchall()
            else:
                ret_val = cur.lastrowid
        except Exception as ex:
            print(ex)
            ret_val = False
        finally:
            if conn is not None:
                conn.commit()
                conn.close()

        return ret_val


class PostgresRepository(Repository):
    def __init__(self):
        super(PostgresRepository, self).__init__()


    def create_tables(self):
        sample_table = Repository.sample_table_templ.substitute(id_pre='SERIAL', id_post='')
        return self.execute_command(sample_table)

    def execute_command(self, command, select=False):
        ret_val = True
        conn = None
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
        #command = f'INSERT INTO samples(submitter, name, location, latitude, longitude, imageLocation, date, time)' \
        #          f' VALUES (\'{submitter}\', \'{name}\', \'{location}\', 0.0, 0.0, \'{image_location}\', ' \
        #          f'\'{date}\', \'{time}\') RETURNING Id'
        command = Repository.add_sample_templ.substitute(
            submitter=submitter, name=name, location=location, latitude=latitude, longitude=longitude,
            image_location=image_location, date=date, time=time, returning='RETURNING id')
        ret_val = self.execute_command(command, select=True)
        return ret_val[0][0]

    def get_sample(self, id):
        command = f'select * from samples where id = {id}'
        ret_val = self.execute_command(command, select=True)
        return ret_val

    def drop_tables(self):
        return self.execute_command('DROP TABLE IF EXISTS samples')

