//!  Sensor base clas, used by all types of external sensors
/*!
* Ansynchronous handling of multiple sensors via main loop ticks.
*/

#ifndef GenericSensor_h
#define GenericSensor_h

#include "Arduino.h"
#include "AveragingBuffer.h"

class GenericSensor
{
public:
    GenericSensor(const char* name, uint8_t bufsize, uint32_t interval, float scale);
    ~GenericSensor();

    /**
     * Main loop call with current time stamp in milliseconds.
     * @param timestamp Current time in main loop.
     * @param sendRequested
     */
    void tick(unsigned long timestamp, bool sendRequested);

    /**
     * Perform sensor conversion, whatever that may entail.
     */
    virtual uint16_t readSensor() { return 0; };

    /**
     * Add new value to the buffer.
     */
    void addValue(uint16_t);

    /**
     * Send the average of the buffer via Serial.
     */
    void send();

    /**
     * Calculate average of values in buffer.
     */
    float getAverage();

    /**
     * Return the name/type of the sensor
     *
     * @return name of the sensor
     */
    const char * getName() { return _name; }

protected:
    AveragingBuffer _buffer;    ///< value buffer, returns average when queried
    const char * _name;         ///< Name of this sensor/type (e.g. temp, for temperature)
    float _scale_factor;        ///< Scale factor to use when reading
    uint32_t _interval;         ///< Interval to trigger sensor reading
    unsigned long _last_ts;     ///< Last timestamp
};

#endif
