import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from app.models import Product, Vinil, CD, Clothing, Accessory, Size
from app.models import Artist, Company
from datetime import date

class Command(BaseCommand):
    help = 'Adiciona produtos para Imagine Dragons ao banco de dados'

    def handle(self, *args, **options):
        try:
            # Buscar instâncias do artista e da empresa
            artist = Artist.objects.get(name="Imagine Dragons")
            company = Company.objects.get(name="Warner Music")
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("Artista 'Imagine Dragons' não encontrado."))
            return
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR("Empresa 'Interscope Records' não encontrada."))
            return


        # Lista de produtos a serem adicionados
        products = [
            {
                "model": Vinil,
                "fields": {
                    "name": "LOOM VINIL",
                    "description": "Vinil do álbum 'LOOM' de Imagine Dragons",
                    "price": 149.90,
                    "image": "vinil.jpg",
                    "stock": 50,
                    "category": "Vinyl",
                    "genre": "Alternative Rock",
                    "lpSize": "12\"",
                    "releaseDate": date(2021, 9, 3),
                },
            },
            {
                "model": CD,
                "fields": {
                    "name": "Live Imagine CD",
                    "description": "CD do álbum 'Evolve' de Imagine Dragons",
                    "price": 39.90,
                    "image": "cd.jpeg",
                    "stock": 100,
                    "category": "CD",
                    "genre": "Alternative Rock",
                    "releaseDate": date(2017, 6, 23),
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Imagine Dragons Chapéu",
                    "description": "Chapéu oficial com logo de Imagine Dragons",
                    "price": 19.90,
                    "image": "chapeu.jpg",
                    "stock": 150,
                    "category": "Accessory",
                    "material": "Algodão",
                    "color": "Preto",
                    "size": "Único",
                },
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Imagine Dragons T-shirt",
                    "description": "Camisola oficial preta de Imagine Dragons com estampa exclusiva",
                    "price": 69.90,
                    "image": "camisola.jpeg",
                    "category": "Clothing",
                    "color": "Preto",
                },
                "sizes": [
                    {"size": "S", "stock": 20},
                    {"size": "M", "stock": 30},
                    {"size": "L", "stock": 40},
                ]
            },
        ]

        def get_image_file(image_name):
            image_path = os.path.join(settings.MEDIA_ROOT, 'products/imagine', image_name)
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
