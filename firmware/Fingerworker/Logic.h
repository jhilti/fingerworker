#pragma once
#include <stdint.h>
#include <stddef.h>
#include <limits.h>
namespace fw {
struct PowerPolicy {
    bool userStandby=false;
    bool shouldRun(bool batteryLow) const { return !userStandby && !batteryLow; }
};
// Cumulative display-force maximum over every valid acquired sample, not BLE frames.
struct Peak {
    uint32_t epoch=0; int32_t milliNewtons=0; bool valid=false;
    void reset(uint32_t token) { epoch=token; milliNewtons=0; valid=false; }
    void begin(uint32_t token) { if(token && token!=epoch) reset(token); }
    void update(int32_t force, int32_t tare, bool measurementValid) {
        if(!measurementValid) return;
        const int64_t display=int64_t(force)-tare;
        if(display<INT32_MIN || display>INT32_MAX) return;
        if(!valid || display>milliNewtons) milliNewtons=int32_t(display);
        valid=true;
    }
};
inline bool batteryLowForSource(bool usb, uint16_t mv, bool wasLow, uint16_t minimum, uint16_t recovery) {
    if (usb) return false;
    if (mv<minimum) return true;
    if (mv>=recovery) return false;
    return wasLow;
}
enum Status : uint16_t { Rails=1, NotReady=2, Timeout=4, Saturated=8, CalibrationMissing=16, Endstop=32, BatteryLow=64, Standby=128 };
inline int32_t sign24(uint32_t x) { return (x & 0x800000) ? int32_t(x | 0xff000000) : int32_t(x & 0xffffff); }
struct Counter {
    uint32_t total=0, changed=0; bool initialized=false, low=false, armed=false, counted=false;
    void invalidate() { initialized=false; armed=false; counted=false; }
    void update(uint32_t now, bool active, bool qualified, bool isometric) {
        if (!qualified || isometric) { invalidate(); return; }
        if (!initialized) { initialized=true; low=active; changed=now; armed=false; counted=false; }
        if (low != active) { low=active; changed=now; counted=false; }
        if (!active && uint32_t(now-changed)>=10) armed=true;
        if (active && uint32_t(now-changed)>=10 && !counted) {
            if (armed) ++total;
            armed=false; counted=true;
        }
    }
};
struct EndstopGate {
    bool blocked=true, highSeen=false; uint32_t highAt=0;
    void update(uint32_t now, bool low, bool qualified) {
        if (!qualified || low) { blocked=true; highSeen=false; return; }
        if (!highSeen) { highSeen=true; highAt=now; }
        if (uint32_t(now-highAt)>=10) blocked=false;
    }
};
struct Point { int32_t raw, milliNewtons; };
struct Calibration {
    uint32_t count=0; Point points[8]{};
    bool valid() const {
        if (count<2 || count>8) return false;
        for (uint32_t i=0;i<count;i++) {
            if (points[i].raw < -8388608 || points[i].raw > 8388607 || points[i].milliNewtons<0) return false;
            if (i && points[i].raw<=points[i-1].raw) return false;
            if (i && points[i].milliNewtons==points[i-1].milliNewtons) return false;
            if (i>1 && ((points[i].milliNewtons>points[i-1].milliNewtons)!=(points[1].milliNewtons>points[0].milliNewtons))) return false;
        }
        return true;
    }
    bool force(int32_t raw, int32_t &out) const {
        if (!valid() || raw<points[0].raw || raw>points[count-1].raw) return false;
        uint32_t i=1; while(i<count-1 && raw>points[i].raw) ++i;
        const auto &a=points[i-1], &b=points[i];
        int64_t value=int64_t(a.milliNewtons)+(int64_t(raw)-a.raw)*(int64_t(b.milliNewtons)-a.milliNewtons)/(int64_t(b.raw)-a.raw);
        if (value<INT32_MIN || value>INT32_MAX) return false;
        out=int32_t(value); return true;
    }
};
inline void put16(uint8_t *p,uint16_t v) { p[0]=v; p[1]=v>>8; }
inline void put32(uint8_t *p,uint32_t v) { for(int i=0;i<4;i++) p[i]=v>>(8*i); }
inline void packet(uint8_t *p,uint8_t mode,uint32_t sequence,uint32_t ms,int32_t raw,int32_t force,int32_t tare,uint16_t battery,uint16_t status,uint32_t count,uint32_t bootID) {
    p[0]=2; p[1]=mode; put32(p+2,sequence); put32(p+6,ms); put32(p+10,uint32_t(raw));
    put32(p+14,uint32_t(force)); put32(p+18,uint32_t(tare)); put16(p+22,battery); put16(p+24,status); put32(p+26,count); put32(p+30,bootID);
}
inline void packetV3(uint8_t *p,uint8_t mode,uint32_t sequence,uint32_t ms,int32_t raw,int32_t force,int32_t tare,uint16_t battery,uint16_t status,uint32_t count,uint32_t bootID,const Peak &peak) {
    packet(p,mode,sequence,ms,raw,force,tare,battery,status,count,bootID);
    p[0]=3; put32(p+34,uint32_t(peak.milliNewtons)); put32(p+38,peak.epoch); p[42]=peak.valid?1:0;
}
}
