//
// Created by reichler on 09/03/16.
//

#include "AveragingBuffer.h"

AveragingBuffer::AveragingBuffer() {
    _size = 0;
    _ar = NULL;
}

AveragingBuffer::~AveragingBuffer() {
    if (_ar != NULL) free(_ar);
}

void AveragingBuffer::setSize(uint16_t bufsize) {
    _size = bufsize;
    _ar = (uint16_t *) malloc(_size * sizeof(uint16_t));
    if (_ar == NULL) _size = 0;
    clear();
}

void AveragingBuffer::clear() {
    _cnt = 0;
    _idx = 0;
    _sum = 0.0;
    for (int i=0; i<_size; i++) _ar[i] = 0;
}

void AveragingBuffer::addValue(uint16_t val)
{
    if (_ar == NULL) return;
    _sum -= _ar[_idx];
    _ar[_idx] = val;
    _sum += _ar[_idx];
    _idx++;
    if (_idx == _size) _idx = 0;
    if (_cnt < _size) _cnt++;
}

float AveragingBuffer::getAverage() {
    if (_cnt == 0) return NAN;
    return _sum / _cnt;
}

uint16_t AveragingBuffer::getElement(uint8_t idx)
{
    if (idx >= _cnt) return NAN;
    return _ar[idx];
}
