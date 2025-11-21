#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ==== Cấu hình Wi-Fi ====
const char* ssid = "4 Thang Dan";       // Đổi tên WiFi
const char* password = "0867533106";
// ==== LCD 16x2 ====
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Thay 0x27 nếu khác địa chỉ I2C

// ==== Web server trên port 80 ====
WebServer server(80);

// Hàm xử lý update số ngón tay
void handleUpdate() {
  if (server.hasArg("fingers")) {
    String data = server.arg("fingers");
    int fingers = data.toInt();

    Serial.print("Received fingers: ");
    Serial.println(fingers);

    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Fingers:");
    lcd.setCursor(0,1);
    lcd.print(fingers);

    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Missing parameter");
  }
}

void setup() {
  Serial.begin(115200);

  // ==== Khởi tạo I2C với SDA/SCL mới ====
  Wire.begin(4, 5); // SDA = GPIO18, SCL = GPIO19

  // ==== Khởi tạo LCD ====
  lcd.begin();
  delay(100);
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("ESP32-C3 Booting");

  // ==== Kết nối Wi-Fi ====
  WiFi.begin(ssid, password);
  lcd.setCursor(0,1);
  lcd.print("Connecting...");
  Serial.println("Connecting to Wi-Fi...");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Connected! IP: ");
  Serial.println(WiFi.localIP());
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("IP:");
  lcd.setCursor(0,1);
  lcd.print(WiFi.localIP());

  // ==== Cấu hình Web server ====
  server.on("/update", handleUpdate);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
