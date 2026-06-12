Característica: Cancelar una reservación de sala
  Como usuario autenticado
  Quiero poder cancelar mis reservaciones vigentes
  Para liberar la sala cuando ya no la necesite, respetando las reglas del sistema

  Escenario: CA-07. Cancelar una reservación vigente con anticipación suficiente
    Dado que el usuario ha iniciado sesión
    Y es propietario de una reservación vigente cuyo inicio ocurrirá dentro de más de 60 minutos
    Cuando confirma la cancelación
    Entonces el sistema cambia el estado de la reservación a "CANCELADA"
    Y registra la fecha y hora de cancelación
    Y muestra un mensaje de confirmación
    Y la sala vuelve a estar disponible para ese horario.

