import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from app.models import Product, Vinil, CD, Clothing, Accessory, Size
from app.models import Artist, Company
from datetime import date

class Command(BaseCommand):
    help = 'Adiciona produtos para Sabrina Carpenter ao banco de dados'

    def handle(self, *args, **options):
        try:
            # Buscar instâncias do artista e da empresa
            artist = Artist.objects.get(name="Sabrina Carpenter")
            company = Company.objects.get(name="Interscope")
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("Artista 'Sabrina Carpenter' não encontrado."))
            return
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR("Empresa 'Interscope' não encontrada."))
            return

        # Caminho base para as imagens
        base_path = os.path.join(settings.MEDIA_ROOT, 'products/sabrina')
        
        # Lista de produtos a serem adicionados
        products = [
            {
                "model": Vinil,
                "fields": {
                    "name": "Emails I Can't Send Vinyl",
                    "description": "Vinil do álbum 'Emails I Can't Send' de Sabrina Carpenter",
                    "price": 139.90,
                    "image": "expresso.jpeg",
                    "stock": 20,
                    "category": "Vinyl",
                    "genre": "Pop",
                    "lpSize": "12\"",
                    "releaseDate": date(2022, 7, 15),
                },
            },
            {
                "model": CD,
                "fields": {
                    "name": "Singular Act II CD",
                    "description": "CD do álbum 'Singular Act II' de Sabrina Carpenter",
                    "price": 29.90,
                    "image": "sabrina.png",
                    "stock": 50,
                    "category": "CD",
                    "genre": "Pop",
                    "releaseDate": date(2019, 7, 19),
                },
            },
            {
                "model": Accessory,
                "fields": {
                    "name": "Sabrina Carpenter Chávena",
                    "description": "Chaveiro oficial de Sabrina Carpenter",
                    "price": 14.90,
                    "image": "chavena.png",
                    "stock": 100,
                    "category": "Accessory",
                    "material": "Metal",
                    "color": "Silver",
                    "size": "Standard",
                },
            },
            {
                "model": Clothing,
                "fields": {
                    "name": "Sabrina Carpenter T-shirt Black",
                    "description": "T-shirt oficial preta de Sabrina Carpenter",
                    "price": 49.90,
                    "image": "camisola.png",
                    "category": "Clothing",
                    "color": "Black",
                },
                "sizes": [
                    {"size": "S", "stock": 20},
                    {"size": "M", "stock": 25},
                    {"size": "L", "stock": 30},
                ]
            },
        ]

        def get_image_file(image_name):
            image_path = os.path.join(settings.MEDIA_ROOT, 'products/sabrina', image_name)
            if os.path.exists(image_path):
                # Defina o nome do arquivo explicitamente
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
