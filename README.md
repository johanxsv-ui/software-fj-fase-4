# Software FJ — Fase 4 de Programación 213023

Proyecto académico para gestionar clientes, salas, equipos, asesorías y reservas mediante programación orientada a objetos. Solo usa la biblioteca estándar de Python. No requiere bases de datos, servicios externos ni instalación de paquetes.

## Ejecución rápida

Requisito: Python 3.10 o posterior. Verificado con Python 3.12.14.

1. Descomprima el proyecto y abra una terminal dentro de la carpeta `Software_FJ`.
2. Ejecute `python main.py --demo` para reproducir las 29 operaciones.
3. Ejecute `python main.py` para utilizar el menú interactivo.
4. Ejecute `python -m unittest discover -s tests -v` para correr las 22 pruebas.

En Windows puede sustituir `python` por `py`. En Linux/macOS puede usar `python3`. El programa empieza con listas vacías cada vez. La demo carga sus propios datos ficticios; no los conserva para otra ejecución.

## Guion de uso del menú

- Opción 1: cliente C1, nombre Cliente de prueba, correo uno@example.com y teléfono 3000000001.
- Opción 2: tipo 1 (sala), ID S1, nombre Sala de reuniones, tarifa 50000 y capacidad 12.
- Opción 3: reserva R1, cliente C1, servicio S1 y duración 2.
- Opción 4: reserva R1, impuesto 0.19 y descuento 0.10. Total esperado: 107100.00 COP.
- Opción 5: reserva R1. Queda COMPLETADA y se libera el recurso.
- Opción 7: muestra las tres colecciones.
- Opción 0: cierra la sesión.

Use punto decimal, no separadores de miles. Los impuestos y descuentos se expresan como fracción: 0.19 equivale a 19 %. El 19 % es solo un parámetro didáctico, no una determinación tributaria del servicio.

## Estructura

| Archivo | Responsabilidad |
|---|---|
| main.py | Menú y selección de modo demo |
| software_fj/modelos.py | Entidades, validación, servicios, costos y estados |
| software_fj/errores.py | Excepciones personalizadas |
| software_fj/gestion.py | Listas en memoria, operaciones protegidas y logs |
| software_fj/demo.py | 29 operaciones secuenciales con resultado esperado |
| tests/test_sistema.py | 22 pruebas automatizadas con casos adicionales |
| evidencias/simulacion.txt | Salida real de la simulación |
| evidencias/pruebas.txt | Salida real de unittest |
| evidencias/menu.txt | Salida real de una sesión automatizada del menú |
| logs/software_fj.log | Eventos y trazas reales de la ejecución |

Las instrucciones ejecutables están comentadas línea por línea. Las pruebas también incluyen comentarios. Las líneas de documentación, en blanco o de cierre se explican mediante su contexto.

## Modelo y reglas adoptadas

El anexo no fija tarifas, duración máxima ni política de ocupación. Se adoptan estas reglas para la simulación:

- Una instancia de servicio representa un único recurso. Puede existir más de una reserva pendiente; solo una puede confirmarse y ocupar ese recurso a la vez.
- No se administra calendario ni concurrencia entre procesos. La ocupación dura desde la confirmación hasta la cancelación o el procesamiento.
- Sala: más de 0 y hasta 12 horas; costo = tarifa × horas; capacidad entera de 1 a 500.
- Equipo: más de 0 y hasta 24 horas; costo = tarifa × horas + cargo de preparación, por defecto 5000 COP.
- Asesoría: de 1 a 8 horas; costo = tarifa × horas × factor; factor de 1 a 3.
- Tarifa positiva, finita y hasta 100000000; costo base positivo y hasta el mismo límite.
- Total = costo base × (1 − descuento) × (1 + impuesto), redondeado a dos decimales con ROUND_HALF_UP. Impuesto y descuento están entre 0 y 1.
- `calcular_costo(horas)`, `calcular_costo(horas, impuesto)` y `calcular_costo(horas, impuesto, descuento)` son variantes mediante parámetros opcionales. Python no ofrece sobrecarga por cantidad de argumentos mediante definiciones repetidas; se aplica la alternativa de parámetros opcionales admitida por el anexo.
- El costo se fija al confirmar. Procesar representa terminar la prestación; no ejecuta pagos ni integra una pasarela.
- Estados: PENDIENTE permite confirmar o cancelar; CONFIRMADA permite procesar o cancelar; CANCELADA y COMPLETADA son finales.
- Las listas internas no se exponen para inserción o borrado: las propiedades devuelven tuplas de referencias.
- El correo se valida por formato básico, sin consultar si existe. Los teléfonos admiten 7 a 15 dígitos, con + inicial opcional.

