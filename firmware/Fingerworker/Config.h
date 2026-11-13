#pragma once
// Set true ONLY after qualification of the assembled Rev A supply ramps,
// settling, USB source switching, battery divider and actual board revision.
constexpr bool HARDWARE_QUALIFIED = false;
#ifndef FINGERWORKER_BENCH_START
#define FINGERWORKER_BENCH_START 0
#endif
// Dedicated first-power build keeps the analog branch off until explicit wake.
constexpr bool BENCH_START = FINGERWORKER_BENCH_START != 0;
// Provisional values for bench bring-up; replace with measured values before qualification.
constexpr uint32_t BOOST_SETTLE_MS = 10;
constexpr uint32_t ANALOG_SETTLE_MS = 20;
constexpr uint16_t BATTERY_MIN_MV = 3400;
constexpr uint16_t BATTERY_RECOVER_MV = 3550;
constexpr float BATTERY_DIVIDER_RATIO = (1510.0f / 510.0f); // XIAO 1M / 510k nominal; calibrate real divider.
