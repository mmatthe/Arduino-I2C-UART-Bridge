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
    String input = String(line).trim();
    if (input.length() == 0) {
        debug("Error: No address provided");
        return;
    }
    
    // Convert hex string to integer
    char* endptr;
    long addr = strtol(input.c_str(), &endptr, 16);
    
    // Check if conversion was successful and address is valid I2C range (7-bit: 0x08-0x77)
    if (*endptr != '\0' || addr < 0x08 || addr > 0x77) {
        debug("Error: Invalid I2C address. Must be hex value between 0x08 and 0x77");
        return;
    }
    
    address = (int8_t)addr;
    debug("I2C address set to: 0x" + String(address, HEX));
}

void readBytes(const char* line) {
    // parse number of bytes from line. Read from I2C and print hex-representation of read bytes to Serial
    String input = String(line).trim();
    if (input.length() == 0) {
        debug("Error: No byte count provided");
        return;
    }
    
    // Convert hex string to integer
    char* endptr;
    long numBytes = strtol(input.c_str(), &endptr, 16);
    
    // Validate input
    if (*endptr != '\0' || numBytes <= 0 || numBytes > 32) {
        debug("Error: Invalid byte count. Must be hex value between 0x01 and 0x20 (1-32 bytes)");
        return;
    }
    
    // Check if address has been set
    if (address == 0) {
        debug("Error: No I2C address set. Use 'a xx' command first");
        return;
    }
    
    // Request bytes from I2C device
    int received = Wire.requestFrom((int)address, (int)numBytes);
    if (received == 0) {
        debug("Error: No response from I2C device at address 0x" + String(address, HEX));
        return;
    }
    
    // Read and print received bytes in hex format
    String output = "";
    bool first = true;
    while (Wire.available()) {
        if (!first) output += " ";
        first = false;
        
        uint8_t data = Wire.read();
        if (data < 0x10) output += "0";
        output += String(data, HEX);
    }
    
    Serial.println(output.toUpperCase());
    debug("Read " + String(received) + " bytes from I2C device");
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
