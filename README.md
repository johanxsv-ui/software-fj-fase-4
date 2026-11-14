# Software FJ | Programación - Fase 4

**Universidad Nacional Abierta y a Distancia (UNAD)**  
**Curso:** Programación 213023 · **Grupo:** 213023A_2204  
**Estudiante:** Johan Sebastian Montagut Vargas  
**Tutora:** VIKY ERIKA SANTANILLA PARRA

## ¿De qué trata el proyecto?

Software FJ es el caso planteado en el Anexo 3 de la Fase 4. La aplicación permite registrar clientes, ofrecer tres servicios (salas, equipos y asesorías) y crear reservas desde un menú de consola.

La idea principal es que el programa no se cierre cuando alguien ingresa un dato equivocado o intenta realizar una operación que no corresponde. Por ejemplo, si la sala ya está ocupada, el sistema rechaza la nueva confirmación, registra el motivo y permite continuar con otra opción.

Está desarrollado en Python con programación orientada a objetos. Los clientes, servicios y reservas se guardan en listas mientras el programa está abierto, **sin utilizar bases de datos**.

## Cómo ejecutarlo

Se necesita Python 3.10 o superior, sin instalar paquetes adicionales. Desde la carpeta principal del proyecto:

```bash
python main.py
```

Con ese comando se abre el menú. Para revisar las operaciones de ejemplo y comprobar las pruebas se utilizan:

```bash
python main.py --demo
python -m unittest discover -s tests -v
```

En Windows también se puede usar `py` y, si el sistema lo requiere, `python3` en Linux o macOS.

La demostración inicia con datos ficticios. Si se cierra la aplicación, las listas se vacían; esto es normal porque el ejercicio no utiliza almacenamiento permanente.

## Qué permite hacer

Primero se registra un cliente y uno de los tres servicios. Después se crea una reserva con las horas de uso y se confirma. Cuando se confirma correctamente, el servicio queda ocupado hasta que la reserva se procese o cancele.

Para repetir una reserva completa en el menú se pueden usar estos datos de ejemplo:

| Paso | Datos |
|---|---|
| 1. Cliente | `C1`, Cliente de prueba, `uno@example.com`, `3000000001` |
| 2. Servicio | Sala `S1`, tarifa `50000`, capacidad `12` |
| 3. Reserva | `R1`, cliente `C1`, sala `S1`, duración `2` horas |
| 4. Confirmación | Impuesto `0.19` y descuento `0.10` |
| 5. Resultado | Total `107100.00` COP. Luego se puede procesar la reserva |

El 19 % y las tarifas se utilizan solo para comprobar los cálculos. No representan una decisión tributaria ni precios reales de una empresa.

## Cómo está organizado el código

| Archivo | Contenido |
|---|---|
| `main.py` | Menú y acceso a la demostración |
| `software_fj/modelos.py` | Clientes, servicios, reservas y reglas de estado |
| `software_fj/errores.py` | Excepciones propias del proyecto |
| `software_fj/gestion.py` | Gestión de listas, manejo de errores y registros |
| `software_fj/demo.py` | Simulación de 29 operaciones |
| `tests/test_sistema.py` | 22 pruebas automatizadas |
| `evidencias/` | Resultados guardados de las ejecuciones y del menú |
| `documentacion/` | Informe académico en PDF y Word |

Se usan clases abstractas, herencia, encapsulación y polimorfismo. La clase `Servicio` establece lo que todos los servicios deben implementar, mientras que `Sala`, `Equipo` y `Asesoria` calculan sus costos según sus propias reglas.

Como el anexo no establece tarifas ni duraciones máximas, se adoptaron estos límites para el ejercicio: sala hasta 12 horas; equipo hasta 24 horas; asesoría entre 1 y 8 horas. Los cálculos se realizan con `Decimal` y se redondean a dos decimales.

