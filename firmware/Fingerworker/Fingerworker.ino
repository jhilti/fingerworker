#include <Arduino.h>
#include <Adafruit_TinyUSB.h>
#include <bluefruit.h>
#include <InternalFileSystem.h>
#include <Adafruit_LittleFS.h>
#include <nrf_power.h>
#include <atomic>
#include "Logic.h"
#include "Config.h"
#include "ADS1220.h"
using Adafruit_LittleFS_Namespace::File;
using Adafruit_LittleFS_Namespace::FILE_O_READ;
using Adafruit_LittleFS_Namespace::FILE_O_WRITE;
// Nordic/Bluefruit UUID arrays are least-significant byte first.
const uint8_t SERVICE_UUID[16]={0x01,0xa0,0x70,0xf7,0x17,0x2c,0x36,0x9c,0x26,0x4a,0x4d,0x7b,0x01,0x00,0x7a,0xc3};
const uint8_t TELEMETRY_UUID[16]={0x01,0xa0,0x70,0xf7,0x17,0x2c,0x36,0x9c,0x26,0x4a,0x4d,0x7b,0x02,0x00,0x7a,0xc3};
BLEService service(SERVICE_UUID);
BLECharacteristic telemetry(TELEMETRY_UUID);
const uint8_t PEAK_RESET_UUID[16]={0x01,0xa0,0x70,0xf7,0x17,0x2c,0x36,0x9c,0x26,0x4a,0x4d,0x7b,0x03,0x00,0x7a,0xc3};
BLECharacteristic peakReset(PEAK_RESET_UUID);
std::atomic<uint32_t> requestedPeakEpoch{0};
fw::Peak devicePeak;
fw::PowerPolicy powerPolicy;
ADS1220 adc;
fw::Counter counter;
fw::EndstopGate gate;
fw::Calibration calibrations[2];
fw::Calibration staging;
uint8_t mode=0;
int32_t raw=0, forceMN=0, tareMN=0;
uint32_t bootID=0, sequence=0, lastADC=0, lastNotify=0, lastBattery=0, settleAt=0;
uint16_t batteryMV=0;
bool adcConfigured=false, haveSample=false, batteryLow=true, standby=false, sourceUSB=false;
uint8_t discarded=0;
char serialLine[96]; size_t lineLength=0; bool lineOverflow=false;
uint32_t buttonAt=0; bool buttonDown=false, longPressHandled=false;

bool usbPowerPresent() { return nrf_power_usbregstatus_vbusdet_get(NRF_POWER); }
void refreshBattery(bool resetHistory=false) {
    batteryMV=uint16_t(analogRead(PIN_VBAT)*3000.0f/4095.0f*BATTERY_DIVIDER_RATIO);
    batteryLow=fw::batteryLowForSource(sourceUSB,batteryMV,resetHistory?false:batteryLow,BATTERY_MIN_MV,BATTERY_RECOVER_MV);
}

