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

#define SECOND 1000
#define MINUTE 60*1000l

// two sticks in the ground
AnalogSensor AS_soil("soil", 3, 10*MINUTE, 30*MINUTE, SOIL_ADC, SOIL_PIN);
// LM35 analog temperature sensor
AnalogSensor AS_temp("temp", 10, 6*SECOND, 1*MINUTE, TEMP_ADC, NO_DIGITAL);
// LDR
AnalogSensor AS_light("light", 10, 6*SECOND, 1*MINUTE, LIGHT_ADC, NO_DIGITAL);

// DS18b20 digital temperature sensor
OneWire ow_bus(ONE_WIRE_BUS);
OneWireSensor DS_temp("temp", &ow_bus, 10, 6*SECOND, 1*MINUTE);

unsigned long currentMillis;

void setup() {
  AS_temp.setScaleFactor(0.488f);
  DS_temp.setScaleFactor(1.0f/16);
  Serial.begin(57600);
}

void loop() {
    currentMillis = millis();

    // ping ALL the sensors to have 'em do their thing
    AS_soil.tick(currentMillis);
    AS_temp.tick(currentMillis);
    AS_light.tick(currentMillis);
    DS_temp.tick(currentMillis);
}
