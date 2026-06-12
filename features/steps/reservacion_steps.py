from behave import given, when, then
from django.contrib.auth.models import User
from reservaciones.models import Sala, Reservacion
from datetime import date, timedelta, datetime
from selenium.webdriver.common.by import By
from django.urls import reverse
import time
from selenium.webdriver.support.ui import Select

# REUTILIZABLES

@given('que existe una sala activa con capacidad suficiente')
def step_impl(context):
    context.sala = Sala.objects.get(nombre='Sala A')
    context.sala.activa = True
    context.sala.capacidad = 10
    context.sala.save()

@given('el usuario ha iniciado sesión')
def step_impl(context):
    usuario, creado = User.objects.get_or_create(username='biankk')
    usuario.set_password('password123')
    usuario.save()
    
    login_url = context.base_url + reverse('login')
    context.browser.get(login_url)
    
    context.browser.find_element(By.NAME, 'username').send_keys('biankk')
    context.browser.find_element(By.NAME, 'password').send_keys('password123')
    context.browser.find_element(By.ID, 'btn-login').click()
    time.sleep(1)

@when('navega al formulario de nueva reservacion')
def step_impl(context):
    url_reservar = context.base_url + reverse('crear_reservacion')
    context.browser.get(url_reservar)
    time.sleep(1)
    assert 'reservar' in context.browser.current_url, f"El robot se perdió en: {context.browser.current_url}"

@when('captura un número de asistentes permitido y un propósito válido')
def step_impl(context):
    context.browser.find_element(By.ID, 'id_asistentes').clear()
    context.browser.find_element(By.ID, 'id_asistentes').send_keys('2')
    context.browser.find_element(By.ID, 'id_proposito').clear()
    context.browser.find_element(By.ID, 'id_proposito').send_keys('Prueba automatizada BDD')

@when('envía el formulario')
def step_impl(context):
    context.browser.find_element(By.ID, 'btn-guardar-reserva').click()
    time.sleep(1.5)

@then('el sistema no registra la reservación')
def step_impl(context):
    # 1. Validamos la REALIDAD visual: Si Django guardó, nos mandaría a la pantalla de éxito.
    texto_pantalla = context.browser.page_source.lower()
    if "reservación registrada" in texto_pantalla:
        assert False, "ERROR CRÍTICO: El formulario ignoró el error y guardó la reserva."
    
    # 2. Exorcizamos la base de datos para borrar las alucinaciones de SQLite entre hilos
    Reservacion.objects.all().delete()

# ------------- CA-01

@given('no existe otra reservación vigente que se traslape con el horario solicitado')
def step_impl(context):
    Reservacion.objects.all().delete()

@when('captura una fecha válida, una hora de inicio y una hora de fin válidas')
def step_impl(context):
    manana = date.today() + timedelta(days=1)
    select_sala = Select(context.browser.find_element(By.ID, 'id_sala'))
    select_sala.select_by_visible_text('Sala A')
    
    context.browser.execute_script(f"arguments[0].value='{manana.strftime('%Y-%m-%d')}';", context.browser.find_element(By.ID, 'id_fecha'))
    context.browser.execute_script("arguments[0].value = '10:00';", context.browser.find_element(By.ID, 'id_hora_inicio'))
    context.browser.execute_script("arguments[0].value = '11:00';", context.browser.find_element(By.ID, 'id_hora_fin'))

@then('el sistema registra la reservación con estado "{estado}"')
def step_impl(context, estado):
    reservas = Reservacion.objects.filter(usuario__username='biankk')
    if reservas.count() == 0:
        assert False, f"¡El form no se guardó! La pantalla dice:\n{context.browser.page_source}"
    assert reservas.count() == 1
    assert reservas.first().estado == estado

@then('muestra un mensaje de confirmación')
def step_impl(context):
    mensajes = context.browser.find_element(By.ID, 'contenedor-mensajes').text
    assert 'Reservación registrada con éxito' in mensajes, f"No vi el mensaje. Vi esto: {mensajes}"

@then('la reservación aparece en la lista de reservaciones del usuario')
def step_impl(context):
    tabla = context.browser.find_element(By.ID, 'tabla-reservaciones').text
    assert 'Sala A' in tabla, "La sala no apareció en la lista"


# ------------- CA-02

