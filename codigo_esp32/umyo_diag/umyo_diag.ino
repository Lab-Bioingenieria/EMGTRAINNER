/*
  EMGTRAINNER — DIAGNOSTICO del anuncio BLE de los uMyo
  =====================================================

  Este sketch NO sirve para grabar sesiones. Es solo para averiguar por que los
  valores salen congelados en umyo_bridge.ino.

  Vuelca, para cada anuncio BLE que contenga "uMyo":
    - la MAC del sensor
    - el paquete de publicidad completo en hexadecimal
    - el desplazamiento donde empiezan los datos del fabricante
    - los campos ya interpretados (sp2, sp3 y el nivel muscular)

  Como leer el resultado
  ----------------------
  Compara dos volcados seguidos DEL MISMO sensor (misma MAC):

    a) Si el HEX cambia entre volcados pero sp2/sp3 no  -> estoy leyendo los
       bytes equivocados: hay que corregir los desplazamientos.

    b) Si el HEX es identico volcado tras volcado        -> el ESP32 nos entrega
       siempre el mismo anuncio cacheado: hay que tocar la configuracion del
       escaneo (filtro de duplicados).

  Configuracion: ESP32S3 Dev Module, USB CDC On Boot = Disabled, monitor 921600.
*/

#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

static const unsigned long SERIAL_BAUD = 921600;

// Se limita el ritmo de volcado para que el monitor sea legible.
static const unsigned long PERIODO_VOLCADO_MS = 500;

static unsigned long ultimoVolcado = 0;
static uint32_t totalAnuncios = 0;

static void volcarHex(const uint8_t *pack, int len) {
  for (int i = 0; i < len; i++) {
    if (pack[i] < 0x10) Serial.print('0');
    Serial.print(pack[i], HEX);
    Serial.print(' ');
  }
}

static void analizar(const uint8_t *pack, int len, const char *mac) {
  if (pack == nullptr || len < 20) return;

  // Buscar la marca [0x08]['u']['M']['y']['o']
  int marca = -1;
  for (int pp = 1; pp < len - 5; pp++) {
    if (pack[pp] == 8 && pack[pp + 1] == 'u' && pack[pp + 2] == 'M'
        && pack[pp + 3] == 'y' && pack[pp + 4] == 'o') {
      marca = pp;
      break;
    }
  }
  if (marca < 0) return;   // no es un uMyo

  totalAnuncios++;

  unsigned long ahora = millis();
  if (ahora - ultimoVolcado < PERIODO_VOLCADO_MS) return;
  ultimoVolcado = ahora;

  // Avanzar hasta los datos del fabricante (0xFF)
  int pp = marca;
  while (pp < len && pack[pp] != 255) pp++;

  Serial.println();
  Serial.print("--- MAC ");
  Serial.print(mac);
  Serial.print(" | len=");
  Serial.print(len);
  Serial.print(" | marca uMyo en ");
  Serial.print(marca);
  Serial.print(" | 0xFF en ");
  Serial.print(pp < len ? pp : -1);
  Serial.print(" | anuncios totales=");
  Serial.println(totalAnuncios);

  Serial.print("--- HEX ");
  volcarHex(pack, len);
  Serial.println();

  if (pp >= len) {
    Serial.println("--- Sin bloque 0xFF: el anuncio no trae datos del fabricante.");
    return;
  }
  pp++;

  if (pp + 15 > len) {
    Serial.print("--- Payload corto: quedan ");
    Serial.print(len - pp);
    Serial.println(" bytes, hacen falta 15.");
    return;
  }

  int adc_id     = pack[pp++];
  int batt_level = pack[pp++];
  int sp0        = pack[pp++];
  int musc_avg   = pack[pp++];
  int16_t sp1    = (int16_t)((pack[pp] << 8) | pack[pp + 1]); pp += 2;
  int16_t sp2    = (int16_t)((pack[pp] << 8) | pack[pp + 1]); pp += 2;
  int16_t sp3    = (int16_t)((pack[pp] << 8) | pack[pp + 1]); pp += 2;

  Serial.print("--- adc_id=");   Serial.print(adc_id);
  Serial.print(" batt=");        Serial.print(2000 + batt_level * 10);
  Serial.print("mV sp0=");       Serial.print(sp0);
  Serial.print(" musc_avg=");    Serial.print(musc_avg);
  Serial.print(" sp1=");         Serial.print(sp1);
  Serial.print(" sp2=");         Serial.print(sp2);
  Serial.print(" sp3=");         Serial.print(sp3);
  Serial.print(" -> nivel=");    Serial.println((float)sp2 + 2.0f * (float)sp3);
}

class CallbackDiag : public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice dev) override {
    String mac = dev.getAddress().toString().c_str();
    analizar(dev.getPayload(), dev.getPayloadLength(), mac.c_str());
  }
};

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(300);
  Serial.println("--- DIAGNOSTICO uMyo. Contraiga el antebrazo mientras mira los volcados.");

  BLEDevice::init("");
  BLEScan *scan = BLEDevice::getScan();
  scan->setAdvertisedDeviceCallbacks(new CallbackDiag(), true);
  scan->setActiveScan(true);
  scan->setInterval(100);
  scan->setWindow(99);
  scan->start(0, nullptr, false);
}

void loop() {
  delay(1000);
  if (totalAnuncios == 0) {
    Serial.println("--- Ningun anuncio de uMyo recibido todavia.");
  }
}
