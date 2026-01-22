// ESP32 + uMyo_BLE - Funcionamiento CONTROLADO POR SERIE
// Espera comandos START_SESSION/STOP_SESSION para iniciar/detener transmision
#include <Arduino.h>
#include <uMyo_BLE.h>

// Variables de estado
bool systemEnabled = false; // Inicia DESACTIVADO (esperando comando)
bool headersSent = false;
unsigned long sessionStartTime = 0;
unsigned long lastDataSent = 0;

void setup() {
  Serial.begin(115200);

  // Inicializar uMyo
  uMyo.begin();

  Serial.println("===============================");
  Serial.println("  SISTEMA EMG CONTROLADO");
  Serial.println("===============================");
  Serial.println("- Esperando START_SESSION...");
  Serial.println("===============================");
}

void loop() {
  // Procesar datos EMG continuamente (necesario para mantener conexion BLE y
  // filtros)
  uMyo.run();

  // 1. Verificar si hay comandos desde Python
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Eliminar \r o espacios extra

    if (command == "START_SESSION") {
      systemEnabled = true;
      sessionStartTime = millis();
      headersSent = false;
      // Confirmacion opcional para debug
      // Serial.println("DEBUG:Sesion iniciada");
    } else if (command == "STOP_SESSION") {
      systemEnabled = false;
      // Serial.println("DEBUG:Sesion detenida");
    }
  }

  // 2. Si el sistema esta activo, enviar datos
  if (systemEnabled) {
    int dev_count = uMyo.getDeviceCount();

    if (dev_count > 0) {
      // Enviar headers solo una vez al inicio de cada sesion
      if (!headersSent) {
        Serial.println("timestamp,emg1,emg2,emg3");
        headersSent = true;
        delay(100);
      }

      // Obtener datos EMG raw
      float emg1 = uMyo.getMuscleLevel(0);
      float emg2 = uMyo.getMuscleLevel(1);
      float emg3 = uMyo.getMuscleLevel(2);

      // Enviar datos cada 50ms (20Hz)
      if (millis() - lastDataSent >= 50) {
        Serial.print(millis());
        Serial.print(",");
        Serial.print(emg1, 2);
        Serial.print(",");
        Serial.print(emg2, 2);
        Serial.print(",");
        Serial.print(emg3, 2);
        Serial.println(); // Importante: Salto de linea al final

        lastDataSent = millis();
      }
    } else {
      // MODO DEMO: Si no hay sensor, enviar datos de prueba (ceros)
      if (millis() - lastDataSent >= 50) {
        if (!headersSent) {
          Serial.println("timestamp,emg1,emg2,emg3");
          headersSent = true;
        }

        Serial.print(millis());
        Serial.print(",");
        Serial.print("0.00,0.00,0.00");
        Serial.println();

        lastDataSent = millis();
      }
    }
  }

  delay(10); // Loop delay
}