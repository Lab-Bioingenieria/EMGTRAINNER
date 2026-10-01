/*
  EMGTRAINNER — Puente uMyo (BLE) -> Serial   [version BLE nativo del ESP32]
  ==========================================================================

  Por que existe esta version
  ---------------------------
  El ejemplo original usaba la libreria ArduinoBLE. En el ESP32-S3 esa libreria
  revienta al arrancar:

      btdm: bss start ...
      MAGIC fadebead VERSION 0001000b
      Guru Meditation Error: Core 1 panic'ed (LoadProhibited)

  ArduinoBLE habla con el controlador por una capa HCI generica que no encaja
  con el S3. Aqui se usa el stack BLE que ya viene incluido en el core de
  Arduino para ESP32 (BLEDevice.h), asi que:

    - NO hace falta instalar ninguna libreria. Ni ArduinoBLE, ni uMyo_BLE.
    - Este archivo es autosuficiente: un solo .ino, sin pestanas extra.

  Los uMyo emiten sus datos dentro del propio paquete de publicidad BLE, de modo
  que basta con escanear y leerlos; no hay que conectarse a ellos. El formato
  del paquete esta portado tal cual desde uMyo_BLE.cpp de Ultimate Robotics.

  Configuracion en el IDE de Arduino
  ---------------------------------
    Placa:              ESP32S3 Dev Module
    USB CDC On Boot:    Disabled      <-- si no, Serial sale por el USB nativo
                                          y no veras nada en el puerto del
                                          puente CH343
    Puerto:             el COM de la placa (NO el del U2D2 de la mano)
    Monitor Serie:      921600

  Salida (una linea por muestra):
      <emg1> <emg2> <emg3>
  Siempre 3 columnas separadas por espacio, que es lo que espera
  parse_emg_line() en backend/app/services/emg_service.py.

  Las lineas de diagnostico empiezan por "---". El backend las descarta (estan
  en su lista de palabras a ignorar), pero tu si las ves en el Monitor Serie.
*/

#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

// Debe coincidir con SerialManager(baudrate=...) en backend/core/serial/manager.py
static const unsigned long SERIAL_BAUD = 921600;

// Canales que espera el backend (emg1, emg2, emg3).
static const int NUM_CANALES = 3;

// Periodo de impresion (~33 Hz, igual que el ejemplo original de uMyo).
static const unsigned long PERIODO_MS = 30;

// Un sensor que lleva este tiempo sin emitir se da por desconectado.
static const unsigned long TIMEOUT_MS = 5000;

// Cada cuanto avisar del estado cuando no hay sensores.
static const unsigned long PERIODO_DIAG_MS = 2000;

static const int MAX_SENSORES = 8;

struct SensorUMyo {
  uint32_t id;
  float    nivel;      // nivel muscular calculado
  int      bateria_mv;
  uint32_t visto_ms;
};

static SensorUMyo sensores[MAX_SENSORES];
static int numSensores = 0;

// Las callbacks del escaneo corren en la tarea BLE; la tabla se toca tambien
// desde loop(). Este mutex evita leer una entrada a medio escribir.
static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;

// Cada cuanto vaciar el buffer de anuncios acumulados (ver loop()).
static const unsigned long PERIODO_LIMPIEZA_MS = 1000;

static unsigned long ultimoDiagnostico = 0;
static unsigned long ultimaImpresion = 0;
static unsigned long ultimaLimpieza = 0;
static bool anuncioHecho = false;

/*
  Extrae el identificador del sensor de su MAC, igual que la libreria original:
  bytes 1..4 de la direccion.
*/
static uint32_t idDesdeMac(const char *mac) {
  uint8_t b[6] = {0, 0, 0, 0, 0, 0};
  for (int n = 0; n < 6; n++) {
    for (int p = 0; p < 2; p++) {
      char c = mac[n * 3 + p];
      b[n] <<= 4;
      if (c >= '0' && c <= '9') b[n] += c - '0';
      else if (c >= 'a' && c <= 'f') b[n] += c + 10 - 'a';
      else if (c >= 'A' && c <= 'F') b[n] += c + 10 - 'A';
    }
  }
  return ((uint32_t)b[1] << 24) | ((uint32_t)b[2] << 16) | ((uint32_t)b[3] << 8) | b[4];
}

