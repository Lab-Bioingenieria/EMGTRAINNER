"""
Módulo de cálculos físicos para la mano robótica.
- Conversión corriente a torque (Nm)
- Conversión torque a fuerza de agarre (N)
- Estimación de fuerza máxima soportada
- Utilidades biomecánicas para análisis de desempeño

Motores objetivo:
- Dynamixel XL330-M288T
"""
# CONSTANTES FÍSICAS

HAND_SCALE_FACTOR = 1.85

# Conversión de unidad interna Dynamixel a amperios
# 1 unidad = 2.69 mA
CURRENT_UNIT_TO_AMP = 0.00269  # [A / unidad]

# Constante de torque del motor Dynamixel XL330
# Torque Constant (Kt) = 1.1 mNm / A
TORQUE_CONSTANT_NM_PER_AMP = 0.0011  # [Nm / A]

# Gravedad
GRAVITY = 9.81  # [m/s²]

# CONVERSIÓN CORRIENTE A TORQUE

def current_units_to_amps(current_units: int) -> float:
    return current_units * CURRENT_UNIT_TO_AMP


def current_to_torque_nm(current_amps: float) -> float:
    return current_amps * TORQUE_CONSTANT_NM_PER_AMP


def current_units_to_torque_nm(current_units: int) -> float:
    amps = current_units_to_amps(current_units)
    return current_to_torque_nm(amps)

# CONVERSIÓN TORQUE → FUERZA

def torque_to_force_n(torque_nm: float, lever_arm_m: float) -> float:
    """
    Fórmula:
        F = τ / r
    """
    if lever_arm_m <= 0:
        raise ValueError("El brazo de palanca debe ser mayor que cero")
    return torque_nm / lever_arm_m

def torque_to_force_grams(torque_nm: float, lever_arm_m: float) -> float:
    force_n = torque_to_force_n(torque_nm, lever_arm_m)
    return (force_n / GRAVITY) * 1000.0

# ESTIMACIÓN DE CARGA MÁXIMA

def max_supported_mass_kg(current_limit_units: int, lever_arm_m: float) -> float:
    torque_nm = current_units_to_torque_nm(current_limit_units)
    force_n = torque_to_force_n(torque_nm, lever_arm_m)
    return force_n / GRAVITY

# MÉTRICAS CLÍNICAS

def grip_strength_index(measured_force_n: float, reference_force_n: float) -> float:
    """
    Índice normalizado de fuerza de agarre usado para seguimiento de pacientes
    """
    if reference_force_n <= 0:
        raise ValueError("La fuerza de referencia debe ser > 0")

    return measured_force_n / reference_force_n

def scale_force_to_human(force_robot_n: float) -> float:
    """Normaliza fuerza robótica a equivalente humano"""
    return force_robot_n / HAND_SCALE_FACTOR
