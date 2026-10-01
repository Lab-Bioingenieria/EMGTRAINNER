/*
  EMGTRAINNER — Puente uMyo (BLE) -> Serial para el backend FastAPI
  ------------------------------------------------------------------
  La ESP32 NO mide nada: solo recibe por Bluetooth los datos de los
  sensores uMyo de la banda y los reenvia por USB al backend.

  Requisitos
    - Placa: ESP32 (Arduino core para ESP32)
    - Libreria: "ArduinoBLE" (Gestor de Librerias del IDE de Arduino)
    - Archivos uMyo_BLE.cpp/.h y quat_math.cpp/.h en esta misma carpeta
    - Los uMyo encendidos y EN MODO BLE (pulsar su boton 1 o 2 veces
      hasta que el LED indique modo BLE)

  Formato de salida (una linea por muestra):
      <emg1> <emg2> <emg3>
  Siempre 3 columnas, separadas por espacio. Es lo que espera
  `parse_emg_line()` en backend/app/services/emg_service.py, que las
  guarda como emg1, emg2 y emg3 en el CSV de la sesion.

  Diagnostico: si no hay ningun uMyo a la vista se imprime una linea que
  empieza con "---". El backend descarta esas lineas (estan en su lista de
  palabras a ignorar), pero tu si las ves en el Monitor Serie. Asi puedes
  distinguir "la placa no arranco" de "la placa corre pero no ve sensores".

  IMPORTANTE — velocidad del puerto:
  El backend abre el puerto a 921600 baudios (SerialManager en
  core/serial/manager.py). Este valor DEBE coincidir. Si ves basura en el
  Monitor Serie, baja ambos a 115200.
*/

#include <uMyo_BLE.h>

// Debe coincidir con SerialManager(baudrate=...) del backend.
static const unsigned long SERIAL_BAUD = 921600;

// Canales que espera el backend (emg1, emg2, emg3).
static const int NUM_CANALES = 3;

// Periodo de muestreo. ~33 Hz, igual que el ejemplo original de uMyo.
static const unsigned long PERIODO_MS = 30;

// Cada cuanto avisar que no se ve ningun sensor.
static const unsigned long PERIODO_DIAG_MS = 1000;

unsigned long ultimoDiagnostico = 0;

/*
  Ordena los indices de los dispositivos por su ID para que el canal 1 sea
  siempre el mismo sensor fisico entre arranques. Sin esto el orden depende
  de cual uMyo responda primero, y las columnas del CSV se intercambian de
  una sesion a otra: el modelo entrenaria con canales mezclados.
*/
void ordenarPorID(int *orden, int n) {
  for (int i = 0; i < n; i++) orden[i] = i;
  for (int i = 1; i < n; i++) {
    int actual = orden[i];
    uint32_t idActual = uMyo.getID(actual);
    int j = i - 1;
    while (j >= 0 && uMyo.getID(orden[j]) > idActual) {
      orden[j + 1] = orden[j];
      j--;
    }
    orden[j + 1] = actual;
  }
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  uMyo.begin();

  // Lleva "---" al principio: el backend ignora esta linea.
  Serial.println("--- EMGTRAINNER puente uMyo listo. Esperando sensores...");
}

void loop() {
  uMyo.run();

  int total = uMyo.getDeviceCount();

  if (total == 0) {
    // Sin sensores a la vista: no se manda ninguna muestra al CSV.
    if (millis() - ultimoDiagnostico > PERIODO_DIAG_MS) {
      ultimoDiagnostico = millis();
      Serial.println("--- Sin uMyo detectados. Enciendalos y pongalos en modo BLE.");
    }
    delay(PERIODO_MS);
    return;
  }

  int orden[MAX_UMYO_DEVICES];
  ordenarPorID(orden, total);

  // Siempre 3 columnas: si falta un sensor se manda 0 en su lugar, para que
  // el CSV no cambie de numero de columnas a mitad de la sesion.
  for (int canal = 0; canal < NUM_CANALES; canal++) {
    float valor = (canal < total) ? uMyo.getMuscleLevel(orden[canal]) : 0.0f;
    Serial.print(valor, 2);
    if (canal < NUM_CANALES - 1) Serial.print(' ');
  }
  Serial.println();

  delay(PERIODO_MS);
}
