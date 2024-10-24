import os
import django

# Setup Django environment (ensure the script runs within Django context)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'merchify.settings')  # Replace 'your_project' with your project name
django.setup()

# Now you can import models
from app.models import Artist  # Replace 'app' with your actual app name

def fix_image_paths():
    for artist in Artist.objects.all():
        if artist.image.name.startswith('artists/artists/'):
            # Remove the duplicate 'artists/' in the path
            artist.image.name = artist.image.name.replace('artists/artists/', 'artists/')
            artist.save()
            print(f"Updated: {artist.name}, New Path: {artist.image.name}")

if __name__ == "__main__":
    fix_image_paths()
