from datetime import date
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
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < date.today():
            raise forms.ValidationError("No se puede reservar en fechas pasadas.")
        return fecha
    
    def clean_sala(self):
        sala = self.cleaned_data.get('sala')
        if sala and not sala.activa:
            raise forms.ValidationError("La sala no se encuentra disponible para reservación.")
        return sala
    
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if hora_inicio and hora_fin:
            if hora_fin <= hora_inicio:
                raise forms.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
        return cleaned_data