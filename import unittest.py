import unittest
from app import app

class SkyCastTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SkyCast', response.data)
        self.assertIn(b'Get Your Forecast', response.data)

    def test_search_route(self):
        response = self.app.get('/search')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SkyCast', response.data)
        self.assertIn(b'Search by City or Zip Code', response.data)

    def test_results_route_invalid_location(self):
        response = self.app.post('/results', data={'location': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"The &#39;location&#39; field is required.", response.data)

    def test_results_route_valid_city(self):
        response = self.app.post('/results', data={'location': 'London', 'units': 'metric'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'London', response.data)

if __name__ == '__main__':
    unittest.main()

