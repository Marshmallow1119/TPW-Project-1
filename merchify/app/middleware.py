from django.conf import settings
from django.shortcuts import render
import re

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Regex pattern to match static and media file URLs
        self.excluded_patterns = re.compile(r'^/(static|media)/')

    def __call__(self, request):
        # Skip the middleware if the request is for static or media files
        if self.excluded_patterns.match(request.path):
            return self.get_response(request)

        try:
            response = self.get_response(request)
        except Exception:
            # Render a custom 500 error page for unhandled exceptions
            return render(request, '500.html', status=500)

        # Render a custom 404 error page if the response status code is 404
        if response.status_code == 404:
            return render(request, '404.html', status=404)

        return response
