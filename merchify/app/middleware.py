from django.http import HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            # Log the error if needed and render a custom 500 page
            return render(request, '500.html', status=500)

        if response.status_code == 404:
            return render(request, '404.html', status=404)

        return response