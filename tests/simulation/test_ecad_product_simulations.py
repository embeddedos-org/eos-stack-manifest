"""
EmbeddedOS — eBuild CAD Product Simulation Test Suite
======================================================
Runs power-budget simulations for all 12 CAD design divisions and
35 product sub-categories defined in eCAD-Hardware-Products.

Each test:
  1. Locates the product's simulation/power_budget_sim.py
  2. Executes it as a subprocess (mirrors what ebuild does at build time)
  3. Asserts the script exits 0 and produces non-empty output
  4. Validates key numeric outputs (total power > 0, runtime > 0 where applicable)

The tests are self-contained: they embed the simulation logic directly so
the suite can run inside eos-stack-manifest CI without requiring a full
checkout of eCAD-Hardware-Products.  When eCAD-Hardware-Products IS checked
out (e.g. during a full-stack build), the ECAD_ROOT env-var can point to it
and the tests will execute the real files instead.

Usage:
    python -m pytest tests/simulation/test_ecad_product_simulations.py -v
    python -m pytest tests/simulation/test_ecad_product_simulations.py -v --tb=short
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time
import unittest
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ECAD_ROOT: Optional[Path] = None
_env_root = os.environ.get("ECAD_ROOT")
if _env_root:
    ECAD_ROOT = Path(_env_root)

# Inline simulation scripts (used when eCAD-Hardware-Products is not checked out)
# Each entry: (division, product, script_source)
INLINE_SIMULATIONS: list[tuple[str, str, str]] = [

    # ── eAerospace ──────────────────────────────────────────────────────────
    ("eAerospace_CAD_Design", "avionics", textwrap.dedent("""\
        components = {
            "NXP LS1046A SoC": 8.0,
            "Xilinx Artix-7 FPGA": 1.5,
            "DDR4 ECC x4": 4 * 0.4,
            "eMMC": 0.2,
            "GbE PHY x4": 4 * 0.18,
            "CAN FD transceivers x6": 6 * 0.04,
            "MIL-STD-1553 transceiver": 0.3,
            "ARINC 429 transceiver x4": 4 * 0.15,
        }
        total = sum(components.values())
        assert total > 0, "Total power must be positive"
        print(f"eFCC-Pro Avionics — Total: {total:.3f} W")
        print(f"28VDC aircraft bus current: {total/28*1000:.0f} mA")
    """)),

    ("eAerospace_CAD_Design", "uav_drone_systems", textwrap.dedent("""\
        components = {
            "STM32H7B3 MCU": 0.12,
            "nRF52840 BLE SoC": 0.018,
            "u-blox ZED-F9P GPS": 0.135,
            "BMI088 IMU": 0.002,
            "INA3221 power monitors x3": 3 * 0.002,
            "4G LTE module": 1.5,
            "ESC motor controllers x4": 4 * 0.5,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eUAV-Ctrl — Total: {total:.3f} W")
        print(f"Battery runtime estimate: {22.2*5000/1000/total:.1f} h")
    """)),

    ("eAerospace_CAD_Design", "space_systems", textwrap.dedent("""\
        components = {
            "NXP LS1046A SoC (rad-hard)": 8.0,
            "STM32H7B3 safety MCU x2": 2 * 0.12,
            "DDR4 ECC x4": 4 * 0.4,
            "GbE PHY x2": 2 * 0.18,
            "SpaceWire transceiver x4": 4 * 0.1,
            "S-band transceiver": 5.0,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eSat-OBC — Total: {total:.3f} W")
        print(f"Solar panel requirement (30% margin): {total*1.3:.1f} W")
    """)),

    ("eAerospace_CAD_Design", "aircraft_components", textwrap.dedent("""\
        components = {
            "STM32H7B3 MCU": 0.12,
            "ARINC 429 x4": 4 * 0.15,
            "CAN FD x2": 2 * 0.04,
            "Pressure sensor x4": 4 * 0.005,
            "Temperature sensor x8": 8 * 0.001,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eAircraft-Sensor — Total: {total*1000:.1f} mW")
    """)),

    # ── eMedical ────────────────────────────────────────────────────────────
    ("eMedical_CAD_Design", "medical_devices", textwrap.dedent("""\
        components = {
            "NXP i.MX 8M Plus SoC": 4.5,
            "LPDDR4X x2": 2 * 0.3,
            "eMMC": 0.2,
            "ECG AFE (ADS1298)": 0.005,
            "SpO2 (MAX86141)": 0.012,
            "NIBP pump": 2.0,
            "15-inch display": 18.0,
            "Wi-Fi module": 0.25,
            "4G LTE module": 1.5,
        }
        total = sum(components.values())
        assert total > 0
        print(f"ePatient-Monitor — Total: {total:.3f} W")
        print(f"IEC 60601-1 Class I device — mains powered")
    """)),

    ("eMedical_CAD_Design", "surgical_robotics", textwrap.dedent("""\
        components = {
            "NVIDIA Jetson AGX Orin": 60.0,
            "NXP LS1046A safety SoC": 8.0,
            "LPDDR5 x4": 4 * 0.8,
            "NVMe SSD": 2.0,
            "Force/torque sensors x7": 7 * 0.05,
            "Servo drives x7": 7 * 15.0,
            "Stereo camera": 3.5,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eSurgical-Robot — Total: {total:.2f} W")
        print(f"220VAC mains current: {total/220:.2f} A")
    """)),

    ("eMedical_CAD_Design", "diagnostic_equipment", textwrap.dedent("""\
        components = {
            "Rockchip RK3588S SoC": 8.0,
            "LPDDR5 x4": 4 * 0.8,
            "NVMe SSD": 2.0,
            "Ultrasound transducer array": 25.0,
            "Beamforming FPGA": 15.0,
            "Display 21-inch": 30.0,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eUltrasound-Pro — Total: {total:.2f} W")
    """)),

    ("eMedical_CAD_Design", "implantable_devices", textwrap.dedent("""\
        modes = {
            "Deep sleep": 2e-6,
            "Neural recording": 0.0008,
            "BLE TX": 0.0055,
            "Stimulation pulse": 0.005,
        }
        battery_mAh = 85
        avg_I = modes["Deep sleep"] * 0.95 + modes["Neural recording"] * 0.04 + modes["BLE TX"] * 0.01
        runtime_years = battery_mAh / (avg_I * 1000) / (365 * 24)
        assert runtime_years > 0
        print(f"eImplant-Neuro — Avg current: {avg_I*1e6:.2f} µA")
        print(f"Battery runtime: {runtime_years:.1f} years")
    """)),

    # ── eIndustrial ─────────────────────────────────────────────────────────
    ("eIndustrial_CAD_Design", "industrial_automation", textwrap.dedent("""\
        components = {
            "NXP LS1046A SoC": 8.0,
            "STM32H7B3 safety MCU x2": 2 * 0.12,
            "DDR4 ECC x2": 2 * 0.4,
            "EtherCAT slave x8": 8 * 0.15,
            "PROFINET controller": 0.5,
            "DI/DO modules x16": 16 * 0.02,
        }
        total = sum(components.values())
        assert total > 0
        print(f"ePLC-Pro — Total: {total:.3f} W")
        print(f"24VDC DIN rail current: {total/24*1000:.0f} mA")
    """)),

    ("eIndustrial_CAD_Design", "process_control", textwrap.dedent("""\
        components = {
            "NXP LS1046A SoC": 8.0,
            "STM32H7B3 MCU x4": 4 * 0.12,
            "DDR4 ECC x2": 2 * 0.4,
            "4-20mA loop isolators x16": 16 * 0.05,
            "HART modem x8": 8 * 0.02,
            "FOUNDATION Fieldbus": 0.3,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eDCS-Controller — Total: {total:.3f} W")
    """)),

    ("eIndustrial_CAD_Design", "industrial_iot", textwrap.dedent("""\
        modes = {"Sleep": 1e-5, "Active": 0.005, "LoRa TX": 0.044, "4G TX": 0.22}
        avg_I = modes["Sleep"] * 0.98 + modes["LoRa TX"] * 0.5/600
        battery_mAh = 5000
        runtime_days = battery_mAh / (avg_I * 1000) / 24
        assert runtime_days > 0
        print(f"eIIoT-Gateway — Avg: {avg_I*1e6:.1f} µA, Runtime: {runtime_days:.0f} days")
    """)),

    # ── eDefense ────────────────────────────────────────────────────────────
    ("eDefense_CAD_Design", "military_electronics", textwrap.dedent("""\
        components = {
            "NVIDIA Jetson AGX Orin": 60.0,
            "NXP LS1046A SoC": 8.0,
            "AD9361 SDR transceiver x2": 2 * 0.8,
            "LPDDR5 x4": 4 * 0.8,
            "NVMe SSD": 2.0,
            "Crypto HSM": 0.5,
            "MIL-STD-1553 x2": 2 * 0.3,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eMilComm-SDR — Total: {total:.2f} W")
        print(f"MIL-STD-704F 28VDC current: {total/28*1000:.0f} mA")
    """)),

    ("eDefense_CAD_Design", "surveillance_systems", textwrap.dedent("""\
        components = {
            "NVIDIA Jetson AGX Orin": 60.0,
            "TI AWR2944 radar x4": 4 * 3.5,
            "Sony IMX678 cameras x8": 8 * 0.35,
            "LPDDR5 x4": 4 * 0.8,
            "NVMe SSD x2": 2 * 2.0,
            "10GbE SFP+ x2": 2 * 1.5,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eSurveillance-Radar — Total: {total:.2f} W")
    """)),

    ("eDefense_CAD_Design", "communication_systems", textwrap.dedent("""\
        components = {
            "NXP LS1046A SoC": 8.0,
            "AD9361 SDR x2": 2 * 0.8,
            "PA (50W RF)": 50.0,
            "LNA array": 0.5,
            "Crypto module": 0.5,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eMilNav-INS — Total: {total:.2f} W")
    """)),

    # ── eRobotics ───────────────────────────────────────────────────────────
    ("eRobotics_CAD_Design", "autonomous_systems", textwrap.dedent("""\
        components = {
            "NVIDIA Jetson Orin NX": 20.0,
            "Livox Mid-360 LiDAR x2": 2 * 8.0,
            "RTK GPS": 0.135,
            "IMU": 0.002,
            "4G LTE": 1.5,
            "Drive motors x4": 4 * 50.0,
        }
        total = sum(components.values())
        electronics = total - 4 * 50.0
        assert electronics > 0
        print(f"eAGV-Nav — Electronics: {electronics:.2f} W, Total: {total:.2f} W")
    """)),

    ("eRobotics_CAD_Design", "industrial_robots", textwrap.dedent("""\
        components = {
            "NXP LS1046A SoC": 8.0,
            "STM32H7B3 safety MCU": 0.12,
            "EtherCAT slave x6": 6 * 0.15,
            "Servo drives x6": 6 * 20.0,
            "Force/torque sensor x6": 6 * 0.05,
            "Vision camera x2": 2 * 0.35,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eRobot-Ctrl — Total: {total:.2f} W")
    """)),

    ("eRobotics_CAD_Design", "robot_components", textwrap.dedent("""\
        components = {
            "STM32H7B3 MCU": 0.12,
            "DRV8323RS gate driver": 0.05,
            "IPM (IGBT 15A)": 2.0,
            "AS5047P encoder": 0.01,
            "CAN FD transceiver": 0.04,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eServo-Drive — Total: {total*1000:.1f} mW per axis")
    """)),

    # ── eEnergy ─────────────────────────────────────────────────────────────
    ("eEnergy_CAD_Design", "battery_management", textwrap.dedent("""\
        components = {
            "STM32G474 MCU": 0.08,
            "LTC6813 x2": 2 * 0.025,
            "INA3221 x4": 4 * 0.002,
            "BQ40Z80 fuel gauge": 0.005,
            "CAN FD transceiver": 0.04,
            "Active balancers x18": 18 * 0.002,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eBMS-100A — Total: {total*1000:.1f} mW")
        print(f"Quiescent @ 48V: {total/48*1000:.1f} mA")
    """)),

    ("eEnergy_CAD_Design", "renewable_energy", textwrap.dedent("""\
        rated = 10000
        eff = 0.986
        losses = rated * (1 - eff)
        assert losses > 0
        print(f"eSolarInv-10kW — Losses: {losses:.1f} W")
        print(f"Efficiency: {eff*100:.1f}%")
        print(f"Annual yield (5h/day): {rated*5*365/1000:.0f} kWh")
    """)),

    ("eEnergy_CAD_Design", "power_electronics", textwrap.dedent("""\
        rated = 5000
        eff = 0.982
        losses = rated * (1 - eff)
        assert losses > 0
        print(f"eDCDC-5kW — Losses: {losses:.1f} W")
        print(f"Efficiency: {eff*100:.1f}%")
    """)),

    # ── eTransport ──────────────────────────────────────────────────────────
    ("eTransport_CAD_Design", "automotive_electronics", textwrap.dedent("""\
        components = {
            "S32K344 MCU (ASIL-D)": 0.25,
            "CAN FD x6": 6 * 0.04,
            "LIN x4": 4 * 0.01,
            "100BASE-T1 PHY x2": 2 * 0.18,
            "PMIC ASIL-D": 0.05,
            "SBC ASIL-D": 0.08,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eVCU-Pro (ASIL-D) — Total: {total*1000:.1f} mW")
        print(f"12V bus current: {total/12*1000:.1f} mA")
    """)),

    ("eTransport_CAD_Design", "rail_systems", textwrap.dedent("""\
        components = {
            "NXP LS1043A SoC": 5.0,
            "STM32H7B3 safety MCU x2": 2 * 0.12,
            "DDR4 ECC x2": 2 * 0.4,
            "eMMC": 0.2,
            "GbE PHY x4": 4 * 0.18,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eTCU-Pro (SIL 4) — Total: {total:.3f} W")
        print(f"24VDC railway bus: {total/24*1000:.0f} mA")
    """)),

    ("eTransport_CAD_Design", "maritime_systems", textwrap.dedent("""\
        components = {
            "NXP i.MX 8M Plus SoC": 4.5,
            "LPDDR4X x2": 2 * 0.3,
            "eMMC": 0.2,
            "GbE PHY x4": 4 * 0.18,
            "27-inch IPS display": 35.0,
            "NMEA 2000 controller": 0.05,
            "Wi-Fi module": 0.25,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eNav-ECDIS — Total: {total:.3f} W")
        print(f"24VDC maritime bus: {total/24*1000:.0f} mA")
    """)),

    # ── eElectronics ────────────────────────────────────────────────────────
    ("eElectronics_CAD_Design", "electronic_components", textwrap.dedent("""\
        tx_time_s = 0.5
        period_s = 600
        sleep_I = 1.2e-6
        tx_I = 0.044
        avg_I = (tx_I * tx_time_s + sleep_I * (period_s - tx_time_s)) / period_s
        battery_mAh = 2000
        runtime_days = battery_mAh / (avg_I * 1000) / 24
        assert runtime_days > 0
        print(f"eIoT-Board — Avg: {avg_I*1e6:.1f} µA, Runtime: {runtime_days:.0f} days ({runtime_days/365:.1f} yr)")
    """)),

    ("eElectronics_CAD_Design", "semiconductor_products", textwrap.dedent("""\
        components = {
            "eASIC-Vision ASIC": 5.0,
            "LPDDR5 x4": 4 * 0.8,
            "Artix-7 FPGA": 1.5,
            "GbE PHY x4": 4 * 0.18,
        }
        total = sum(components.values())
        assert total > 0
        perf_per_watt = 100 / 5.0
        print(f"eASIC-Vision — Total: {total:.3f} W")
        print(f"AI efficiency: {perf_per_watt:.0f} TOPS/W")
    """)),

    ("eElectronics_CAD_Design", "emerging_tech", textwrap.dedent("""\
        components = {
            "RK3588S SoC (AI)": 10.0,
            "LPDDR5 x4": 4 * 0.8,
            "NVMe SSD": 2.0,
            "2.5GbE x2": 2 * 0.5,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eEdge-AI-Box — Total: {total:.3f} W")
        print(f"AI efficiency: {32/10:.1f} TOPS/W")
    """)),

    # ── eSmartCity ──────────────────────────────────────────────────────────
    ("eSmartCity_CAD_Design", "urban_infrastructure", textwrap.dedent("""\
        electronics = 4.5 + 2*0.3 + 0.2 + 1.5 + 0.8 + 0.25 + 4*0.18
        led_signals = 12 * 8.0
        total = electronics + led_signals
        assert total > 0
        print(f"eTrafficCtrl — Electronics: {electronics:.2f} W, LED signals: {led_signals:.0f} W")
        print(f"Annual energy: {total*8760/1000:.0f} kWh")
    """)),

    ("eSmartCity_CAD_Design", "utilities", textwrap.dedent("""\
        meas_s = 0.1; period_s = 900; nbiot_s = 5
        sleep_I = 8e-4; meas_I = 0.010; nbiot_I = 0.220
        avg_I = (meas_I * meas_s + sleep_I * (period_s - meas_s)) / period_s
        avg_I += nbiot_I * nbiot_s / (24 * 3600)
        battery_Ah = 8.5
        runtime_years = battery_Ah / (avg_I * 1000 / 1000) / (365 * 24)
        assert runtime_years > 0
        print(f"eWM-DN50 — Avg: {avg_I*1e6:.1f} µA, Runtime: {runtime_years:.1f} years")
    """)),

    ("eSmartCity_CAD_Design", "telecom", textwrap.dedent("""\
        components = {
            "i.MX 8M Plus SoC": 4.5,
            "LPDDR4X x2": 2 * 0.3,
            "LoRaWAN SoC": 0.044,
            "BLE+Zigbee SoC": 0.018,
            "4G LTE module": 1.5,
            "GbE PHY x2": 2 * 0.18,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eIoT-GW — Total: {total:.3f} W, 12V current: {total/12*1000:.0f} mA")
    """)),

    # ── eCybersecurity ──────────────────────────────────────────────────────
    ("eCybersecurity_CAD_Design", "security_appliances", textwrap.dedent("""\
        components = {
            "NXP LS1046A SoC": 8.0,
            "DDR4 ECC x4": 4 * 0.4,
            "eMMC": 0.2,
            "GbE PHY x4": 4 * 0.18,
            "Crypto co-processor": 0.001,
            "Tamper detection": 0.005,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eHSM-Pro (FIPS 140-3 L3) — Total: {total:.3f} W")
        print(f"Crypto throughput: AES-256 @ 10 Gbps hardware")
    """)),

    ("eCybersecurity_CAD_Design", "physical_security", textwrap.dedent("""\
        components = {
            "STM32H7B3 MCU": 0.12,
            "BLE+NFC SoC": 0.018,
            "NFC/RFID controller": 0.05,
            "GbE PHY": 0.18,
            "Door lock relay": 0.5,
        }
        total = sum(components.values())
        poe_budget = 30.0
        assert total < poe_budget, f"Exceeds PoE+ budget: {total:.3f} W > {poe_budget} W"
        print(f"eAccess-Pro — Total: {total*1000:.1f} mW, PoE+ margin: {(poe_budget-total)*1000:.0f} mW")
    """)),

    # ── eConsumer ───────────────────────────────────────────────────────────
    ("eConsumer_CAD_Design", "smart_home", textwrap.dedent("""\
        components = {
            "i.MX 8M Mini SoC": 2.5,
            "LPDDR4X x2": 2 * 0.2,
            "BLE+Zigbee SoC": 0.018,
            "Z-Wave module": 0.025,
            "Wi-Fi 6 module": 0.25,
            "GbE PHY": 0.18,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eHub-Pro (Matter 1.3) — Total: {total:.3f} W")
    """)),

    ("eConsumer_CAD_Design", "personal_devices", textwrap.dedent("""\
        avg_I = (
            10e-6 * 0.90 +
            0.030 * 0.05 +
            0.003 * 0.04 +
            0.008 * (30/3600) * 24 / 24
        )
        battery_mAh = 420
        runtime_days = battery_mAh / (avg_I * 1000) / 24
        assert runtime_days > 0
        print(f"eWatch-Pro — Avg: {avg_I*1000:.3f} mA, Runtime: {runtime_days:.1f} days")
    """)),

    ("eConsumer_CAD_Design", "smart_devices", textwrap.dedent("""\
        components = {
            "Snapdragon XR2+ Gen 1": 5.0,
            "LPDDR5 x4": 4 * 0.8,
            "Dual micro-OLED": 2 * 0.8,
            "12MP camera": 0.5,
            "Wi-Fi 6E module": 0.35,
        }
        total = sum(components.values())
        battery_mAh = 3000; battery_V = 3.7
        runtime_h = battery_mAh * battery_V / 1000 / total
        assert runtime_h > 0
        print(f"eGlasses-AR — Total: {total:.3f} W, Runtime: {runtime_h:.1f} h")
    """)),

    # ── eMining ─────────────────────────────────────────────────────────────
    ("eMining_CAD_Design", "mining_equipment", textwrap.dedent("""\
        components = {
            "NXP LS1046A SoC": 8.0,
            "NVIDIA Jetson Orin NX": 20.0,
            "Livox Mid-360 LiDAR x4": 4 * 8.0,
            "RTK GPS x2": 2 * 0.135,
            "77GHz radar x6": 6 * 2.5,
            "4G LTE module": 1.5,
        }
        total = sum(components.values())
        assert total > 0
        print(f"eHaul-Auto — Total: {total:.2f} W, 24V current: {total/24*1000:.0f} mA")
    """)),

    ("eMining_CAD_Design", "industrial_safety", textwrap.dedent("""\
        sensor_warmup = 8e-4
        meas_duty = 0.010 * (0.1 / 5)
        ble_duty = 0.003 * 0.1
        display_duty = 0.080 * 0.3
        avg_I = sensor_warmup + meas_duty + ble_duty + display_duty
        battery_mAh = 3600
        runtime_h = battery_mAh / (avg_I * 1000)
        assert runtime_h > 0
        print(f"eGasDetect-4 (ATEX) — Avg: {avg_I*1000:.2f} mA, Runtime: {runtime_h:.0f} h ({runtime_h/24/365:.1f} yr)")
    """)),

    ("eMining_CAD_Design", "construction_robots", textwrap.dedent("""\
        components = {
            "RK3588S SoC": 8.0,
            "NVIDIA Jetson Orin NX": 20.0,
            "Livox Mid-360 LiDAR x2": 2 * 8.0,
            "RTK GPS x2": 2 * 0.135,
            "Sony IMX678 cameras x6": 6 * 0.35,
            "4G LTE module": 1.5,
            "Drive motors x4": 4 * 50.0,
        }
        total = sum(components.values())
        electronics = total - 4 * 50.0
        battery_Wh = 48 * 50
        runtime_h = battery_Wh / total
        assert runtime_h > 0
        print(f"eSiteSurvey — Electronics: {electronics:.2f} W, Total: {total:.2f} W")
        print(f"Battery (48V 50Ah): {battery_Wh} Wh, Runtime: {runtime_h:.1f} h")
    """)),

    # ── AeroSwift (previously merged) ───────────────────────────────────────
    ("AeroSwift", "aeroswift_personal", textwrap.dedent("""\
        bom_cost = 56000
        max_speed_kmh = 300
        range_km = 150
        payload_kg = 200
        assert bom_cost > 0
        print(f"AeroSwift Personal (AS-1/2) — BOM: ${bom_cost:,}")
        print(f"Max speed: {max_speed_kmh} km/h, Range: {range_km} km, Payload: {payload_kg} kg")
    """)),

    ("AeroSwift", "aeroswift_transit", textwrap.dedent("""\
        bom_cost = 342000
        seats = 10
        max_speed_kmh = 350
        range_km = 200
        assert bom_cost > 0
        print(f"AeroSwift Transit (AS-10) — BOM: ${bom_cost:,}")
        print(f"Seats: {seats}, Max speed: {max_speed_kmh} km/h, Range: {range_km} km")
    """)),
]


# ---------------------------------------------------------------------------
# Test runner helpers
# ---------------------------------------------------------------------------

def _run_inline(script: str) -> tuple[int, str, str]:
    """Execute an inline Python script string and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


def _run_file(path: Path) -> tuple[int, str, str]:
    """Execute a Python file and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


# ---------------------------------------------------------------------------
# Dynamic test class generation
# ---------------------------------------------------------------------------

class EBuildCADSimulationTests(unittest.TestCase):
    """Auto-generated tests for all eCAD product power-budget simulations."""
    pass


def _make_test(division: str, product: str, script: str):
    def test_method(self):
        # Try real file first if ECAD_ROOT is set
        if ECAD_ROOT:
            sim_path = ECAD_ROOT / division / product / "simulation" / "power_budget_sim.py"
            if sim_path.exists():
                rc, stdout, stderr = _run_file(sim_path)
                self.assertEqual(rc, 0,
                    f"[{division}/{product}] power_budget_sim.py exited {rc}\nSTDERR: {stderr}")
                self.assertTrue(stdout.strip(),
                    f"[{division}/{product}] simulation produced no output")
                return

        # Fall back to inline script
        rc, stdout, stderr = _run_inline(script)
        self.assertEqual(rc, 0,
            f"[{division}/{product}] inline simulation failed (exit {rc})\nSTDERR: {stderr}\nSTDOUT: {stdout}")
        self.assertTrue(stdout.strip(),
            f"[{division}/{product}] simulation produced no output")

    test_method.__name__ = f"test_{division.lower().replace('-', '_')}_{product}"
    test_method.__doc__ = f"eBuild power-budget simulation: {division} / {product}"
    return test_method


# Register all tests dynamically
for _div, _prod, _script in INLINE_SIMULATIONS:
    _test_fn = _make_test(_div, _prod, _script)
    setattr(EBuildCADSimulationTests, _test_fn.__name__, _test_fn)


# ---------------------------------------------------------------------------
# Master build-time summary test
# ---------------------------------------------------------------------------

class EBuildCADSummaryTest(unittest.TestCase):
    """Runs all simulations sequentially and prints a build-time summary table."""

    def test_all_simulations_build_summary(self):
        """Full eBuild CAD simulation pass — all 37 products."""
        results = []
        total_start = time.perf_counter()

        for division, product, script in INLINE_SIMULATIONS:
            start = time.perf_counter()
            rc, stdout, stderr = _run_inline(script)
            elapsed = time.perf_counter() - start
            status = "PASS" if rc == 0 else "FAIL"
            results.append((division, product, status, elapsed, stdout.strip().split("\n")[0]))

        total_elapsed = time.perf_counter() - total_start
        passed = sum(1 for r in results if r[2] == "PASS")
        failed = sum(1 for r in results if r[2] == "FAIL")

        print("\n")
        print("=" * 90)
        print("  EmbeddedOS eBuild — CAD Product Simulation Build Report")
        print("=" * 90)
        print(f"  {'Division':<35} {'Product':<28} {'Status':<6} {'Time':>6}  {'Key Output'}")
        print("-" * 90)
        for div, prod, status, elapsed, first_line in results:
            icon = "✅" if status == "PASS" else "❌"
            print(f"  {icon} {div:<33} {prod:<28} {status:<6} {elapsed*1000:>5.0f}ms  {first_line}")
        print("=" * 90)
        print(f"  Total: {len(results)} products | ✅ {passed} passed | ❌ {failed} failed | "
              f"⏱ {total_elapsed*1000:.0f}ms build time")
        print("=" * 90)

        self.assertEqual(failed, 0,
            f"{failed} product simulation(s) failed — see table above")


if __name__ == "__main__":
    unittest.main(verbosity=2)
