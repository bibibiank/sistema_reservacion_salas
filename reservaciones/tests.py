from django.test import TestCase
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time, timedelta
from reservaciones.forms import ReservacionForm
from .models import Sala, Reservacion
from .services import crear_reservacion
from django.urls import reverse
from django.test import TransactionTestCase
import threading
from .services import cancelar_reservacion
from django.db import OperationalError
from time import sleep, timezone
from django.utils import timezone


class ReservacionTests(TestCase):
    fixtures = ['salas_iniciales.json']

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='biankk', password='jungkook')
        self.sala = Sala.objects.get(nombre='Sala A')
        self.url = reverse('crear_reservacion')

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
            'proposito': 'corto'  # ¡Menos de 10 caracteres!
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
            crear_reservacion(
                self.usuario, self.sala, date(
                    2026, 6, 18), time(
                    9, 30), time(
                    10, 30), 2, "Parcial")
        with self.assertRaises(ValidationError):
            crear_reservacion(
                self.usuario, self.sala, date(
                    2026, 6, 18), time(
                    10, 30), time(
                    11, 30), 2, "Contenido")

    def test_ut09_permitir_horarios_adyacentes(self):
        crear_reservacion(
            self.usuario, self.sala, date(
                2026, 6, 19), time(
                10, 0), time(
                11, 0), 2, "Reserva 1")
        res_2 = crear_reservacion(
            self.usuario, self.sala, date(
                2026, 6, 19), time(
                11, 0), time(
                12, 0), 2, "Reserva 2")
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

    def test_ut11_impedir_acceso_anonimo(self):
        response = self.client.get(self.url)
        # Debe redirigir al login (código HTTP 302)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_ut12_crear_reservacion_post(self):
        self.client.login(username='biankk', password='jungkook')
        data = {
            'sala': self.sala.id,
            'fecha': date.today() + timedelta(days=1),
            'hora_inicio': '10:00',
            'hora_fin': '11:00',
            'asistentes': 2,
            'proposito': 'Reserva desde vista'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reservacion.objects.count(), 1)


class ConcurrenciaTests(TransactionTestCase):
    fixtures = ['salas_iniciales.json']

    def setUp(self):
        self.usuario1 = User.objects.create_user(
            username='miguelon', password='skrillex')
        self.usuario2 = User.objects.create_user(
            username='sadnisbi', password='bts')
        self.sala = Sala.objects.get(nombre='Sala A')

    def test_it01_solicitudes_concurrentes(self):
        def intento_de_reserva(usuario, retardo):
            sleep(retardo)
            try:
                crear_reservacion(
                    usuario, self.sala, date(2026, 6, 25),
                    time(10, 0), time(11, 0), 2, "Concurrencia"
                )
            except (ValidationError, OperationalError):
                pass

        hilo1 = threading.Thread(
            target=intento_de_reserva, args=(
                self.usuario1, 0))
        hilo2 = threading.Thread(
            target=intento_de_reserva, args=(
                self.usuario2, 0.1))

        hilo1.start()
        hilo2.start()
        hilo1.join()
        hilo2.join()

        self.assertEqual(Reservacion.objects.count(), 1)


class CancelacionTests(TestCase):
    fixtures = ['salas_iniciales.json']

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='biankk', password='pwd')
        self.otro_usuario = User.objects.create_user(
            username='intruso', password='pwd')
        self.sala = Sala.objects.get(nombre='Sala A')

        manana = date.today() + timedelta(days=1)
        self.reserva = Reservacion.objects.create(
            usuario=self.usuario, sala=self.sala, fecha=manana,
            hora_inicio=time(15, 0), hora_fin=time(16, 0),
            asistentes=2, proposito="Reserva a cancelar", estado='VIGENTE'
        )

    def test_ut13_cancelar_reservacion_valida(self):
        res_cancelada = cancelar_reservacion(self.usuario, self.reserva.id)

        self.assertEqual(res_cancelada.estado, 'CANCELADA')
        self.assertIsNotNone(res_cancelada.fecha_cancelacion)

    def test_ut14_rechazar_cancelacion_ajena(self):
        with self.assertRaises(ValidationError):
            cancelar_reservacion(self.otro_usuario, self.reserva.id)

    def test_ut15_rechazar_cancelacion_60_minutos_exactos(self):
        ahora = timezone.now()
        self.reserva.fecha = ahora.date()
        self.reserva.hora_inicio = (ahora + timedelta(minutes=60)).time()
        self.reserva.save()
        with self.assertRaises(ValidationError):
            cancelar_reservacion(self.usuario, self.reserva.id)

    def test_ut16_rechazar_cancelacion_menor_60_minutos(self):
        ahora = timezone.now()
        self.reserva.fecha = ahora.date()
        self.reserva.hora_inicio = (ahora + timedelta(minutes=30)).time()
        self.reserva.save()
        with self.assertRaises(ValidationError):
            cancelar_reservacion(self.usuario, self.reserva.id)

    def test_ut17_rechazar_segunda_cancelacion(self):
        cancelar_reservacion(self.usuario, self.reserva.id)
        with self.assertRaises(ValidationError):
            cancelar_reservacion(self.usuario, self.reserva.id)

    def test_ut18_liberar_sala_tras_cancelacion(self):
        cancelar_reservacion(self.usuario, self.reserva.id)
        nueva_reserva = crear_reservacion(
            self.otro_usuario, self.sala, self.reserva.fecha,
            self.reserva.hora_inicio, self.reserva.hora_fin, 2, "Nueva"
        )
        self.assertEqual(nueva_reserva.estado, 'VIGENTE')


class CancelacionVistasTests(TestCase):
    fixtures = ['salas_iniciales.json']

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='biankk', password='pwd')
        self.sala = Sala.objects.get(nombre='Sala A')
        manana = date.today() + timedelta(days=1)
        self.reserva = Reservacion.objects.create(
            usuario=self.usuario, sala=self.sala, fecha=manana,
            hora_inicio=time(15, 0), hora_fin=time(16, 0),
            asistentes=2, proposito="Reserva a cancelar", estado='VIGENTE'
        )
        self.url = reverse('cancelar_reservacion', args=[self.reserva.id])

    def test_ut19_impedir_cancelacion_anonima(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_ut20_cancelar_reservacion_post(self):
        self.client.login(username='biankk', password='pwd')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.estado, 'CANCELADA')
