import datetime
from safetoswim.repository import PostgresRepository, SqliteRepository


class TestsRepository(object):
    def __init__(self):
        repo = PostgresRepository()
        repo = SqliteRepository('test.sqlite')
        repo.drop_tables()

    def test_repo_create_tables(self):
        repo = PostgresRepository()
        repo = SqliteRepository('test.sqlite')
        result = repo.create_tables()
        assert result is True


    def test_repo_insert_sample(self):
        repo = PostgresRepository()
        repo = SqliteRepository('test.sqlite')
        result = repo.create_tables()
        assert result == 0
        submitter = 'tim@safetoswim.org'
        dt = datetime.datetime.now()
        id = repo.add_sample(submitter, 'image location', dt.date(), dt.time(), 'name', 'OakLedge')
        assert id == 1
        result = repo.get_sample(id)
        assert result[0][1] == submitter

if __name__ == '__main__':
    tests = TestsRepository()
    tests.test_repo_insert_sample()