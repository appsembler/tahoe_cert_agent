from subprocess import CalledProcessError, STDOUT, Popen, PIPE
import logging
import re

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import validators.domain
from .permissions import APIKeyPermission
from django.conf import settings


log = logging.getLogger(__name__)
whitelist_pattern = re.compile("[^\.-_a-zA-Z0-9]")


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
            process = Popen(ansible_cmd, stdout=PIPE, stderr=STDOUT, shell=True)

            process.wait()
            if process.returncode != 0:
                log.error("Ansible exited with non zero return code!")
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except CalledProcessError as e:
            log.error(str(e))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_202_ACCEPTED)


domain_activate = DomainActivateView.as_view()