La fórmula utilizada es: **total = costo base × (1 − descuento) × (1 + impuesto)**. El método permite dejar el impuesto y el descuento como parámetros opcionales.

## Qué pasa cuando hay un error

Se crearon excepciones personalizadas para datos inválidos, duplicados, registros no encontrados, servicios ocupados, transiciones de reserva incorrectas y errores de cálculo.

`Sistema.ejecutar()` contiene los bloques `try`, `except`, `else` y `finally` para controlar cada operación. También se utiliza `raise ... from` para conservar la causa original. Esto permite mostrar un mensaje, dejar constancia del error y continuar usando el menú.

Las operaciones y sus trazas se registran normalmente en `logs/software_fj.log`, que se crea al ejecutar el programa. Como la carpeta de logs se excluye de Git para evitar archivos cambiantes, la evidencia compartida está en `evidencias/registro_simulacion.txt`. Si no se puede escribir el archivo, el programa lo advierte y muestra el evento en consola.

## Resultados comprobados

En la simulación se ejecutaron **29 operaciones**: 18 terminaron con éxito y 11 tuvieron un rechazo esperado. Entre las situaciones probadas están los datos inválidos, un servicio ocupado, una reserva ya cancelada y un error aritmético provocado. Después de este último, el programa pudo continuar con una consulta normal.

Las **22 pruebas automáticas** finalizaron correctamente. Se pueden consultar sus resultados en `evidencias/pruebas.txt` o volver a ejecutarlas con el comando indicado arriba.

También hay un flujo de GitHub Actions en `.github/workflows/pruebas.yml`, que comprueba el proyecto cuando se suben cambios y cuando se abre un pull request.

## Trabajo colaborativo

La guía establece que la actividad es colaborativa. Este repositorio tiene una plantilla de issues, una plantilla para pull requests y un archivo `CONTRIBUYENDO.md` para organizar el trabajo de los integrantes.

Es importante distinguir la organización del repositorio de la participación real del grupo: **los archivos y plantillas por sí solos no demuestran que hayan participado cinco estudiantes**. Esa parte debe comprobarse con contribuciones propias, revisiones y cambios identificables de cada persona.

## Enlace y documento para entregar

- **Repositorio:** https://github.com/johanxsv-ui/software-fj-fase-4
- **Historial de cambios:** https://github.com/johanxsv-ui/software-fj-fase-4/commits/main
- **Pruebas en GitHub:** https://github.com/johanxsv-ui/software-fj-fase-4/actions
- **Informe PDF:** `documentacion/FASE_4_JOHAN_MONTAGUT_213023A_2204.pdf`
- **Informe Word:** `documentacion/FASE_4_JOHAN_MONTAGUT_213023A_2204.docx`

La entrega del aula requiere el **PDF**; el enlace del repositorio debe compartirse en el foro, como indica la guía de Fase 4. El ZIP se proporciona como respaldo, no como sustituto del informe.

## Referencias consultadas

- Universidad Nacional Abierta y a Distancia. (2026). *Guía para el desarrollo del componente práctico: Fase 4, prácticas simuladas*. Material del curso Programación 213023.
- Universidad Nacional Abierta y a Distancia. (s. f.). *Anexo 3: Problema a desarrollar, Fase 4*. Material del curso Programación 213023.
- Python Software Foundation. (s. f.). [Errores y excepciones](https://docs.python.org/es/3.12/tutorial/errors.html).
- Python Software Foundation. (s. f.). [Módulo logging](https://docs.python.org/es/3.12/library/logging.html).
- Python Software Foundation. (s. f.). [Módulo abc](https://docs.python.org/es/3.12/library/abc.html).
- Python Software Foundation. (s. f.). [Módulo decimal](https://docs.python.org/es/3.12/library/decimal.html).

En la preparación y revisión se utilizaron herramientas digitales, incluida inteligencia artificial. Las pruebas y el funcionamiento pueden verificarse directamente con el código.
