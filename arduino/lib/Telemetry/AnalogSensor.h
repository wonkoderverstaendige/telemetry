//!  AnalogSensor class.
/*!
* Analog sensors read directly from the built-in ADC.
* Some sensors may require switching an auxiliary pin HIGH/LOW,
* for example the soil moisture sensor. Said sensor however shouldn't
* remain HIGH when not in use to reduce corrosion of the electrodes.
* Hence the additional logic to toggle pins as needed.
*/

#ifndef AnalogSensor_h
#define AnalogSensor_h

#include <Arduino.h>
#include "GenericSensor.h"

class AnalogSensor: public GenericSensor
{
public:
    AnalogSensor(const char*, uint8_t, unsigned long, unsigned long,
                 uint8_t a_pin, uint8_t d_pin);

    ~AnalogSensor();

    uint16_t readSensor();

protected:
    uint8_t _a_pin;    ///< Analog pin to read from
    uint8_t _d_pin;    ///< Digital pin for sensors requiring additional actions
};

#endif
