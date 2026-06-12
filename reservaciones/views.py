from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import ReservacionForm
from .services import crear_reservacion, cancelar_reservacion
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import PermissionDenied

from .models import Reservacion 

@login_required
def crear_reservacion_view(request):
    if request.method == 'POST':
        form = ReservacionForm(request.POST)
        if form.is_valid():
            try:
                crear_reservacion(
                    usuario=request.user,
                    sala=form.cleaned_data['sala'],
                    fecha=form.cleaned_data['fecha'],
                    hora_inicio=form.cleaned_data['hora_inicio'],
                    hora_fin=form.cleaned_data['hora_fin'],
                    asistentes=form.cleaned_data['asistentes'],
                    proposito=form.cleaned_data['proposito']
                )
                messages.success(request, 'Reservación registrada con éxito.')
                return redirect('inicio')
            except ValidationError as e:
                form.add_error(None, e.message)
    else:
        form = ReservacionForm()
    return render(request, 'reservaciones/crear_reservacion.html', {'form': form})

@login_required
def cancelar_reservacion_view(request, reservacion_id):
    if request.method == 'POST':
        try:
            cancelar_reservacion(request.user, reservacion_id)
            messages.success(request, "Reservación cancelada con éxito.")
        except ValidationError as e:
            messages.error(request, e.message)
            
    return redirect('inicio')

@login_required
def lista_reservaciones_view(request):
    reservaciones = Reservacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'reservaciones/lista.html', {'reservaciones': reservaciones})