## Excepciones y estabilidad

La interfaz y la demo pasan cada operación por `Sistema.ejecutar`. Esta frontera registra errores, conserva la causa con `raise ... from`, devuelve un resultado controlado y usa `finally` para registrar el cierre. `Reserva.confirmar` usa `try/except/else` y solo cambia el estado después de calcular el importe y obtener el recurso.

Los métodos de dominio lanzan excepciones al consumidor. Si se utilizan desde otro programa, deben invocarse dentro de `Sistema.ejecutar` o de una frontera equivalente para que queden registradas. No se promete recuperar un cierre del sistema operativo, interrupción forzada, agotamiento de memoria o mutación deliberada de atributos privados.

El programa solo escribe archivos para eventos y errores. Los `.txt` de evidencias se obtuvieron redirigiendo la salida de las ejecuciones, no son una persistencia de clientes o reservas. Los datos comerciales se pierden al cerrar. Si el archivo de log no puede abrirse o escribirse, se informa y se envía el evento a la salida de error; no se afirma que quedó guardado en disco.

## Resultados verificados

- 29 de 29 escenarios con el comportamiento esperado: 18 éxitos y 11 errores controlados.
- 22 pruebas automatizadas aprobadas; varias prueban múltiples entradas con subcasos.
- Estado final de la demo: 2 clientes, 3 servicios y 4 reservas. R1, R3 y R4 completadas; R2 cancelada. Los tres servicios quedan libres.
- Costos: R1 = 107100.00; R2 = 50000.00 (cancelada, no se suma a prestaciones completadas); R3 = 65000.00; R4 = 240000.00 COP.
- Total de prestaciones completadas: 412100.00 COP. Es una suma de simulación, no ingresos ni pagos reales.

## Publicación y colaboración en GitHub (pendientes de completar)

El repositorio remoto aún no está creado ni se publicó en el foro. La guía exige ambas acciones y aunque se confirmó la conexión de GitHub, sus operaciones de repositorio no quedaron disponibles en esta sesión; tampoco existe autenticación activa en la consola ni en el navegador de trabajo. El proyecto está preparado para cargarse sin modificaciones funcionales.

1. Cree un repositorio `software-fj-fase4` en su cuenta de GitHub; configure acceso para que el tutor pueda revisarlo.
2. Suba `main.py`, `README.md`, `.gitignore`, las carpetas `software_fj`, `tests` y `evidencias`. Las evidencias solo contienen datos ficticios. Puede añadir el log de muestra si se solicita; no incluya contactos reales en un repositorio público.
3. Abra el repositorio y compruebe que aparecen archivos y carpetas en la raíz correcta.
4. Copie la URL real y sustitúyala en la sección de repositorio del Word. Exporte nuevamente a PDF.
5. Comparta el enlace en el foro y entregue el PDF en el entorno de evaluación.

No se inventó un historial de commits ni la participación de otros integrantes. La guía define actividad colaborativa para cinco estudiantes; este paquete desarrolla la solución técnica con un solo autor identificado, sin afirmar que exista autorización institucional para sustituir el componente colaborativo.

## Fuentes

- Universidad Nacional Abierta y a Distancia. (2026). Guía para el desarrollo del componente práctico — Fase 4 — Prácticas simuladas. Material suministrado del curso 213023.
- Universidad Nacional Abierta y a Distancia. (s. f.). Anexo 3 — Problema a desarrollar Fase 4. Material suministrado del curso 213023.
- Python Software Foundation. (s. f.). Errores y excepciones. https://docs.python.org/es/3.12/tutorial/errors.html
- Python Software Foundation. (s. f.). abc — Abstract Base Classes. https://docs.python.org/es/3.12/library/abc.html
- Python Software Foundation. (s. f.). decimal — Decimal fixed-point and floating-point arithmetic. https://docs.python.org/es/3.12/library/decimal.html
- Python Software Foundation. (s. f.). logging — Logging facility for Python. https://docs.python.org/es/3.12/library/logging.html

El código es una solución preparada con asistencia de inteligencia artificial para esta actividad. Debe revisarse y comprenderse antes de su sustentación; su uso debe ajustarse a las indicaciones del curso.

## Verificación continua y aportes del grupo

Al publicar el repositorio, GitHub Actions ejecutará sintaxis, 22 pruebas y 29 simulaciones en cada push y pull request mediante `.github/workflows/pruebas.yml`. Incluye `CONTRIBUYENDO.md`, plantilla de tarea y plantilla de pull request para organizar el trabajo posterior. Estos archivos son preparación, no evidencia de trabajo conjunto ya realizado.
