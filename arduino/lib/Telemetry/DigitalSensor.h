//!  DigitalSensor class.
/*!
* Digital sensor reads binary state of digital input pin. Can also be used
* to register a pin state change via interrupt. Simply set both sample and send
* intervals to zero and call tick() from within the ISR with any non-zero value.
*/

#ifndef DigitalSensor_h
#define DigitalSensor_h

#include <Arduino.h>
#include "GenericSensor.h"

class DigitalSensor: public GenericSensor
{
public:
    DigitalSensor(const char*, uint8_t, uint8_t, unsigned long, unsigned long);

    ~DigitalSensor();

    uint16_t readSensor();

    /**
     * Add an auxiliary pin. This pin is toggled before/after reading state.
     */
    void auxPin(uint8_t);

protected:
    uint8_t _aux_pin;    ///< Auxiliary pin, e.g. toggling external actuators
    uint8_t _dig_pin;    ///< Digital pin to read
};

#endif
