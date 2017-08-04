from django.conf import settings
from rest_framework import permissions


class APIKeyPermission(permissions.BasePermission):
    message = 'Invalid or missing API Key.'

    def has_permission(self, request, view):
        api_key = request.META.get('HTTP_API_KEY', '')
        return api_key == settings.APPSEMBLER_SECRET_KEY
