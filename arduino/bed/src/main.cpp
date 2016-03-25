#include <Arduino.h>
#include <OneWire.h>
#include "OneWireSensor.h"
#include "AnalogSensor.h"
#include "DigitalSensor.h"

#define NUM_SENSORS 3
#define ONE_WIRE_BUS 8
#define STRAIN_ADC A5
#define MOTION_DIG 2

#define SECOND 1000
#define MINUTE 60*1000l

OneWire ow_bus(ONE_WIRE_BUS);
// 0: 2 strain gauges in wheatstone bridge
AnalogSensor AS_strain("strain", 20, 500, 10*SECOND, STRAIN_ADC);
// 1: DS18b20
OneWireSensor OW_temp("temp", &ow_bus, 10, 6*SECOND, 1*MINUTE);
// 2: PIR with digital output
DigitalSensor DS_motion("motion", 1, 0, 0, MOTION_DIG);

GenericSensor* sensors[NUM_SENSORS] = {&OW_temp, &AS_strain, &DS_motion};

void motion() {
  Serial.println("motion!");
  sensors[2]->tick(millis());
}

void setup() {
  Serial.begin(57600);

  sensors[2]->setScaleFactor(1.0f/16);
  attachInterrupt(digitalPinToInterrupt(MOTION_DIG), motion, CHANGE);
}

void loop() {
  // ping ALL the sensors to have 'em do their thing
  // NOTE: Skipping last sensor, we call that one via interrupt
  for (byte i=0; i<NUM_SENSORS-1; i++) sensors[i]->tick(millis());
}
