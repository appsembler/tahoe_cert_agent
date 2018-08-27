from django.test import RequestFactory, TestCase
from ..views import DomainActivateView


class DomainActivateViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_missing_api_key(self):
        request = self.factory.post('/domain_activate/')
        response = DomainActivateView.as_view()(request)
        self.assertEqual(response.status_code, 403)

    def test_missing_domain(self):
        request = self.factory.post('/domain_activate/', HTTP_API_KEY='secret_key')
        response = DomainActivateView.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_invalid_domain(self):
        request = self.factory.post('/domain_activate/', HTTP_API_KEY='secret_key',
                                    data={'domain': '!!! '})
        response = DomainActivateView.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_simple_command(self):
        request = self.factory.post('/domain_activate/', HTTP_API_KEY='secret_key',
                                    data={'domain': "www.example.com"})
        with self.settings(ANSIBLE_CMD="true"):
            response = DomainActivateView.as_view()(request)
            self.assertEqual(response.status_code, 202)

    def test_failed_command(self):
        request = self.factory.post('/domain_activate/', HTTP_API_KEY='secret_key',
                                    data={'domain': "www.example.com"})
        with self.settings(ANSIBLE_CMD="false"):
            response = DomainActivateView.as_view()(request)
            self.assertEqual(response.status_code, 500)
