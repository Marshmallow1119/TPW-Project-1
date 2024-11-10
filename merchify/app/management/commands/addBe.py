import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from app.models import Product, Vinil, CD, Clothing, Accessory, Size
from app.models import Artist, Company
from datetime import date

class Command(BaseCommand):
    help = 'Adiciona produtos para Beyoncé ao banco de dados'

    def handle(self, *args, **options):
        try:
            # Buscar instâncias do artista e da empresa
            artist = Artist.objects.get(name="Beyoncé")
            company = Company.objects.get(name="Republic Records")
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("Artista 'Beyoncé' não encontrado."))
            return
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR("Empresa 'Parkwood Entertainment' não encontrada."))
            return


        # Lista de produtos a serem adicionados
        products = [
            {
                "model": Vinil,
                "fields": {
                    "name": "Renaissance Vinil",
                    "description": "Vinil do álbum 'Renaissance' de Beyoncé",
                    "price": 149.90,
                    "image": "renaissance-beyonce.jpg",
                    "stock": 100,
                    "category": "Vinyl",
                    "genre": "Pop/R&B",
                    "releaseDate": date(2022, 7, 29),
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Beyoncé Tote Bag",
                    "description": "Bolsa oficial de Beyoncé com logo 'Beyoncé'",
                    "price": 49.90,
                    "image": "tot.jpeg",
                    "stock": 200,
                    "category": "Accessory",
                    "material": "Algodão",
                    "color": "Branco",
                    "size": "Único",
                },
            },
            {
                "model": CD,
                "fields": {
                    "name": "Beyonce R&B CD",
                    "description": "CD do álbum 'Renaissance' de Beyoncé",
                    "price": 39.90,
                    "image": "cd.jpg",
                    "stock": 80,
                    "category": "CD",
                    "genre": "Pop/R&B",
                    "releaseDate": date(2015, 11, 13),
                },
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Beyoncé T-shirt Preta",
                    "description": "Camiseta preta oficial de Beyoncé com estampa do álbum 'Renaissance'",
                    "price": 89.90,
                    "image": "camisola.jpg",
                    "category": "Clothing",
                    "color": "Preto",
                },
                "sizes": [
                    {"size": "XS", "stock": 20},
                    {"size": "S", "stock": 25},
                    {"size": "L", "stock": 30},
                ]
            },
        ]

        def get_image_file(image_name):
            image_path = os.path.join(settings.MEDIA_ROOT, 'products/Beyonce', image_name)
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
