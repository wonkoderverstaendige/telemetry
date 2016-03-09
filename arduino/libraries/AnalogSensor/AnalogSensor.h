#ifndef AnalogSensor_h
#define AnalogSensor_h

#include "Arduino.h"

class AnalogSensor
{
public:
    //AnalogSensor(void);
    AnalogSensor(const char*, int, int, byte, float);
    AnalogSensor(const char*, int, int, byte, byte, float);
    
    ~AnalogSensor();
    
    void clear();
    void tick(unsigned long, bool);
    void send();
    void addValue(uint16_t);
    
    float getAverage();
    
    uint16_t getElement(uint8_t idx);
    uint8_t getSize() { return _size; }
    uint8_t getCount() { return _cnt; }
    const char * getType() { return _type; }
    
protected:
    const char * _type;
    uint8_t _size;
    float _scale_factor;
    byte _a_pin;
    byte _d_pin;
    int _interval;
    unsigned long _last_ts;
    uint16_t * _ar;

    uint8_t _cnt;
    uint8_t _idx;
    float _sum;
};

#endif
