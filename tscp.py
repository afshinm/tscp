import threading


class ThreadSafeConnectionPool(object):
    _lock = threading.Lock()
    _connections = []
    _connections_count = 0
    _locked_connections = []
    _counter = 0

    def __init__(self, connection_handler, connections_count=10):
        self._connections_count = connections_count
        self._connections = [connection_handler() for _ in range(connections_count)]

    def _next_connection_id(self):
        if self._counter > self._connections_count - 1:
            self._counter = 0

        tmp = self._counter
        self._counter += 1
        return tmp

    def _next_connection(self):
        i = 0
        while True:
            n = self._next_connection_id()
            connection = self._connections[n]

            if connection not in self._locked_connections:
                break

            if i > self._connections_count - 1:
                return None

            i += 1

        self._locked_connections.append(connection)

        return connection

    def get_connection(self):
        self._lock.acquire()
        connection = self._next_connection()
        self._lock.release()

        return ConnectionWrapper(connection, self)

    def release_connection(self, connection):
        self._locked_connections.remove(connection)

    def get_connections_count(self):
        return self._connections_count


class ConnectionWrapper(object):
    connection = None
    pool = None

    def __init__(self, connection, pool):
        self.connection = connection
        self.pool = pool

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.release_connection(self.connection)
