from .models import Reservacion
from django.core.exceptions import ValidationError

def crear_reservacion(usuario, sala, fecha, hora_inicio, hora_fin, asistentes, proposito):
    # Regla RN-02: Validar capacidad
    if asistentes > sala.capacidad:
        raise ValidationError("El número de asistentes supera la capacidad de la sala.")
    reservacion = Reservacion.objects.create(
        usuario=usuario,
        sala=sala,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        asistentes=asistentes,
        proposito=proposito,
        estado='VIGENTE'
    )
    return reservacion