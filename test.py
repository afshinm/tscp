import random
import unittest
import threading
from tscp import ThreadSafeConnectionPool


connections = []


def dummy_connection():
    return random.random()


def smoke_test(assertTrue, pool):
    with pool.get_connection() as connection:
        if connection is not None:
            assertTrue(connection not in connections)
            connections.append(connection)
        else:
            assertTrue(len(connections) > 0)

    connection is not None and connections.remove(connection)


class TestThreadPool(unittest.TestCase):
    def test_create_pool(self):
        tscp = ThreadSafeConnectionPool(dummy_connection, 5)
        self.assertTrue(tscp.get_connections_count(), 5)

    def test_thread_safety(self):
        tscp = ThreadSafeConnectionPool(dummy_connection, 1)
        threads = [threading.Thread(target=smoke_test, args=(self.assertTrue, tscp)) for _ in range(50)]
        list(map(lambda x: x.start() and x.join(), threads))


if __name__ == '__main__':
    unittest.main()