from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.analysis.models import Analise, Parecer
from apps.report.models import Reporte
from apps.items.models import Item

class Command(BaseCommand):
    help = "Popula a base com Análises e Pareceres"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Iniciando criação de análises..."))

        admin = User.objects.filter(username="admin").first()
        if not admin:
            self.stdout.write(self.style.ERROR("Admin não encontrado. Execute o seed principal primeiro."))
            return

        reportes_perdidos = Reporte.objects.filter(tipo=Reporte.Tipo.PERDIDO)
        itens_estoque = Item.objects.filter(status=Item.Status.NO_ESTOQUE)

        if not reportes_perdidos.exists():
            self.stdout.write(self.style.ERROR("Nenhum reporte de item perdido encontrado."))
            return

        reportes_list = list(reportes_perdidos)
        estoque_list = list(itens_estoque)

        # 1. REPORTES PENDENTES (Aguardando Análise) -> Aparecem na tabela da dashboard
        # Criamos análises com status PENDENTE para 6 reportes perdidos
        for reporte in reportes_list[:6]:
            Analise.objects.get_or_create(
                reporte=reporte,
                defaults={
                    "administrador": admin,
                    "status": Analise.Status.PENDENTE,
                    "justificativa": "",
                }
            )
        self.stdout.write("✓ 6 Análises criadas em 'Aguardando Análise' (PENDENTE).")

        # 2. ANÁLISES EM ANDAMENTO (EM_ANALISE - com parecer gerado, sem conclusão) -> 2 casos
        if len(reportes_list) >= 8:
            # Caso 1: Fone JBL
            reporte_em_andamento_1 = reportes_list[6]
            analise_1, created_1 = Analise.objects.get_or_create(
                reporte=reporte_em_andamento_1,
                defaults={
                    "administrador": admin,
                    "status": Analise.Status.EM_ANALISE,
                    "item_encontrado": estoque_list[3] if len(estoque_list) > 3 else None, # Fone Redmi
                    "justificativa": "Aguardando validação presencial do aluno para confirmar se o fone Redmi é o dele.",
                }
            )
            if created_1:
                Parecer.objects.create(
                    analise=analise_1,
                    score_correspondencia=78,
                    convergencias={"categoria": "Ambos são fones de ouvido", "cor": "Ambos são pretos"},
                    inconsistencias={"marca": "Perdido relata JBL, o do estoque é Redmi."},
                    recomendacao="Compatibilidade média de cor e tipo. Verificar marca no local."
                )

            # Caso 2: Mochila Targus
            reporte_em_andamento_2 = reportes_list[7]
            analise_2, created_2 = Analise.objects.get_or_create(
                reporte=reporte_em_andamento_2,
                defaults={
                    "administrador": admin,
                    "status": Analise.Status.EM_ANALISE,
                    "item_encontrado": estoque_list[0] if len(estoque_list) > 0 else None, # Mochila Dell
                    "justificativa": "Análise iniciada pela IA. Aguardando verificação dos compartimentos internos.",
                }
            )
            if created_2:
                Parecer.objects.create(
                    analise=analise_2,
                    score_correspondencia=85,
                    convergencias={"categoria": "Mochilas de notebook", "cor": "Preto"},
                    inconsistencias={"detalhe": "Chaveiro Star Wars não localizado na foto do estoque."},
                    recomendacao="Alta compatibilidade física. Confirmar chaveiro com o proprietário."
                )

            self.stdout.write("✓ 2 Análises criadas com status 'EM_ANALISE' (com Parecer IA).")

        # 3. ANÁLISE CONCLUÍDA (CORRESPONDENCIA_ENCONTRADA) -> 1 caso
        if len(reportes_list) >= 9:
            reporte_concluido = reportes_list[8]
            analise_3, created_3 = Analise.objects.get_or_create(
                reporte=reporte_concluido,
                defaults={
                    "administrador": admin,
                    "status": Analise.Status.CORRESPONDENCIA_ENCONTRADA,
                    "item_encontrado": estoque_list[4] if len(estoque_list) > 4 else None,
                    "justificativa": "Item identificado e entregue com sucesso ao proprietário.",
                }
            )
            if created_3:
                Parecer.objects.create(
                    analise=analise_3,
                    score_correspondencia=95,
                    convergencias={"categoria": "Chaveiro e chaves", "cor": "Azul/Preto"},
                    inconsistencias={},
                    recomendacao="Correspondência confirmada."
                )
            self.stdout.write("✓ 1 Análise concluída com 'CORRESPONDENCIA_ENCONTRADA'.")

        self.stdout.write(self.style.SUCCESS("\nSeed de análises concluído com sucesso!"))