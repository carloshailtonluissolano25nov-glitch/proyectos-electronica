#include <ESP32Servo.h> // Librería necesaria para los ESC de los motores principales

// --- pines de los motores (ESC) ---
const int PIN_ESC_IZQ = 25;
const int PIN_ESC_DER = 26;
Servo escIzq;
Servo escDer;

// --- pines de la banda recolectora  (L298N) ---
const int PIN_BANDA_IN1 = 27;
const int PIN_BANDA_IN2 = 14;
const int PIN_BANDA_ENA = 12;

// Configuración de PWM para la ESP32 (Control de velocidad de la banda)
const int freqPWM = 5000;
const int resolucionPWM = 8; // Resolución de 8 bits (valores de 0 a 255)

void setup() {
  // Iniciar comunicación serial con la Raspberry Pi a 115200 baudios
  Serial.begin(115200);

  // 1. configuracion de la banda(L298N)
  pinMode(PIN_BANDA_IN1, OUTPUT);
  pinMode(PIN_BANDA_IN2, OUTPUT);
  
  // ¡NUEVA SINTAXIS PARA ESP32 CORE 3.X!
  // Configurar el módulo PWM de la ESP32 directamente al pin
  ledcAttach(PIN_BANDA_ENA, freqPWM, resolucionPWM);
  
  // Asegurarnos de que la banda inicie apagada por seguridad
  detenerBanda();

  // 2.configuracion de los motores (ESC)
  escIzq.attach(PIN_ESC_IZQ, 1000, 2000); // Tiempos de pulso estándar para ESC
  escDer.attach(PIN_ESC_DER, 1000, 2000);
  
  // Armar los ESC (mandando señal de 0 velocidad al inicio)
  escIzq.write(0);
  escDer.write(0);
  
  Serial.println("INFO: ESP32 Inicializada. Puente H y ESC listos.");
}

void loop() {
  // --- escuchar ordenes de la raspberry  ---
  // Revisa si han llegado al menos 2 bytes (El comando 'A', 'B' etc., y el byte de potencia)
  if (Serial.available() >= 2) { 
    char comando = Serial.read();
    char potenciaChar = Serial.read();
    
    // Limpiar el salto de línea (\n) del buffer para evitar que interfiera en la siguiente lectura
    if (Serial.peek() == '\n') {
      Serial.read();
    }

    // Convertir el carácter ASCII que envió Python al número real de potencia
    int potenciaPorcentaje = (int)potenciaChar; 
    
    // Ejecutar la acción
    ejecutarComando(comando, potenciaPorcentaje);
  }

  // (Aquí iría la lectura del módulo GPS usando Serial1 o Serial2 para luego enviarlo con Serial.print("GPS:..."); )
}


// --- FUNCIONES DE CONTROL ---

void ejecutarComando(char comando, int potenciaPorcentaje) {
  // Convertir porcentaje (0-100) a señal para el ESC (0-180)
  int potenciaESC = map(potenciaPorcentaje, 0, 100, 0, 180);

  switch (comando) {
    case 'A': // Navegar Adelante
      escIzq.write(potenciaESC);
      escDer.write(potenciaESC);
      Serial.println("INFO: Avanzando al " + String(potenciaPorcentaje) + "%");
      break;
      
    case 'I': // Girar Izquierda (Motor derecho empuja, izquierdo frena)
      escIzq.write(0); 
      escDer.write(potenciaESC);
      Serial.println("INFO: Girando Izquierda al " + String(potenciaPorcentaje) + "%");
      break;
      
    case 'D': // Girar Derecha (Motor izquierdo empuja, derecho frena)
      escIzq.write(potenciaESC);
      escDer.write(0);
      Serial.println("INFO: Girando Derecha al " + String(potenciaPorcentaje) + "%");
      break;
      
    case 'P': // Parar Propulsión
      escIzq.write(0);
      escDer.write(0);
      Serial.println("INFO: Motores de propulsion DETENIDOS");
      break;

    case 'B': // Encender Banda Recolectora
      // Encendemos la banda a un valor PWM fuerte por defecto (ej. 200 de 255)
      encenderBanda(200); 
      Serial.println("INFO: Banda Recolectora ENCENDIDA (Recogiendo basura)");
      break;

    case 'b': // Apagar Banda Recolectora
      detenerBanda();
      Serial.println("INFO: Banda Recolectora APAGADA");
      break;

    default:
      // Ignorar comandos no reconocidos
      break;
  }
}

// --- LÓGICA DEL PUENTE H (L298N) ---

void encenderBanda(int velocidadPWM) {
  // Dirección de recogida (Adelante)
  digitalWrite(PIN_BANDA_IN1, HIGH);
  digitalWrite(PIN_BANDA_IN2, LOW);
  
  // ¡NUEVA SINTAXIS! Enviar el valor PWM indicando el PIN en lugar del canal
  ledcWrite(PIN_BANDA_ENA, velocidadPWM);
}

void detenerBanda() {
  // Freno activo (Ambos pines en LOW frena el motor en seco)
  digitalWrite(PIN_BANDA_IN1, LOW);
  digitalWrite(PIN_BANDA_IN2, LOW);
  
  // ¡NUEVA SINTAXIS! Cortar el voltaje PWM usando el PIN
  ledcWrite(PIN_BANDA_ENA, 0);
}
