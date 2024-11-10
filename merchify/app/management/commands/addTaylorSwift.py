import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from app.models import Product, Vinil, CD, Clothing, Accessory, Size
from app.models import Artist, Company
from datetime import date

class Command(BaseCommand):
    help = 'Adiciona produtos para Taylor Swift ao banco de dados'

    def handle(self, *args, **options):
        try:
            # Buscar instâncias do artista e da empresa
            artist = Artist.objects.get(name="Taylor Swift")
            company = Company.objects.get(name="Republic Records")
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("Artista 'Taylor Swift' não encontrado."))
            return
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR("Empresa 'Republic Records' não encontrada."))
            return

        # Caminho base para as imagens
        base_path = os.path.join(settings.MEDIA_ROOT, 'products/taylor')

        # Lista de produtos a serem adicionados
        products = [
            {
                "model": Vinil,
                "fields": {
                    "name": "Midnights Vinyl",
                    "description": "Vinil do álbum 'Midnights' de Taylor Swift",
                    "price": 149.90,
                    "image": "taylor1989.jpg",
                    "stock": 30,
                    "category": "Vinyl",
                    "genre": "Pop",
                    "lpSize": "12\"",
                    "releaseDate": date(2022, 10, 21),
                },
            },
            {
                "model": CD,
                "fields": {
                    "name": "1989 (Taylor's Version) CD",
                    "description": "CD do álbum '1989 (Taylor's Version)' de Taylor Swift",
                    "price": 39.90,
                    "image": "cdtaylor.jpg",
                    "stock": 60,
                    "category": "CD",
                    "genre": "Pop",
                    "releaseDate": date(2023, 10, 27),
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Taylor Swift Mega Caneca",
                    "description": "Caneca oficial de Taylor Swift",
                    "price": 19.90,
                    "image": "canecataylor.jpg",
                    "stock": 150,
                    "category": "Accessory",
                    "material": "Porcelana",
                    "color": "Branco",
                    "size": "Standard",
                },
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Taylor Swift Red T-shirt",
                    "description": "T-shirt oficial vermelha de Taylor Swift",
                    "price": 59.90,
                    "image": "taylortshirt.png",
                    "category": "Clothing",
                    "color": "Preta",
                },
                "sizes": [
                    {"size": "S", "stock": 15},
                    {"size": "M", "stock": 20},
                    {"size": "L", "stock": 25},
                ]
            },
        ]

        def get_image_file(image_name):
            image_path = os.path.join(settings.MEDIA_ROOT, 'products/taylor', image_name)
            if os.path.exists(image_path):
                return ImageFile(open(image_path, 'rb'), name=os.path.basename(image_name))
            else:
                self.stdout.write(self.style.WARNING(f"Imagem '{image_name}' não encontrada em '{image_path}'."))
                return None

        # Adicionar produtos ao banco de dados
        for product_data in products:
            model = product_data["model"]
            fields = product_data["fields"]
            fields["artist"] = artist
            fields["company"] = company

            image_file = get_image_file(fields["image"])
            if image_file:
                fields["image"] = image_file

            try:
                product, created = model.objects.get_or_create(
                    name=fields["name"],
                    defaults=fields,
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Produto '{product.name}' adicionado com sucesso!"))
                else:
                    self.stdout.write(self.style.WARNING(f"Produto '{product.name}' já existe."))

                # Adicionar tamanhos para produtos de roupas
                if model == Clothing:
                    for size_data in product_data.get("sizes", []):
                        size, size_created = Size.objects.get_or_create(
                            clothing=product,
                            size=size_data["size"],
                            defaults={"stock": size_data["stock"]},
                        )
                        if size_created:
                            self.stdout.write(self.style.SUCCESS(f"Tamanho '{size.size}' adicionado para '{product.name}'."))
                        else:
                            self.stdout.write(self.style.WARNING(f"Tamanho '{size.size}' para '{product.name}' já existe."))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao adicionar '{fields['name']}': {str(e)}"))

        self.stdout.write(self.style.SUCCESS("Processo de adição de produtos concluído."))
