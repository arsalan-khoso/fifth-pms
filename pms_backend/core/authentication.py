from rest_framework import authentication, exceptions
from .models import APIKey

class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication using API key in header
    """
    def authenticate(self, request):
        api_key_header = request.META.get('HTTP_X_API_KEY')
        if not api_key_header:
            return None

        try:
            api_key = APIKey.objects.get(key=api_key_header, is_active=True)
            return (None, api_key)  # Return None for user, and api_key as auth
        except (APIKey.DoesNotExist, ValueError):
            raise exceptions.AuthenticationFailed('Invalid API Key')

    def authenticate_header(self, request):
        return 'API-Key'