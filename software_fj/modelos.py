"""Modelo de dominio; no lee ni escribe datos de negocio en archivos."""
from abc import ABC, abstractmethod  # Define contratos abstractos obligatorios.
from decimal import Decimal, DecimalException, ROUND_HALF_UP  # Calcula dinero exacto.
from enum import Enum  # Limita los estados a valores conocidos.
import re  # Valida textos mediante patrones.
from .errores import ValidacionError, CalculoError, EstadoError, DisponibilidadError  # Errores del dominio.


def texto(valor, campo, limite=80):  # Centraliza el control de cadenas.
    if not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > limite:  # Descarta vacíos y textos excesivos.
        raise ValidacionError(f'{campo}: texto obligatorio de 1 a {limite} caracteres.')  # Explica la regla sin revelar el dato.
    return valor.strip()  # Devuelve el texto normalizado.


def numero(valor, campo, minimo=0, maximo=100000000, incluir_minimo=False):  # Convierte y acota valores numéricos.
    try:  # Protege la conversión de entradas externas.
        if isinstance(valor, bool) or not isinstance(valor, (str, int, float, Decimal)):  # Rechaza booleanos y objetos ajenos.
            raise ValueError('Tipo numérico no permitido.')  # Conserva una causa técnica.
        resultado = Decimal(str(valor))  # Evita convertir directamente desde float.
        if not resultado.is_finite():  # Descarta NaN e infinitos antes de comparar.
            raise ValueError('Número no finito.')  # Señala el origen de la falla.
    except (ValueError, DecimalException) as causa:  # Captura errores propios de la conversión.
        raise ValidacionError(f'{campo}: se requiere un número finito.') from causa  # Encadena la excepción original.
    if resultado > Decimal(str(maximo)) or resultado < Decimal(str(minimo)) or (resultado == Decimal(str(minimo)) and not incluir_minimo):  # Aplica límites del dominio.
        raise ValidacionError(f'{campo}: valor fuera del rango permitido.')  # Impide valores incoherentes.
    return resultado  # Entrega un Decimal validado.


class Entidad(ABC):  # Representa cualquier entidad identificable.
    def __init__(self, identificador):  # Inicializa la identidad inmutable.
        valor = texto(identificador, 'Identificador', 24)  # Verifica presencia y longitud.
        if not re.fullmatch(r'[A-Za-z0-9_-]+', valor):  # Acepta identificadores seguros para el log.
            raise ValidacionError('Identificador: use letras, números, guion o guion bajo.')  # Rechaza saltos de línea y símbolos ajenos.
        self.__identificador = valor  # Encapsula el identificador.

    @property  # Expone lectura sin setter público.
    def identificador(self):  # Consulta la identidad.
        return self.__identificador  # Mantiene el dato protegido de asignaciones normales.

    @abstractmethod  # Obliga a implementar una descripción en cada entidad concreta.
    def describir(self):  # Declara la interfaz común.
        """Devuelve una descripción legible de la entidad."""


class Cliente(Entidad):  # Especializa la entidad para los datos personales.
    def __init__(self, identificador, nombre, correo, telefono):  # Exige todos los datos básicos.
        super().__init__(identificador)  # Reutiliza la validación de identidad.
        self.__nombre = texto(nombre, 'Nombre')  # Guarda el nombre validado.
        self.actualizar_contacto(correo, telefono)  # Valida ambos contactos antes de guardarlos.

    @property  # Habilita la lectura controlada del nombre.
    def nombre(self):  # Consulta el nombre registrado.
        return self.__nombre  # No ofrece un setter que salte la validación.

    @property  # Habilita la lectura controlada del correo.
    def correo(self):  # Consulta el correo.
        return self.__correo  # Devuelve el atributo encapsulado.

    @property  # Habilita la lectura controlada del teléfono.
    def telefono(self):  # Consulta el teléfono.
        return self.__telefono  # Devuelve el atributo encapsulado.

    def actualizar_contacto(self, correo, telefono):  # Actualiza de forma atómica los dos contactos.
        email = texto(correo, 'Correo', 120)  # Normaliza antes de validar el formato.
        tel = texto(telefono, 'Teléfono', 15)  # Conserva el teléfono como texto.
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):  # Comprueba una estructura básica de correo.
            raise ValidacionError('Correo: formato inválido.')  # No imprime el correo recibido.
        if not re.fullmatch(r'\+?[0-9]{7,15}', tel):  # Acepta entre 7 y 15 dígitos y un prefijo opcional.
            raise ValidacionError('Teléfono: use entre 7 y 15 dígitos.')  # Informa la condición incumplida.
        self.__correo, self.__telefono = email, tel  # Solo cambia los atributos si ambas validaciones pasan.

    def describir(self):  # Implementa el método abstracto para el cliente.
        return f'{self.identificador} | {self.nombre}'  # Evita divulgar el contacto en listados generales.


