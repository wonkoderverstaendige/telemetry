//!  OneWireSensor class.
/*!
* Sensors communicating via the Maxim OneWire bus. Will most likely only be
* used for the DS18b20 temperature sensor. There aren't very many other useful
* devices for the OneWire bus out there, it seems. Or I don't grok that platform
* at all.
*/

#ifndef OneWireSensor_h
#define OneWireSensor_h

#include "Arduino.h"
#include "OneWire.h"
#include "GenericSensor.h"

class OneWireSensor: public GenericSensor
{
public:
  OneWireSensor(const char* name, OneWire* wire, uint8_t bufsize,
                uint32_t interval, float scale);

  ~OneWireSensor();

  uint16_t readSensor();
  void printCRC();

protected:
  OneWire* _wire;    ///< The actual OneWire bus to talk over
  uint8_t _addr[8];   ///< Device ROM (unique 64bit field/address)
  uint8_t _data[12];  ///< returned scratchpad data
};

#endif
