#include "AnalogSensor.h"

AnalogSensor::AnalogSensor(const char* name,
                           uint8_t adc_pin,
                           uint8_t bufsize,
                           unsigned long sample_interval,
                           unsigned long send_interval) :
              GenericSensor(name, bufsize, sample_interval, send_interval)
{
  _aux_pin = 0;
  _adc_pin = adc_pin;
  pinMode(_adc_pin, INPUT);
}

AnalogSensor::~AnalogSensor() { }

uint16_t AnalogSensor::readSensor()
{
  if (_aux_pin != 0) digitalWrite(_aux_pin, HIGH);
  uint16_t val = analogRead(_adc_pin);
  if (_aux_pin != 0) digitalWrite(_aux_pin, LOW);

  return val;
}

void AnalogSensor::auxPin(uint8_t aux_pin) {
  _aux_pin = aux_pin;
  if (_aux_pin != 0) pinMode(_aux_pin, OUTPUT);
}
