#pragma once
#include <Arduino.h>
#include <SPI.h>
#include "Logic.h"
class ADS1220 {
    void select() { SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1)); digitalWrite(D2,LOW); }
    void release() { digitalWrite(D2,HIGH); SPI.endTransaction(); }
public:
    void command(uint8_t cmd) { select(); SPI.transfer(cmd); release(); }
    bool start() {
        command(0x06); delay(1);
        const uint8_t config[4]={0x06,0x84,0x40,0x00};
        select(); SPI.transfer(0x43); for(auto v:config) SPI.transfer(v); release();
        select(); SPI.transfer(0x23); bool match=true;
        for(auto v:config) { if(SPI.transfer(0xff)!=v) match=false; } release();
        if(match) command(0x08);
        return match;
    }
    bool read(int32_t &raw) {
        if(digitalRead(D3)!=LOW) return false;
        select(); SPI.transfer(0x10); uint32_t value=0;
        for(int i=0;i<3;i++) value=(value<<8)|SPI.transfer(0xff);
        release(); raw=fw::sign24(value); return true;
    }
};
