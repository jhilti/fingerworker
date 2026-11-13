#include "../Fingerworker/Logic.h"
#include <cassert>
#include <fstream>
#include <iostream>
int main() {
    fw::PowerPolicy policy;
    assert(policy.shouldRun(false)); assert(!policy.shouldRun(true));
    policy.userStandby=true;
    assert(!policy.shouldRun(false)); assert(!policy.shouldRun(true));
    policy.userStandby=false; assert(policy.shouldRun(false));
    fw::Peak peak;
    peak.reset(123);
    peak.update(100000,10000,true); peak.update(250000,10000,true);
    peak.update(120000,10000,true); // Short spike before next BLE frame must survive.
    peak.update(900000,0,false); // Endstop/fault must never enter peak.
    assert(peak.valid && peak.milliNewtons==240000 && peak.epoch==123);
    peak.begin(123); peak.begin(0); assert(peak.valid && peak.milliNewtons==240000);
    peak.begin(124); assert(!peak.valid && peak.epoch==124);
    peak.reset(456); assert(!peak.valid);
    peak.update(1000,2000,true); assert(peak.valid && peak.milliNewtons==-1000);
    peak.update(INT32_MAX,INT32_MIN,true); assert(peak.milliNewtons==-1000);
    // USB-only startup/attach clears a low battery immediately; detach must
    // classify a fresh battery reading before enabling the analog rails.
    assert(!fw::batteryLowForSource(true,0,true,3400,3550));
    assert(fw::batteryLowForSource(false,0,false,3400,3550));
    assert(fw::batteryLowForSource(false,3399,false,3400,3550));
    assert(!fw::batteryLowForSource(false,3400,false,3400,3550));
    assert(fw::batteryLowForSource(false,3400,true,3400,3550));
    assert(fw::batteryLowForSource(false,3549,true,3400,3550));
    assert(!fw::batteryLowForSource(false,3550,true,3400,3550));
    assert(!fw::batteryLowForSource(false,4000,false,3400,3550));
    assert(fw::sign24(0xffffff)==-1); assert(fw::sign24(0x800000)==-8388608); assert(fw::sign24(0x7fffff)==8388607);
    fw::Counter c;
    c.update(0,true,true,false); c.update(20,true,true,false); assert(c.total==0);
    c.update(30,false,true,false); c.update(40,false,true,false);
    c.update(50,true,true,false); c.update(59,true,true,false); assert(c.total==0);
    c.update(60,true,true,false); c.update(100,true,true,false); assert(c.total==1);
    c.update(110,false,true,false); c.update(115,true,true,false); c.update(130,true,true,false); assert(c.total==1);
    c.update(140,false,true,false); c.update(150,false,true,false); c.update(160,true,true,false); c.update(170,true,true,false); assert(c.total==2);
    c.update(180,false,true,false); c.update(190,false,true,false); c.update(200,true,false,false); c.update(220,true,true,false); assert(c.total==2);
    c.update(230,false,true,true); c.update(240,false,true,true); c.update(250,true,true,true); assert(c.total==2);
    c.invalidate(); c.update(UINT32_MAX-5,false,true,false); c.update(5,false,true,false); c.update(6,true,true,false); c.update(16,true,true,false); assert(c.total==3);
    c.total=UINT32_MAX; c.update(20,false,true,false); c.update(30,false,true,false); c.update(40,true,true,false); c.update(50,true,true,false); assert(c.total==0);
    fw::EndstopGate g; g.update(0,false,true); g.update(10,false,true); assert(!g.blocked);
    g.update(11,true,true); assert(g.blocked); g.update(12,false,true); g.update(21,false,true); assert(g.blocked); g.update(22,false,true); assert(!g.blocked);
    g.update(23,false,false); assert(g.blocked);
    fw::Calibration cal; int32_t force=0; assert(!cal.force(0,force));
    cal.count=3; cal.points[0]={-100,0}; cal.points[1]={100,100000}; cal.points[2]={300,300000};
    assert(cal.valid()); assert(cal.force(0,force) && force==50000); assert(cal.force(200,force) && force==200000);
    assert(!cal.force(301,force)); assert(!cal.force(-101,force));
    cal.points[1].raw=-100; assert(!cal.valid()); cal.points[1].raw=100;
    cal.points[0].milliNewtons=300000; cal.points[2].milliNewtons=0; assert(cal.valid()); assert(cal.force(200,force) && force==50000);
    uint8_t packet[34]; fw::packet(packet,1,42,1000,-123,125000,5000,3950,32,17,0x12345678);
    assert(packet[0]==2 && packet[26]==17 && packet[30]==0x78 && packet[33]==0x12);
    std::ofstream out("/tmp/fingerworker-v2-packet.bin",std::ios::binary); out.write((char*)packet,34);
    peak.reset(789); peak.update(250000,10000,true);
    uint8_t v3[43]; fw::packetV3(v3,0,43,1001,-124,120000,10000,3950,32,18,0x12345678,peak);
    std::ofstream out3("/tmp/fingerworker-v3-packet.bin",std::ios::binary); out3.write((char*)v3,43);
    std::cout<<"Firmware checks passed: USB-only power, detach battery check, battery hysteresis, ADC sign, debounce, boot-low, faults, isometry, timer/counter wrap, validity gate, calibration and v2 packet\n";
}
