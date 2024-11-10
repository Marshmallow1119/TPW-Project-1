import os
from django.core.management.base import BaseCommand
from app.models import Artist
from django.core.files import File

class Command(BaseCommand):
    help = 'Adicionar artistas ao banco de dados'

    base_path = 'app/media/artists'  # Atualize com o caminho para as imagens
    artistas = [
        {
            "name": "Beyoncé",
            "description": "Cantora, compositora e atriz norte-americana, conhecida por suas performances e influência na cultura pop.",
            "image_path": "Beyonce.jpeg",
            "background_image_path": "beyonce_back.jpg"
        },
        {
            "name": "Jay-Z",
            "description": "Rapper, produtor musical e empresário norte-americano, um dos maiores nomes do hip-hop.",
            "image_path": "JayZ.jpeg",
            "background_image_path": "jayz_back.jpg"
        },
        {
            "name": "Olivia Rodrigo",
            "description": "Cantora e compositora norte-americana, conhecida por suas músicas de sucesso como 'Drivers License' e 'Good 4 U'.",
            "image_path": "olivia.jpg",
            "background_image_path": "olivia_back.png"
        },
        {
            "name": "Justin Bieber",
            "description": "Cantor e compositor canadense, que alcançou fama mundial ainda na adolescência.",
            "image_path": "JustinBiber.jpeg",
            "background_image_path": "justin_back.png"
        },
        {
            "name": "Sabrina Carpenter",
            "description": "Cantora, compositora e atriz norte-americana, conhecida por suas músicas pop e atuações na TV.",
            "image_path": "sabrina.jpg",
            "background_image_path": "sabrinabackground.jpg"
        },
        {
            "name": "Pink Floyd",
            "description": "Banda britânica de rock progressivo, conhecida por seus álbuns conceituais e shows inovadores.",
            "image_path": "pingfloyd.jpg",
            "background_image_path": "pink_back.png"
        },
        {
            "name": "Pedro Sampaio",
            "description": "DJ e produtor musical brasileiro, conhecido por seus sucessos no funk e música pop.",
            "image_path": "PedroSampaio.jpg",
            "background_image_path": "ps_back.jpg"
        },
        {
            "name": "Anitta",
            "description": "Cantora e compositora brasileira, conhecida por sua popularidade internacional e hits no reggaeton e funk.",
            "image_path": "anitta.png",
            "background_image_path": "anitta_back.png"
        },
        {
            "name": "Imagine Dragons",
            "description": "Banda norte-americana de rock, conhecida por seus sucessos como 'Radioactive' e 'Believer'.",
            "image_path": "imagine.jpg",
            "background_image_path": "imagine_back.jpg"
        },
        {
            "name": "The Weeknd",
            "description": "Cantor, compositor e produtor canadense, conhecido por suas músicas de sucesso e performances cativantes.",
            "image_path": "theweeknd.jpg",
            "background_image_path": "theweeknd_back.jpg"
        },
        {
            "name": "Arctic Monkeys",
            "description": "Banda britânica de rock, conhecida por seu som distinto e letras cativantes.",
            "image_path": "artic.jpg",
            "background_image_path": "arcticmonkeys.jpeg"
        },
    ]

    def handle(self, *args, **options):
        for artista in self.artistas:
            image_path = os.path.join(self.base_path, artista["image_path"])
            background_image_path = os.path.join(self.base_path, artista["background_image_path"])

            try:
                with open(image_path, "rb") as img_file, open(background_image_path, "rb") as bg_file:
                    artist, created = Artist.objects.get_or_create(
                        name=artista["name"],
                        defaults={
                            "description": artista["description"],
                            "image": File(img_file),
                            "background_image": File(bg_file)
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Artista '{artist.name}' adicionado com sucesso!"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Artista '{artist.name}' já existe."))

            except FileNotFoundError as e:
                self.stdout.write(self.style.ERROR(f"Erro ao adicionar '{artista['name']}': {str(e)}"))
