import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


mysql_module = types.ModuleType('mysql')
mysql_connector = types.ModuleType('mysql.connector')
mysql_connector.Error = type('Error', (Exception,), {})
mysql_module.connector = mysql_connector
pytz_module = types.ModuleType('pytz')
pytz_module.timezone = lambda name: name

with patch.dict(
    sys.modules,
    {
        'mysql': mysql_module,
        'mysql.connector': mysql_connector,
        'pytz': pytz_module,
    },
):
    module_spec = importlib.util.spec_from_file_location(
        'db_autocomplete_under_test',
        Path(__file__).resolve().parents[1] / 'db.py',
    )
    db = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(db)


class AutocompleteDatabaseTests(unittest.TestCase):
    def test_player_names_are_ordered_by_latest_activity(self):
        class Cursor:
            query = None

            def execute(self, query):
                self.query = query

            def fetchall(self):
                return [('Recent Player',), ('Older Player',), ('Never Played',)]

            def close(self):
                pass

        class Connection:
            def __init__(self):
                self.test_cursor = Cursor()

            def cursor(self):
                return self.test_cursor

            def is_connected(self):
                return True

            def close(self):
                pass

        connection = Connection()
        with patch.object(db, 'connect_to_mysql', return_value=(connection, None)):
            names, error = db.return_users_from_individuals()

        self.assertIsNone(error)
        self.assertEqual(names, ['Recent Player', 'Older Player', 'Never Played'])
        self.assertIn('LEFT JOIN BCSS_Players', connection.test_cursor.query)
        self.assertIn('MAX(p.date) DESC', connection.test_cursor.query)
        self.assertIn('MAX(p.date) IS NULL ASC', connection.test_cursor.query)


if __name__ == '__main__':
    unittest.main()
