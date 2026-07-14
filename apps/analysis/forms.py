from django import forms
from apps.analysis.models import Analise
from apps.items.models import Item

class AnaliseForm(forms.ModelForm):
    """
    Formulário de cadastro de analise
    """

    class Meta():
        model = Analise
        fields=[
            "item_encontrado",
            "justificativa"
        ]

        item_encontrado = forms.ModelChoiceField(
            queryset=Item.objects.none(),
            required=False
        )


        