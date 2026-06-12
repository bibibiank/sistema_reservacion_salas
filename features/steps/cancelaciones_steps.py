from behave import given, when, then
from django.contrib.auth.models import User
from reservaciones.models import Sala, Reservacion
from datetime import date, timedelta
from django.utils import timezone
from django.urls import reverse
from selenium.webdriver.common.by import By
import time

# ======================================================================
# --- PASOS COMPARTIDOS (Para evitar que Behave truene por duplicados)
# ======================================================================

@given('que el usuario ha iniciado sesión')
def step_impl(context):
    usuario, _ = User.objects.get_or_create(username='biankk')
    usuario.set_password('password123')
    usuario.save()
    
    context.browser.get(context.base_url + reverse('login'))
    context.browser.find_element(By.NAME, 'username').send_keys('biankk')
    context.browser.find_element(By.NAME, 'password').send_keys('password123')
    context.browser.find_element(By.ID, 'btn-login').click()
    time.sleep(1)

@given('es propietario de una reservación vigente cuyo inicio ocurrirá dentro de más de 60 minutos')
def step_impl(context):
    Reservacion.objects.all().delete()
    sala, _ = Sala.objects.get_or_create(nombre='Sala CA-07', activa=True, capacidad=10)
    
    usuario, creado = User.objects.get_or_create(username='biankk')
    if creado:
        usuario.set_password('password123')
        usuario.save()
    
    manana = date.today() + timedelta(days=1)
    
    context.reserva = Reservacion.objects.create(
        usuario=usuario, sala=sala, fecha=manana,
        hora_inicio='10:00', hora_fin='11:00', asistentes=2,
        proposito="Reserva lista para cancelar", estado='VIGENTE'
    )

@then('el sistema rechaza la operación')
def step_impl(context):
    texto = context.respuesta_ataque.content.decode('utf-8').lower()
    assert "éxito" not in texto, "¡El sistema permitió la cancelación ilegal!"

@then('mantiene la reservación en estado "VIGENTE"')
def step_impl(context):
    reserva = getattr(context, 'reserva', getattr(context, 'reserva_ajena', None))
    reserva.refresh_from_db()
    assert reserva.estado == 'VIGENTE', "La reserva se canceló por error."

@then('conserva el estado "CANCELADA"')
def step_impl(context):
    context.reserva.refresh_from_db()
    assert context.reserva.estado == 'CANCELADA', "Estado alterado mágicamente."


# --- CA-07. Cancelar con anticipación
@when('confirma la cancelación')
def step_impl(context):
    context.browser.get(context.base_url + reverse('inicio')) 
    time.sleep(1)
    boton_cancelar = context.browser.find_element(By.ID, f'btn-cancelar-{context.reserva.id}')
    boton_cancelar.click()
    time.sleep(1.5)

@then('el sistema cambia el estado de la reservación a "CANCELADA"')
def step_impl(context):
    context.reserva.refresh_from_db()
    assert context.reserva.estado == 'CANCELADA', f"Sigue en estado {context.reserva.estado}"

@then('registra la fecha y hora de cancelación')
def step_impl(context):
    context.reserva.refresh_from_db()
    assert context.reserva.fecha_cancelacion is not None, "El campo fecha_cancelacion está vacío."

@then('la sala vuelve a estar disponible para ese horario.')
def step_impl(context):
    nueva_reserva_valida = not Reservacion.objects.filter(
        sala=context.reserva.sala, fecha=context.reserva.fecha,
        hora_inicio=context.reserva.hora_inicio, estado='VIGENTE'
    ).exists()
    assert nueva_reserva_valida, "La sala sigue bloqueada, no liberó el horario."