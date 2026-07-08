from django.contrib import admin
from apps.category.models import Categoria
from apps.color.models import Cor

# Register your models here.

admin.site.register(Categoria)
admin.site.register(Cor)