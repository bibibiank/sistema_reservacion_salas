from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time, timedelta

from reservaciones.forms import ReservacionForm
from .models import Sala, Reservacion

from .services import crear_reservacion

class ReservacionTests(TestCase):
    fixtures = ['salas_iniciales.json']

    def setUp(self):
        self.usuario = User.objects.create_user(username='biankk', password='jungkook')
        self.sala = Sala.objects.get(nombre='Sala A') # Capacidad 4, Activa

    def test_ut01_crear_reservacion_valida(self):
        reservacion = crear_reservacion(
            usuario=self.usuario,
            sala=self.sala,
            fecha=date(2026, 6, 15),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            asistentes=2,
            proposito="sisisi"
        )

        self.assertEqual(reservacion.estado, 'VIGENTE')
        self.assertEqual(Reservacion.objects.count(), 1)        

    def test_ut02_rechazar_proposito_corto(self):
        form_data = {
            'sala': self.sala.id,
            'fecha': date.today() + timedelta(days=1),
            'hora_inicio': '10:00',
            'hora_fin': '11:00',
            'asistentes': 2,
            'proposito': 'corto' # ¡Menos de 10 caracteres!
        }
        form = ReservacionForm(data=form_data)
    
        self.assertFalse(form.is_valid())
        self.assertIn('proposito', form.errors)