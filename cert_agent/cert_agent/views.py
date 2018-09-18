from datetime import datetime
from subprocess import CalledProcessError, STDOUT, Popen, PIPE
import logging
import os
import re

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import validators.domain
from .permissions import APIKeyPermission
from django.conf import settings


log = logging.getLogger(__name__)
whitelist_pattern = re.compile("[^\.-_a-zA-Z0-9]")


def log_filename(domain, now=None):
    """ ansible log file name. timestamp and domain to make it easy to find

    expects `domain` to already be sanitized.
    """
    if not now:
        now = datetime.utcnow()
    return "{}-{}.log".format(now.strftime("%Y-%m-%dT%X"), domain)


class DomainActivateView(APIView):
    permission_classes = (APIKeyPermission,)

    def post(self, request, format=None):
        domain = request.data.get('domain')
        if not domain or not validators.domain(domain):
            return Response("Please enter a valid domain", status=status.HTTP_400_BAD_REQUEST)

        log.debug("Calling ansible script for domain {}".format(domain))

        try:
            # remove any potentially unsafe chars from `domain` before passing it to the shell
            domain = whitelist_pattern.sub("", domain)
            ansible_cmd = settings.ANSIBLE_CMD + " --extra-vars 'letsencrypt_single_cert=%s'" % domain
            my_env = os.environ.copy()
            my_env['ANSIBLE_LOG_PATH'] = os.path.join(settings.ANSIBLE_LOG_DIR, log_filename(domain))
            process = Popen(ansible_cmd, stdout=PIPE, stderr=STDOUT, shell=True,
                            env=my_env)
            process.wait()
            if process.returncode != 0:
                log.error("Ansible exited with non zero return code!")
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except CalledProcessError as e:
            log.error(str(e))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_202_ACCEPTED)


domain_activate = DomainActivateView.as_view()
