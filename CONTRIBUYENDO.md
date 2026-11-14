# Cómo trabajar en equipo en Software FJ

**Curso:** Programación 213023 · **Grupo:** 213023A_2204  
**Tutora:** VIKY ERIKA SANTANILLA PARRA

La guía de la Fase 4 pide que los cinco integrantes participen en el desarrollo del proyecto. Para que esa participación se pueda revisar en GitHub, cada persona debe trabajar desde su propia cuenta y dejar identificados sus cambios.

## Pasos para hacer un aporte

1. Revisar el README y ejecutar el programa para conocer cómo funciona
2. Crear o elegir una tarea en la sección **Issues** y explicar qué se va a revisar
3. Crear una rama con un nombre sencillo, por ejemplo `pruebas/nuevos-casos` o `mejora/validaciones`
4. Hacer cambios pequeños y registrar commits que expliquen qué se modificó
5. Ejecutar `python -m unittest discover -s tests -v` y `python main.py --demo`
6. Abrir un pull request hacia `main`, explicar la mejora y pedir revisión a otro integrante
7. Incorporar las observaciones y completar la revisión antes de unir los cambios

Para el informe final, conviene guardar el enlace de cada issue, rama, commit y pull request que corresponda a las tareas reales de los compañeros. No basta con escribir el nombre de una persona en el documento si no existen aportes que puedan comprobarse.

## Temas que se pueden revisar

- Casos adicionales de validación y recuperación de errores
- Mensajes del menú que ayuden al usuario a corregir un dato
- Consistencia entre los logs, las pruebas y los resultados de la simulación
- Correcciones de documentación o mejoras de accesibilidad

**Nota:** este archivo explica una forma de organizar el trabajo en grupo, pero no representa por sí solo evidencias de participación de cinco estudiantes. Los aportes deben aparecer realmente en el historial de GitHub.
