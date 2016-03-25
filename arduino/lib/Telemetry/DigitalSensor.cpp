#include "DigitalSensor.h"

DigitalSensor::DigitalSensor(const char* name,
                            uint8_t bufsize,
                            unsigned long sample_interval,
                            unsigned long send_interval,
                            uint8_t dig_pin) :
              GenericSensor(name, bufsize, sample_interval, send_interval)
{
  _aux_pin = 0;
  _dig_pin = dig_pin;
  pinMode(_dig_pin, INPUT_PULLUP);
}

DigitalSensor::~DigitalSensor() { }

uint16_t DigitalSensor::readSensor()
{
  if (_aux_pin != 0) digitalWrite(_aux_pin, HIGH);
  uint16_t state = digitalRead(_dig_pin);
  if (_dig_pin != 0) digitalWrite(_dig_pin, LOW);

  return state;
}

void DigitalSensor::auxPin(uint8_t aux_pin) {
  _aux_pin = aux_pin;
  if (_aux_pin != 0) pinMode(_aux_pin, OUTPUT);
}
