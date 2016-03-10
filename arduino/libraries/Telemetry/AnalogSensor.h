//!  AnalogSensor class.
/*!
* Ansynchronous handling of multiple analog sensors.
*/

#ifndef AnalogSensor_h
#define AnalogSensor_h

#include "Arduino.h"
#include "AveragingBuffer.h"

class AnalogSensor
{
public:
    AnalogSensor(const char* type, uint8_t bufsize, uint8_t interval, uint8_t a_pin, uint8_t d_pin, float scale);

    ~AnalogSensor();

    /**
     * Main loop call with current time stamp in milliseconds.
     * @param timestamp Current time in main loop.
     * @param sendRequested
     */
    void tick(unsigned long timestamp, bool sendRequested);

    /**
     * Send the average of the buffer via Serial.
     */
    void send();

    /**
     * Add new value to the buffer.
     */
    void addValue(uint16_t);

    /**
     * Calculate average of values in buffer.
     */
    float getAverage();

    /**
     * Return the name/type of the sensor (I should have chosen a better name for this...)
     *
     * @return name of the sensor
     */
    const char * getType() { return _type; }

protected:
    AveragingBuffer _buffer;    ///< Buffer holding the values, return average when queried
    const char * _type;         ///< Name of this sensor/type (e.g. temp, for temperature)
    float _scale_factor;        ///< Scale factor to use when reading
    uint8_t _a_pin;             ///< Analog pin to read from
    uint8_t _d_pin;             ///< Digital pin for sensors requiring additional actions
    uint8_t _interval;              ///< Interval to trigger sensor reading
    unsigned long _last_ts;     ///< Last timestamp
};

#endif
