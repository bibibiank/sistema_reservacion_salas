from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time
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