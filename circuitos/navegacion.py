import math
# (Asegúrate de que aquí estén tus otros imports como flask, serial, etc.)

# --- COORDENADAS DE DESTINO (Punto B) ---
# Cambia estos números por los del lugar a donde quieres que vaya el barco
LAT_DESTINO = 15.8642
LON_DESTINO = -97.0754

def calcular_distancia(lat_actual, lon_actual):
    """Calcula la distancia en metros entre el barco y el objetivo."""
    R = 6371000.0  # Radio de la Tierra en metros
    
    # Convertir a radianes
    phi1 = math.radians(lat_actual)
    phi2 = math.radians(LAT_DESTINO)
    delta_phi = math.radians(LAT_DESTINO - lat_actual)
    delta_lambda = math.radians(LON_DESTINO - lon_actual)
    
    # Fórmula de Haversine
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def calcular_angulo(lat_actual, lon_actual):
    """Calcula hacia qué ángulo (0 a 360 grados) debe apuntar el barco."""
    phi1 = math.radians(lat_actual)
    phi2 = math.radians(LAT_DESTINO)
    delta_lambda = math.radians(LON_DESTINO - lon_actual)
    
    x = math.sin(delta_lambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - (math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))
    
    angulo_grados = math.degrees(math.atan2(x, y))
    
    # Convertir para que siempre sea de 0 a 360 grados como una brújula
    return (angulo_grados + 360) % 360

def tomar_decision_autonoma(lat_actual, lon_actual, rumbo_actual_barco):
    """El cerebro del barco: decide qué hacer basado en los cálculos."""
    distancia = calcular_distancia(lat_actual, lon_actual)
    angulo_meta = calcular_angulo(lat_actual, lon_actual)
    
    print(f"INFO - Distancia faltante: {distancia:.2f} m | Ángulo meta: {angulo_meta:.2f}°")
    
    # 1. Fase de Llegada (Zona muerta)
    if distancia < 3.0:  # Si está a menos de 3 metros, ya llegó
        print("¡META ALCANZADA!")
        return "DETENER"
        
    # 2. Calcular cuánto tenemos que girar
    error_angulo = angulo_meta - rumbo_actual_barco
    
    # Ajustar para encontrar el giro más corto (evita que dé una vuelta completa a lo tonto)
    if error_angulo > 180:
        error_angulo -= 360
    elif error_angulo < -180:
        error_angulo += 360
        
    # 3. Fase de Orientación
    # Si estamos desviados por más de 15 grados, corregimos el rumbo
    if error_angulo > 15:
        return "DERECHA"
    elif error_angulo < -15:
        return "IZQUIERDA"
        
    # 4. Fase de Traslación
    # Si el ángulo está bien (menos de 15 grados de error), avanzamos
    return "AVANZAR"