# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Sala(models.Model):
    nombre = models.CharField(max_length=50)
    capacidad = models.IntegerField()
    ubicacion = models.CharField(max_length=100)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Reservacion(models.Model):
    ESTADOS = (
        ('VIGENTE', 'Vigente'),
        ('CANCELADA', 'Cancelada'),
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    asistentes = models.IntegerField()
    proposito = models.CharField(max_length=200)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='VIGENTE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.sala.nombre} - {self.fecha} ({self.hora_inicio} a {self.hora_fin})"