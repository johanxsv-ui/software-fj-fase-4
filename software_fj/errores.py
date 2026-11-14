"""Errores de dominio que la interfaz puede comunicar sin cerrar el programa."""

class ErrorSistema(Exception):  # Agrupa las excepciones propias del proyecto.
    """Base de los errores controlados de Software FJ."""

class ValidacionError(ErrorSistema):  # Representa datos que no cumplen las reglas.
    """Entrada inválida o incompleta."""

class NoEncontradoError(ErrorSistema):  # Distingue referencias inexistentes.
    """No existe una entidad con el identificador solicitado."""

class DuplicadoError(ErrorSistema):  # Evita insertar dos entidades con el mismo ID.
    """Identificador repetido dentro de una colección."""

class DisponibilidadError(ErrorSistema):  # Identifica un recurso ya ocupado.
    """El servicio no puede asignarse a otra reserva activa."""

class EstadoError(ErrorSistema):  # Impide transiciones no permitidas.
    """La operación no corresponde al estado actual de la reserva."""

class CalculoError(ErrorSistema):  # Mantiene separadas las fallas monetarias.
    """No fue posible calcular un importe válido."""

class OperacionError(ErrorSistema):  # Agrega contexto conservando la causa original.
    """Falla de una operación completa de la aplicación."""
