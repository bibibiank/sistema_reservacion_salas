from multiprocessing import context

from behave import given, when, then
from django.contrib.auth.models import User
from reservaciones.models import Sala, Reservacion
from datetime import date, timedelta
from selenium.webdriver.common.by import By
from django.urls import reverse
import time
from selenium.webdriver.support.ui import Select
from datetime import datetime


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


# -----------------------CA-02 

@given('existe una reservación previa en la sala de "{h_inicio}" a "{h_fin}" para mañana')
def step_impl(context, h_inicio, h_fin):
    manana = date.today() + timedelta(days=1)
    t_inicio = datetime.strptime(h_inicio, '%H:%M').time()
    t_fin = datetime.strptime(h_fin, '%H:%M').time()
    
    Reservacion.objects.create(
        usuario=User.objects.get(username='biankk'),
        sala=context.sala,
        fecha=manana,
        hora_inicio=t_inicio,
        hora_fin=t_fin,
        asistentes=2,
        proposito="Reserva base para probar el traslape",
        estado='VIGENTE'
    )

@when('captura la misma fecha, hora de inicio "{h_inicio}" y hora de fin "{h_fin}"')
def step_impl(context, h_inicio, h_fin):
    manana = date.today() + timedelta(days=1)
    
    elemento_sala = context.browser.find_element(By.ID, 'id_sala')
    select_sala = Select(elemento_sala)
    select_sala.select_by_visible_text('Sala A')
    fecha_input = context.browser.find_element(By.ID, 'id_fecha')
    fecha_input.clear()
    context.browser.execute_script(
    f"arguments[0].value='{manana.strftime('%Y-%m-%d')}';",
    fecha_input
)
    hora_inicio_input = context.browser.find_element(By.ID, 'id_hora_inicio')
    hora_fin_input = context.browser.find_element(By.ID, 'id_hora_fin')
    
    context.browser.execute_script(f"arguments[0].value = '{h_inicio}';", hora_inicio_input)
    context.browser.execute_script(f"arguments[0].value = '{h_fin}';", hora_fin_input)

@then('el sistema rechaza la reservación')
def step_impl(context):
    reservas = Reservacion.objects.filter(usuario__username='biankk')
    assert reservas.count() == 1, f"¡Error crítico! El traslape se guardó en la BD. Hay {reservas.count()} reservas."

@then('muestra un mensaje de error indicando el traslape')
def step_impl(context):
    print(context.browser.page_source)

    assert (
        "La sala ya tiene una reservación vigente en ese horario."
        in context.browser.page_source
    ), "No se mostró el mensaje de error de traslape en la pantalla."


#----CA- 03-----

@given('que una sala activa tiene capacidad para 4 personas')
def step_impl(context):
    context.sala = Sala.objects.first()
    context.sala.capacidad = 4
    context.sala.save()

@when('intenta registrar una reservación para 5 asistentes')
def step_impl(context):
    manana = date.today() + timedelta(days=1)

    context.browser.get(context.get_url('/reservar/'))

    print(context.browser.current_url)
    print(context.browser.page_source)

    Select(
        context.browser.find_element(By.ID, 'id_sala')
    ).select_by_visible_text('Sala A')

    context.browser.find_element(
        By.ID, 'id_fecha'
    ).send_keys(manana.strftime('%Y-%m-%d'))

    context.browser.find_element(
        By.ID, 'id_hora_inicio'
    ).send_keys('10:00')

    context.browser.find_element(
        By.ID, 'id_hora_fin'
    ).send_keys('11:00')

    context.browser.find_element(
        By.ID, 'id_asistentes'
    ).send_keys('5')

    context.browser.find_element(
        By.ID, 'id_proposito'
    ).send_keys('Prueba capacidad')

    context.browser.find_element(
        By.ID, 'btn-guardar-reserva'
    ).click()

@then('el sistema no registra la reservación')
def step_impl(context):
    assert not Reservacion.objects.filter(
        usuario=User.objects.get(username='biankk'),
        asistentes=5
    ).exists()

@then('muestra un mensaje indicando que el número de asistentes supera la capacidad de la sala')
def step_impl(context):
    assert 'supera la capacidad de la sala' in context.browser.page_source
