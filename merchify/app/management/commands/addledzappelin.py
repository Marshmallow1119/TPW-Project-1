import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from app.models import Product, Vinil, CD, Clothing, Accessory, Size
from app.models import Artist, Company
from datetime import date

class Command(BaseCommand):
    help = 'Adiciona produtos para Led Zeppelin ao banco de dados'

    def handle(self, *args, **options):
        try:
            # Buscar instâncias do artista e da empresa
            artist = Artist.objects.get(name="Led Zeppelin")
            company = Company.objects.get(name="Atlantic Records")
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("Artista 'Led Zeppelin' não encontrado."))
            return
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR("Empresa 'Atlantic Records' não encontrada."))
            return

        # Caminho base para as imagens
        base_path = os.path.join(settings.MEDIA_ROOT, 'products/ledzeppelin')

        # Lista de produtos a serem adicionados
        products = [
            {
                "model": Vinil,
                "fields": {
                    "name": "Led Zeppelin IV Vinyl",
                    "description": "Vinil clássico do álbum 'Led Zeppelin IV'",
                    "price": 159.90,
                    "image": "vinil.jpeg",
                    "stock": 40,
                    "category": "Vinyl",
                    "genre": "Rock",
                    "lpSize": "12\"",
                    "releaseDate": date(1971, 11, 8),
                },
            },
            {
                "model": CD,
                "fields": {
                    "name": "Physical Graffiti CD",
                    "description": "CD do álbum duplo 'Physical Graffiti' de Led Zeppelin",
                    "price": 49.90,
                    "image": "cd.jpeg",
                    "stock": 70,
                    "category": "CD",
                    "genre": "Rock",
                    "releaseDate": date(1975, 2, 24),
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Led Zeppelin Keychain",
                    "description": "Chaveiro oficial com logo de Led Zeppelin",
                    "price": 24.90,
                    "image": "chapeu.jpeg",
                    "stock": 200,
                    "category": "Accessory",
                    "material": "Metal",
                    "color": "Silver",
                    "size": "Standard",
                },
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Led Zeppelin T-shirt Classic Logo",
                    "description": "T-shirt preta com o logo clássico de Led Zeppelin",
                    "price": 69.90,
                    "image": "camisolaled.jpg",
                    "category": "Clothing",
                    "color": "Black",
                },
                "sizes": [
                    {"size": "S", "stock": 20},
                    {"size": "M", "stock": 30},
                    {"size": "L", "stock": 40},
                ]
            },
        ]

        def get_image_file(image_name):
            image_path = os.path.join(settings.MEDIA_ROOT, 'products/ledzeppelin', image_name)
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
