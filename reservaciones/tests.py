from django.test import TestCase
from django.core.exceptions import ValidationError
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

    def test_ut03_rechazar_asistentes_cero_o_negativo(self):
        form_data = {
            'sala': self.sala.id,
            'fecha': date.today() + timedelta(days=1),
            'hora_inicio': '10:00',
            'hora_fin': '11:00',
            'asistentes': 0, 
            'proposito': 'Reunión de estudio válida'
        }
        form = ReservacionForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('asistentes', form.errors)

    def test_ut04_rechazar_asistentes_superiores_capacidad(self):
        with self.assertRaises(ValidationError):
            crear_reservacion(
                usuario=self.usuario,
                sala=self.sala,
                fecha=date(2026, 6, 16),
                hora_inicio=time(10, 0),
                hora_fin=time(11, 0),
                asistentes=5, 
                proposito="Reunión de estudio"
            )

    def test_ut05_rechazar_fecha_pasada(self):
        form_data = {
            'sala': self.sala.id,
            'fecha': date.today() - timedelta(days=1), 
            'hora_inicio': '10:00',
            'hora_fin': '11:00',
            'asistentes': 2,
            'proposito': 'Reunión de estudio válida'
        }
        form = ReservacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha', form.errors)

    def test_ut06_rechazar_hora_fin_invalida(self):
        form_data = {
            'sala': self.sala.id,
            'fecha': date.today() + timedelta(days=1),
            'hora_inicio': '11:00',
            'hora_fin': '10:00', 
            'asistentes': 2,
            'proposito': 'Reunión de estudio válida'
        }
        form = ReservacionForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_ut07_rechazar_duracion_invalida(self):
        with self.assertRaises(ValidationError):
            crear_reservacion(
                self.usuario, self.sala, date(2026, 6, 17), 
                time(10, 0), time(10, 20), 2, "Proposito válido"
            )
        with self.assertRaises(ValidationError):
            crear_reservacion(
                self.usuario, self.sala, date(2026, 6, 17), 
                time(10, 0), time(13, 0), 2, "Proposito válido"
            )

    def test_ut08_detectar_traslapes(self):
        crear_reservacion(
            self.usuario, self.sala, date(2026, 6, 18), 
            time(10, 0), time(12, 0), 2, "Reserva Base"
        )

        with self.assertRaises(ValidationError):
            crear_reservacion(self.usuario, self.sala, date(2026, 6, 18), time(9, 30), time(10, 30), 2, "Parcial")
        with self.assertRaises(ValidationError):
            crear_reservacion(self.usuario, self.sala, date(2026, 6, 18), time(10, 30), time(11, 30), 2, "Contenido")
    
    def test_ut09_permitir_horarios_adyacentes(self):
        crear_reservacion(self.usuario, self.sala, date(2026, 6, 19), time(10, 0), time(11, 0), 2, "Reserva 1")
        res_2 = crear_reservacion(self.usuario, self.sala, date(2026, 6, 19), time(11, 0), time(12, 0), 2, "Reserva 2")
        self.assertEqual(res_2.estado, 'VIGENTE')

    def test_ut10_ignorar_reservaciones_canceladas(self):
        Reservacion.objects.create(
            usuario=self.usuario, sala=self.sala, fecha=date(2026, 6, 20),
            hora_inicio=time(10, 0), hora_fin=time(11, 0), asistentes=2,
            proposito="Cancelada", estado='CANCELADA'
        )
        res_nueva = crear_reservacion(
            self.usuario, self.sala, date(2026, 6, 20), 
            time(10, 0), time(11, 0), 2, "Nueva"
        )
        self.assertEqual(res_nueva.estado, 'VIGENTE')