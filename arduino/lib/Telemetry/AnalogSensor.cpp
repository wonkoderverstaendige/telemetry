#include "AnalogSensor.h"

AnalogSensor::AnalogSensor(const char* name,
                           uint8_t adc_pin,
                           uint8_t bufsize,
                           unsigned long sample_interval,
                           unsigned long send_interval,
                           uint8_t aux_pin1,
                           uint8_t aux_pin2) :
              GenericSensor(name, bufsize, sample_interval, send_interval)
{
  _aux_pin1 = aux_pin1;
  _aux_pin2 = aux_pin2;
  if (_aux_pin1 != 0) pinMode(_aux_pin1, OUTPUT);
  if (_aux_pin2 != 0) pinMode(_aux_pin2, OUTPUT);
  _adc_pin = adc_pin;
  pinMode(_adc_pin, INPUT);
}

AnalogSensor::~AnalogSensor() { }

uint16_t AnalogSensor::readSensor()
{
  // no aux pins set, simple ADC conversion
  if (!(_aux_pin1 || _aux_pin2)) return analogRead(_adc_pin);

  // at least one pin set, so toggle aux_pin before conversion
  if ((_aux_pin1 || _aux_pin2) && !(_aux_pin1 && _aux_pin2)) {
    uint8_t pin = _aux_pin1 > _aux_pin2 ? _aux_pin1 : _aux_pin2;
    digitalWrite(pin, HIGH);
    // let settle a teensy moment
    delay(20);
    uint16_t val = analogRead(_adc_pin);
    digitalWrite(pin, LOW);
    return val;
  }

  if (_aux_pin1 && _aux_pin2) {
    // round 1
    digitalWrite(_aux_pin1, HIGH);
    digitalWrite(_aux_pin2, LOW);
    delay(100);  // let settle a teensy moment
    uint16_t v1 = 1023 - analogRead(_adc_pin);
    digitalWrite(_aux_pin1, LOW);
    digitalWrite(_aux_pin2, LOW);
    delay(100);

    // round 2, the other way round
    digitalWrite(_aux_pin1, LOW);
    digitalWrite(_aux_pin2, HIGH);
    delay(100);  // let settle a teensy moment
    uint16_t v2 = analogRead(_adc_pin);
    digitalWrite(_aux_pin1, LOW);
    digitalWrite(_aux_pin2, LOW);
    return (v1+v2)/2;
  }
}

void AnalogSensor::auxPins(uint8_t aux_pin1, uint8_t aux_pin2=0) {
  _aux_pin1 = aux_pin1;
  _aux_pin2 = aux_pin2;
  if (_aux_pin1 != 0) pinMode(_aux_pin1, OUTPUT);
  if (_aux_pin2 != 0) pinMode(_aux_pin2, OUTPUT);
}
