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

  Escenario: CA-08. Impedir que un usuario cancele una reservación ajena
    Dado que existe una reservación vigente perteneciente a otro usuario
    Y el usuario autenticado intenta cancelarla
    Entonces el sistema rechaza la operación
    Y mantiene la reservación en estado "VIGENTE"
    Y responde sin revelar información sensible de la reservación.

  Escenario: CA-09. Impedir cancelación fuera del periodo permitido
    Dado que el usuario es propietario de una reservación vigente
    Y faltan 60 minutos o menos para su inicio
    Cuando intenta cancelarla
    Entonces el sistema rechaza la operación
    Y mantiene la reservación en estado "VIGENTE"
    Y muestra un mensaje indicando que el periodo de cancelación ha concluido.

  Escenario: CA-10. Impedir cancelar nuevamente una reservación cancelada
    Dado que el usuario es propietario de una reservación cancelada
    Cuando intenta cancelarla nuevamente
    Entonces el sistema rechaza la operación
    Y conserva el estado "CANCELADA"
    Y muestra un mensaje indicando que la reservación ya fue cancelada.