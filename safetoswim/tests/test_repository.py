from safetoswim.repository import PostgresRepository


class TestsRepository(object):
    def __init__(self):
        repo = PostgresRepository()
        repo.drop_tables()

    def test_repo_create_tables(self):
        repo = PostgresRepository()
        result = repo.create_tables()
        assert result is True


    def test_repo_insert_sample(self):
        repo = PostgresRepository()
        result = repo.create_tables()
        assert result is True
        submitter = 'tim@safetoswim.org'
        id = repo.add_sample(submitter, 'image location', 'name', 'OakLedge')
        assert result is True
        assert id == 1
        result = repo.get_sample(id)
        assert result[0][1] == submitter

if __name__ == '__main__':
    tests = TestsRepository()
    tests.test_repo_insert_sample()