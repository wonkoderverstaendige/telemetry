//!  AveragingBuffer
/*!
* Holds data and return average over buffered data on request.
*/

#ifndef ARDUINO_AVERAGINGBUFFER_H
#define ARDUINO_AVERAGINGBUFFER_H

#include <Arduino.h>

class AveragingBuffer
{
public:
    AveragingBuffer();

    ~AveragingBuffer();

    void addValue(uint16_t);
    float getAverage();
    uint16_t getElement(uint8_t idx);

    void setSize(uint16_t);
    uint8_t getSize() { return _size; }
    uint8_t getCount() { return _cnt; }

    void clear();

private:
    uint8_t _size;
    uint16_t * _ar;
    uint8_t _cnt;
    uint8_t _idx;
    float _sum;
};
#endif //ARDUINO_AVERAGINGBUFFER_H
