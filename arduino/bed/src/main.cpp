#include <Arduino.h>
#include <OneWire.h>
#include "OneWireSensor.h"
#include "AnalogSensor.h"

#define NO_DIGITAL 0
#define ONE_WIRE_BUS 8
#define STRAIN_ADC A5

#define SECOND 1000
#define MINUTE 60*1000l

OneWire ow_bus(ONE_WIRE_BUS);
OneWireSensor DS_temp("temp", &ow_bus, 10, 6*SECOND, 1*MINUTE);  // DS18b20

AnalogSensor AS_strain("strain", 20, 500, 10*SECOND, STRAIN_ADC, NO_DIGITAL);

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
