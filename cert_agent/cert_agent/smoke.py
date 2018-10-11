from smoketest import SmokeTest
from django.conf import settings


class SettingsTest(SmokeTest):
    def test_api_secret_key_is_set(self):
        """ API_SECRET_KEY needs to be set via an environment variable
        if it has not, we get the default "secret_key" value.

        This test makes sure that that doesn't happen in production."""
        self.assertNotEqual(settings.API_SECRET_KEY, 'secret_key')

    # TODO: smoketest to check that the ansible_playbook command
    # exists on the machine and is executable by the user this
    # is running as
