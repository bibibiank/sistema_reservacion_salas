from django import forms
from .models import Reservacion

class ReservacionForm(forms.ModelForm):
    class Meta:
        model = Reservacion
        fields = ['sala', 'fecha', 'hora_inicio', 'hora_fin', 'asistentes', 'proposito']

    def clean_proposito(self):
        proposito = self.cleaned_data.get('proposito', '').strip()
        if len(proposito) < 10:
            raise forms.ValidationError("El propósito debe tener al menos 10 caracteres.")
        return proposito