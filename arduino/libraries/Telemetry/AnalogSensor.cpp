#include "AnalogSensor.h"
#include <stdlib.h>
#include <string.h>

AnalogSensor::AnalogSensor(const char* type, uint8_t bufsize, uint8_t interval, uint8_t a_pin, uint8_t d_pin, float scale)
{
    _type = type;

    _scale_factor = scale;
    _a_pin = a_pin;
    _d_pin = d_pin;
    pinMode(_d_pin, OUTPUT);
    _interval = interval;
    _last_ts = 0;

    _buffer = AveragingBuffer();
    _buffer.setSize(bufsize);
}

AnalogSensor::~AnalogSensor() { }

void AnalogSensor::tick(unsigned long timestamp, bool sendRequested)
{
    // TODO: Take care of overflow for millis every 50 days or so
    if (timestamp-_last_ts >= _interval) {
        _last_ts = timestamp;
        if (_d_pin != 0) digitalWrite(_d_pin, HIGH);
        uint16_t val = analogRead(_a_pin);
        addValue(val);
        if (_d_pin != 0) digitalWrite(_d_pin, LOW);
    }

    if (sendRequested) send();
}

void AnalogSensor::addValue(uint16_t val)
{
    _buffer.addValue(val);
}

float AnalogSensor::getAverage()
{
    return _buffer.getAverage(); //* _scale_factor;
}

void AnalogSensor::send()
{
    Serial.print(_type);
    Serial.print(':');
    Serial.println(getAverage());
}
