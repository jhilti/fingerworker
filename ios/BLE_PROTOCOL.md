# Fingerworker BLE protocol

Development interface, 11 October 2026. Firmware and app implement v3; physical interoperability remains to be tested. Service `C37A0001-7B4D-4A26-9C36-2C17F770A001`, advertised name Fingerworker. Telemetry `C37A0002-7B4D-4A26-9C36-2C17F770A001` is read + notify.

## Version 3 telemetry

Exactly 43 bytes, multibyte integers little endian. ATT MTU must be at least 46; firmware requests 64 and only notifies when the MTU is sufficient.

| Offset | Type | Meaning |
| --- | --- | --- |
| 0 | uint8 | Version 3 |
| 1 | uint8 | Mode: 0 dynamic / 1 isometric |
| 2 | uint32 | Publication sequence, wrapping |
| 6 | uint32 | Milliseconds of latest acquired ADC sample, wrapping |
| 10 | int32 | Sign-extended 24-bit raw ADC value |
| 14 | int32 | Absolute calibrated force, mN |
| 18 | int32 | User display tare, mN |
| 22 | uint16 | Battery, mV |
| 24 | uint16 | Current measurement status |
| 26 | uint32 | Repetition total since boot, wrapping |
| 30 | uint32 | Random boot identifier |
| 34 | int32 | Cumulative maximum of valid display force (absolute minus tare), mN |
| 38 | uint32 | Peak epoch token acknowledged by firmware |
| 42 | uint8 | Peak valid: 0 no valid sample in epoch / 1 peak present; other values rejected |

Status bit positions: 0 RAILS_UNQUALIFIED, 1 ADC_NOT_READY, 2 ADC_TIMEOUT, 3 ADC_SATURATED, 4 CALIBRATION_MISSING (including out of calibrated range), 5 ENDSTOP_OR_OPEN, 6 BATTERY_LOW, 7 STANDBY. Unknown status bits make the current force invalid. Current Newton display requires status zero. Diagnostic fault packets may retain old raw value/timestamp.

The cumulative peak is historical and has its own validity flag: a later fault does not invalidate a maximum recorded earlier while status was zero. The phone may accept that historical peak during a fault, but must still hide the invalid current force.

## Peak recording and reset acknowledgement

Peak reset characteristic: `C37A0003-7B4D-4A26-9C36-2C17F770A001`, write with response, exactly four bytes: a nonzero little-endian uint32 epoch token. Zero and wrong lengths are ignored. This command resets only the diagnostic peak accumulator; it cannot enable power, change mode/tare, save calibration or reset repetitions. It is an open local BLE command; another connected client could reset the accumulator. Unexpected epochs are visible and the recording app requests its own token again.

Recording start generates a token and writes it. Firmware applies the request in its acquisition loop. Repeated writes with the current token are idempotent and preserve the peak. The app only accepts a device peak with its matching token, retries unacknowledged requests at most once per second on arriving packets, and resets the epoch again after a device reboot. Acquisition begins when the device acknowledges the reset, not retroactively at the phone tap. Peaks before that acknowledgement or across a device reboot cannot be recovered.

Every freshly acquired valid ADC sample updates the accumulator, independently of 25-Hz publications. It survives notification loss, BLE disconnection and analog standby within the same boot/epoch. At stop, the app waits for the next notification, at most one second, to save the final cumulative peak; timeout marks the session interrupted. ADC acquisition is nominally 330 SPS, loop-polled; blocked firmware or suspended/terminated app cannot guarantee complete raw capture. The app CSV stores received notifications and device peaks, not every ADC conversion.

## Repetitions

NC switch polling requires 10 ms stable HIGH followed by 10 ms stable LOW. Boot/wake already LOW, isometry and rail/ADC/battery faults disarm counting. Opening a cable is indistinguishable from endstop activation and may count once. A sustained LOW does not repeat. Calibration is not required for qualified switch counting. This is not a safety channel.

Device total survives BLE disconnection and standby, resets on reboot. App reset/recording start only resets its displayed count; CSV retains total and boot ID. On reconnect, wrapping unsigned deltas recover missed increments. App cannot reconstruct raw samples missed during interruption.

## Legacy and simulation

The app still accepts v1 (26 bytes, offsets 0–25) and v2 (34 bytes, offsets 0–33). Legacy devices use the received-sample peak; v1 also uses phone-side switch counting. UI distinguishes `Session peak · received` from `Session peak · device`. New firmware emits v3 only. Simulation is explicitly labelled, locally generated and uses the received-sample peak.

Calibration, mode, tare and standby remain USB serial commands. The peak-reset command is the sole writable BLE function.
