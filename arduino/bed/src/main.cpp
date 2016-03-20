#include "Arduino.h"
#include "OneWire.h"
#include "OneWireSensor.h"
#include "AnalogSensor.h"

#define NO_DIGITAL 0
#define ONE_WIRE_BUS 8
#define STRAIN_ADC A5

OneWire ow_bus(ONE_WIRE_BUS);
OneWireSensor DS_temp("temp", &ow_bus, 5, 2000, 1.0f/16);  // DS18b20
AnalogSensor AS_strain("strain", 10, 100, STRAIN_ADC, NO_DIGITAL, 1.0f);

bool sendRequested = false;

unsigned long currentMillis;
void setup() {
  Serial.begin(57600);
}

void loop() {
  currentMillis = millis();
  AS_strain.tick(currentMillis, sendRequested);
  DS_temp.tick(currentMillis, sendRequested);
  if (sendRequested) sendRequested = false;
}


void serialEvent() {
  while (Serial.available()) Serial.read();
  sendRequested = true;
}
