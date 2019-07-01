import unittest

from ponthe import app

class ProjectTests(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        pass

    def test_login_page(self):
        response = self.app.get('/v1/login', follow_redirects=True)
        self.assertIn(b'Connecte-toi !', response.data)


if __name__ == "__main__":
    unittest.main()
