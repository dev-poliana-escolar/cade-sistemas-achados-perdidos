from django import forms
from apps.items.models import Item


class ItemForm(forms.ModelForm):
    """
    Formulário de cadastro e edição de itens encontrados.
    """
    imagem = forms.ImageField(required=False, label="Foto do item")



    class Meta:
        model = Item

        fields = [
            "imagem",
            "categoria",
            "cor",
            "descricao",
            "dados_sensiveis",
        ]

        widgets = {
            "descricao": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Descreva o item encontrado..."
                }
            ),
        }       

        labels = {
            "imagem": "Foto do item",
            "categoria": "Categoria",
            "descricao": "Descrição",
            "cor": "Cor predominante",
            "dados_sensiveis": "Contém dados sensíveis",
        }

        help_texts = {
            "dados_sensiveis": (
                "Marque esta opção para documentos, cartões "
                "ou itens com informações pessoais."
            ),
        }


    # def clean_descricao(self):
    #     descricao = self.cleaned_data["descricao"].strip()

    #     if len(descricao) < 10:
    #         raise forms.ValidationError(
    #             "Descreva melhor o item."
    #         )

    #     return descricao
    

