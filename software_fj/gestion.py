"""Colecciones en memoria y frontera de ejecución que registra los errores."""
from dataclasses import dataclass  # Representa el resultado de cada operación.
from pathlib import Path  # Construye rutas compatibles con Windows y Linux.
import logging  # Registra eventos y trazas de excepción.
import sys  # Ofrece una salida alternativa si no se puede escribir el log.
from .modelos import Cliente, Servicio, Reserva  # Importa entidades del dominio.
from .errores import ErrorSistema, ValidacionError, DuplicadoError, NoEncontradoError, OperacionError  # Clasifica fallas.


class ArchivoSeguro(logging.FileHandler):  # Conserva la aplicación si el disco falla después de abrir el log.
    def handleError(self, record):  # Sustituye el comportamiento por defecto ante un error de escritura.
        print('AVISO: no se pudo escribir en el log; el evento se muestra en consola.', file=sys.stderr)  # Hace visible la limitación.
        print(self.format(record), file=sys.stderr)  # Rescata el evento y su traza en la salida de error.


def crear_logger(ruta='logs/software_fj.log'):  # Prepara un archivo de eventos y errores.
    logger = logging.getLogger(f'software_fj.{Path(ruta).resolve()}')  # Separa registros de ejecución y de pruebas.
    logger.setLevel(logging.INFO)  # Incluye eventos normales y errores.
    logger.propagate = False  # Evita duplicados por el logger raíz.
    for anterior in logger.handlers[:]:  # Permite reinicializar el mismo registro sin duplicar líneas.
        anterior.close()  # Cierra el recurso anterior.
        logger.removeHandler(anterior)  # Retira el manejador cerrado.
    try:  # Controla permisos y problemas del sistema de archivos.
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)  # Crea el directorio de logs si falta.
        salida = ArchivoSeguro(ruta, encoding='utf-8')  # Abre el único archivo usado por el sistema de negocio.
    except OSError:  # No termina la aplicación por falta de acceso al disco.
        salida = logging.StreamHandler(sys.stderr)  # Conserva los eventos en consola.
        print('AVISO: log en consola; no fue posible abrir el archivo.', file=sys.stderr)  # No finge que el archivo existe.
    salida.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))  # Agrega fecha, nivel y mensaje.
    logger.addHandler(salida)  # Activa el destino disponible.
    return logger  # Entrega el registrador configurado.


@dataclass(frozen=True)  # Hace inmutable el resultado entregado a la interfaz.
class Resultado:  # Distingue éxito de valores legítimos como cero o None.
    exito: bool  # Indica si la operación terminó correctamente.
    mensaje: str  # Contiene un mensaje breve para la consola.
    valor: object = None  # Guarda el dato devuelto por una operación exitosa.


class Sistema:  # Coordina el caso de uso sin base de datos.
    def __init__(self, logger):  # Recibe el registrador como dependencia explícita.
        self.__clientes, self.__servicios, self.__reservas = [], [], []  # Mantiene todas las entidades en listas internas.
        self.logger = logger  # Permite pruebas con un log independiente.

    @property  # Evita exponer la lista mutable de clientes.
    def clientes(self):  # Ofrece una vista de solo lectura de la colección.
        return tuple(self.__clientes)  # Devuelve una copia inmutable de las referencias.

    @property  # Evita inserciones externas en servicios.
    def servicios(self):  # Consulta el catálogo actual.
        return tuple(self.__servicios)  # Conserva el control sobre la lista interna.

    @property  # Evita borrar reservas accidentalmente desde la interfaz.
    def reservas(self):  # Consulta las reservas disponibles.
        return tuple(self.__reservas)  # Entrega una vista inmutable.

    def _buscar(self, coleccion, identificador):  # Localiza una entidad por ID dentro de una lista.
        for entidad in coleccion:  # Recorre objetos sin realizar consultas a una base de datos.
            if entidad.identificador == identificador:  # Compara identidades del mismo tipo de colección.
                return entidad  # Devuelve la entidad existente.
        raise NoEncontradoError('Identificador no registrado en la colección solicitada.')  # No crea entidades implícitas.

    def _agregar(self, coleccion, entidad):  # Inserta únicamente objetos con un ID nuevo.
        if any(item.identificador == entidad.identificador for item in coleccion):  # Comprueba duplicados antes de mutar.
            raise DuplicadoError('Identificador ya registrado.')  # Mantiene intacta la colección.
        coleccion.append(entidad)  # Inserta después de superar la validación.
        return entidad  # Permite usar la instancia recién registrada.

    def registrar_cliente(self, *args, **kwargs):  # Recibe los datos requeridos por Cliente.
        return self._agregar(self.__clientes, Cliente(*args, **kwargs))  # Construye primero y agrega solo si es válido.

    def registrar_servicio(self, clase, *args, **kwargs):  # Permite ampliar servicios sin cambiar el almacenamiento.
        if not isinstance(clase, type) or not issubclass(clase, Servicio):  # Verifica el contrato del catálogo.
            raise ValidacionError('El tipo debe heredar de Servicio.')  # Rechaza objetos ajenos al modelo.
        return self._agregar(self.__servicios, clase(*args, **kwargs))  # Deja que cada subclase valide sus parámetros.

    def crear_reserva(self, identificador, cliente_id, servicio_id, duracion):  # Asocia registros existentes.
        cliente = self._buscar(self.__clientes, cliente_id)  # No acepta clientes sin registrar.
        servicio = self._buscar(self.__servicios, servicio_id)  # No acepta servicios sin registrar.
        return self._agregar(self.__reservas, Reserva(identificador, cliente, servicio, duracion))  # Inserta una reserva válida pendiente.

    def reserva(self, identificador):  # Permite operar sobre una reserva registrada.
        return self._buscar(self.__reservas, identificador)  # Reutiliza la búsqueda controlada.

    def ejecutar(self, etiqueta, funcion, *args, **kwargs):  # Frontera común para cada opción de menú y simulación.
        try:  # Mantiene controlados los errores de la operación completa.
            try:  # Agrega contexto a errores de dominio o parámetros faltantes.
                valor = funcion(*args, **kwargs)  # Incluye lectura y conversión de datos cuando se usa desde el menú.
            except (ErrorSistema, TypeError, ValueError) as causa:  # Captura fallas previstas y argumentos incorrectos.
                raise OperacionError(f'No se completó: {etiqueta}.') from causa  # Conserva el encadenamiento en la traza.
        except OperacionError as error:  # Maneja el fallo sin terminar la sesión.
            self.logger.exception('ERROR | %s', etiqueta)  # Guarda tipo, causa y traza completa en el log.
            return Resultado(False, f'{error} {error.__cause__}')  # Informa el motivo sin modificar las colecciones.
        except Exception as error:  # Última frontera para fallas inesperadas recuperables de la operación.
            self.logger.exception('ERROR INESPERADO | %s', etiqueta)  # Conserva evidencia para corregir el defecto.
            return Resultado(False, f'{etiqueta}: error inesperado ({type(error).__name__}); revise el log.')  # Permite seguir con otra opción.
        else:  # Se ejecuta únicamente si la función no produjo errores.
            self.logger.info('OK | %s', etiqueta)  # Registra también eventos correctos.
            return Resultado(True, f'Operación completada: {etiqueta}.', valor)  # Distingue éxito de una salida vacía.
        finally:  # Se ejecuta incluso si la función retorna desde un except.
            self.logger.info('FIN | %s', etiqueta)  # Marca el cierre de cada intento.
