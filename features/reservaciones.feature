Característica: Registrar una reservación de sala
  Como usuario autenticado
  Quiero seleccionar una sala disponible y registrar una reservación
  Para asegurar el uso exclusivo de la sala durante un periodo determinado

  Escenario: CA-01. Registrar una reservación válida
    Dado que existe una sala activa con capacidad suficiente
    Y el usuario ha iniciado sesión
    Y no existe otra reservación vigente que se traslape con el horario solicitado
    Cuando navega al formulario de nueva reservacion
    Y captura una fecha válida, una hora de inicio y una hora de fin válidas
    Y captura un número de asistentes permitido y un propósito válido
    Y envía el formulario
    Entonces el sistema registra la reservación con estado "VIGENTE"
    Y muestra un mensaje de confirmación
    Y la reservación aparece en la lista de reservaciones del usuario

  Escenario: CA-02. Rechazar una reservación con horario traslapado
    Dado que existe una reservación vigente para una sala entre las "10:00" y las "11:00"
    Y el usuario ha iniciado sesión
    Cuando navega al formulario de nueva reservacion
    Y intenta registrar otra reservación para la misma sala entre las "10:30" y las "11:30"
    Y captura un número de asistentes permitido y un propósito válido
    Y envía el formulario
    Entonces el sistema no registra la nueva reservación
    Y muestra un mensaje indicando que la sala no está disponible en el horario solicitado

  Escenario: CA-03. Rechazar una reservación que exceda la capacidad
    Dado que una sala activa tiene capacidad para 4 personas
    Y el usuario ha iniciado sesión
    Cuando navega al formulario de nueva reservacion
    Y intenta registrar una reservación para 5 asistentes
    Y envía el formulario
    Entonces el sistema no registra la reservación
    Y muestra un mensaje indicando que el número de asistentes supera la capacidad de la sala

  Escenario: CA-04. Rechazar una fecha u horario inválidos
    Dado el usuario ha iniciado sesión
    Cuando navega al formulario de nueva reservacion
    Y intenta reservar una sala con una fecha anterior al día actual o la hora de fin no es posterior a la hora de inicio
    Y envía el formulario
    Entonces el sistema no registra la reservación
    Y muestra el mensaje de validación correspondiente

  Escenario: CA-05. Rechazar una sala inactiva
    Dado que existe una sala marcada como inactiva
    Y el usuario ha iniciado sesión
    Cuando navega al formulario de nueva reservacion
    Y intenta registrar una reservación para esa sala
    Y envía el formulario
    Entonces el sistema no registra la reservación
    Y muestra un mensaje indicando que la sala no se encuentra disponible para reservación

Escenario: CA-06. Evitar una doble reservación ante solicitudes concurrentes
    Dado que una sala está disponible para un horario específico
    Cuando dos solicitudes intentan registrar simultáneamente una reservación para la misma sala y el mismo horario
    Entonces solo una reservación queda registrada como vigente
    Y la segunda solicitud recibe una respuesta controlada indicando que la sala ya no está disponible