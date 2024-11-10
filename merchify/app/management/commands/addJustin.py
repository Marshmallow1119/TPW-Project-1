import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from app.models import Product, Vinil, CD, Clothing, Accessory, Size
from app.models import Artist, Company
from datetime import date

class Command(BaseCommand):
    help = 'Adiciona produtos para Justin Bieber ao banco de dados'

    def handle(self, *args, **options):
        try:
            # Buscar instâncias do artista e da empresa
            artist = Artist.objects.get(name="Justin Bieber")
            company = Company.objects.get(name="Warner Music")
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("Artista 'Justin Bieber' não encontrado."))
            return
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR("Empresa 'Def Jam Recordings' não encontrada."))
            return

        

        # Lista de produtos a serem adicionados
        products = [
            {
                "model": Vinil,
                "fields": {
                    "name": "Justice Vinyl",
                    "description": "Vinil do álbum 'Justice' de Justin Bieber",
                    "price": 159.90,
                    "image": "vinil.jpeg",
                    "stock": 50,
                    "category": "Vinyl",
                    "genre": "Pop",
                    "lpSize": "12\"",
                    "releaseDate": date(2021, 3, 19),
                },
            },
            {
                "model": CD,
                "fields": {
                    "name": "Purpose CD",
                    "description": "CD do álbum 'Purpose' de Justin Bieber",
                    "price": 39.90,
                    "image": "cd.jpeg",
                    "stock": 80,
                    "category": "CD",
                    "genre": "Pop/R&B",
                    "releaseDate": date(2015, 11, 13),
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Justin Bieber Boné",
                    "description": "Boné oficial de Justin Bieber",
                    "price": 29.90,
                    "image": "bone.jpeg",
                    "stock": 100,
                    "category": "Accessory",
                    "material": "Algodão",
                    "color": "Preto",
                    "size": "Único",
                },
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Justin Bieber T-shirt",
                    "description": "Camiseta oficial de Justin Bieber com estampa exclusiva",
                    "price": 69.90,
                    "image": "camisola.jpeg",
                    "category": "Clothing",
                    "color": "Preto",
                },
                "sizes": [
                    {"size": "S", "stock": 25},
                    {"size": "M", "stock": 35},
                    {"size": "L", "stock": 40},
                ]
            },
        ]

        def get_image_file(image_name):
            image_path = os.path.join(settings.MEDIA_ROOT, 'products/justin', image_name)
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


