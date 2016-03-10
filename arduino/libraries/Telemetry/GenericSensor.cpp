#include "GenericSensor.h"

GenericSensor::GenericSensor(const char* name, uint8_t bufsize, uint8_t interval, float scale)
{
    _name = name;
    _scale_factor = scale;
    _interval = interval;
    _last_ts = 0;
    _buffer = AveragingBuffer();
    _buffer.setSize(bufsize);
}

GenericSensor::~GenericSensor() {};

void GenericSensor::tick(unsigned long timestamp, bool sendRequested)
{
    // TODO: Take care of overflow for millis every 50 days or so
    if (timestamp-_last_ts >= _interval) {
        uint16_t val = readSensor();
        addValue(val);
        _last_ts = timestamp;
    }

    if (sendRequested) send();
}

void GenericSensor::addValue(uint16_t val)
{
    _buffer.addValue(val);
}

float GenericSensor::getAverage()
{
    return _buffer.getAverage() * _scale_factor;
}

void GenericSensor::send()
{
    Serial.print(_name);
    Serial.print(':');
    Serial.println(getAverage());
}
