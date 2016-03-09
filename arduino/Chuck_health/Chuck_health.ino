#include "AnalogSensor.h"
#define LED_PIN 13
#define SOIL_PIN 7
#define SOIL_ADC A0
#define TEMP_ADC A1
#define LIGHT_ADC A2

// two sticks in the ground
AnalogSensor AS_soil = AnalogSensor("soil", 20, 10000, SOIL_ADC, SOIL_PIN, 1.0);
// LM35
AnalogSensor AS_temp = AnalogSensor("temp", 10, 1000, TEMP_ADC, 0.488f);
// LDR
AnalogSensor AS_light = AnalogSensor("light", 10, 1000, LIGHT_ADC, 1.0);

bool sendRequested = false;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(57600);
}

unsigned long currentMillis = millis();
void loop() {
    currentMillis = millis();
    // ping sensors
    digitalWrite(LED_PIN, HIGH);
    AS_temp.tick(currentMillis, sendRequested);
    delay(50);
    AS_soil.tick(currentMillis, sendRequested);
    delay(50);
    AS_light.tick(currentMillis, sendRequested);
    delay(50);
    digitalWrite(LED_PIN, LOW);
    if (sendRequested) sendRequested = false;
}

void serialEvent() {
  while (Serial.available()) {
    Serial.read();
  }
  sendRequested = true;
  // send sensor values
//  send_current_averages(&ABsoil);
//  send_current_averages(&ABlight);
//  send_current_averages(&ABtemp);
}

//void send_current_averages(AveragingBuffer* AB) {
//  Serial.print(AB->getType());
//  Serial.print(":");
//  Serial.println(AB->getAverage());
//}