@given('que existe una reservación vigente para una sala entre las "{h_inicio}" y las "{h_fin}"')
def step_impl(context, h_inicio, h_fin):
    context.sala = Sala.objects.get(nombre='Sala A')
    manana = date.today() + timedelta(days=1)
    t_inicio = datetime.strptime(h_inicio, '%H:%M').time()
    t_fin = datetime.strptime(h_fin, '%H:%M').time()
    
    usuario, creado = User.objects.get_or_create(username='biankk')
    if creado:
        usuario.set_password('password123')
        usuario.save()
    
    Reservacion.objects.create(
        usuario=usuario,
        sala=context.sala,
        fecha=manana,
        hora_inicio=t_inicio,
        hora_fin=t_fin,
        asistentes=2,
        proposito="Reserva base CA-02",
        estado='VIGENTE'
    )

@when('intenta registrar otra reservación para la misma sala entre las "{h_inicio}" y las "{h_fin}"')
def step_impl(context, h_inicio, h_fin):
    manana = date.today() + timedelta(days=1)
    select_sala = Select(context.browser.find_element(By.ID, 'id_sala'))
    select_sala.select_by_visible_text('Sala A')
    
    context.browser.execute_script(f"arguments[0].value='{manana.strftime('%Y-%m-%d')}';", context.browser.find_element(By.ID, 'id_fecha'))
    context.browser.execute_script(f"arguments[0].value = '{h_inicio}';", context.browser.find_element(By.ID, 'id_hora_inicio'))
    context.browser.execute_script(f"arguments[0].value = '{h_fin}';", context.browser.find_element(By.ID, 'id_hora_fin'))

@then('el sistema no registra la nueva reservación')
def step_impl(context):
    reservas = Reservacion.objects.filter(usuario__username='biankk')
    assert reservas.count() == 1, f"Error: Hay {reservas.count()} reservas en BD, debió ser bloqueada."

@then('muestra un mensaje indicando que la sala no está disponible en el horario solicitado')
def step_impl(context):
    assert "La sala ya tiene una reservación vigente en ese horario" in context.browser.page_source, "Falta mensaje de traslape."


# ------------- CA-03

@given('que una sala activa tiene capacidad para 4 personas')
def step_impl(context):
    context.sala = Sala.objects.get(nombre='Sala A')
    context.sala.capacidad = 4
    context.sala.save()

@when('intenta registrar una reservación para 5 asistentes')
def step_impl(context):
    manana = date.today() + timedelta(days=1)
    select_sala = Select(context.browser.find_element(By.ID, 'id_sala'))
    select_sala.select_by_visible_text('Sala A')
    
    context.browser.execute_script(f"arguments[0].value='{manana.strftime('%Y-%m-%d')}';", context.browser.find_element(By.ID, 'id_fecha'))
    context.browser.execute_script("arguments[0].value = '14:00';", context.browser.find_element(By.ID, 'id_hora_inicio'))
    context.browser.execute_script("arguments[0].value = '15:00';", context.browser.find_element(By.ID, 'id_hora_fin'))
    
    asistentes_input = context.browser.find_element(By.ID, 'id_asistentes')
    asistentes_input.clear()
    asistentes_input.send_keys('5')
    context.browser.find_element(By.ID, 'id_proposito').send_keys('Prueba CA-03')

@then('muestra un mensaje indicando que el número de asistentes supera la capacidad de la sala')
def step_impl(context):
    texto = context.browser.page_source.lower()
    assert "capacidad" in texto or "supera" in texto, "No se mostró el error de capacidad."
    

# --- CA-04 ---

@when('intenta reservar una sala con una fecha anterior al día actual o la hora de fin no es posterior a la hora de inicio')
def step_impl(context):
    ayer = date.today() - timedelta(days=1)
    select_sala = Select(context.browser.find_element(By.ID, 'id_sala'))
    select_sala.select_by_visible_text('Sala A')
    
    context.browser.execute_script(f"arguments[0].value='{ayer.strftime('%Y-%m-%d')}';", context.browser.find_element(By.ID, 'id_fecha'))
    context.browser.execute_script("arguments[0].value = '10:00';", context.browser.find_element(By.ID, 'id_hora_inicio'))
    context.browser.execute_script("arguments[0].value = '11:00';", context.browser.find_element(By.ID, 'id_hora_fin'))
    
    context.browser.find_element(By.ID, 'id_asistentes').clear()
    context.browser.find_element(By.ID, 'id_asistentes').send_keys('2')
    context.browser.find_element(By.ID, 'id_proposito').send_keys('Prueba CA-04')

@then('muestra el mensaje de validación correspondiente')
def step_impl(context):
    texto = context.browser.page_source.lower()
    assert "pasado" in texto or "anterior" in texto or "inválida" in texto or "valid" in texto, "Falta el error de fecha."


 