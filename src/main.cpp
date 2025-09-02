#include <Arduino.h>
#include <Wire.h>

int8_t address;
bool showDebug = true;

void setup() {
    Serial.begin(9600);
    Serial.setTimeout(100000);
    Wire.begin();

}

void debug(const String& line, bool force=false) {
    if (showDebug || force) {
        Serial.print("[DBG] ");
        for (int i = 0; i < line.length(); i++) {
            Serial.print(line[i]);
            if (line[i] == '\n')
                Serial.print("[DBG] ");
        }
        Serial.println();
    }
}

void parseAddress(const char* line) {
    // Parse hex byte from line and save to address variable
}

void readBytes(const char* line) {
    // parse number of bytes from line. Read from I2C and print hex-representation of read bytes to Serial
}

void writeBytes(const char* line) {
    // parse the bytes from the line and send them to the device via I2C.
}

void processLine(const String& line) {
    if (line[0] == 'a') {
        parseAddress(line+1);
    }
    else if (line[0] == 'r') {
        readBytes(line+1);
    }

    else if (line[0] == 'w') {
        writeBytes(line+1);
    }
    else {
        debug("Help: (xx = hex byte) \n\n"
              "a xx\\n : set target address\n"
              "w xx xx xx xx xx ...\\n : write given byte sequence\n"
              "r xx\\n : read xx bytes from device");
    }

}

void loop() {
    String line = Serial.readStringUntil('\n');
    line.trim();
    processLine(line);
}
