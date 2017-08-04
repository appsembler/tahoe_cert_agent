from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import validators.domain
from .permissions import APIKeyPermission


class DomainActivateView(APIView):
    permission_classes = (APIKeyPermission,)

    def post(self, request, format=None):
        domain = request.data.get('domain')
        if not domain or validators.domain(domain):
            return Response("Please enter a valid domain", status=status.HTTP_400_BAD_REQUEST)

        print "Calling ansible script for domain {}".format(domain)
        return Response(status=status.HTTP_202_ACCEPTED)

domain_activate = DomainActivateView.as_view()
