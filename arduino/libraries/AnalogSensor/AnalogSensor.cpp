#include "AnalogSensor.h"
#include <stdlib.h>
#include <string.h>

AnalogSensor::AnalogSensor(const char* type, int n, int interval, byte a_pin, byte d_pin, float scale)
{
    _type = type;
    _size = n;
    _scale_factor = scale;
    _a_pin = a_pin;
    _d_pin = d_pin;
    pinMode(_d_pin, OUTPUT);
    _interval = interval;
    _last_ts = 0;
    _ar = (uint16_t *) malloc(_size * sizeof(uint16_t));
    if (_ar == NULL) _size = 0;
    clear();
}

AnalogSensor::AnalogSensor(const char* type, int n, int interval, byte a_pin, float scale)
{
    _type = type;
    _size = n;
    _scale_factor = scale;
    _a_pin = a_pin;
    _d_pin = 0;
    _interval = interval;
    _last_ts = 0;
    _ar = (uint16_t *) malloc(_size * sizeof(uint16_t));
    if (_ar == NULL) _size = 0;
    clear();
}

AnalogSensor::~AnalogSensor()
{
    if (_ar != NULL) free(_ar);
}

void AnalogSensor::clear()
{
    _cnt = 0;
    _idx = 0;
    _sum = 0.0;
    for (int i=0; i<_size; i++) _ar[i] = 0.0;
}

void AnalogSensor::tick(unsigned long timestamp, bool sendRequested)
{
    // TODO: Take care of overflow for millis every 50 days or so
    if (timestamp-_last_ts >= _interval) {
        _last_ts = timestamp;
        if (_d_pin != 0) {
            digitalWrite(_d_pin, HIGH);
            addValue(analogRead(_a_pin));
            digitalWrite(_d_pin, LOW);
        } else {
            addValue(analogRead(_a_pin));
        }
    }
    
    if (sendRequested) send();
}

void AnalogSensor::addValue(uint16_t val)
{
    if (_ar == NULL) return;
    _sum -= _ar[_idx];
    _ar[_idx] = val;
    _sum += _ar[_idx];
    _idx++;
    if (_idx == _size) _idx = 0;
    if (_cnt < _size) _cnt++;
}

float AnalogSensor::getAverage()
{
    if (_cnt == 0) return NAN;
    return _sum / _cnt * _scale_factor;
}

uint16_t AnalogSensor::getElement(uint8_t idx)
{
    if (idx >= _cnt) return NAN;
    return _ar[idx];
}

void AnalogSensor::send()
{
    Serial.print(_type);
    Serial.print(':');
    Serial.println(getAverage());
}