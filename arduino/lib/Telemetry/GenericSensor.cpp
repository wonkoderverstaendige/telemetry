#include "GenericSensor.h"

GenericSensor::GenericSensor(const char* name,
                             uint8_t bufsize,
                             unsigned long sample_interval,
                             unsigned long send_interval)
{
    _name = name;
    _interval_sampling = sample_interval;
    _interval_sending = send_interval;

    _scale_factor = 1.0;
    _scale_offset = 0;

    _next_sample = 0;
    _next_send = 0;

    _buffer = AveragingBuffer();
    _buffer.setSize(bufsize);
}

GenericSensor::~GenericSensor() {};

void GenericSensor::tick(unsigned long timestamp)
{
  // TODO: Take care of overflow for millis every 50 days or so
  if (timestamp >= _interval_sampling) {
    addValue(readSensor());
    _next_sample = timestamp + _interval_sampling;
  }

  if (timestamp >= _next_send) {
    if (timestamp > 0) send();
    _next_send = timestamp + _interval_sending;
  }
}

void GenericSensor::send()
{
    Serial.print(_name);
    Serial.print(':');
    Serial.println(getAverage());
}
