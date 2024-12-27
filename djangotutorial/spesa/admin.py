from django.contrib import admin
from .models import Spesa, Categoria

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descrizione')
    search_fields = ('nome',)

class SpesaCategoriaInline(admin.TabularInline):
    model = Spesa.categorie.through # Usa il modello "through"
    extra = 1

class SpesaAdmin(admin.ModelAdmin):
    list_display = ('owner', 'spesa', 'data', 'saldata', 'mostra_categorie')
    list_filter = ('data', 'saldata', 'categorie')
    search_fields = ('owner',)
    inlines = [SpesaCategoriaInline] # Usa il nuovo inline
    date_hierarchy = 'data'
    ordering = ('-data',)
    raw_id_fields = ('categorie',)
    def mostra_categorie(self, obj):
        return ", ".join([categoria.nome for categoria in obj.categorie.all()])
    mostra_categorie.short_description = "Categorie"

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Spesa, SpesaAdmin)