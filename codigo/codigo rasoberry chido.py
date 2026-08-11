import serial
import time
import pynmea2 

# Ajusta el puerto según cómo detecte la Raspberry a la ESP32 conectada por USB
puerto_esp32 = '/dev/ttyUSB0' 
baudrate = 115200

def enviar_comando(direccion, potencia):
    """
    Función para enviar comandos compactos según la tabla ASCII.
    Trama enviada: [Letra Dirección] + [Carácter Potencia] + [\n]
    """
    # PROTECCIÓN DE INGENIERÍA: El número 10 en ASCII es un "Enter" (\n).
    # Si enviamos 10, la ESP32 pensará que el mensaje terminó antes de tiempo.
    # Lo auto-corregimos a 11% (así es seguro y no altera la velocidad del motor).
    if potencia == 10:
        potencia = 11
        
    # Convertimos el porcentaje (0, 11, 20, 30, 40, 50) en su carácter ASCII
    caracter_potencia = chr(potencia)
    
    # Construimos la trama compacta (Ejemplo: 'A' + '2' + '\n')
    trama = f"{direccion}{caracter_potencia}\n"
    
    # Enviamos los bytes por el puerto serie
    esp32.write(trama.encode('utf-8'))
    
    # Imprimimos en la pantalla lo que se está enviando (revelando invisibles con repr)
    print(f"🚀 Enviado -> Dirección: {direccion} | Potencia: {potencia}% | Trama real: {repr(trama)}")

# --- INICIO DEL PROGRAMA PRINCIPAL ---
try:
    # 1. Conectar con la ESP32
    print(f"Conectando a la ESP32 en el puerto {puerto_esp32}...")
    esp32 = serial.Serial(puerto_esp32, baudrate, timeout=1)
    time.sleep(2) # Pausa de seguridad para que la ESP32 se reinicie correctamente
    
    # --- EJEMPLO DE RUTINA DE ÓRDENES CON TU NUEVO FORMATO ---
    print("\n--- INICIANDO RUTINA DE PRUEBA DE MOTORES (MÁX 50%) ---")
    
    # Enciende la banda (Usamos 'B', potencia 0 porque la banda suele ser ON/OFF)
    enviar_comando('B', 0)
    time.sleep(2) 
    
    # Avanza hacia adelante al 20%
    enviar_comando('A', 20)
    time.sleep(2)
    
    # Gira a la izquierda al 30%
    enviar_comando('I', 30)
    time.sleep(2)
    
    # Gira a la derecha al 40%
    enviar_comando('D', 40)
    time.sleep(2)
    
    # Velocidad máxima permitida adelante (50%)
    enviar_comando('A', 50)
    time.sleep(2)
    
    # Probamos potencia baja del 10% (el código la enviará como 11% de forma segura)
    enviar_comando('A', 10)
    time.sleep(2)
    
    # Detiene los motores de navegación (Potencia 0)
    enviar_comando('P', 0)
    time.sleep(1)
    
    # Apaga la banda recolectora (Comando 'b' minúscula)
    enviar_comando('b', 0)
    
    print("\nRutina finalizada con éxito.")
    print("Modo escucha activado: Procesando telemetría de la ESP32...\n")
    
    # 2. BUCLE PRINCIPAL (El cerebro se queda escuchando)
    while True:
        if esp32.in_waiting > 0:
            # Leer la línea que manda la ESP32
            linea = esp32.readline().decode('utf-8', errors='replace').strip()
            
            # Si el texto empieza con "GPS:"
            if linea.startswith("GPS:"):
                trama_nmea = linea.replace("GPS:", "")
                
                # Traducir los datos del GPS a algo entendible
                if trama_nmea.startswith("$GPGGA"):
                    try:
                        mensaje = pynmea2.parse(trama_nmea)
                        print(f"📍 Ubicación -> Latitud: {mensaje.latitude}, Longitud: {mensaje.longitude}")
                    except pynmea2.ParseError:
                        pass # Ignora errores si el GPS aún está buscando satélites
            
            # Si el texto empieza con "INFO:" (Confirmaciones de la ESP32)
            elif linea.startswith("INFO:"):
                print(f"🤖 Sistema: {linea.replace('INFO: ', '')}")

except serial.SerialException:
    print(f"\n❌ Error: No se pudo abrir el puerto {puerto_esp32}.")
    print("Revisa que el cable USB esté bien conectado a la raspberri")