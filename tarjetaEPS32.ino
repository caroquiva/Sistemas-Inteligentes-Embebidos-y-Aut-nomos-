#include "WiFi.h"
#include <WebServer.h>
#include "esp_system.h"
#include <ESP32Servo.h>

// Declaración correcta de la función interna de lectura de temperatura
#ifdef __cplusplus
extern "C" {
#endif
uint8_t temprature_sens_read();
#ifdef __cplusplus
}
#endif

// Crear el objeto servo
Servo miServo;

// Definir el pin GPIO al que se conecta el cable de señal (Naranja)
const int pinServo = 18;
int anguloActual = 0;
bool incrementando = true;
unsigned long ultimoMovimientoServo = 0;

// Credenciales Wi-Fi
const char* ssid = "OPPO A5 Pro 5G v5gz";
const char* password = "myc02012307";

WebServer server(80);
String tablaHTML = "";

// Función para generar la página HTML
String obtenerHTML() {
  int rssi = WiFi.RSSI();
  String redConectada = (WiFi.status() == WL_CONNECTED) ? WiFi.SSID() : "Desconectado";
  float tempCelsius = (temprature_sens_read() - 32) / 1.8;

  String html = "<!DOCTYPE html><html lang='es'><head>";
  html += "<meta charset='UTF-8'>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<title>ESP32 - Panel de Control</title>";
  html += "<style>";
  html += "body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f9; padding: 20px; }";
  html += ".grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; max-width: 900px; margin: 0 auto; }";
  html += ".card { background: white; width: 260px; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }";
  html += "h1, h2 { color: #333; font-size: 20px; margin-bottom: 10px; }";
  html += ".val { font-size: 40px; font-weight: bold; color: #007bff; margin: 15px 0; }";
  html += ".sub { color: #666; font-size: 14px; }";
  html += "table { width: 100%; max-width: 800px; margin: 20px auto; border-collapse: collapse; background: #fff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }";
  html += "th, td { padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }";
  html += "th { background-color: #007bff; color: white; }";
  html += "tr:hover { background-color: #f1f1f1; }";
  html += "a.btn { display: inline-block; padding: 10px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; }";
  html += "</style>";

  html += "<script>";
  html += "setInterval(function() {";
  html += "  fetch('/data').then(response => response.json()).then(data => {";
  html += "    document.getElementById('rssi').innerText = data.rssi + ' dBm';";
  html += "    document.getElementById('ssid').innerText = data.ssid;";
  html += "    document.getElementById('servo-angle').innerText = data.angulo + '°';";
  html += "  });";
  html += "}, 1000);";
  html += "</script>";
  html += "</head><body>";

  html += "<div class='grid'>";

  // Tarjeta Wi-Fi
  html += "<div class='card'>";
  html += "<h1>Señal Wi-Fi</h1>";
  html += "<p class='sub'>Conectado a: <b id='ssid'>" + redConectada + "</b></p>";
  html += "<div class='val' id='rssi'>" + String(rssi) + " dBm</div>";
  html += "</div>";

  // Tarjeta ESP32
  html += "<div class='card'>";
  html += "<h1>Tarjeta ESP32</h1>";
  html += "<p class='sub'>Temperatura Interna</p>";
  html += "<div class='val'>" + String(tempCelsius, 1) + " °C</div>";
  html += "</div>";

  // Tarjeta Servomotor
  html += "<div class='card'>";
  html += "<h1>Servomotor MG90S</h1>";
  html += "<p class='sub'>GPIO Signal: <b>Pin " + String(pinServo) + "</b></p>";
  html += "<div class='val' id='servo-angle'>" + String(anguloActual) + "°</div>";
  html += "</div>";

  html += "</div>";

  // Tabla de redes escaneadas
  html += "<h2>Lista de Redes Wi-Fi Escaneadas</h2>";
  html += "<table><thead><tr>";
  html += "<th>#</th>";
  html += "<th>Red (SSID)</th>";
  html += "<th>Señal (RSSI)</th>";
  html += "<th>Seguridad</th>";
  html += "</tr></thead><tbody>";
  html += tablaHTML;
  html += "</tbody></table>";

  html += "<a href='/' class='btn'>Actualizar Escaneo</a>";
  html += "</body></html>";
  return html;
}

void handleRoot() {
  server.send(200, "text/html", obtenerHTML());
}

void handleData() {
  String json = "{\"ssid\":\"" + WiFi.SSID() + "\",\"rssi\":" + String(WiFi.RSSI()) + ",\"angulo\":" + String(anguloActual) + "}";
  server.send(200, "application/json", json);
}

void setup() {
  Serial.begin(115200);

  miServo.attach(pinServo, 500, 2400);
  miServo.write(anguloActual);
  Serial.println("Servomotor MG90S inicializado.");

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  Serial.println("\nIniciando conexión Wi-Fi...");
  WiFi.begin(ssid, password);

  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 20) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n¡Conexión exitosa!");
    Serial.print("Ingresa desde el navegador a: http://");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nNo se pudo conectar a la red.");
  }

  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.begin();
  Serial.println("Servidor Web HTTP activo.");
}

void loop() {
  server.handleClient();

  // Movimiento progresivo sin bloqueos
  if (millis() - ultimoMovimientoServo >= 15) {
    ultimoMovimientoServo = millis();

    if (incrementando) {
      anguloActual++;
      if (anguloActual >= 180) {
        anguloActual = 180;
        incrementando = false;
      }
    } else {
      anguloActual--;
      if (anguloActual <= 0) {
        anguloActual = 0;
        incrementando = true;
      }
    }
    miServo.write(anguloActual);
  }

  // Escaneo periódico cada 10 segundos
  static unsigned long ultimoEscaneo = 0;
  if (millis() - ultimoEscaneo > 10000) {
    ultimoEscaneo = millis();

    Serial.println("\nEscaneando redes Wi-Fi...");
    int n = WiFi.scanNetworks();
    tablaHTML = "";

    if (n > 0) {
      for (int i = 0; i < n; ++i) {
        tablaHTML += "<tr>";
        tablaHTML += "<td>" + String(i + 1) + "</td>";
        tablaHTML += "<td><b>" + WiFi.SSID(i) + "</b></td>";
        tablaHTML += "<td>" + String(WiFi.RSSI(i)) + " dBm</td>";
        tablaHTML += "<td>" + String((WiFi.encryptionType(i) == WIFI_AUTH_OPEN) ? "Abierta 🔓" : "Protegida 🔒") + "</td>";
        tablaHTML += "</tr>";
      }
    }
    WiFi.scanDelete();
  }
}