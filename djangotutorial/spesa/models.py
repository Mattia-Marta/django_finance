from django.db import models
from django.utils import timezone
from datetime import date


class Categoria(models.Model):
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome Categoria")
    descrizione = models.TextField(blank=True, null=True, verbose_name="Descrizione")

    def __str__(self):
        return self.nome

    class Meta:
      verbose_name_plural = "Categorie"


class Spesa(models.Model):
    OWNER_CHOICES = [
        ('Mattia', 'Mattia'),
        ('Annalisa', 'Annalisa'),
    ]
    owner = models.CharField(max_length=255, choices=OWNER_CHOICES, verbose_name="Proprietario")
    spesa = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importo")
    categorie = models.ManyToManyField("Categoria", blank=True, related_name="spese", verbose_name="Categorie")

    data = models.DateField(verbose_name="Data", default=timezone.now())
    saldata = models.BooleanField(default=False, verbose_name="Saldato")

    def __str__(self):
        categorie_str = ", ".join([categoria.nome for categoria in self.categorie.all()])
        return f"{self.owner} - {self.spesa}€ - {self.data} - {categorie_str}"

    class Meta:
      verbose_name_plural = "Spese"
