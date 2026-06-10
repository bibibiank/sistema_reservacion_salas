from .models import Reservacion

def crear_reservacion(usuario, sala, fecha, hora_inicio, hora_fin, asistentes, proposito):
    # Guardamos la reservación directo en la base de datos
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
