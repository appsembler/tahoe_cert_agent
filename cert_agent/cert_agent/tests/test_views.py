from django.test import TestCase
from django.test.client import Client


class IndexTest(TestCase):
    def test_index(self):
        """ dummy test to get things started

        the index page just serves up a 404
        """
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 404)
