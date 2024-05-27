import unittest
from app import app

class SearchTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_search_route(self):
        response = self.client.get('/search')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Search Page', response.data)

if __name__ == '__main__':
    unittest.main()