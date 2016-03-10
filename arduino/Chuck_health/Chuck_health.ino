#include <Arduino.h>
#include "AnalogSensor.h"
#include "OneWire.h"
#include "OneWireSensor.h"

#define SOIL_PIN 7
#define SOIL_ADC A0
#define TEMP_ADC A1
#define LIGHT_ADC A2
#define NO_DIGITAL 0
#define ONE_WIRE_BUS 8

AnalogSensor AS_soil("soil", 20, 10000, SOIL_ADC, SOIL_PIN, 1.0f);      // two sticks in the ground
AnalogSensor AS_temp("temp", 10, 1000, TEMP_ADC, NO_DIGITAL, 0.488f);   // LM35
AnalogSensor AS_light("light", 10, 1000, LIGHT_ADC, NO_DIGITAL, 1.0f);  // LDR

OneWire ow_bus(ONE_WIRE_BUS);
OneWireSensor DS_temp("ds_temp", &ow_bus, 5, 2000, 1.0f/16);  // DS18b20

bool sendRequested = false;

void setup() {
  Serial.begin(57600);
}

unsigned long currentMillis = millis();
void loop() {
    currentMillis = millis();

    // ping ALL the sensors to have 'em do their thing
    AS_soil.tick(currentMillis, sendRequested);
    AS_temp.tick(currentMillis, sendRequested);
    AS_light.tick(currentMillis, sendRequested);
    DS_temp.tick(currentMillis, sendRequested);

    if (sendRequested) sendRequested = false;
}

void serialEvent() {
  while (Serial.available()) { Serial.read(); }
  sendRequested = true;
}
