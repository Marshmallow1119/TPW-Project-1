from django.conf import settings
from django.shortcuts import render
import re

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_patterns = re.compile(r'^/(static|media)/')

    def __call__(self, request):
        if self.excluded_patterns.match(request.path):
            return self.get_response(request)

        try:
            response = self.get_response(request)
        except Exception:
            return render(request, '500.html', status=500)

        if response.status_code == 404 or response.status_code == 403:
            return render(request, '404.html', status=404)

        return response
