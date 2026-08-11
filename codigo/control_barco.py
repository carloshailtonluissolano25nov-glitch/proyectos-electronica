"""
=============================================================================
Control manual web y navegacion autonoma 
=============================================================================
Este codigo  implementa el sistema de control principal del vehículo utilizando 
un servidor web local (Flask) y comunicación serial. 

Características principales:
1. Interfaz Web (Control Remoto): Levanta una página HTML accesible desde 
   cualquier dispositivo (ej. celular) en la misma red Wi-Fi para enviar 
   órdenes manuales de movimiento y control de la banda recolectora.
2. Comunicación Serial: Traduce los clics de la página web en comandos 
   de texto y los transmite al ESP32 a través del cable USB.
3. Base de Control Autónomo: Integra la lógica inicial para tomar 
   decisiones de navegación basadas en coordenadas GPS y brújula.
=============================================================================
"""
from navegacion import tomar_decision_autonoma
from flask import Flask, render_template_string
import serial
import time

app = Flask(__name__)

# ==========================================
# 1. Conexion con la esp32
# ==========================================
esp32 = None
try:
    # OJO: Usa 'COM3' (o el número de COM que asigne tu PC) para probar en Windows. 
    # Cuando lo pases a la Raspberry Pi, cámbialo por '/dev/ttyUSB0'
    esp32 = serial.Serial('COM3', 115200, timeout=1)
    time.sleep(2) # Pausa para que el ESP32 reinicie correctamente
    print("Conexión exitosa con ESP32")
except:
    print("ERROR: No se encontró el ESP32. Revisa el cable USB o el puerto.")

# ==========================================
# 2. Pagina web para el celular 
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mando del Barco</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { text-align: center; font-family: Arial, sans-serif; background-color: #f4f4f9; margin-top: 30px; }
        button { width: 110px; height: 60px; font-size: 16px; margin: 10px; background-color: #007BFF; color: white; border: none; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); touch-action: manipulation; }
        button:active { background-color: #0056b3; transform: translateY(2px); }
        .red { background-color: #DC3545; font-weight: bold; }
        .red:active { background-color: #a71d2a; }
        .green { background-color: #28a745; }
    </style>
</head>
<body>
    <h2>Control Inalámbrico</h2>
    <div>
        <button onclick="mandarComando('AVANZAR')">Adelante</button>
    </div>
    <div>
        <button onclick="mandarComando('IZQUIERDA')">Izquierda</button>
        <button class="red" onclick="mandarComando('DETENER')">STOP</button>
        <button onclick="mandarComando('DERECHA')">Derecha</button>
    </div>
    <div>
        <button onclick="mandarComando('RETROCEDER')">Atrás</button>
    </div>
    <br><hr><br>
    <div>
        <button class="green" onclick="mandarComando('BANDA_ON')">Banda ON</button>
        <button class="red" onclick="mandarComando('BANDA_OFF')">Banda OFF</button>
    </div>

    <script>
        // Esta función envía silenciosamente la orden al servidor
        function mandarComando(cmd) {
            fetch('/comando/' + cmd);
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. Servidor web rutas de acceso
# ==========================================
@app.route('/')
def inicio():
    # Cuando entres desde el celular, te mostrará la página web
    return render_template_string(HTML_PAGE)

@app.route('/comando/<cmd>')
def ejecutar_comando(cmd):
    print(f"El celular pidió: {cmd}")
    
    # Verificamos que el cable esté conectado antes de enviar
    if esp32 is not None and esp32.is_open:
        # Preparamos el mensaje con formato perfecto para Arduino
        mensaje = f"{cmd.upper()}\n"
        # Lo codificamos a pulsos eléctricos (bytes) y lo enviamos
        esp32.write(mensaje.encode('utf-8'))
        print(f"Orden enviada por el cable USB al ESP32: {cmd.upper()}")
    else:
        print("Aviso: Botón presionado, pero el ESP32 no está conectado por USB.")
        
    return "OK", 200

# ==========================================
# 4.Arranque del sistema  (SIMULACRO + SERVIDOR)
# ==========================================
if __name__ == '__main__':
    print("\n--- 1. INICIANDO PRUEBA DE NAVEGACIÓN AUTÓNOMA ---")
    
    # Coordenadas inventadas donde supuestamente está el barco ahora mismo
    latitud_falsa = 15.8600
    longitud_falsa = -97.0700
    rumbo_falso = 0  # 0 grados significa que el barco apunta directo al Norte
    
    # Llamamos al "Cerebro" para ver qué decide hacer
    decision = tomar_decision_autonoma(latitud_falsa, longitud_falsa, rumbo_falso)
    
    print(f"La orden que se enviaría a los motores es: {decision}")
    print("--------------------------------------------------\n")
    
    print("--- 2. INICIANDO EL SERVIDOR WEB (CONTROL MANUAL) ---")
    # host='0.0.0.0' permite que cualquier dispositivo en el Wi-Fi se pueda conectar
    app.run(host='0.0.0.0', port=5000)
