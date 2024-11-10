import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from app.models import Product, Vinil, CD, Clothing, Accessory, Size
from app.models import Artist, Company
from datetime import date

class Command(BaseCommand):
    help = 'Adiciona produtos para Anitta ao banco de dados'

    def handle(self, *args, **options):
        try:
            # Buscar instâncias do artista e da empresa
            artist = Artist.objects.get(name="Anitta")
            company = Company.objects.get(name="Warner Music")
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("Artista 'Anitta' não encontrado."))
            return
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR("Empresa 'Warner Music' não encontrada."))
            return

        # Caminho base para as imagens
        base_path = os.path.join(settings.MEDIA_ROOT, 'products/anitta')

        # Lista de produtos a serem adicionados
        products = [
            {
                "model": CD,
                "fields": {
                    "name": "Versions of Me CD",
                    "description": "CD do álbum 'Versions of Me' de Anitta",
                    "price": 39.90,
                    "image": "cd.jpg",
                    "stock": 100,
                    "category": "CD",
                    "genre": "Pop/Funk",
                    "releaseDate": date(2022, 4, 12),
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Anitta Caneca",
                    "description": "Caneca oficial com logo de Anitta",
                    "price": 24.90,
                    "image": "caneca.jpeg",
                    "stock": 150,
                    "category": "Accessory",
                    "material": "Porcelana",
                    "color": "Branco",
                    "size": "Único",
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Anitta Tot",
                    "description": "Tot oficial de Anitta",
                    "price": 24.90,
                    "image": "tot.jpg",
                    "stock": 150,
                    "category": "Accessory",
                    "material": "Pano",
                    "color": "Branco",
                    "size": "Único",
                },
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Anitta T-shirt Preta",
                    "description": "Camiseta oficial Preta de Anitta com estampa exclusiva",
                    "price": 79.90,
                    "image": "anittacamisola.png",
                    "category": "Clothing",
                    "color": "Preto",
                },
                "sizes": [
                    {"size": "M", "stock": 20},
                    {"size": "S", "stock": 25},
                    {"size": "L", "stock": 30},
                ]
            },
        ]

        def get_image_file(image_name):
            image_path = os.path.join(settings.MEDIA_ROOT, 'products/anitta', image_name)
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
