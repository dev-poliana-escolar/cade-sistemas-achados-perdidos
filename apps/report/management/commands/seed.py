from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils import timezone

from apps.category.models import Categoria
from apps.color.models import Cor
from apps.items.models import Item
from apps.report.models import Reporte


class Command(BaseCommand):
    help = "Popula o banco com dados iniciais"
    
    def handle(self, *args, **kwargs):

        if Item.objects.exists():
            self.stdout.write(
                self.style.WARNING("Banco já possui dados. Seed ignorado.")
            )
            return
         
        self.stdout.write(self.style.NOTICE("Criando categorias..."))

        categorias = {}
        for nome in [
            "Documento",
            "Eletrônico",
            "Mochila",
            "Chave",
            "Vestuário",
        ]:
            categorias[nome], _ = Categoria.objects.get_or_create(nome=nome)

        self.stdout.write(self.style.NOTICE("Criando cores..."))

        cores = {}
        for nome in [
            "Preto",
            "Branco",
            "Azul",
            "Cinza",
            "Vermelho",
        ]:
            cores[nome], _ = Cor.objects.get_or_create(nome=nome)

        self.stdout.write(self.style.NOTICE("Criando administrador..."))

        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@cade.local",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "Administrador criado.\n"
                    "Usuário: admin\n"
                    "Senha: admin123"
                )
            )
        else:
            self.stdout.write("Administrador já existe.")

        self.stdout.write(self.style.NOTICE("Criando itens..."))

        self.stdout.write(self.style.NOTICE("Criando 10 itens em estoque (encontrados)..."))
        itens_encontrados_data = [
            ("Mochila Dell preta para notebook 15.6", "Mochila", "Preto", "Biblioteca"),
            ("Garrafa de água metálica azul 500ml", "Vestuário", "Azul", "Quadra de Esportes"),
            ("Caderno universitário capa preta 10 matérias", "Documento", "Preto", "Bloco B"),
            ("Fone Bluetooth Redmi Airdots preto com case", "Eletrônico", "Preto", "Cantina"),
            ("Molho de chaves com fita azul e 2 chaves", "Chave", "Azul", "Estacionamento"),
            ("Calculadora Científica Casio FX-82MS", "Eletrônico", "Cinza", "Laboratório 3"),
            ("Casaco de frio Adidas preto tamanho G", "Vestuário", "Preto", "Auditório"),
            ("Carteira de identidade (RG) em nome de Maria Clara", "Documento", "Branco", "Guarita"),
            ("Carregador de iPhone com cabo branco", "Eletrônico", "Branco", "Biblioteca - Sala de Estudos"),
            ("Guarda-chuva dobrável vermelho", "Vestuário", "Vermelho", "Entrada Principal"),
        ]
        
        for desc, cat_nome, cor_nome, local in itens_encontrados_data:
            item, _ = Item.objects.get_or_create(
                descricao=desc,
                defaults={
                    "categoria": categorias[cat_nome],
                    "cor": cores[cor_nome],
                    "status": Item.Status.NO_ESTOQUE,
                    "dados_sensiveis": cat_nome == "Documento",
                },
            )
            Reporte.objects.get_or_create(
                usuario=admin,
                item=item,
                defaults={
                    "tipo": Reporte.Tipo.ENCONTRADO,
                    "data": timezone.now(),
                    "local": local,
                    "observacoes": "Encontrado e entregue na recepção.",
                },
            )

        # --- 10 ITENS PERDIDOS ---
        self.stdout.write(self.style.NOTICE("Criando 10 itens perdidos..."))
        itens_perdidos_data = [
            ("Mochila Targus preta com chaveiro de Star Wars", "Mochila", "Preto", "Bloco A"),
            ("Smartphone Samsung Galaxy A52 preto", "Eletrônico", "Preto", "Pátio Central"),
            ("Carteira de motorista (CNH) em nome de Lucas Santos", "Documento", "Branco", "Estacionamento"),
            ("Fone JBL Tune 510BT preto", "Eletrônico", "Preto", "Biblioteca"),
            ("Casaco de moletom cinza com capuz", "Vestuário", "Cinza", "Quadra de Esportes"),
            ("Molho de chaves com chaveiro de couro preto", "Chave", "Preto", "Bloco C"),
            ("Garrafa térmica azul 750ml", "Vestuário", "Azul", "Cantina"),
            ("Carregador de notebook Dell 65W preto", "Eletrônico", "Preto", "Laboratório 1"),
            ("Relógio de pulso Casio digital preto", "Eletrônico", "Preto", "Campo de Futebol"),
            ("Sombrinha preta pequena dobrável", "Vestuário", "Preto", "Corredor Principal"),
        ]
        
        for desc, cat_nome, cor_nome, local in itens_perdidos_data:
            item, _ = Item.objects.get_or_create(
                descricao=desc,
                defaults={
                    "categoria": categorias[cat_nome],
                    "cor": cores[cor_nome],
                    "status": Item.Status.PERDIDO,
                    "dados_sensiveis": cat_nome == "Documento",
                },
            )
            Reporte.objects.get_or_create(
                usuario=admin,
                item=item,
                defaults={
                    "tipo": Reporte.Tipo.PERDIDO,
                    "data": timezone.now(),
                    "local": local,
                    "observacoes": "Usuário relatou perda recente.",
                },
            )
            
            
        mochila, _ = Item.objects.get_or_create(
            descricao="Mochila Nike preta com chaveiro azul",
            defaults={
                "categoria": categorias["Mochila"],
                "cor": cores["Preto"],
                "status": Item.Status.NO_ESTOQUE,
                "dados_sensiveis": False,
            },
        )

        carteira, _ = Item.objects.get_or_create(
            descricao="Carteira estudantil IFRN",
            defaults={
                "categoria": categorias["Documento"],
                "cor": cores["Branco"],
                "status": Item.Status.PERDIDO,
                "dados_sensiveis": True,
            },
        )

        fone, _ = Item.objects.get_or_create(
            descricao="Fone JBL Tune 520BT",
            defaults={
                "categoria": categorias["Eletrônico"],
                "cor": cores["Preto"],
                "status": Item.Status.AGUARDANDO_ENTREGA,
                "dados_sensiveis": False,
            },
        )

        self.stdout.write(self.style.NOTICE("Criando reportes..."))

        Reporte.objects.get_or_create(
            usuario=admin,
            item=mochila,
            defaults={
                "tipo": Reporte.Tipo.ENCONTRADO,
                "data": timezone.now(),
                "local": "Bloco A",
                "observacoes": "Encontrada próxima ao laboratório.",
            },
        )

        Reporte.objects.get_or_create(
            usuario=admin,
            item=carteira,
            defaults={
                "tipo": Reporte.Tipo.PERDIDO,
                "data": timezone.now(),
                "local": "Biblioteca",
                "observacoes": "Perdida durante a manhã.",
            },
        )

        Reporte.objects.get_or_create(
            usuario=admin,
            item=fone,
            defaults={
                "tipo": Reporte.Tipo.ENCONTRADO,
                "data": timezone.now(),
                "local": "Cantina",
                "observacoes": "Encontrado sobre uma mesa.",
            },
        )
                
        self.stdout.write(
            self.style.SUCCESS("\nSeed executado com sucesso!")
        )
        
        self.stdout.write(self.style.NOTICE("\nExecutando seed de análises..."))
        call_command("seed_analysis")