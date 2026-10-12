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


class EditarAnaliseForm(AnaliseForm):
    """
    Formulário específico para edição.
    Herda tudo do AnaliseForm e adiciona o campo 'status' sem quebrar o original.
    """
    class Meta(AnaliseForm.Meta):
        fields = AnaliseForm.Meta.fields + ["status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item_encontrado"].queryset = Item.objects.filter(
            status=Item.Status.NO_ESTOQUE
        )

    def clean_status(self) -> Analise.Status:
        """
        Garante que o Service receba o Enum certinho, e não uma string.
        """
        status_str = self.cleaned_data.get("status")
        if status_str:
            return Analise.Status(status_str)
        return None