import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from app.models import Product, Vinil, CD, Clothing, Accessory, Size
from app.models import Artist, Company
from datetime import date

class Command(BaseCommand):
    help = 'Adiciona produtos para Pedro Sampaio ao banco de dados'

    def handle(self, *args, **options):
        try:
            # Buscar instâncias do artista e da empresa
            artist = Artist.objects.get(name="Pedro Sampaio")
            company = Company.objects.get(name="Atlantic Records")
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("Artista 'Pedro Sampaio' não encontrado."))
            return
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR("Empresa 'Warner Music Brazil' não encontrada."))
            return

        # Caminho base para as imagens
        base_path = os.path.join(settings.MEDIA_ROOT, 'products/pedrosampaio')

        # Lista de produtos a serem adicionados
        products = [
            {
                "model": CD,
                "fields": {
                    "name": "Pedro Sampaio CD",
                    "description": "CD com os maiores sucessos de Pedro Sampaio",
                    "price": 34.90,
                    "image": "cdpedro.jpeg",
                    "stock": 80,
                    "category": "CD",
                    "genre": "Funk",
                    "releaseDate": date(2023, 5, 15),
                },
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Pedro Sampaio Camiseta Branca",
                    "description": "Camiseta oficial branca de Pedro Sampaio com estampa exclusiva",
                    "price": 79.90,
                    "image": "sampaio.jpeg",
                    "category": "Clothing",
                    "color": "Branco",
                },
                "sizes": [
                    {"size": "M", "stock": 25},
                    {"size": "S", "stock": 30},
                    {"size": "L", "stock": 35},
                ]
            },
        ]

        def get_image_file(image_name):
            image_path = os.path.join(settings.MEDIA_ROOT, 'products/pedrosampaio', image_name)
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
