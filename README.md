# Software FJ - Programación Fase 4

**Estudiante:** Johan Sebastian Montagut Vargas  
**Curso:** Programación 213023  
**Grupo:** 213023A_2204  
**Tutora:** VIKY ERIKA SANTANILLA PARRA

## Mi proyecto

Para esta fase desarrollé Software FJ, un programa de consola en Python con el que puedo registrar clientes, administrar salas, equipos y asesorías, y gestionar sus reservas. Separé el trabajo en clases para que el código fuera más fácil de entender y mantener.

Me concentré en el manejo de errores. Si ingreso un dato inválido, intento registrar algo repetido o confirmo una reserva cuando el servicio está ocupado, el sistema me muestra el problema, lo guarda en el registro de eventos y me permite seguir trabajando sin cerrar la aplicación.

## Cómo lo ejecuto

Utilizo Python 3.10 o una versión superior. No necesito instalar librerías adicionales. Abro una terminal en la carpeta principal y ejecuto:

```bash
python main.py
```

Para reproducir los casos de prueba y comprobar los resultados, uso:

```bash
python main.py --demo
python -m unittest discover -s tests -v
```

El programa guarda la información en memoria mientras está abierto. Cuando lo cierro, los registros se pierden, porque esta práctica no incluye una base de datos.

## Qué implementé

- Creé las clases de clientes, servicios y reservas. Para los servicios utilicé herencia y polimorfismo con `Sala`, `Equipo` y `Asesoria`.
- Validé datos, duración, disponibilidad y cambios de estado de las reservas.
- Implementé excepciones propias, bloques `try/except/else/finally` y encadenamiento con `raise ... from`.
- Registré operaciones y errores con `logging`. El archivo se genera en `logs/software_fj.log` cuando ejecuto el programa.
- Preparé una simulación con 29 operaciones, de las cuales 18 terminan correctamente y 11 producen errores controlados que se esperan en la prueba.
- Ejecuté 22 pruebas automatizadas para revisar cálculos, validaciones, reservas, excepciones y continuidad del sistema.

## Archivos del proyecto

| Archivo o carpeta | Contenido |
|---|---|
| `main.py` | Menú principal y demostración |
| `software_fj/` | Clases, validaciones, gestión de reservas y excepciones |
| `tests/` | Pruebas automatizadas |
| `evidencias/` | Salidas de las pruebas, simulaciones y registros de eventos |
| `documentacion/` | Mi informe de la Fase 4 en PDF y Word |
| `.github/workflows/` | Comprobación automática de las pruebas en GitHub |

Los archivos de `evidencias/` muestran los resultados que obtuve. También puedo repetir las pruebas con los comandos anteriores. Los porcentajes y las tarifas de ejemplo se usan únicamente para comprobar las operaciones del ejercicio.

## Informe

Mi informe se encuentra en [documentacion](documentacion/), con el nombre `FASE_4_JOHAN_MONTAGUT_213023A_2204` en PDF y Word. Allí expliqué el diseño, el control de errores, las simulaciones y las conclusiones.

El repositorio permite consultar mi trabajo y el historial de cambios. Para el componente colaborativo de la actividad, cualquier aporte de otro integrante debe quedar registrado con sus propios cambios en GitHub.
