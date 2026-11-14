"""Simulación reproducible; todos los clientes son datos ficticios de prueba."""
from .modelos import Sala, Equipo, Asesoria  # Incluye los tres comportamientos polimórficos.


def simular(sistema):  # Recibe un sistema vacío creado exclusivamente para la demostración.
    casos = [  # Cada fila contiene descripción, función y resultado esperado.
        ('Cliente válido C1', lambda: sistema.registrar_cliente('C1', 'Cliente de prueba uno', 'uno@example.com', '3000000001'), True),  # Registra un cliente correcto.
        ('Correo inválido', lambda: sistema.registrar_cliente('C2', 'Cliente prueba', 'invalido', '3000000002'), False),  # Rechaza el correo.
        ('Cliente duplicado', lambda: sistema.registrar_cliente('C1', 'Duplicado', 'dos@example.com', '3000000002'), False),  # Protege la identidad.
        ('Parámetros faltantes', lambda: sistema.registrar_cliente('C2', 'Incompleto'), False),  # Controla TypeError en la frontera.
        ('Cliente válido C2', lambda: sistema.registrar_cliente('C2', 'Cliente de prueba dos', 'dos@example.com', '3000000002'), True),  # Demuestra continuidad tras errores.
        ('Crear sala S1', lambda: sistema.registrar_servicio(Sala, 'S1', 'Sala de reuniones', 50000, 12), True),  # Registra una sala válida.
        ('Servicio con tarifa negativa', lambda: sistema.registrar_servicio(Sala, 'S0', 'Inválida', -1, 12), False),  # Rechaza precios negativos.
        ('Crear equipo E1', lambda: sistema.registrar_servicio(Equipo, 'E1', 'Proyector', 20000), True),  # Incluye preparación de 5000 COP.
        ('Crear asesoría A1', lambda: sistema.registrar_servicio(Asesoria, 'A1', 'Sesión técnica', 80000, 'Redes', '1.5'), True),  # Usa factor de complejidad.
        ('Servicio sin especialidad', lambda: sistema.registrar_servicio(Asesoria, 'A0', 'Inválida', 80000, ''), False),  # Valida campos específicos.
        ('Crear reserva R1', lambda: sistema.crear_reserva('R1', 'C1', 'S1', 2), True),  # Crea una reserva pendiente.
        ('Confirmar R1 con impuesto y descuento', lambda: sistema.reserva('R1').confirmar('0.19', '0.10'), True),  # Debe producir 107100.00 COP.
        ('Crear reserva competidora R2', lambda: sistema.crear_reserva('R2', 'C2', 'S1', 1), True),  # Crear no implica ocupar.
        ('Confirmar servicio ocupado', lambda: sistema.reserva('R2').confirmar(), False),  # Rechaza doble ocupación.
        ('Cliente inexistente', lambda: sistema.crear_reserva('RX', 'C9', 'S1', 1), False),  # Evita referencias inexistentes.
        ('Duración inválida', lambda: sistema.crear_reserva('RX', 'C1', 'E1', 0), False),  # Rechaza duración cero.
        ('Procesar R1', lambda: sistema.reserva('R1').procesar(), True),  # Completa y libera la sala.
        ('Confirmar R2 tras liberación', lambda: sistema.reserva('R2').confirmar(), True),  # Demuestra recuperación del recurso.
        ('Cancelar R2', lambda: sistema.reserva('R2').cancelar(), True),  # Libera una reserva confirmada.
        ('Procesar reserva cancelada', lambda: sistema.reserva('R2').procesar(), False),  # Protege estados finales.
        ('Crear reserva de equipo R3', lambda: sistema.crear_reserva('R3', 'C1', 'E1', 3), True),  # Prepara costo de 65000 COP.
        ('Confirmar R3', lambda: sistema.reserva('R3').confirmar(), True),  # Comprueba fórmula de equipo.
        ('Procesar R3', lambda: sistema.reserva('R3').procesar(), True),  # Cierra el préstamo.
        ('Crear reserva de asesoría R4', lambda: sistema.crear_reserva('R4', 'C2', 'A1', 2), True),  # Prepara costo de 240000 COP.
        ('Confirmar R4 con descuento inválido', lambda: sistema.reserva('R4').confirmar(descuento='1.20'), False),  # No ocupa la asesoría si falla el cálculo.
        ('Confirmar R4 después del error', lambda: sistema.reserva('R4').confirmar(), True),  # Comprueba recuperación tras fallo monetario.
        ('Procesar R4', lambda: sistema.reserva('R4').procesar(), True),  # Completa la asesoría.
        ('Falla inesperada controlada', lambda: 1 / 0, False),  # Inyecta una falla aritmética para comprobar la última frontera.
        ('Consulta final tras los errores', lambda: len(sistema.reservas), True),  # Verifica que el programa sigue activo.
    ]  # Finaliza la definición de escenarios independientes de la interfaz.
    resultados = []  # Conserva resultados solo en memoria durante la ejecución.
    for indice, (nombre, funcion, esperado) in enumerate(casos, 1):  # Ejecuta los escenarios de forma secuencial.
        resultado = sistema.ejecutar(nombre, funcion)  # Registra éxito o fallo sin detener el ciclo.
        coincide = resultado.exito == esperado  # Comprueba que el comportamiento corresponde al escenario.
        resultados.append((indice, nombre, esperado, resultado.exito, coincide))  # Guarda la matriz de verificación.
        estado = 'ÉXITO' if resultado.exito else 'ERROR CONTROLADO'  # Diferencia un rechazo esperado de un defecto.
        print(f'{indice:02d} | {estado} | {nombre} | {"VERIFICADO" if coincide else "FALLO"}')  # Muestra la evidencia real.
        if resultado.exito and resultado.valor is not None:  # Imprime el valor cuando resulta significativo.
            print('     ', resultado.valor.describir() if hasattr(resultado.valor, 'describir') else resultado.valor)  # Describe objetos sin direcciones de memoria.
    print(f'RESUMEN: {sum(fila[4] for fila in resultados)}/{len(resultados)} resultados esperados.')  # Resume el comportamiento observado.
    return resultados  # Permite que las pruebas comprueben toda la simulación.
