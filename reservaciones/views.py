from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import ReservacionForm
from .services import crear_reservacion, cancelar_reservacion

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
    return render(request, 'reservaciones/crear.html', {'form': form})

@login_required
def cancelar_reservacion_view(request, reservacion_id):
    if request.method == 'POST':
        try:
            cancelar_reservacion(request.user, reservacion_id)
            messages.success(request, 'Reservación cancelada con éxito.')
        except ValidationError as e:
            messages.error(request, e.message)
    return redirect('inicio')