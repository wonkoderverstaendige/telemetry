#include <Arduino.h>
#include <OneWire.h>
#include "GenericSensor.h"
#include "AnalogSensor.h"
#include "OneWireSensor.h"

#define NUM_SENSORS 4
#define SOIL_ADC A0
#define SOIL_AUX 7
#define TEMP_ADC A1
#define LIGHT_ADC A2
#define ONE_WIRE_BUS 8

#define SECOND 1000l
#define MINUTE 60*1000l

OneWire ow_bus(ONE_WIRE_BUS);
// 0, two sticks in the ground
AnalogSensor AS_soil("soil", SOIL_ADC, 3, 10*MINUTE, 30*MINUTE);
// 1, LM35 analog temperature sensor
AnalogSensor AS_temp("temp", TEMP_ADC, 10, 6*SECOND, 1*MINUTE);
// 2, LDR
AnalogSensor AS_light("light", LIGHT_ADC, 10, 6*SECOND, 1*MINUTE);
// 3, DS18b20 digital temperature sensor
OneWireSensor OW_temp("ds_temp", &ow_bus, 10, 6*SECOND, 1*MINUTE);

GenericSensor* sensors[NUM_SENSORS] = {&AS_soil, &AS_temp, &AS_light, &OW_temp};

void setup() {
  Serial.begin(57600);

  sensors[0]->auxPin(SOIL_AUX);
  sensors[1]->setScaleFactor(0.488f);
  sensors[3]->setScaleFactor(1.0f/16);
}

void loop() {
  // ping ALL the sensors to have 'em do their thing
  for (byte i=0; i<NUM_SENSORS; i++) sensors[i]->tick(millis());
}
