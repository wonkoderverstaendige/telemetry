#include "OneWireSensor.h"

OneWireSensor::OneWireSensor(const char* name,
                             OneWire* wire,
                             uint8_t bufsize,
                             uint32_t sample_interval,
                             uint32_t send_interval) :
               GenericSensor(name, bufsize, sample_interval, send_interval)
{
  _wire = wire;

  // start looking for our device, store its address
  wire->search(_addr);
  // OneWire::printAddr();

  if (OneWire::crc8(_addr, 7) != _addr[7]) {
    //Serial.println("CRC not valid!");
  }
}

OneWireSensor::~OneWireSensor() {}

uint16_t OneWireSensor::readSensor()
{
  // stuff happens
  _wire->reset();
  _wire->select(_addr);
  _wire->write(0x44);
  _wire->reset();
  _wire->select(_addr);
  _wire->write(0xBE);

  for (uint8_t i = 0; i < 9; i++) {
    _data[i] = _wire->read();
  }
  int16_t raw = (_data[1] << 8) | _data[0];
  return raw;
}

void OneWireSensor::printCRC()
{
  Serial.print("\n CRC: ");
  Serial.println(OneWire::crc8(_data, 8), HEX);
}

void OneWireSensor::printAddr()
{
  for (uint8_t i=0; i< 8; i++) {
    Serial.print(_addr[i], HEX);
    Serial.print(" ");
  }
}
