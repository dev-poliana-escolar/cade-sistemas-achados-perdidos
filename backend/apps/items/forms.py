from django import forms
from apps.items.models import Item


class ItemForm(forms.ModelForm):
    """
    Formulário de cadastro e edição de itens encontrados.
    """

    CORES = [
        ("PRETO", "Preto"),
        ("BRANCO", "Branco"),
        ("AZUL", "Azul"),
        ("VERMELHO", "Vermelho"),
        ("VERDE", "Verde"),
        ("AMARELO", "Amarelo"),
        ("ROXO", "Roxo"),
        ("ROSA", "Rosa"),
        ("CINZA", "Cinza"),
        ("MARROM", "Marrom"),
        ("LARANJA", "Laranja"),
        ("TRANSPARENTE", "Transparente"),
        ("OUTRA", "Outra"),
    ]

    cor = forms.ChoiceField(
        choices=CORES,
        label="Cor predominante"
    )

    outra_cor = forms.CharField(
        required=False,
        label="Digite a cor",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ex: Bege claro"
            }
        )
    )

    class Meta:
        model = Item

        fields = [
            "imagem",
            "categoria",
            "descricao",
            "cor",
            "outra_cor",
            "local_encontrado",
            "dados_sensiveis",
            "data_encontro",
        ]

        widgets = {
            "descricao": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Descreva o item encontrado..."
                }
            ),

            "data_encontro": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local"
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

        labels = {
            "imagem": "Foto do item",
            "categoria": "Categoria",
            "descricao": "Descrição",
            "cor": "Cor predominante",
            "local_encontrado": "Local onde foi encontrado",
            "dados_sensiveis": "Contém dados sensíveis",
            "data_encontro": "Data e hora do encontro",
        }

        help_texts = {
            "dados_sensiveis": (
                "Marque esta opção para documentos, cartões "
                "ou itens com informações pessoais."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.data_encontro:
            self.initial["data_encontro"] = (
                self.instance.data_encontro.strftime("%Y-%m-%dT%H:%M")
            )

    def clean(self):
        cleaned_data = super().clean()
        # Ensure image is present for new instances
        imagem = cleaned_data.get("imagem")

        if not imagem:
            # If editing and an image already exists on the instance, allow no new upload
            if not (self.instance and self.instance.pk and getattr(self.instance, "imagem")):
                self.add_error(
                    "imagem",
                    "Envie uma foto do item."
                )

        # Handle color logic: when 'OUTRA' is selected, require and normalize the text field
        cor = cleaned_data.get("cor")
        outra_cor = cleaned_data.get("outra_cor")

        if cor == "OUTRA":
            if not outra_cor or not outra_cor.strip():
                self.add_error(
                    "outra_cor",
                    "Informe a cor do item."
                )
            else:
                cleaned_data["cor"] = outra_cor.strip().upper()

        return cleaned_data

    def clean_local_encontrado(self):
        local = self.cleaned_data.get("local_encontrado")

        if not local or len(local.strip()) < 3:
            raise forms.ValidationError(
                "Informe um local válido."
            )

        # normalize
        return local.strip()

    def clean_descricao(self):
        descricao = self.cleaned_data.get("descricao")

        if not descricao or len(descricao.strip()) < 3:
            raise forms.ValidationError(
                "Informe uma descrição válida."
            )

        descricao = descricao.strip()

        # Detect sensitive keywords and flag the dados_sensiveis field
        sensitive_keywords = [
            "cpf",
            "rg",
            "matricula",
            "cartao",
            "senha",
        ]

        lower = descricao.lower()

        if any(k in lower for k in sensitive_keywords):
            # force the boolean field to True so the view/model can act accordingly
            self.cleaned_data["dados_sensiveis"] = True

        return descricao