static void guardarMuestra(uint32_t id, float nivel, int bateria_mv) {
  uint32_t ahora = millis();
  portENTER_CRITICAL(&mux);
  int idx = -1;
  for (int i = 0; i < numSensores; i++) {
    if (sensores[i].id == id) { idx = i; break; }
  }
  if (idx < 0 && numSensores < MAX_SENSORES) {
    idx = numSensores++;
    sensores[idx].id = id;
  }
  if (idx >= 0) {
    sensores[idx].nivel = nivel;
    sensores[idx].bateria_mv = bateria_mv;
    sensores[idx].visto_ms = ahora;
  }
  portEXIT_CRITICAL(&mux);
}

/*
  Parsea el paquete de publicidad de un uMyo.

  Estructura buscada (portada de uMyo_BLE.cpp):
    ... [0x08]['u']['M']['y']['o'] ... [0xFF] <payload>
         ^ nombre corto del dispositivo        ^ datos del fabricante

  Payload, en big endian:
    adc_id(1) bateria(1) sp0(1) media_muscular(1)
    sp1(2) sp2(2) sp3(2) qw(2) qx(1) qy(1) qz(1)

  El nivel muscular es sp2 + 2*sp3, igual que uMyo_BLE::getMuscleLevel().
*/
static void parsearAnuncio(const uint8_t *pack, int len, const char *mac) {
  if (pack == nullptr || len < 20) return;

  /*
    IMPORTANTE — se busca la marca "uMyo" EMPEZANDO POR EL FINAL.

    La libreria BLE del core de ESP32 no reemplaza el payload de un dispositivo
    ya conocido: lo va CONCATENANDO. Tras N anuncios el buffer contiene los N
    registros pegados (crece unos 29 bytes cada vez). Si se busca la primera
    marca se lee siempre el anuncio mas viejo y el valor sale congelado.
    El dato vivo es el ULTIMO registro del buffer.
  */
  int marca = -1;
  for (int i = len - 6; i >= 1; i--) {
    if (pack[i] == 8 && pack[i + 1] == 'u' && pack[i + 2] == 'M'
        && pack[i + 3] == 'y' && pack[i + 4] == 'o') {
      marca = i;
      break;
    }
  }
  if (marca < 0) return;

  // Avanzar hasta los datos del fabricante (tipo 0xFF) de ese registro.
  int pp = marca;
  while (pp < len && pack[pp] != 255) pp++;
  if (pp >= len) return;
  pp++;

  // La libreria original no comprobaba limites; aqui si, para no leer fuera
  // del buffer y provocar otro panic.
  if (pp + 15 > len) return;

  /* int adc_id      = */ pack[pp++];
  int batt_level    = pack[pp++];
  /* int16_t sp0     = */ pack[pp++];   // componente 0, precision reducida
  /* int muscle_avg  = */ pack[pp++];
  /* int16_t sp1     = */ pp += 2;
  int16_t sp2       = (int16_t)((pack[pp] << 8) | pack[pp + 1]); pp += 2;
  int16_t sp3       = (int16_t)((pack[pp] << 8) | pack[pp + 1]); pp += 2;

  float nivel = (float)sp2 + 2.0f * (float)sp3;
  guardarMuestra(idDesdeMac(mac), nivel, 2000 + batt_level * 10);
}

