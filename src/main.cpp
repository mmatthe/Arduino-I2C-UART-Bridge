#include <Arduino.h>
#include <Wire.h>


void setup() {
    Serial.begin(9600);
    Serial.setTimeout(100000);
    Wire.begin();

}

void processLine(const String& line) {
    if (line[0] == 'r') {
        uint8_t addr = line[1] - '0';
        uint8_t bytes = line[2] - '0';

        Serial.print("Requesting ");
        Serial.print(int(bytes));
        Serial.print(" bytes from addr ");
        Serial.println(int(addr));

        Wire.requestFrom(addr, bytes);
        Serial.print(" >>> ");
        while (Wire.available()) {
            char c = Wire.read();
            Serial.print(c);
        }
        Serial.println();
    }

    if (line[0] == 'w') {
        uint8_t addr = line[1] - '0';
        String txt = line.substring(2);

        Serial.print("Sending to addr ");
        Serial.print(int(addr));
        Serial.print(" the data '");
        Serial.print(txt);
        Serial.println("'");

        Wire.beginTransmission(addr);
        Wire.write(txt.c_str());
        Wire.endTransmission();
    }

}

void loop() {
    String line = Serial.readStringUntil('\n');
    line.trim();
    processLine(line);
}