uint32_t checksum(const uint8_t *p,size_t n) { uint32_t h=2166136261u; while(n--) h=(h^*p++)*16777619u; return h; }
bool loadCalibration(uint8_t which) {
    char path[12]; snprintf(path,sizeof(path),"/cal%u.bin",which);
    File file(InternalFS); if(!file.open(path,FILE_O_READ)) return false;
    uint32_t magic=0,crc=0; fw::Calibration cal;
    bool ok=file.read((uint8_t*)&magic,4)==4 && file.read((uint8_t*)&cal,sizeof(cal))==sizeof(cal) && file.read((uint8_t*)&crc,4)==4;
    file.close();
    if(!ok || magic!=0x46574331 || crc!=checksum((uint8_t*)&cal,sizeof(cal)) || !cal.valid()) return false;
    calibrations[which]=cal; return true;
}
bool saveCalibration() {
    if(!staging.valid() || !standby) return false;
    char path[12]; snprintf(path,sizeof(path),"/cal%u.bin",mode);
    // Fail closed on power loss: incomplete files fail length/checksum checks at next boot.
    InternalFS.remove(path); File file(InternalFS); if(!file.open(path,FILE_O_WRITE)) return false;
    uint32_t magic=0x46574331,crc=checksum((uint8_t*)&staging,sizeof(staging));
    bool ok=file.write((uint8_t*)&magic,4)==4 && file.write((uint8_t*)&staging,sizeof(staging))==sizeof(staging) && file.write((uint8_t*)&crc,4)==4;
    file.close(); return ok && loadCalibration(mode);
}
void powerOff() {
    adc.command(0x02); digitalWrite(D1,LOW); digitalWrite(D0,LOW);
    adcConfigured=false; haveSample=false; counter.invalidate(); gate=fw::EndstopGate(); standby=true;
}
void powerOn() {
    digitalWrite(D0,HIGH); delay(BOOST_SETTLE_MS); digitalWrite(D1,HIGH); delay(ANALOG_SETTLE_MS);
    settleAt=millis(); adcConfigured=adc.start(); lastADC=millis(); discarded=0; haveSample=false;
    counter.invalidate(); gate=fw::EndstopGate(); standby=false;
}
uint16_t status(uint32_t now) {
    uint16_t s=0;
    if(!HARDWARE_QUALIFIED || uint32_t(now-settleAt)<100) s|=fw::Rails;
    if(standby) s|=fw::Standby;
    if(!adcConfigured || !haveSample) s|=fw::NotReady;
    if(!standby && uint32_t(now-lastADC)>30) s|=fw::Timeout;
    if(raw==8388607 || raw==-8388608) s|=fw::Saturated;
    if(!calibrations[mode].force(raw,forceMN)) { s|=fw::CalibrationMissing; forceMN=0; }
    if(gate.blocked) s|=fw::Endstop;
    if(batteryLow) s|=fw::BatteryLow;
    return s;
}
void serialCommand(char *line) {
    long a,b;
    if(!strcmp(line,"raw")) { Serial.print("raw="); Serial.print(raw); Serial.print(" status="); Serial.print(status(millis())); Serial.print(" count="); Serial.println(counter.total); }
    else if(!strcmp(line,"cal clear")) { staging=fw::Calibration(); Serial.println("Staging cleared; existing calibration retained"); }
    else if(sscanf(line,"cal %ld %ld",&a,&b)==2 && staging.count<8 && a>=-8388608 && a<=8388607 && b>=0 && b<=INT32_MAX) {
        staging.points[staging.count++]={int32_t(a),int32_t(b)}; Serial.println("Point staged (raw, millinewtons); ascending raw and monotonic force required");
    }
    else if(!strcmp(line,"cal save")) Serial.println(saveCalibration()?"Calibration saved":"Rejected: enter standby; need 2-8 monotonic points and working flash");
    else if(!strcmp(line,"tare")) {
        if(status(millis())==0) { tareMN=forceMN; Serial.println("Display tare applied; absolute force unchanged"); }
        else Serial.println("Tare rejected: measurement invalid");
    }
    else if(!strcmp(line,"mode 0") || !strcmp(line,"mode 1")) { mode=line[5]-'0'; staging=fw::Calibration(); tareMN=0; counter.invalidate(); Serial.println("Mode selected; mode-specific calibration required"); }
    else if(!strcmp(line,"standby")) { powerPolicy.userStandby=true; powerOff(); Serial.println("Standby: analog power off; BLE/USB remain active"); }
    else if(!strcmp(line,"wake")) { powerPolicy.userStandby=false; if(!batteryLow) { if(!standby) powerOff(); powerOn(); } else Serial.println("Wake rejected: battery low/unknown"); }
    else Serial.println("Commands: raw, cal clear, cal <raw> <mN>, standby, cal save, wake, tare, mode 0, mode 1");
}
void connected(uint16_t handle) { Bluefruit.Connection(handle)->requestMtuExchange(64); }
void resetPeakWritten(uint16_t, BLECharacteristic*, uint8_t *data, uint16_t length) {
    if(length!=4) return;
    const uint32_t token=uint32_t(data[0])|uint32_t(data[1])<<8|uint32_t(data[2])<<16|uint32_t(data[3])<<24;
    if(token) requestedPeakEpoch.store(token);
}
void setup() {
    pinMode(PIN_CHARGING_CURRENT,INPUT); // P0.13 no pull: nominal 50mA charge current.
    digitalWrite(VBAT_ENABLE,LOW); pinMode(VBAT_ENABLE,OUTPUT); // P0.14 must never be driven HIGH.
    digitalWrite(D0,LOW); pinMode(D0,OUTPUT); digitalWrite(D1,LOW); pinMode(D1,OUTPUT);
    digitalWrite(D2,HIGH); pinMode(D2,OUTPUT);
    pinMode(D3,INPUT_PULLUP); pinMode(D4,INPUT_PULLUP); pinMode(D5,INPUT); pinMode(D6,INPUT);
    Serial.begin(115200); SPI.begin(); analogReadResolution(12); analogReference(AR_INTERNAL_3_0);
    InternalFS.begin(); loadCalibration(0); loadCalibration(1);
    Bluefruit.configPrphBandwidth(BANDWIDTH_HIGH); Bluefruit.begin(); Bluefruit.autoConnLed(false);
    bool nonceReady=false;
    for(uint8_t attempt=0;attempt<100;attempt++) {
        if(sd_rand_application_vector_get((uint8_t*)&bootID, sizeof(bootID))==NRF_SUCCESS) { nonceReady=true; break; }
        delay(1);
    }
    if(!nonceReady) { Serial.println("Boot nonce RNG failed; advertising disabled"); while(true) delay(1000); }
    Bluefruit.setName("Fingerworker"); Bluefruit.Periph.setConnectCallback(connected);
    service.begin(); telemetry.setProperties(CHR_PROPS_READ|CHR_PROPS_NOTIFY);
    telemetry.setPermission(SECMODE_OPEN,SECMODE_NO_ACCESS); telemetry.setFixedLen(43); telemetry.begin();
    peakReset.setProperties(CHR_PROPS_WRITE); peakReset.setPermission(SECMODE_NO_ACCESS,SECMODE_OPEN);
    peakReset.setFixedLen(4); peakReset.setWriteCallback(resetPeakWritten); peakReset.begin();
    Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
    Bluefruit.Advertising.addService(service); Bluefruit.ScanResponse.addName();
    Bluefruit.Advertising.restartOnDisconnect(true); Bluefruit.Advertising.setInterval(32,244); Bluefruit.Advertising.start(0);
    // The nRF52840 VBUS detector also works before USB enumeration. The Rev A
    // D6 divider does not guarantee a logic HIGH over the USB voltage range.
    sourceUSB=usbPowerPresent();
    refreshBattery(true);
    powerPolicy.userStandby=BENCH_START;
    if(powerPolicy.shouldRun(batteryLow)) powerOn(); else standby=true;
}
void loop() {
    uint32_t now=millis();
    const bool usb=usbPowerPresent();
    if(usb!=sourceUSB) {
        sourceUSB=usb; powerOff(); refreshBattery(true); lastBattery=millis();
        if(powerPolicy.shouldRun(batteryLow)) powerOn();
        now=millis();
    }
    if(uint32_t(now-lastBattery)>=1000) {
        lastBattery=now; refreshBattery();
        if(batteryLow && !standby) powerOff();
        else if(standby && powerPolicy.shouldRun(batteryLow)) powerOn();
    }
    now=millis(); // Power transitions above can block; never compare an old time to a new settleAt.
    const uint32_t peakToken=requestedPeakEpoch.exchange(0);
    devicePeak.begin(peakToken);
    bool freshSample=false;
    if(!standby && adcConfigured && adc.read(raw)) { lastADC=now; if(discarded<8) ++discarded; else { haveSample=true; freshSample=true; } }
    const bool qualified=HARDWARE_QUALIFIED && !standby && uint32_t(now-settleAt)>=100;
    const bool active=digitalRead(D5)==LOW;
    gate.update(now,active,qualified);
    const uint16_t s=status(now);
    if(freshSample) devicePeak.update(forceMN,tareMN,s==0);
    counter.update(now,active,qualified && !(s&(fw::NotReady|fw::Timeout|fw::Saturated|fw::BatteryLow)),mode==1);
    if(uint32_t(now-lastNotify)>=40) {
        lastNotify=now;
        // Never resend a stale ADC sample as a fresh sample: error packets carry current status.
        uint8_t packet[43]; fw::packetV3(packet,mode,sequence++,lastADC,raw,forceMN,tareMN,batteryMV,s,counter.total,bootID,devicePeak);
        telemetry.write(packet,sizeof(packet));
        if(Bluefruit.connected() && telemetry.notifyEnabled()) {
            auto *connection=Bluefruit.Connection(Bluefruit.connHandle());
            if(connection && connection->getMtu()>=46) telemetry.notify(packet,sizeof(packet));
        }
    }
    const bool pressed=digitalRead(D4)==LOW;
    if(pressed && !buttonDown) { buttonAt=now; buttonDown=true; longPressHandled=false; }
    if(pressed && buttonDown && !longPressHandled && uint32_t(now-buttonAt)>=1500) {
        powerPolicy.userStandby=!powerPolicy.userStandby;
        if(powerPolicy.shouldRun(batteryLow)) { if(standby) powerOn(); } else powerOff(); longPressHandled=true;
    }
    if(!pressed && buttonDown) {
        if(!longPressHandled && uint32_t(now-buttonAt)>=30 && s==0) tareMN=forceMN;
        buttonDown=false;
    }
    // Bound parser work so a continuous host stream cannot monopolize acquisition.
    uint8_t serialBudget=16;
    while(serialBudget-- && Serial.available()) {
        char c=Serial.read();
        if(c=='\n') { serialLine[lineLength]=0; if(!lineOverflow) serialCommand(serialLine); else Serial.println("Command too long"); lineLength=0; lineOverflow=false; }
        else if(c!='\r') { if(!lineOverflow && lineLength<sizeof(serialLine)-1) serialLine[lineLength++]=c; else lineOverflow=true; }
    }
    delay(1);
}
