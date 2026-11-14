"""Pruebas de invariantes, recuperación, dinero y registro; solo biblioteca estándar."""
import contextlib  # Redirige la salida de la simulación durante las pruebas.
import io  # Captura texto sin archivos de negocio.
from decimal import Decimal  # Compara importes exactos.
from pathlib import Path  # Lee el archivo real de eventos.
import tempfile  # Aísla los logs de cada prueba.
import unittest  # Ejecuta pruebas sin instalar paquetes externos.
from unittest.mock import patch  # Simula fallas del disco y del cálculo.
from software_fj.modelos import Entidad, Servicio, Cliente, Sala, Equipo, Asesoria, Reserva, Estado  # Entidades bajo prueba.
from software_fj.gestion import Sistema, crear_logger  # Frontera de errores y registro.
from software_fj.errores import ValidacionError, CalculoError, EstadoError, DisponibilidadError, DuplicadoError  # Excepciones esperadas.
from software_fj.demo import simular  # Escenario completo.


class PruebasSistema(unittest.TestCase):  # Agrupa pruebas aisladas del sistema.
    def setUp(self):  # Crea un contexto nuevo antes de cada método.
        self.temporal = tempfile.TemporaryDirectory()  # Evita mezclar evidencias de pruebas diferentes.
        self.ruta = Path(self.temporal.name) / 'pruebas.log'  # Selecciona un log temporal.
        self.sistema = Sistema(crear_logger(self.ruta))  # Inicializa listas vacías.
        self.cliente = Cliente('C', 'Prueba', 'prueba@example.com', '3000000000')  # Usa datos ficticios.
        self.sala = Sala('S', 'Sala', 50000, 10)  # Fija una tarifa conocida.

    def tearDown(self):  # Libera los recursos después de cada prueba.
        for handler in self.sistema.logger.handlers[:]:  # Recorre manejadores abiertos.
            handler.close()  # Cierra el archivo también en Windows.
            self.sistema.logger.removeHandler(handler)  # Evita referencias a archivos ya eliminados.
        self.temporal.cleanup()  # Elimina los logs temporales de prueba.

    def test_abstraccion(self):  # Verifica que los contratos no se puedan instanciar.
        for clase in (Entidad, Servicio):  # Comprueba las dos clases abstractas exigidas.
            with self.subTest(clase=clase), self.assertRaises(TypeError):  # Espera rechazo por métodos abstractos.
                clase('X')  # Intenta crear una entidad incompleta.

    def test_datos_cliente_invalidos(self):  # Comprueba campos personales sin aceptar registros corruptos.
        for datos in [('C', '', 'a@b.co', '3000000000'), ('C', 'Prueba', 'mal', '3000000000'), ('C', 'Prueba', 'a@b.co', 'abc')]:  # Cubre tres reglas distintas.
            with self.subTest(datos=datos), self.assertRaises(ValidacionError):  # Espera errores de validación.
                Cliente(*datos)  # Construye con cada entrada defectuosa.

    def test_contacto_atomico(self):  # Comprueba que un error no cambie parcialmente el contacto.
        with self.assertRaises(ValidacionError):  # El teléfono nuevo es inválido.
            self.cliente.actualizar_contacto('nuevo@example.com', 'x')  # Intenta cambiar ambos campos.
        self.assertEqual(self.cliente.correo, 'prueba@example.com')  # Conserva el correo anterior.

    def test_identidad_encapsulada(self):  # Protege identidad y estado contra asignaciones públicas.
        with self.assertRaises(AttributeError):  # La propiedad no tiene setter.
            self.cliente.identificador = 'OTRO'  # Intenta saltarse la validación.
        reserva = Reserva('R', self.cliente, self.sala, 1)  # Prepara un estado válido.
        with self.assertRaises(AttributeError):  # El estado también es de solo lectura.
            reserva.estado = Estado.COMPLETADA  # Impide terminar sin procesar.

    def test_variantes_calculo(self):  # Comprueba base, impuesto y descuento opcionales.
        self.assertEqual(self.sala.calcular_costo(2), Decimal('100000.00'))  # Valida la tarifa base.
        self.assertEqual(self.sala.calcular_costo(2, '0.19'), Decimal('119000.00'))  # Valida la variante con impuesto.
        self.assertEqual(self.sala.calcular_costo(2, '0.19', '0.10'), Decimal('107100.00'))  # Valida las dos opciones juntas.

    def test_polimorfismo(self):  # Verifica fórmulas distintas mediante una misma interfaz.
        servicios = [self.sala, Equipo('E', 'Equipo', 20000), Asesoria('A', 'Asesoría', 80000, 'Redes', '1.5')]  # Reúne subclases.
        self.assertEqual([s.calcular_costo(2) for s in servicios], [Decimal('100000'), Decimal('45000'), Decimal('240000')])  # Compara resultados independientes.

    def test_numeros_no_finitos(self):  # Rechaza valores que pueden romper comparaciones y cálculos.
        for valor in ('NaN', 'Infinity', '-Infinity', True, None, [], 0, -1):  # Cubre casos límite de tarifas.
            with self.subTest(valor=valor), self.assertRaises(ValidacionError):  # Todos deben fallar antes de crear el servicio.
                Sala('X', 'Sala', valor, 10)  # Prueba la frontera numérica.

    def test_parametros_especializados(self):  # Verifica restricciones propias de las subclases.
        constructores = [lambda: Sala('S', 'Sala', 1, True), lambda: Equipo('E', 'Equipo', 1, -1), lambda: Asesoria('A', 'Asesoría', 1, 'Redes', 4)]  # Tres configuraciones inválidas.
        for construir in constructores:  # Evalúa cada regla particular.
            with self.assertRaises(ValidacionError):  # Requiere un rechazo de dominio.
                construir()  # Intenta construir el servicio.

    def test_limites_duracion(self):  # Verifica mínimos y máximos de cada servicio.
        servicios = [(self.sala, 12, 13), (Equipo('E', 'Equipo', 1), 24, 25), (Asesoria('A', 'Asesoría', 1, 'Redes'), 8, 9)]  # Define bordes válidos e inválidos.
        for servicio, valido, invalido in servicios:  # Aplica la misma prueba a las tres subclases.
            self.assertEqual(servicio.validar_parametros(valido), valido)  # Acepta el máximo exacto.
            with self.assertRaises(ValidacionError):  # Rechaza el siguiente valor.
                servicio.validar_parametros(invalido)  # Comprueba el máximo.
        with self.assertRaises(ValidacionError):  # La asesoría exige al menos una hora.
            servicios[-1][0].validar_parametros('0.5')  # Comprueba el límite inferior.

    def test_descuento_total_y_redondeo(self):  # Evita confundir costo cero con un error.
        self.assertEqual(self.sala.calcular_costo(1, descuento=1), Decimal('0.00'))  # Acepta descuento del 100 por ciento.
        self.assertEqual(Sala('S2', 'Sala', '0.335', 1).calcular_costo(1), Decimal('0.34'))  # Verifica redondeo monetario.

    def test_calculo_inconsistente(self):  # Simula una subclase defectuosa que devuelve un costo negativo.
        with patch.object(self.sala, 'costo_base', return_value=Decimal('-1')):  # Inyecta la falla sin modificar código productivo.
            with self.assertRaises(CalculoError):  # El cálculo común debe detectar la inconsistencia.
                self.sala.calcular_costo(1)  # Ejecuta la validación del resultado.

    def test_error_confirmacion_no_ocupa(self):  # Comprueba que un cálculo fallido no deje el recurso bloqueado.
        reserva = Reserva('R', self.cliente, self.sala, 1)  # Prepara una reserva pendiente.
        with self.assertRaises(CalculoError):  # Descuento mayor que uno no está permitido.
            reserva.confirmar(descuento=2)  # Intenta una cotización inválida.
        self.assertEqual(reserva.estado, Estado.PENDIENTE)  # El estado no avanzó.
        self.assertIsNone(reserva.total)  # No quedó un importe parcial.
        self.assertTrue(self.sala.disponible)  # El servicio continúa libre.

    def test_doble_reserva_y_recuperacion(self):  # Verifica exclusión y liberación del recurso.
        r1, r2 = Reserva('R1', self.cliente, self.sala, 1), Reserva('R2', self.cliente, self.sala, 1)  # Crea dos candidatas.
        r1.confirmar()  # La primera ocupa el recurso.
        with self.assertRaises(DisponibilidadError):  # La segunda no puede ocuparlo simultáneamente.
            r2.confirmar()  # Intenta la confirmación competidora.
        self.assertEqual(r2.estado, Estado.PENDIENTE)  # Conserva su estado anterior.
        r1.procesar()  # Libera al terminar la primera prestación.
        r2.confirmar()  # Ahora puede reservar el recurso.
        self.assertEqual(r2.estado, Estado.CONFIRMADA)  # Comprueba la recuperación.

    def test_cancelacion_pendiente_no_libera_otra(self):  # Protege la ocupación de otra reserva.
        r1, r2 = Reserva('R1', self.cliente, self.sala, 1), Reserva('R2', self.cliente, self.sala, 1)  # Crea dos reservas.
        r1.confirmar()  # Ocupa con la primera.
        r2.cancelar()  # Cancela la segunda, que no era dueña del recurso.
        self.assertFalse(self.sala.disponible)  # La primera conserva la ocupación.

    def test_cancelacion_confirmada_libera(self):  # Verifica la liberación por cancelación del dueño.
        reserva = Reserva('R', self.cliente, self.sala, 1)  # Crea una reserva.
        reserva.confirmar()  # Ocupa el recurso.
        reserva.cancelar()  # Ejecuta la transición permitida.
        self.assertTrue(self.sala.disponible)  # Comprueba disponibilidad recuperada.
        self.assertEqual(reserva.estado, Estado.CANCELADA)  # Confirma el estado final.

    def test_estados_finales(self):  # Impide repetir operaciones sobre una reserva terminada.
        reserva = Reserva('R', self.cliente, self.sala, 1)  # Inicia pendiente.
        reserva.confirmar()  # Confirma normalmente.
        reserva.procesar()  # Completa la prestación.
        for operacion in (reserva.confirmar, reserva.cancelar, reserva.procesar):  # Revisa tres transiciones prohibidas.
            with self.assertRaises(EstadoError):  # Ninguna debe modificar el estado final.
                operacion()  # Intenta repetir o revertir el proceso.

    def test_procesar_pendiente(self):  # Exige confirmación previa al procesamiento.
        with self.assertRaises(EstadoError):  # El estado pendiente no permite prestar el servicio.
            Reserva('R', self.cliente, self.sala, 1).procesar()  # Ejecuta la transición inválida.

    def test_duplicado_no_muta_lista(self):  # Mantiene una sola entidad por identidad.
        self.sistema.registrar_cliente('C', 'Prueba', 'a@example.com', '3000000000')  # Registra el cliente inicial.
        with self.assertRaises(DuplicadoError):  # La segunda inserción debe rechazarse.
            self.sistema.registrar_cliente('C', 'Otro', 'b@example.com', '3000000001')  # Repite el ID.
        self.assertEqual(len(self.sistema.clientes), 1)  # Comprueba integridad de la colección.
        self.assertIsInstance(self.sistema.clientes, tuple)  # No entrega la lista mutable al consumidor.

    def test_faltantes_y_log_encadenado(self):  # Verifica causa original, registro y continuidad.
        resultado = self.sistema.ejecutar('datos incompletos', self.sistema.registrar_cliente, 'C')  # Provoca TypeError por parámetros faltantes.
        self.assertFalse(resultado.exito)  # El fallo se comunica como resultado controlado.
        registro = self.ruta.read_text(encoding='utf-8')  # Inspecciona la evidencia real.
        for fragmento in ('TypeError', 'OperacionError', 'FIN | datos incompletos'):  # Busca causa, contexto y cierre.
            self.assertIn(fragmento, registro)  # Exige trazabilidad completa.
        self.assertTrue(self.sistema.ejecutar('continuar', lambda: 42).exito)  # Comprueba que la frontera sigue operativa.

    def test_excepcion_inesperada(self):  # Comprueba el último nivel de protección.
        resultado = self.sistema.ejecutar('división', lambda: 1 / 0)  # Inyecta una falla no prevista en el dominio.
        self.assertFalse(resultado.exito)  # Debe convertirse en un resultado controlado.
        self.assertIn('ZeroDivisionError', self.ruta.read_text(encoding='utf-8'))  # La causa queda registrada.

    def test_log_sin_permiso(self):  # Verifica degradación explícita cuando no puede abrirse el archivo.
        with patch('software_fj.gestion.ArchivoSeguro', side_effect=PermissionError), contextlib.redirect_stderr(io.StringIO()) as salida:  # Simula permiso denegado.
            logger = crear_logger(Path(self.temporal.name) / 'otro.log')  # Configura un destino alternativo.
            self.assertTrue(Sistema(logger).ejecutar('continuar', lambda: 1).exito)  # La aplicación permanece activa.
            self.assertIn('no fue posible', salida.getvalue())  # Se advierte que el archivo no se escribió.
        for handler in logger.handlers[:]:  # Cierra el registro alternativo.
            logger.removeHandler(handler)  # Retira la referencia a la captura temporal.

    def test_demo_completa(self):  # Comprueba la simulación y sus invariantes finales.
        with contextlib.redirect_stdout(io.StringIO()):  # Evita mezclar la salida de demo con el informe de pruebas.
            resultados = simular(self.sistema)  # Ejecuta los 29 escenarios reales.
        self.assertEqual(len(resultados), 29)  # Asegura el número documentado de operaciones.
        self.assertTrue(all(fila[4] for fila in resultados))  # Exige resultados esperados en todos los escenarios.
        self.assertEqual((len(self.sistema.clientes), len(self.sistema.servicios), len(self.sistema.reservas)), (2, 3, 4))  # Revisa colecciones finales.
        self.assertTrue(all(servicio.disponible for servicio in self.sistema.servicios))  # Ningún recurso queda bloqueado.
        self.assertEqual(self.sistema.reserva('R4').total, Decimal('240000.00'))  # Comprueba el resultado monetario final.


if __name__ == '__main__':  # Permite ejecutar este archivo como módulo de pruebas.
    unittest.main()  # Inicia el descubrimiento y el informe de resultados.
