//!  Sensor base clas, used by all types of external sensors
/*!
* Ansynchronous handling of multiple sensors via main loop ticks.
*/

#ifndef GenericSensor_h
#define GenericSensor_h

#include <Arduino.h>
#include "AveragingBuffer.h"

class GenericSensor
{
public:
    GenericSensor(const char*, uint8_t, unsigned long, unsigned long);
    ~GenericSensor();

    /**
     * Main loop call with current time stamp in milliseconds.
     * @param timestamp Current time in main loop.
     * @param sendRequested
     */
    void tick(unsigned long timestamp);

    /**
     * Perform sensor conversion, whatever that may entail.
     */
    virtual uint16_t readSensor() { return 0; };

    /**
     * Placeholder for analog sensor. Me stoopid.
     */
    virtual void auxPins(uint8_t aux_pin1=0, uint8_t aux_pin=0) {};

    /**
     * Add new value to the buffer.
     */
    void addValue(uint16_t val) { _buffer.addValue(val); };

    /**
     * Send the average of the buffer via Serial.
     */
    void send();

    /**
     * Calculate average of values in buffer.
     */
    float getAverage();

    /**
     * Return currently set scaling offset
     *
     * @return signed int offset to use for scaling the buffered average
     */
    float getOffset() { return _scale_offset; }

    /**
     * Return currently set scaling offset
     */
    void setOffset(float offset) { _scale_offset = offset; }

    /**
     * Return currently set scaling offset
     *
     * @return signed int offset to use for scaling the buffered average
     */
    float getScaleFactor() { return _scale_factor; }

    /**
     * Return currently set scaling offset
     */
    void setScaleFactor(float factor) { _scale_factor = factor; }

    /**
     * Return the name/type of the sensor
     *
     * @return name of the sensor
     */
    const char * getName() { return _name; }

protected:
    AveragingBuffer _buffer;    ///< value buffer, returns average when queried
    const char * _name;         ///< Name of this sensor/type (e.g. temp, for temperature)
    float _scale_factor;        ///< Scale factor to use when returning average
    float _scale_offset;          ///< Scale offset to use when returning average
    unsigned long _interval_sampling;///< Interval to trigger sensor reading
    unsigned long _interval_sending; ///< Interval to trigger average transmission
    unsigned long _next_sample; ///< Timestamp of next sample to take
    unsigned long _next_send;   ///< Timestamp of next average to transmit
};

#endif
