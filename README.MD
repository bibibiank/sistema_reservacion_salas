# Sistema de Reservación de Salas de Estudio

Este proyecto es una aplicación web funcional para consultar disponibilidad y registrar reservaciones de salas de estudio. Fue desarrollado estrictamente bajo las metodologías de Desarrollo Guiado por Pruebas (TDD) y Desarrollo Guiado por Comportamiento (BDD).

## Requisitos Previos
* Python 3.10 o superior.
* Git.

## 1. Clonar el repositorio
Para obtener una copia local del proyecto, ejecuta el siguiente comando en tu terminal:
```bash
git clone <https://github.com/bibibiank/sistema_reservacion_salas.git>
cd <sistema_reservacion_salas>
```

## 2. Creación y activación del Entorno Virtual
El proyecto requiere un entorno virtual aislado para instalar sus dependencias.

Para usuarios de Windows:
```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno
.\.venv\Scripts\activate

# Nota: Si PowerShell bloquea la ejecución por políticas de seguridad, ejecuta primero:
# Set-ExecutionPolicy Unrestricted -Scope CurrentUser
```

Para usuarios de macOS y Linux:

```bash
# Crear el entorno virtual
python3 -m venv .venv

# Activar el entorno
source .venv/bin/activate
```

## 3. Instalación de Dependencias
Con el entorno virtual activado (.venv), instala las herramientas y librerías requeridas (Django, Behave, Selenium, herramientas de cobertura y linter):

```bash
pip install django behave behave-django selenium coverage flake8 radon
```

## 4. Migraciones y Base de Datos Local
El proyecto utiliza SQLite como base de datos local para el entorno de desarrollo. Aplica las migraciones para generar las tablas:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 5. Carga de Datos Iniciales
El sistema requiere un catálogo de salas obligatorio para funcionar. Carga los datos iniciales ejecutando:

```bash
python manage.py loaddata salas_iniciales.json
```

## 6. Ejecución de Pruebas Unitarias (TDD)
El sistema cuenta con una suite de pruebas unitarias automatizadas que cubren las reglas de negocio, modelos, formularios y vistas. Para ejecutar la suite completa de pruebas construidas, utiliza:

```bash
python manage.py test reservaciones
```

## 7. Ejecución de Pruebas de Aceptación (DD)
El sistema cuenta con una suite de pruebas de aceptación automatizadas que validan el comportamiento esperado del sistema a través de los criterios de aceptación definidos en las historias de usuario, utilizando escenarios escritos. Se cubren los flujos principales del sistema, incluyendo el registro y cancelación de reservaciones, validaciones de negocio, restricciones de acceso y mensajes mostrados al usuario. Para ejecutar la suite completa de pruebas de aceptación, utiliza:

```bash
python manage.py behave
```

## 8. Ejecución del Servidor Local
Para levantar la aplicación y visualizarla en el navegador web:

```bash
python manage.py runserver
```
###### Accede a ```http://127.0.0.1:8000/``` desde tu navegador.

## 9. Credenciales de Prueba
Para validar las funcionalidades que requieren autenticación, puedes utilizar el siguiente usuario de prueba generado en las prueba de aceptación (o crear un superusuario nuevo con ```python manage.py createsuperuser```):

#### Usuario: biankk
#### Contraseña: password123

# Cobertura, PEP 8 y Complejidad Ciclomática.

Estando en el mismo entorno virtual (.venv) en la terminal, a continuación, se presentan los comandos para ejectutar personalmente la cobertura, el PEP 8 y la complejidad ciclomática.

## 1. Cobertura (coverage)
Permite medir qué porcentaje del código fuente es ejecutado durante las pruebas automatizadas, ayudando a identificar secciones que aún no están siendo verificadas. Para más información, checar ```/htmlcov```.

```bash
# Corre las pruebas mediante el coverage
coverage run manage.py test

# Genera el reporte en consola
coverage report -m

# Genera la carpeta "/htmlcov"
coverage html
```

## 2. PEP 8 (flake8)
Permite verificar que el código fuente cumpla con las convenciones de estilo y buenas prácticas establecidas por el estándar PEP 8 para Python.

```bash
flake8 . --exclude=.venv,migrations
```

## 3. Complejidad Ciclomática (radon)
Permite analizar la complejidad de funciones y métodos del proyecto, identificando posibles áreas que podrían beneficiarse de una refactorización para mejorar su mantenibilidad. Se utilizó el siguiente comando:

```bash
radon cc . -s -a
```

Y se obtuvo una complejidad ciclomática de ```A (1.6237623762376239)```. El comando puesto en el examen "```radon cc . -s -a -x '*/migrations/*```", no funcionó, por lo que la complejidad obtenida incluye "/migrations"... Aún así, se demuestra que no fue alta.