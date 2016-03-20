#include <Arduino.h>
#include <OneWire.h>
#include "OneWireSensor.h"
#include "AnalogSensor.h"

#define NO_DIGITAL 0
#define ONE_WIRE_BUS 8
#define STRAIN_ADC A5

OneWire ow_bus(ONE_WIRE_BUS);
OneWireSensor DS_temp("temp", &ow_bus, 10, 6000, 60000);  // DS18b20

AnalogSensor AS_strain("strain", 10, 500, 5000, STRAIN_ADC, NO_DIGITAL);

unsigned long currentMillis;
void setup() {
  DS_temp.setScaleFactor(1.0f/16);
  Serial.begin(57600);
}

void loop() {
  currentMillis = millis();
  AS_strain.tick(currentMillis);
  DS_temp.tick(currentMillis);
}
