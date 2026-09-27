from django.core.management.base import BaseCommand
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