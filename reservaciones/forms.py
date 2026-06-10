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
    
    def clean_asistentes(self):
        asistentes = self.cleaned_data.get('asistentes')
        if asistentes is not None and asistentes <= 0:
            raise forms.ValidationError("Debe haber al menos 1 asistente.")
        return asistentes