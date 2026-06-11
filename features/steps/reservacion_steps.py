from behave import given, when, then
from django.contrib.auth.models import User
from reservaciones.models import Sala, Reservacion
from datetime import date, timedelta
from selenium.webdriver.common.by import By
from django.urls import reverse
import time
from selenium.webdriver.support.ui import Select

@given('que existe una sala activa con capacidad suficiente')
def step_impl(context):
    context.sala = Sala.objects.get(nombre='Sala A')

@given('el usuario ha iniciado sesión')
def step_impl(context):
    User.objects.create_user(username='biankk', password='jungkook')
    
    login_url = context.base_url + reverse('login')
    context.browser.get(login_url)
    
    context.browser.find_element(By.NAME, 'username').send_keys('biankk')
    context.browser.find_element(By.NAME, 'password').send_keys('jungkook')
    context.browser.find_element(By.ID, 'btn-login').click()
    time.sleep(1)
    
@when('navega al formulario de nueva reservacion')
def step_impl(context):
    url_reservar = context.base_url + reverse('crear_reservacion')
    context.browser.get(url_reservar)
    time.sleep(1)
    
    assert 'reservar' in context.browser.current_url, f"El robot se perdió, está en: {context.browser.current_url}"

@when('captura una fecha válida, una hora de inicio y una hora de fin válidas')
def step_impl(context):
    manana = date.today() + timedelta(days=1)

    elemento_sala = context.browser.find_element(By.ID, 'id_sala')
    select_sala = Select(elemento_sala)
    select_sala.select_by_visible_text('Sala A')

    context.browser.find_element(By.ID, 'id_fecha').send_keys(
        manana.strftime('%Y-%m-%d')
    )

    context.browser.find_element(
        By.ID,
        'id_hora_inicio'
    ).send_keys('10:00')

    context.browser.find_element(
        By.ID,
        'id_hora_fin'
    ).send_keys('11:00')
    
@when('captura un número de asistentes permitido y un propósito válido')
def step_impl(context):
    context.browser.find_element(By.ID, 'id_asistentes').send_keys('2')
    context.browser.find_element(By.ID, 'id_proposito').send_keys('Revisión de BDD')

@when('envía el formulario')
def step_impl(context):
    context.browser.find_element(By.ID, 'btn-guardar-reserva').click()
    # FRENO DE MANO 3: Le damos 1.5 segundos a Django para procesar la base de datos
    time.sleep(1.5)

@then('el sistema registra la reservación con estado "{estado}"')
def step_impl(context, estado):
    reservas = Reservacion.objects.filter(usuario__username='biankk')
    
    # SÚPER DETECTOR DE MENTIRAS: Si la BD está vacía, que nos lea qué dice la página
    if reservas.count() == 0:
        texto_pantalla = context.browser.find_element(By.TAG_NAME, 'body').text
        assert False, f"¡El form no se guardó! La pantalla dice:\n{texto_pantalla}"
        
    assert reservas.count() == 1
    assert reservas.first().estado == estado

@then('muestra un mensaje de confirmación')
def step_impl(context):
    # Ya estamos en la página de inicio, verificamos el mensaje
    mensajes = context.browser.find_element(By.ID, 'contenedor-mensajes').text
    assert 'Reservación registrada con éxito' in mensajes, f"No vi el mensaje. Vi esto: {mensajes}"

@then('la reservación aparece en la lista de reservaciones del usuario')
def step_impl(context):
    # Verificamos que la tabla html contenga el nombre de la sala
    tabla = context.browser.find_element(By.ID, 'tabla-reservaciones').text
    assert 'Sala A' in tabla, "La sala no apareció en la lista"