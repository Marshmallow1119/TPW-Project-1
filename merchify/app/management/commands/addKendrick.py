import os
from django.core.management.base import BaseCommand
from app.models import Product, Vinil, CD, Clothing, Accessory, Size  # Import Size model
from app.models import Artist  # Assuming Artist model is in artists app
from app.models import Company  # Assuming Company model is in companies app
from datetime import date

class Command(BaseCommand):
    help = 'Adds Kendrick Lamar products to the database'

    def handle(self, *args, **options):
        # Fetch the artist and company instances
        artist = Artist.objects.get(name="Kendrick Lamar")
        company = Company.objects.get(name="Interscope")

        # Define base path for images
        base_path = 'products/kendricklamar/'  # Update based on MEDIA_ROOT path

        # List of products to be added with type-specific data
        products = [
            {
                "model": Vinil,
                "fields": {
                    "name": "Damn Vinyl",
                    "description": "Vinyl album of Kendrick Lamar's 'Damn'",
                    "price": 149.90,
                    "image": "damnVinyl.jpg",
                    "stock": 20,
                    "category": "Vinyl",
                    "genre": "Hip-Hop",
                    "lpSize": "12\"",
                    "releaseDate": date(2017, 4, 14),
                },
            },
            {
                "model": Vinil,
                "fields": {
                    "name": "Good Kid Vinyl",
                    "description": "Vinyl album of Kendrick Lamar's 'Good Kid, M.A.A.D City'",
                    "price": 129.90,
                    "image": "goodKid.jpg",
                    "stock": 15,
                    "category": "Vinyl",
                    "genre": "Hip-Hop",
                    "lpSize": "12\"",
                    "releaseDate": date(2012, 10, 22),
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Kendrick Lamar Mug 1",
                    "description": "Official Kendrick Lamar mug",
                    "price": 19.90,
                    "image": "mug1.jpg",
                    "stock": 50,
                    "category": "Accessory",
                    "material": "Ceramic",
                    "color": "White",
                    "size": "Standard",
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Kendrick Lamar Mug 2",
                    "description": "Official Kendrick Lamar mug",
                    "price": 19.90,
                    "image": "mug2.jpeg",
                    "stock": 50,
                    "category": "Accessory",
                    "material": "Ceramic",
                    "color": "White",
                    "size": "Standard",
                },
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Kendrick Lamar T-shirt 1",
                    "description": "Official Kendrick Lamar T-shirt",
                    "price": 79.90,
                    "image": "tshirt1.jpg",
                    "category": "Clothing",
                    "color": "Black",
                },
                "sizes": [
                    {"size": "L", "stock": 30}
                ]
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Kendrick Lamar T-shirt 2",
                    "description": "Official Kendrick Lamar T-shirt",
                    "price": 89.90,
                    "image": "tshirt2.jpg",
                    "category": "Clothing",
                    "color": "White",
                },
                "sizes": [
                    {"size": "M", "stock": 25}
                ]
            },
        ]

        # Iterate over the products and add them
        for product_data in products:
            model = product_data["model"]
            fields = product_data["fields"]
            fields["artist"] = artist
            fields["company"] = company
            fields["image"] = os.path.join(base_path, fields["image"])

            # Create the product in the database
            product, created = model.objects.get_or_create(
                name=fields["name"],
                defaults=fields,
            )

            # Output the result
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added {product.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"{product.name} already exists"))

            # If the product is Clothing, create Size instances
            if model == Clothing:
                for size_data in product_data.get("sizes", []):
                    size_data["clothing"] = product  # Set the foreign key
                    size, size_created = Size.objects.get_or_create(
                        clothing=product,
                        size=size_data["size"],
                        defaults={"stock": size_data["stock"]},
                    )
                    if size_created:
                        self.stdout.write(self.style.SUCCESS(f"Added size {size.size} for {product.name}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Size {size.size} for {product.name} already exists"))

