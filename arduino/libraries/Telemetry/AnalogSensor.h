//!  AnalogSensor class.
/*!
* Ansynchronous handling of multiple analog sensors.
*/

#ifndef AnalogSensor_h
#define AnalogSensor_h

#include "Arduino.h"
#include "GenericSensor.h"

class AnalogSensor: public GenericSensor
{
public:
    AnalogSensor(const char* type, uint8_t bufsize, uint8_t interval,
        uint8_t a_pin, uint8_t d_pin, float scale);

    ~AnalogSensor();

    uint16_t readSensor();

protected:
    uint8_t _a_pin;    ///< Analog pin to read from
    uint8_t _d_pin;    ///< Digital pin for sensors requiring additional actions
};

#endif
