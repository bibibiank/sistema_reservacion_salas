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
    sala, _ = Sala.objects.get_or_create(
        nombre='Sala CA-07', activa=True, capacidad=10)

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
    reserva = getattr(
        context,
        'reserva',
        getattr(
            context,
            'reserva_ajena',
            None))
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
    boton_cancelar = context.browser.find_element(
        By.ID, f'btn-cancelar-{context.reserva.id}')
    boton_cancelar.click()
    time.sleep(1.5)


@then('el sistema cambia el estado de la reservación a "CANCELADA"')
def step_impl(context):
    context.reserva.refresh_from_db()
    assert context.reserva.estado == 'CANCELADA', f"Sigue en estado {
        context.reserva.estado}"


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

# --- CA-08. Impedir cancelar reserva ajena
#


@given('que existe una reservación vigente perteneciente a otro usuario')
def step_impl(context):
    Reservacion.objects.all().delete()
    sala, _ = Sala.objects.get_or_create(
        nombre='Sala CA-08', activa=True, capacidad=10)
    victima, _ = User.objects.get_or_create(username='victima_08')

    context.reserva_ajena = Reservacion.objects.create(
        usuario=victima, sala=sala, fecha=date.today() + timedelta(days=1),
        hora_inicio='15:00', hora_fin='16:00', asistentes=2,
        proposito="Reserva secreta de victima", estado='VIGENTE'
    )


@given('el usuario autenticado intenta cancelarla')
def step_impl(context):
    context.test.client.login(username='biankk', password='password123')
    url = reverse('cancelar_reservacion', args=[context.reserva_ajena.id])
    context.respuesta_ataque = context.test.client.post(url, follow=True)


@then('responde sin revelar información sensible de la reservación.')
def step_impl(context):
    texto = context.respuesta_ataque.content.decode('utf-8').lower()
    assert "reserva secreta" not in texto, "¡Fuga de datos! Mostró detalles de la víctima."

# --- CA-09. Fuera de periodo permitido


@given('que el usuario es propietario de una reservación vigente')
def step_impl(context):
    context.execute_steps(
        'Dado es propietario de una reservación vigente cuyo inicio ocurrirá dentro de más de 60 minutos')


@given('faltan 60 minutos o menos para su inicio')
def step_impl(context):
    ahora = timezone.now()
    inicio_cercano = ahora + timedelta(minutes=30)  # Faltan solo 30 mins
    context.reserva.fecha = inicio_cercano.date()
    context.reserva.hora_inicio = inicio_cercano.time()
    context.reserva.hora_fin = (inicio_cercano + timedelta(hours=1)).time()
    context.reserva.save()


@when('intenta cancelarla')
def step_impl(context):
    context.test.client.login(username='biankk', password='password123')
    url = reverse('cancelar_reservacion', args=[context.reserva.id])
    context.respuesta_ataque = context.test.client.post(url, follow=True)


@then('muestra un mensaje indicando que el periodo de cancelación ha concluido.')
def step_impl(context):
    texto = context.respuesta_ataque.content.decode('utf-8').lower()
    assert "anticipación" in texto or "60" in texto, f"Falta error de tiempo. Django dijo: {texto}"

# --- CA-10. Cancelar algo ya cancelado


@given('que el usuario es propietario de una reservación cancelada')
def step_impl(context):
    context.execute_steps(
        'Dado es propietario de una reservación vigente cuyo inicio ocurrirá dentro de más de 60 minutos')
    context.reserva.estado = 'CANCELADA'
    context.reserva.save()


@when('intenta cancelarla nuevamente')
def step_impl(context):
    context.test.client.login(username='biankk', password='password123')
    url = reverse('cancelar_reservacion', args=[context.reserva.id])
    context.respuesta_ataque = context.test.client.post(url, follow=True)


@then('muestra un mensaje indicando que la reservación ya fue cancelada.')
def step_impl(context):
    texto = context.respuesta_ataque.content.decode('utf-8').lower()
    assert "ya fue cancelada" in texto or "cancelada" in texto, f"Falta mensaje de doble cancelación. Django dijo: {texto}"

# --- CA-11


@given('que el usuario cancela correctamente una reservación')
def step_impl(context):
    context.execute_steps('''
        Dado que el usuario ha iniciado sesión
        Y es propietario de una reservación vigente cuyo inicio ocurrirá dentro de más de 60 minutos
        Cuando confirma la cancelación
    ''')


@when('consulta su historial')
def step_impl(context):
    context.browser.get(context.base_url + reverse('inicio'))
    time.sleep(1)


@then('observa la reservación con estado "CANCELADA"')
def step_impl(context):
    html = context.browser.page_source.upper()
    assert "CANCELADA" in html, "No aparece el texto CANCELADA en la tabla."


@then('puede identificar la fecha y hora en la que se realizó la cancelación.')
def step_impl(context):
    html = context.browser.page_source.lower()
    assert "cancelada el:" in html or "cancelada" in html, "No se imprimió la fecha de cancelación."
