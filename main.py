"""Entrada por consola: python main.py o python main.py --demo."""
import argparse  # Selecciona simulación o sesión interactiva.
from software_fj.gestion import Sistema, crear_logger  # Prepara la aplicación y el registro.
from software_fj.modelos import Sala, Equipo, Asesoria  # Ofrece todos los tipos de servicio.
from software_fj.demo import simular  # Importa la demostración automática.
from software_fj.errores import ValidacionError  # Comunica opciones no permitidas.


def menu(sistema):  # Mantiene la sesión activa hasta una salida explícita.
    def cliente():  # Lee un cliente dentro de la frontera de errores.
        return sistema.registrar_cliente(input('ID: '), input('Nombre: '), input('Correo: '), input('Teléfono: '))  # Valida los datos en el modelo.

    def servicio():  # Lee el tipo y los atributos del servicio.
        tipo = input('Tipo (1 sala, 2 equipo, 3 asesoría): ').strip()  # Solicita la especialización.
        if tipo not in ('1', '2', '3'):  # Rechaza tipos antes de pedir otros datos.
            raise ValidacionError('Tipo de servicio inválido.')  # Regresa al menú mediante ejecutar.
        datos = (input('ID: '), input('Nombre: '), input('Tarifa por hora COP: '))  # Conserva la tarifa como texto decimal.
        if tipo == '1':  # Completa los atributos de una sala.
            return sistema.registrar_servicio(Sala, *datos, int(input('Capacidad: ')))  # Controla la conversión en ejecutar.
        if tipo == '2':  # Completa los atributos del equipo.
            return sistema.registrar_servicio(Equipo, *datos, input('Cargo de preparación COP: '))  # Permite cargo cero.
        return sistema.registrar_servicio(Asesoria, *datos, input('Especialidad: '), input('Factor entre 1 y 3: '))  # Completa la asesoría.

    def reserva():  # Recibe las referencias de la nueva reserva.
        return sistema.crear_reserva(input('ID reserva: '), input('ID cliente: '), input('ID servicio: '), input('Horas: '))  # Valida existencia y duración.

    def confirmar():  # Permite costo base, con impuesto o con descuento.
        objeto = sistema.reserva(input('ID reserva: '))  # Recupera una reserva registrada.
        return objeto.confirmar(input('Impuesto fracción (Enter=0): ') or '0', input('Descuento fracción (Enter=0): ') or '0')  # Usa parámetros opcionales sin porcentajes ambiguos.

    def listar():  # Muestra los objetos conservados en memoria.
        for nombre, elementos in [('CLIENTES', sistema.clientes), ('SERVICIOS', sistema.servicios), ('RESERVAS', sistema.reservas)]:  # Recorre las tres colecciones.
            print('\n' + nombre)  # Identifica la colección.
            for elemento in elementos:  # Recorre sus objetos concretos.
                print(elemento.describir())  # Aplica polimorfismo al describir.

    opciones = {'1': cliente, '2': servicio, '3': reserva, '4': confirmar, '5': lambda: sistema.reserva(input('ID reserva: ')).procesar(), '6': lambda: sistema.reserva(input('ID reserva: ')).cancelar(), '7': listar}  # Centraliza las acciones disponibles.
    while True:  # Repite tras cada operación exitosa o fallida.
        print('\nSOFTWARE FJ | 1 Cliente | 2 Servicio | 3 Reserva | 4 Confirmar | 5 Procesar | 6 Cancelar | 7 Listar | 0 Salir')  # Presenta opciones claras.
        try:  # Permite cerrar ordenadamente con teclado o fin de entrada.
            opcion = input('Seleccione: ').strip()  # Lee la opción sin convertirla a entero.
            if opcion == '0':  # Reconoce la salida explícita.
                sistema.logger.info('CIERRE | salida solicitada')  # Registra el fin normal de sesión.
                break  # Termina el ciclo del menú.
            if opcion not in opciones:  # Evita buscar una clave inexistente.
                sistema.logger.warning('ERROR | opción de menú inválida')  # Registra el intento incorrecto.
                print('Opción inválida; elija de 0 a 7.')  # Orienta sin cerrar la aplicación.
                continue  # Solicita otra opción.
            resultado = sistema.ejecutar('Opción ' + opcion, opciones[opcion])  # Incluye todas las conversiones en la frontera.
            print(resultado.mensaje)  # Comunica si la operación se completó.
            if resultado.exito and resultado.valor is not None:  # Muestra el resultado de dominio cuando exista.
                print(resultado.valor.describir() if hasattr(resultado.valor, 'describir') else resultado.valor)  # Presenta un texto legible.
        except (EOFError, KeyboardInterrupt):  # Atiende una orden de cierre fuera de los errores de negocio.
            sistema.logger.info('CIERRE | interrupción de entrada')  # Registra la salida controlada.
            print('\nSesión cerrada.')  # Evita una traza innecesaria por cierre del usuario.
            break  # Finaliza sin insistir en la lectura.


def main():  # Configura el modo de ejecución desde la línea de comandos.
    parser = argparse.ArgumentParser(description='Software FJ — gestión en memoria')  # Proporciona ayuda incorporada.
    parser.add_argument('--demo', action='store_true', help='Ejecutar 29 operaciones de prueba')  # Activa el modo reproducible.
    args = parser.parse_args()  # Interpreta los argumentos.
    sistema = Sistema(crear_logger())  # Inicia listas vacías y registro en archivo.
    if args.demo:  # Selecciona simulación sin entradas manuales.
        resultados = simular(sistema)  # Ejecuta la secuencia documentada.
        return 0 if all(fila[4] for fila in resultados) else 1  # Devuelve un código verificable al sistema operativo.
    menu(sistema)  # Inicia la interfaz interactiva por defecto.
    return 0  # Informa salida normal.


if __name__ == '__main__':  # Evita ejecutar el menú cuando se importa el módulo.
    raise SystemExit(main())  # Propaga el estado de la ejecución.