/*
  Callback del escaneo.

  Ojo con la firma: la libreria BLE incluida en el core de ESP32 declara
  `onResult(BLEAdvertisedDevice advertisedDevice)` POR VALOR, tanto en el core
  2.x como en el 3.x. (NimBLE-Arduino, que es otra libreria distinta, si usa
  puntero. No confundirlas.)
*/
class CallbackEscaneo : public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice dev) override {
    String mac = dev.getAddress().toString().c_str();
    parsearAnuncio(dev.getPayload(), dev.getPayloadLength(), mac.c_str());
  }
};

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(300);
  Serial.println("--- EMGTRAINNER: puente uMyo (BLE nativo ESP32). Iniciando...");

  BLEDevice::init("");
  BLEScan *scan = BLEDevice::getScan();
  // El segundo argumento (duplicados) es imprescindible: los uMyo mandan cada
  // muestra en un anuncio nuevo. Si se filtran duplicados solo llega la primera.
  scan->setAdvertisedDeviceCallbacks(new CallbackEscaneo(), true);
  scan->setActiveScan(true);
  scan->setInterval(100);
  scan->setWindow(99);
  // Duracion 0 = escaneo continuo en segundo plano.
  scan->start(0, nullptr, false);

  Serial.println("--- Escaneando. Encienda los uMyo y pongalos en modo BLE.");
}

void loop() {
  uint32_t ahora = millis();

  /*
    Vaciar periodicamente los resultados del escaneo.

    Sin esto el buffer de anuncios crece sin limite (unos 29 bytes por anuncio
    y por sensor: en el diagnostico llego a 15 KB tras 952 anuncios). Acabaria
    agotando la memoria y ralentizando el parseo. clearResults() lo reinicia
    sin detener el escaneo.
  */
  if (ahora - ultimaLimpieza > PERIODO_LIMPIEZA_MS) {
    ultimaLimpieza = ahora;
    BLEDevice::getScan()->clearResults();
  }

  // Retirar los sensores que dejaron de emitir.
  portENTER_CRITICAL(&mux);
  for (int i = 0; i < numSensores; ) {
    if (ahora - sensores[i].visto_ms > TIMEOUT_MS) {
      for (int j = i + 1; j < numSensores; j++) sensores[j - 1] = sensores[j];
      numSensores--;
    } else {
      i++;
    }
  }

  // Copia local para no imprimir con el mutex tomado.
  SensorUMyo copia[MAX_SENSORES];
  int total = numSensores;
  for (int i = 0; i < total; i++) copia[i] = sensores[i];
  portEXIT_CRITICAL(&mux);

  if (total == 0) {
    anuncioHecho = false;
    if (ahora - ultimoDiagnostico > PERIODO_DIAG_MS) {
      ultimoDiagnostico = ahora;
      Serial.println("--- Sin uMyo detectados. Enciendalos y pongalos en modo BLE.");
    }
    delay(PERIODO_MS);
    return;
  }

  /*
    Orden estable por ID: el canal 1 debe ser SIEMPRE el mismo sensor fisico
    entre arranques. Si dependiera del orden de descubrimiento, las columnas del
    CSV se intercambiarian de una sesion a otra y el modelo se entrenaria con
    canales mezclados.
  */
  for (int i = 1; i < total; i++) {
    SensorUMyo actual = copia[i];
    int j = i - 1;
    while (j >= 0 && copia[j].id > actual.id) { copia[j + 1] = copia[j]; j--; }
    copia[j + 1] = actual;
  }

  // Al detectar sensores nuevos, listar una vez que ID es cada canal. Sirve
  // para saber que sensor fisico corresponde a emg1, emg2 y emg3.
  if (!anuncioHecho) {
    anuncioHecho = true;
    Serial.print("--- ");
    Serial.print(total);
    Serial.print(" uMyo detectados. Canales por ID:");
    for (int i = 0; i < total; i++) {
      Serial.print("  emg");
      Serial.print(i + 1);
      Serial.print("=0x");
      Serial.print(copia[i].id, HEX);
      Serial.print(" (");
      Serial.print(copia[i].bateria_mv);
      Serial.print("mV)");
    }
    Serial.println();
  }

  if (ahora - ultimaImpresion >= PERIODO_MS) {
    ultimaImpresion = ahora;
    // Siempre 3 columnas: 0 si falta un sensor, para que el CSV no cambie de
    // numero de columnas a mitad de sesion.
    for (int c = 0; c < NUM_CANALES; c++) {
      float valor = (c < total) ? copia[c].nivel : 0.0f;
      Serial.print(valor, 2);
      if (c < NUM_CANALES - 1) Serial.print(' ');
    }
    Serial.println();
  }

  delay(5);
}
