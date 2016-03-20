#include "AnalogSensor.h"

AnalogSensor::AnalogSensor(const char* name,
                           uint8_t bufsize,
                           unsigned long sample_interval,
                           unsigned long send_interval,
                           uint8_t a_pin,
                           uint8_t d_pin) :
              GenericSensor(name, bufsize, sample_interval, send_interval)
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
