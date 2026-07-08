from django import forms

from apps.report.models import Reporte


class ReporteForm(forms.ModelForm):
    """
    Formulário para registro de um reporte de item
    encontrado ou perdido.
    """

    data = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = Reporte

        fields = [
            "tipo",
            "data",
            "local",
            "observacoes",
        ]

        widgets = {
            "observacoes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Informações adicionais (opcional)..."
                }
            ),
            "local": forms.TextInput(
                attrs={
                    "placeholder": "Ex.: Biblioteca, Bloco A..."
                }
            ),
        }

        labels = {
            "tipo": "Tipo do reporte",
            "data": "Data e hora",
            "local": "Local",
            "observacoes": "Observações",
        }

    # def clean_local(self):
    #     local = self.cleaned_data.get("local")

    #     if len(local.strip()) < 3:
    #         raise forms.ValidationError(
    #             "Informe um local válido."
    #         )

    #     return local