class Servicio(Entidad):  # Contrato abstracto para los servicios ofrecidos.
    def __init__(self, identificador, nombre, tarifa):  # Inicializa los atributos comunes.
        super().__init__(identificador)  # Valida la identidad del servicio.
        self.__nombre = texto(nombre, 'Nombre del servicio')  # Guarda un nombre no vacío.
        self.__tarifa = numero(tarifa, 'Tarifa')  # Requiere una tarifa positiva y finita.
        self.__ocupante = None  # Un servicio representa un recurso individual.

    @property  # Expone el nombre sin permitir cambios directos.
    def nombre(self):  # Consulta el nombre del servicio.
        return self.__nombre  # Retorna el valor encapsulado.

    @property  # Expone la tarifa de referencia.
    def tarifa(self):  # Consulta el precio por hora.
        return self.__tarifa  # Mantiene la tarifa validada e inmutable.

    @property  # Calcula disponibilidad a partir de la reserva activa.
    def disponible(self):  # Consulta si el recurso está libre.
        return self.__ocupante is None  # Evita mantener dos indicadores contradictorios.

    def ocupar(self, reserva):  # Asigna el recurso a una reserva confirmada.
        if not self.disponible:  # Impide dos ocupaciones simultáneas.
            raise DisponibilidadError('Servicio ocupado por otra reserva.')  # Deja intacto al ocupante actual.
        self.__ocupante = reserva  # Guarda la referencia del dueño de la ocupación.

    def liberar(self, reserva):  # Libera únicamente al dueño correcto.
        if self.__ocupante is not reserva:  # Protege contra liberaciones ajenas.
            raise EstadoError('La reserva no posee este servicio.')  # Evita modificar recursos de otro proceso.
        self.__ocupante = None  # Restablece la disponibilidad.

    @abstractmethod  # Obliga a validar las particularidades del servicio.
    def validar_parametros(self, duracion):  # Recibe la duración en horas.
        """Devuelve una duración válida para este servicio."""

    @abstractmethod  # Define el punto de variación del cálculo.
    def costo_base(self, duracion):  # Recibe horas y devuelve un Decimal.
        """Calcula el costo antes de descuentos e impuestos."""

    def calcular_costo(self, duracion, impuesto=0, descuento=0):  # Ofrece variantes por parámetros opcionales, no firmas repetidas.
        try:  # Controla tanto validación como aritmética.
            horas = self.validar_parametros(duracion)  # Usa polimorfismo para la regla de cada subclase.
            tasa = numero(impuesto, 'Impuesto', maximo=1, incluir_minimo=True)  # Admite fracciones entre cero y uno.
            rebaja = numero(descuento, 'Descuento', maximo=1, incluir_minimo=True)  # Admite descuentos de 0 a 100 por ciento.
            base = numero(self.costo_base(horas), 'Costo base')  # Detecta cálculos negativos o no finitos.
            return (base * (1 - rebaja) * (1 + tasa)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # Redondea solo el total.
        except (ValidacionError, DecimalException, ArithmeticError) as causa:  # Conserva errores numéricos y de validación.
            raise CalculoError('No se pudo calcular el costo del servicio.') from causa  # Agrega contexto sin perder la causa.


class Sala(Servicio):  # Servicio de reserva de una sala física.
    def __init__(self, identificador, nombre, tarifa, capacidad):  # Exige capacidad además de los datos comunes.
        super().__init__(identificador, nombre, tarifa)  # Inicializa la parte heredada.
        if type(capacidad) is not int or not 1 <= capacidad <= 500:  # Requiere un entero positivo razonable.
            raise ValidacionError('Capacidad: entero entre 1 y 500.')  # Rechaza cero, booleanos y fracciones.
        self.__capacidad = capacidad  # Encapsula el aforo.

    def validar_parametros(self, duracion):  # Sobrescribe la regla de duración de salas.
        return numero(duracion, 'Horas de sala', maximo=12)  # Admite más de cero y hasta doce horas.

    def costo_base(self, duracion):  # Sobrescribe el cálculo por hora.
        return self.tarifa * self.validar_parametros(duracion)  # Multiplica horas válidas por tarifa.

    def describir(self):  # Sobrescribe la descripción común.
        return f'{self.identificador} | Sala {self.nombre} | aforo {self.__capacidad} | {self.tarifa} COP/h'  # Resume el recurso.


class Equipo(Servicio):  # Servicio de alquiler de un equipo individual.
    def __init__(self, identificador, nombre, tarifa, cargo_preparacion=5000):  # Permite definir el cargo fijo de preparación.
        super().__init__(identificador, nombre, tarifa)  # Reutiliza la inicialización común.
        self.__cargo = numero(cargo_preparacion, 'Preparación', incluir_minimo=True)  # Acepta cargo cero pero no negativo.

    def validar_parametros(self, duracion):  # Sobrescribe el rango del alquiler.
        return numero(duracion, 'Horas de equipo', maximo=24)  # Limita el préstamo a veinticuatro horas.

    def costo_base(self, duracion):  # Sobrescribe la fórmula con un componente fijo.
        return self.tarifa * self.validar_parametros(duracion) + self.__cargo  # Suma alquiler y preparación.

    def describir(self):  # Describe los componentes del precio.
        return f'{self.identificador} | Equipo {self.nombre} | {self.tarifa} COP/h + {self.__cargo} COP'  # Muestra el cargo una sola vez.


class Asesoria(Servicio):  # Servicio de asesoría especializada.
    def __init__(self, identificador, nombre, tarifa, especialidad, factor=1):  # Recibe el área y su factor de complejidad.
        super().__init__(identificador, nombre, tarifa)  # Reutiliza el contrato común.
        self.__especialidad = texto(especialidad, 'Especialidad')  # Exige un área identificable.
        self.__factor = numero(factor, 'Factor', minimo=1, maximo=3, incluir_minimo=True)  # Acota el multiplicador de 1 a 3.

    def validar_parametros(self, duracion):  # Sobrescribe el rango de la asesoría.
        return numero(duracion, 'Horas de asesoría', minimo=1, maximo=8, incluir_minimo=True)  # Exige sesiones de una a ocho horas.

    def costo_base(self, duracion):  # Sobrescribe la fórmula según complejidad.
        return self.tarifa * self.validar_parametros(duracion) * self.__factor  # Aplica horas, tarifa y factor.

    def describir(self):  # Describe la especialidad contratada.
        return f'{self.identificador} | Asesoría {self.__especialidad} | {self.tarifa} COP/h x {self.__factor}'  # Presenta la fórmula usada.


class Estado(Enum):  # Enumera los únicos estados permitidos.
    PENDIENTE = 'PENDIENTE'  # Todavía no ocupa el servicio.
    CONFIRMADA = 'CONFIRMADA'  # Mantiene el servicio ocupado.
    CANCELADA = 'CANCELADA'  # Estado final por cancelación.
    COMPLETADA = 'COMPLETADA'  # Estado final después del procesamiento.


class Reserva(Entidad):  # Integra cliente, servicio, duración, costo y estado.
    def __init__(self, identificador, cliente, servicio, duracion):  # Construye una reserva pendiente.
        super().__init__(identificador)  # Reutiliza el identificador validado.
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):  # Exige objetos válidos del dominio.
            raise ValidacionError('La reserva necesita un Cliente y un Servicio.')  # Evita referencias de tipos ajenos.
        self.__cliente, self.__servicio = cliente, servicio  # Encapsula las asociaciones.
        self.__duracion = servicio.validar_parametros(duracion)  # Valida antes de crear el estado operativo.
        self.__estado, self.__total = Estado.PENDIENTE, None  # Inicializa sin cobro ni ocupación.

    @property  # Permite consultar el estado sin modificarlo directamente.
    def estado(self):  # Devuelve el estado actual.
        return self.__estado  # Obliga a usar las transiciones públicas.

    @property  # Permite revisar el costo fijado al confirmar.
    def total(self):  # Devuelve None si aún no existe una cotización confirmada.
        return self.__total  # Conserva el importe como Decimal.

    def confirmar(self, impuesto=0, descuento=0):  # Confirma y bloquea el recurso de forma secuencial.
        if self.estado is not Estado.PENDIENTE:  # Solo una reserva nueva puede confirmarse.
            raise EstadoError('Solo se puede confirmar una reserva pendiente.')  # Impide confirmaciones repetidas.
        try:  # Protege la cotización antes de modificar el recurso.
            total = self.__servicio.calcular_costo(self.__duracion, impuesto, descuento)  # Calcula todas las variantes.
            self.__servicio.ocupar(self)  # Verifica disponibilidad al confirmar, no solo al crear.
        except (CalculoError, DisponibilidadError):  # Mantiene pendiente si falla la validación.
            raise  # Propaga la misma causa a la frontera que la registra.
        else:  # Solo confirma si cálculo y ocupación fueron exitosos.
            self.__total, self.__estado = total, Estado.CONFIRMADA  # Guarda costo y estado juntos.
            return total  # Entrega el valor confirmado a la interfaz.

    def cancelar(self):  # Cancela una reserva pendiente o confirmada.
        if self.estado not in (Estado.PENDIENTE, Estado.CONFIRMADA):  # Protege los estados finales.
            raise EstadoError('La reserva ya terminó y no puede cancelarse.')  # Informa la transición prohibida.
        if self.estado is Estado.CONFIRMADA:  # Solo la confirmada es dueña del recurso.
            self.__servicio.liberar(self)  # Devuelve disponibilidad sin afectar otra reserva.
        self.__estado = Estado.CANCELADA  # Finaliza la reserva después de liberar.
        return self.estado.value  # Informa el resultado de la operación.

    def procesar(self):  # Simula la prestación completa del servicio, no un pago real.
        if self.estado is not Estado.CONFIRMADA:  # Exige confirmación previa.
            raise EstadoError('Solo se puede procesar una reserva confirmada.')  # Evita cobros o procesos duplicados.
        self.__servicio.liberar(self)  # Termina la ocupación del recurso.
        self.__estado = Estado.COMPLETADA  # Registra el cierre de la prestación.
        return self.total  # Devuelve el costo previamente confirmado.

    def describir(self):  # Presenta las asociaciones y el estado de la reserva.
        return f'{self.identificador} | {self.__cliente.identificador} | {self.__servicio.identificador} | {self.__duracion} h | {self.estado.value} | {self.total} COP'  # Resume el estado actual.
