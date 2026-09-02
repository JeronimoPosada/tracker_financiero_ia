def generar_barra_progreso(actual: float, objetivo: float, longitud: int = 10) -> str:
    if objetivo <= 0:
        return "░" * longitud
    porcentaje = min(actual / objetivo, 1.0)
    llenos = int(porcentaje * longitud)
    vacios = longitud - llenos
    return "█" * llenos + "░" * vacios