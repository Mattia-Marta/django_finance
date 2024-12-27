from django import forms
from .models import Spesa

class SpesaForm(forms.ModelForm):
    class Meta:
        model = Spesa
        fields = '__all__'  # Includi tutti i campi
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'spesa': forms.NumberInput(attrs={'class': 'form-control'}),
            'saldata': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'categorie': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
        OWNER_CHOICES = [
            ('Mattia', 'Mattia'),
            ('Annalisa', 'Annalisa'),
        ]
        labels = {
            'owner': 'Proprietario'
        }
        help_texts = {
            'owner': 'Inserisci il proprietario della spesa (Mattia o Annalisa)',
        }