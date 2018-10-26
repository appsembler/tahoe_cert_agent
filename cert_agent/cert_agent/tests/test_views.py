
from datetime import datetime
from django.test import Client, RequestFactory, TestCase
from ..views import DomainActivateView, log_filename

from mock import patch


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

    @patch('cert_agent.views.log')
    def test_simple_command(self, mock_logger):
        request = self.factory.post('/domain_activate/', HTTP_API_KEY='secret_key',
                                    data={'domain': "www.example.com"})
        with self.settings(ANSIBLE_CMD="true"):
            response = DomainActivateView.as_view()(request)
            self.assertEqual(response.status_code, 202)
            mock_logger.debug.assert_called_with('Calling ansible script for domain www.example.com')

    @patch('cert_agent.views.log')
    def test_multiline_command(self, mock_logger):
        request = self.factory.post('/domain_activate/', HTTP_API_KEY='secret_key',
                                    data={'domain': "www.example.com"})
        with self.settings(ANSIBLE_CMD="echo 'one\ntwo\nthree'"):
            response = DomainActivateView.as_view()(request)
            self.assertEqual(response.status_code, 202)
            # mock logger only remembers the last one it was called with
            mock_logger.debug.assert_called_with('Calling ansible script for domain www.example.com')

    @patch('cert_agent.views.log')
    def test_failed_command(self, mock_logger):
        request = self.factory.post('/domain_activate/', HTTP_API_KEY='secret_key',
                                    data={'domain': "www.example.com"})
        with self.settings(ANSIBLE_CMD="false"):
            response = DomainActivateView.as_view()(request)
            self.assertEqual(response.status_code, 500)
            mock_logger.error.assert_called_with("Ansible exited with non zero return code!")


class TestHelpers(TestCase):
    def test_log_filename(self):
        d = datetime(year=2018, month=1, day=1, hour=12, minute=0, second=0)
        domain = "foo.example.com"
        r = log_filename(domain, now=d)
        self.assertEqual(r, "2018-01-01T12:00:00-foo.example.com.log")


class SmokeTestViews(TestCase):
    def test_smoketest(self):
        c = Client()
        # fail by default
        response = c.get('/smoketest/')
        self.assertFalse('PASS' in str(response.content))
        self.assertEqual(response.status_code, 500)
        # set the API_SECRET_KEY to make it pass
        with self.settings(API_SECRET_KEY='not the default'):
            response = c.get('/smoketest/')
            self.assertTrue('PASS' in str(response.content))
            self.assertEqual(response.status_code, 200)
