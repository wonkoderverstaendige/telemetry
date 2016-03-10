#include "AnalogSensor.h"

AnalogSensor::AnalogSensor(const char* name,
                           uint8_t bufsize,
                           uint32_t interval,
                           uint8_t a_pin,
                           uint8_t d_pin,
                           float scale) :
              GenericSensor(name, bufsize, interval, scale)
{
    _a_pin = a_pin;
    _d_pin = d_pin;
    if (_d_pin != 0) pinMode(_d_pin, OUTPUT);
}

AnalogSensor::~AnalogSensor() { }

uint16_t AnalogSensor::readSensor()
{
    if (_d_pin != 0) digitalWrite(_d_pin, HIGH);
    uint16_t val = analogRead(_a_pin);
    if (_d_pin != 0) digitalWrite(_d_pin, LOW);

    return val;
}
