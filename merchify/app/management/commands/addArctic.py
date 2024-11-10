import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from app.models import Product, Vinil, CD, Clothing, Accessory, Size
from app.models import Artist, Company
from datetime import date

class Command(BaseCommand):
    help = 'Adiciona produtos para Olivia Rodrigo ao banco de dados'

    def handle(self, *args, **options):
        try:
            artist = Artist.objects.get(name="Arctic Monkeys")
            company = Company.objects.get(name="Capitol Records")
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("Artista 'The Weeknd' não encontrado."))
            return
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR("Empresa 'Sony Music' não encontrada."))
            return

        # Caminho base para as imagens
        base_path = os.path.join(settings.MEDIA_ROOT, 'products/theweekend')

        # Lista de produtos a serem adicionados
        products = [
            {
                "model": Vinil,
                "fields": {
                    "name": "AM - Vinyl",
                    "description": "Vinil do álbum 'AM' de Arctic Monkeys",
                    "price": 44.99,
                    "image": "am.jpeg",
                    "stock": 120,
                    "category": "Alternative",
                    "genre": "Alternative",
                    "releaseDate": date(2010, 5, 21),
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Poster Arctic Monkeys",
                    "description": "Poster Oficial dos Arctic Monkeys",
                    "price": 19.90,
                    "image": "poster2.jpg",
                    "stock": 150,
                    "category": "Accessory",
                    "material": "Papel",
                    "color": "Preto",
                    "size": "Único",
                },
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Arctic Monkeys T-shirt",
                    "description": "Camisola Branca oficial de Arctic Monkeys com logo da banda",
                    "price": 79.90,
                    "image": "tshirtarctic.jpeg",
                    "category": "Clothing",
                    "color": "Preto",
                },
                "sizes": [
                    {"size": "S", "stock": 20},
                    {"size": "M", "stock": 25},
                    {"size": "XL", "stock": 30},
                ]
            },
            {
                "model": CD,
                "fields": {
                    "name": "The Car CD",
                    "description": "CD do álbum 'The Car' de Arctic Monkeys",
                    "price": 25.90,
                    "image": "cd2.jpg",
                    "stock": 100,
                    "category": "Alternative",
                    "genre": "Alternative",
                    "releaseDate": date(2021, 12, 21),
                },
            },
        ]

        def get_image_file(image_name):
            image_path = os.path.join(settings.MEDIA_ROOT, 'products/', image_name)
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
