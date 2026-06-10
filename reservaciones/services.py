from datetime import datetime, date
from .models import Reservacion
from django.core.exceptions import ValidationError

def crear_reservacion(usuario, sala, fecha, hora_inicio, hora_fin, asistentes, proposito):
    if asistentes > sala.capacidad:
        raise ValidationError("El número de asistentes supera la capacidad de la sala.")
    inicio_dt = datetime.combine(fecha, hora_inicio)
    fin_dt = datetime.combine(fecha, hora_fin)
    duracion_minutos = (fin_dt - inicio_dt).total_seconds() / 60
    
    if duracion_minutos < 30 or duracion_minutos > 120:
        raise ValidationError("La reservación debe durar entre 30 minutos y 2 horas.")
    traslapes = Reservacion.objects.filter(
        sala=sala,
        fecha=fecha,
        estado='VIGENTE',
        hora_inicio__lt=hora_fin,
        hora_fin__gt=hora_inicio
    )
    if traslapes.exists():
        raise ValidationError("La sala ya tiene una reservación vigente en ese horario.")
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