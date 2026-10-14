"""Generate the v2 hybrid-car assistant spec files, with vehicle state named after COVESA VSS signals.

Usage:
    python generate_specs.py OUT_DIR [--vss-json FULL_VSS_EXPORT.json]

Every state value is either a standard VSS signal (checked against vss_reference.json) or an
extension declared in the overlay file this script writes (2026-10-14_hybrid_v2_vss_overlay.vspec).
Pass --vss-json with a full `vspec export json` of VSS to refresh vss_reference.json.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1])
PREFIX = "2026-10-14_hybrid_v2"
REF_PATH = HERE / "vss_reference.json"
VSS_COMMIT = "dcc7cf570f27378d7ff9333f2a4d1cf552645cfe"
VSS_VERSION = "7.0-dev"

# ------------------------------------------------------------------ instances
# VSS names seats, doors and HVAC stations by row and side. DriverSide is the left side in this
# left-hand-drive car.
SIDES = {"row1_driver_side": ("Row1", "DriverSide"), "row1_passenger_side": ("Row1", "PassengerSide"),
         "row2_driver_side": ("Row2", "DriverSide"), "row2_passenger_side": ("Row2", "PassengerSide")}
SIDE_WORD = {"row1_driver_side": "Driver", "row1_passenger_side": "Front passenger",
             "row2_driver_side": "Rear driver-side", "row2_passenger_side": "Rear passenger-side"}
FRONT = ["row1_driver_side", "row1_passenger_side"]
STATIONS = {"row1_driver": "Row1.Driver", "row1_passenger": "Row1.Passenger", "row2_driver": "Row2.Driver", "row2_passenger": "Row2.Passenger"}
STATION_WORD = {"row1_driver": "Driver", "row1_passenger": "Front passenger", "row2_driver": "Rear driver-side", "row2_passenger": "Rear passenger-side"}
WHEELS = {"Row1.Wheel.Left": "Front-left", "Row1.Wheel.Right": "Front-right", "Row2.Wheel.Left": "Rear-left", "Row2.Wheel.Right": "Rear-right"}
CHARGE_PORT = "Vehicle.Powertrain.TractionBattery.Charging.ChargingPort.FrontLeft"


def one_of(values):
    vals = [f'"{v}"' if isinstance(v, str) else str(v) for v in values]
    if len(vals) == 2:
        return f"one of {vals[0]} or {vals[1]}."
    return "one of " + ", ".join(vals[:-1]) + f", or {vals[-1]}."


def P(type_, desc, required=True, default=None, samples=None):
    p = {"type": type_, "required": required}
    if not required:
        p["default"] = default
    p["description"] = desc
    if samples:
        p["sample_values"] = samples
    return p


# ------------------------------------------------------------------ VSS reference
if "--vss-json" in sys.argv:
    full = json.load(open(sys.argv[sys.argv.index("--vss-json") + 1]))
    flat = {}

    def walk(n, path):
        for k, v in n.get("children", {}).items():
            p = f"{path}.{k}" if path else k
            if v["type"] == "branch":
                walk(v, p)
            else:
                flat[p] = {x: v[x] for x in ("type", "datatype", "unit", "min", "max", "allowed", "description") if x in v}
    walk({"children": full}, "")
    VSS_ALL = flat
else:
    VSS_ALL = None
REF = json.load(open(REF_PATH))["signals"] if REF_PATH.exists() and VSS_ALL is None else None

# ------------------------------------------------------------------ state
STATE, META, EXT = {}, {}, {}
PIPE_TYPE = {"boolean": "bool", "string": "str", "float": "float", "double": "float",
             "uint8": "int", "int8": "int", "uint16": "int", "int16": "int", "uint32": "int", "int32": "int"}


def vss_lookup(path):
    src = VSS_ALL if VSS_ALL is not None else REF
    return src.get(path)


def S(path, desc, initial="random", default=None, minimum=None, maximum=None, step=None, enum=None, ext=None, type_=None):
    """Declare one state value. `ext` declares a VSS extension: dict(type=, datatype=, unit=, description=)."""
    if ext:
        assert vss_lookup(path) is None, f"{path} exists in VSS; do not declare it as an extension"
        EXT[path] = ext
        vss = {"type": ext["type"], "datatype": ext["datatype"], **({"unit": ext["unit"]} if "unit" in ext else {})}
        META[path] = {"standard": False, **vss}
    else:
        vss = vss_lookup(path)
        assert vss is not None, f"{path} is not a VSS signal"
        META[path] = {"standard": True, **{k: vss[k] for k in ("type", "datatype", "unit", "min", "max", "allowed") if k in vss}}
    t = type_ or PIPE_TYPE[vss["datatype"]]
    unit = vss.get("unit")
    tail = f"VSS {'extension, ' if ext else ''}{vss['type']}, {vss['datatype']}" + (f", {unit}" if unit else "") + "."
    s = {"type": t}
    if minimum is not None:
        s["minimum"], s["maximum"] = minimum, maximum
    if step is not None:
        s["step"] = step
    if enum is not None:
        s["enum"] = enum
    s["initial"] = initial
    if initial == "fixed":
        s["default"] = default
    s["description"] = f"{desc} {tail}"
    STATE[path] = s


C = "Vehicle.Cabin"
# --- windows, sunroof, shades
for k, (row, side) in SIDES.items():
    S(f"{C}.Door.{row}.{side}.Window.Position", f"{SIDE_WORD[k]} window opening, 0 closed, 100 fully open.", minimum=0, maximum=100, step=5)
S(f"{C}.IsWindowChildLockEngaged", "Rear window switches are disabled, so only the driver can move the rear windows.")
S(f"{C}.Sunroof.Position", "Sunroof position: 0 closed, 100 fully open, negative values tilt it up, -100 fully tilted.", initial="from_weather", minimum=-100, maximum=100, step=5)
S(f"{C}.Sunroof.Shade.Position", "Sunroof shade opening, 0 closed, 100 fully open. Must be 100 whenever the sunroof position is above 0.", minimum=0, maximum=100, step=5)
S(f"{C}.RearShade.Position", "Rear window sun shade, 0 retracted, 100 fully raised.", minimum=0, maximum=100, step=10)
# --- doors and access
for k, (row, side) in SIDES.items():
    S(f"{C}.Door.{row}.{side}.IsLocked", f"{SIDE_WORD[k]} door locked.")
for k in ["row2_driver_side", "row2_passenger_side"]:
    row, side = SIDES[k]
    S(f"{C}.Door.{row}.{side}.IsChildLockActive", f"{SIDE_WORD[k]} door child safety lock. A mechanical switch on the door, so it can be read but not set from the cabin.")
S("Vehicle.Body.Trunk.Rear.IsOpen", "Trunk lid open. Can only be true while the car is stopped in park.", initial="fixed", default=False)
S("Vehicle.Body.Trunk.Rear.IsLocked", "Trunk locked.")
S("Vehicle.Powertrain.FuelSystem.IsFuelPortFlapOpen", "Fuel filler door open. Can only be true while the car is stopped in park.", initial="fixed", default=False)
S(f"{CHARGE_PORT}.IsFlapOpen", "Charging port door, on the front-left fender, open. Can only be true while the car is stopped in park.", initial="fixed", default=False)
S(f"{CHARGE_PORT}.IsChargingCableConnected", "Charging cable plugged in. Always false while driving.", initial="fixed", default=False)
S(f"{CHARGE_PORT}.IsChargingCableLocked", "Charging cable locked into the port so it cannot be pulled out.", initial="fixed", default=False)
# --- exterior lights
B = "Vehicle.Body"
S(f"{B}.Lights.Beam.Low.IsOn", "Low beam headlights on. On at night, in rain, snow, fog, or storm.", initial="from_weather")
S(f"{B}.Lights.Beam.High.IsOn", "High beam headlights on. Always false while the front fog lights are on.")
S(f"{B}.Lights.Fog.Front.IsOn", "Front fog lights on. Usually on only in fog, heavy rain, or snow.", initial="from_weather")
S(f"{B}.Lights.Fog.Rear.IsOn", "Rear fog light on. Usually on only in fog or heavy snow.", initial="from_weather")
S(f"{B}.Lights.Hazard.IsSignaling", "Hazard warning lights flashing.", initial="fixed", default=False)
# --- wipers and mirrors
WIPE = ["OFF", "SLOW", "MEDIUM", "FAST", "INTERVAL", "RAIN_SENSOR"]
S(f"{B}.Windshield.Front.Wiping.Mode", "Front wiper mode. Should not be \"OFF\" when it rains or snows.", initial="from_weather", enum=WIPE)
S(f"{B}.Windshield.Front.Wiping.Intensity", "Front wiper interval frequency or rain sensor sensitivity, 1 lowest, 4 highest. Only matters in \"INTERVAL\" and \"RAIN_SENSOR\" mode.", enum=[1, 2, 3, 4])
S(f"{B}.Windshield.Rear.Wiping.Mode", "Rear wiper mode. This car's rear wiper supports only these modes.", initial="from_weather", enum=["OFF", "INTERVAL", "SLOW"])
for side in ["DriverSide", "PassengerSide"]:
    word = "Driver-side" if side == "DriverSide" else "Passenger-side"
    S(f"{B}.Mirrors.{side}.IsFolded", f"{word} exterior mirror folded in.", initial="fixed", default=False)
    S(f"{B}.Mirrors.{side}.IsHeatingOn", f"{word} exterior mirror heating on. Usually on in snow, fog, or below 3 Celsius.", initial="from_weather")
# --- interior lights
for k, (row, side) in SIDES.items():
    S(f"{C}.Light.Spotlight.{row}.{side}.IsLightOn", f"{SIDE_WORD[k]} reading light on.")
AMBIENT = {"white": "#FFFFFF", "red": "#FF0000", "orange": "#FF8000", "yellow": "#FFD700", "green": "#00C853",
           "cyan": "#00FFFF", "blue": "#0050FF", "purple": "#8000FF", "pink": "#FF4FA0"}
for k, (row, side) in SIDES.items():
    base = f"{C}.Light.AmbientLight.{row}.{side}"
    S(f"{base}.IsLightOn", f"{SIDE_WORD[k]} zone ambient light on.")
    S(f"{base}.Color", f"{SIDE_WORD[k]} zone ambient light color as an RGB hex code. This car offers nine preset colors.", enum=list(AMBIENT.values()))
    S(f"{base}.Intensity", f"{SIDE_WORD[k]} zone ambient light brightness in percent.", minimum=10, maximum=100, step=10)
# --- climate
H = f"{C}.HVAC"
S(f"{H}.IsAutoModeActive", "Climate auto mode: the car picks fan speed and air distribution to reach the target temperatures. Manual fan or air distribution changes switch it off.",
  initial="fixed", default=True, ext={"type": "actuator", "datatype": "boolean", "description": "Climate control automatic mode. True = the system controls fan speed and air distribution."})
for k, st in STATIONS.items():
    S(f"{H}.Station.{st}.Temperature", f"{STATION_WORD[k]} zone target temperature in Celsius. VSS sets no range; this car accepts 16 to 28.", minimum=16.0, maximum=28.0, step=0.5)
    S(f"{H}.Station.{st}.FanSpeed", f"{STATION_WORD[k]} zone fan speed in percent. This car has five fan levels, 20 percent each.", enum=[0, 20, 40, 60, 80, 100])
    S(f"{H}.Station.{st}.AirDistribution", f"{STATION_WORD[k]} zone air direction: \"UP\" windshield, \"MIDDLE\" face, \"DOWN\" feet.", enum=["UP", "MIDDLE", "DOWN"])
S(f"{H}.IsAirConditioningActive", "Air conditioning compressor on. Usually on when it is hot.", initial="from_weather")
S(f"{H}.IsRecirculationActive", "Cabin air recirculation on. False means fresh outside air.")
S(f"{H}.IsFrontDefrosterActive", "Front windshield defroster on. Usually on in snow, fog, or below 3 Celsius.", initial="from_weather")
S(f"{H}.IsRearDefrosterActive", "Rear window defroster on. Usually on in snow, fog, or below 3 Celsius.", initial="from_weather")
S(f"{H}.AmbientAirTemperature", "Measured cabin air temperature in Celsius. Drifts toward the outside temperature when climate is off.", initial="from_weather", minimum=-20.0, maximum=55.0, step=0.5)
S("Vehicle.Exterior.AirTemperature", "Outside air temperature in Celsius, taken from the weather of the current city.", initial="from_weather", minimum=-30.0, maximum=50.0, step=0.5)
S("Vehicle.Exterior.Humidity", "Outside relative humidity in percent, taken from the weather of the current city.", initial="from_weather", minimum=0.0, maximum=100.0, step=1.0)
# --- seats and steering wheel
HC = [-100, -66, -33, 0, 33, 66, 100]
for k, (row, side) in SIDES.items():
    base = f"{C}.Seat.{row}.{side}"
    S(f"{base}.OccupancyStatus", f"{SIDE_WORD[k]} seat occupancy sensor." + (" The driver seat is always occupied." if k == "row1_driver_side" else ""),
      initial="fixed" if k == "row1_driver_side" else "random", default="OCCUPIED" if k == "row1_driver_side" else None, enum=["OCCUPIED", "EMPTY"])
    if k in FRONT:
        S(f"{base}.HeatingCooling", f"{SIDE_WORD[k]} seat heating (positive) or ventilation cooling (negative). Levels 1 to 3 map to 33, 66, 100. A seat cannot heat and cool at once, which this one signal guarantees.", initial="from_weather", enum=HC)
    else:
        S(f"{base}.HeatingCooling", f"{SIDE_WORD[k]} seat heating. Rear seats heat only; levels 1 to 3 map to 33, 66, 100.", initial="from_weather", enum=[0, 33, 66, 100])
for k in FRONT:
    row, side = SIDES[k]
    base = f"{C}.Seat.{row}.{side}"
    S(f"{base}.Massage.Level", f"{SIDE_WORD[k]} seat massage intensity in percent, 0 off. This car offers 0, 33, 66, and 100.", enum=[0, 33, 66, 100])
    S(f"{base}.Massage.TypeActive", f"{SIDE_WORD[k]} seat massage program. Ignored while the massage level is 0.", enum=["WAVE", "PULSE", "STRETCH", "LUMBAR"])
    S(f"{base}.Position", f"{SIDE_WORD[k]} seat fore-aft position in mm from the frontmost position.", minimum=0, maximum=250, step=10)
    S(f"{base}.Backrest.Recline", f"{SIDE_WORD[k]} backrest recline in degrees from upright; positive leans back.", minimum=0.0, maximum=40.0, step=1.0)
S(f"{C}.Seat.Row1.DriverSide.MemoryProfile", "Last recalled driver seat memory profile, 0 means none recalled.", enum=[0, 1, 2, 3],
  ext={"type": "actuator", "datatype": "uint8", "description": "Driver seat memory profile last recalled. 0 = none."})
S("Vehicle.Chassis.SteeringWheel.HeatingCooling", "Steering wheel heating. This wheel heats only; levels 1 to 3 map to 33, 66, 100.", initial="from_weather", enum=[0, 33, 66, 100])
# --- media
M = f"{C}.Infotainment.Media"
SOURCES = ["FM", "AM", "DAB", "BLUETOOTH", "USB", "INTERNET"]
S(f"{M}.Played.Source", "Active audio source. \"INTERNET\" is the streaming service.", enum=SOURCES)
S(f"{M}.Action", "Last playback command. \"PLAY\" means playing, \"STOP\" means paused.", enum=["PLAY", "STOP", "SKIP_FORWARD", "SKIP_BACKWARD"])
S(f"{M}.Volume", "Audio volume in percent.", minimum=0, maximum=100, step=1)
S(f"{M}.IsMuted", "Audio muted without changing the volume.",
  ext={"type": "actuator", "datatype": "boolean", "description": "Media audio muted. The Volume value is kept."})
S(f"{M}.Radio.FMFrequency", "Tuned FM frequency in MHz.", minimum=87.5, maximum=108.0, step=0.1,
  ext={"type": "actuator", "datatype": "float", "description": "Tuned FM radio frequency in MHz."})
S(f"{M}.SelectedURI", "Identifier of the last media item chosen by search, empty when none.", initial="fixed", default="")
# --- driving and telemetry
S("Vehicle.Speed", "Current vehicle speed in km/h. 0 means stopped.", minimum=0.0, maximum=160.0, step=1.0)
S("Vehicle.Powertrain.Transmission.SelectedGear", "Selected gear: 126 park, 127 drive, 0 neutral, -1 reverse. Speed is 0 whenever the gear is 126.", enum=[126, 127, 0, -1])
S("Vehicle.TraveledDistance", "Odometer in meters.", minimum=0, maximum=300000000, step=1000)
S("Vehicle.TripMeterReading", "Trip meter since the last reset, in meters.", minimum=0, maximum=2000000, step=100)
S("Vehicle.TripDuration", "Driving time since the trip was started, in seconds.", minimum=0.0, maximum=86400.0, step=60.0)
S("Vehicle.AverageSpeed", "Average speed since the trip was started, in km/h.", minimum=0.0, maximum=130.0, step=1.0)
for w, word in WHEELS.items():
    S(f"Vehicle.Chassis.Axle.{w}.Tire.Pressure", f"{word} tire pressure in kPa. Recommended 230 to 250.", minimum=150, maximum=280, step=5)
    S(f"Vehicle.Chassis.Axle.{w}.Tire.IsPressureLow", f"{word} tire low-pressure warning. True when the pressure is below 200 kPa.")
S("Vehicle.Service.DistanceToService", "Distance until the next scheduled service in km; 0 means due now.", minimum=0.0, maximum=30000.0, step=100.0)
S("Vehicle.Service.IsServiceDue", "Scheduled service is due.")
S("Vehicle.Powertrain.CombustionEngine.EngineOil.Level", "Engine oil level.", enum=["CRITICALLY_LOW", "LOW", "NORMAL", "HIGH"])
S(f"{B}.Windshield.Front.WasherFluid.Level", "Windshield washer fluid level in percent.", minimum=0, maximum=100, step=5)
S("Vehicle.LowVoltageBattery.CurrentVoltage", "12 V battery voltage. Below 11.8 V means it is weak.", minimum=11.0, maximum=14.8, step=0.1)
# --- powertrain and energy
PT = "Vehicle.Powertrain"
S(f"{PT}.Type", "Powertrain type.", initial="fixed", default="HYBRID", enum=["HYBRID"])
S(f"{PT}.FuelSystem.HybridType", "Hybrid architecture: plug-in hybrid.", initial="fixed", default="PHEV", enum=["PHEV"])
S(f"{PT}.FuelSystem.TankCapacity", "Fuel tank capacity in liters.", initial="fixed", default=45.0, minimum=30.0, maximum=80.0, step=0.5)
S(f"{PT}.TractionBattery.NetCapacity", "Usable high-voltage battery capacity in kWh.", initial="fixed", default=18, minimum=8, maximum=40, step=1)
S(f"{PT}.FuelSystem.RelativeLevel", "Fuel level in percent of tank capacity.", minimum=0, maximum=100, step=1)
S(f"{PT}.FuelSystem.IsFuelLevelLow", "Low fuel warning. True when the fuel level is below 10 percent.")
S(f"{PT}.TractionBattery.StateOfCharge.Displayed", "Battery level shown to the driver, in percent.", minimum=0.0, maximum=100.0, step=1.0)
S(f"{PT}.RangeExtender.ChargeDepleting.EnergyConsumption", "Reference electric consumption for range estimates, in kWh per 100 km.", initial="fixed", default=18.0, minimum=12.0, maximum=25.0, step=0.5)
S(f"{PT}.FuelSystem.AverageConsumption", "Average fuel consumption with the engine running, in liters per 100 km. Used for fuel range estimates.", minimum=3.0, maximum=12.0, step=0.1)
S(f"{PT}.CombustionEngine.IsRunning", "Combustion engine running. False whenever the hybrid mode is \"ELECTRIC\".")
S(f"{PT}.RangeExtender.OperatingMode", "How the hybrid currently runs: \"CHARGE_DEPLETING\" uses battery first, \"CHARGE_SUSTAINING\" keeps the battery level, \"BLENDED\" mixes both. Follows the hybrid mode.",
  enum=["CHARGE_DEPLETING", "CHARGE_SUSTAINING", "BLENDED"])
S(f"{PT}.Hybrid.Mode", "Driver-selected hybrid mode: \"AUTO\" blends battery and engine, \"ELECTRIC\" drives on battery only, \"HOLD\" saves the battery level for later, \"CHARGE\" runs the engine to charge the battery to the charge target.",
  enum=["AUTO", "ELECTRIC", "HOLD", "CHARGE"], ext={"type": "actuator", "datatype": "string", "description": "Driver-selected hybrid operating mode."})
S(f"{PT}.Hybrid.ChargeTarget", "Battery level the engine charges up to in \"CHARGE\" mode, in percent.", minimum=20, maximum=80, step=10,
  ext={"type": "actuator", "datatype": "uint8", "unit": "percent", "description": "Target state of charge while the hybrid mode is CHARGE."})
S(f"{PT}.Hybrid.RegenLevel", "Regenerative braking strength, 0 coasting, 3 strongest.", enum=[0, 1, 2, 3],
  ext={"type": "actuator", "datatype": "uint8", "description": "Regenerative braking level. 0 = coasting, 3 = strongest."})
S(f"{PT}.Transmission.PerformanceMode", "Driving mode for throttle response and efficiency. This car offers these three.", enum=["NORMAL", "SPORT", "ECONOMY"])
CH = f"{PT}.TractionBattery.Charging"
S(f"{CH}.ChargeLimit", "Battery level plug-in charging stops at, in percent.", minimum=50, maximum=100, step=5)
S(f"{CH}.Timer.Mode", "Charging timer: \"INACTIVE\" charges as soon as the cable is plugged in, \"START_TIME\" waits until the timer time, \"END_TIME\" finishes by the timer time.", enum=["INACTIVE", "START_TIME", "END_TIME"])
S(f"{CH}.Timer.Time", "Timer time of day as HH:MM local time, empty while the timer mode is \"INACTIVE\". VSS stores a full ISO 8601 timestamp; the simulator keeps the time of day.", initial="fixed", default="")
S(f"{CH}.IsCharging", "Battery is charging from a cable. Always false while driving.", initial="fixed", default=False)
S(f"{CH}.MaxAcceptedPowerAC", "Most AC charging power this car accepts, in kW.", initial="fixed", default=7.4, enum=[3.7, 7.4, 11.0],
  ext={"type": "attribute", "datatype": "float", "unit": "kW", "description": "Maximum AC charging power the vehicle accepts."})
S(f"{CH}.MaxAcceptedPowerDC", "Most DC fast charging power this car accepts, in kW. 0 means no DC charging.", initial="fixed", default=50.0, enum=[0.0, 50.0, 80.0],
  ext={"type": "attribute", "datatype": "float", "unit": "kW", "description": "Maximum DC charging power the vehicle accepts. 0 = no DC charging."})
# --- vehicle identity
S("Vehicle.VehicleIdentification.VehicleExteriorColor", "Exterior paint color.", initial="fixed", default="Blue", enum=["Black", "White", "Silver", "Gray", "Blue", "Red", "Green"])
# --- navigation
N = f"{C}.Infotainment.Navigation"
NEXT = lambda d: {"type": "actuator", "datatype": d["datatype"], "description": d["description"]}
S(f"{N}.IsGuidanceActive", "A route is set and guidance is running.", initial="fixed", default=False,
  ext=NEXT({"datatype": "boolean", "description": "Route guidance active."}))
S(f"{N}.DestinationSet.Latitude", "Latitude of the final destination, 0 when no route is set.", initial="fixed", default=0.0, minimum=-90.0, maximum=90.0)
S(f"{N}.DestinationSet.Longitude", "Longitude of the final destination, 0 when no route is set.", initial="fixed", default=0.0, minimum=-180.0, maximum=180.0)
S(f"{N}.DestinationSet.LocationId", "Location ID of the final destination, empty when no route is set.", initial="fixed", default="",
  ext=NEXT({"datatype": "string", "description": "Location ID of the destination in the map database."}))
for i in (1, 2, 3):
    S(f"{N}.Waypoints.Stop{i}.LocationId", f"Location ID of intermediate stop {i} in driving order, empty when unused. Stops fill from 1 upward without gaps.", initial="fixed", default="",
      ext=NEXT({"datatype": "string", "description": f"Location ID of intermediate stop {i}."}))
S(f"{N}.RouteId", "Route ID of the leg currently followed, empty when no route is set.", initial="fixed", default="",
  ext=NEXT({"datatype": "string", "description": "ID of the route leg being followed."}))
S(f"{N}.RouteOptions.IsTollAvoided", "Route planning avoids toll roads.", ext=NEXT({"datatype": "boolean", "description": "Avoid toll roads when planning routes."}))
S(f"{N}.RouteOptions.IsHighwayAvoided", "Route planning avoids highways.", ext=NEXT({"datatype": "boolean", "description": "Avoid highways when planning routes."}))
S(f"{N}.Mute", "Spoken guidance: \"UNMUTED\" speaks every instruction, \"ALERT_ONLY\" only speaks alerts, \"MUTED\" is silent.", enum=["UNMUTED", "ALERT_ONLY", "MUTED"])
S(f"{N}.Volume", "Navigation voice volume in percent.", minimum=0, maximum=100, step=5)
S(f"{N}.IsDestinationReached", "The final destination has been reached.", initial="fixed", default=False)


def paths(prefix):
    return [p for p in STATE if p.startswith(prefix)]


def sel(*rx):
    return [p for p in STATE if any(re.search(r, p) for r in rx)]


# ------------------------------------------------------------------ tools
TOOLS, TOOL_STATE = {}, {}


def tool(name, domain, kind, desc, params=None, writes=None, reads=None, external=False):
    TOOLS[name] = {"description": desc, "domain": domain, "kind": kind, "parameters": params or {}, "sample_commands": []}
    if external:
        TOOL_STATE[name] = {"external": True}
    elif kind == "action":
        TOOL_STATE[name] = {"writes": writes}
    else:
        TOOL_STATE[name] = {"reads": reads}


STOPPED = "Blocked unless the car is stopped in park (`Vehicle.Speed` is 0 and `Vehicle.Powertrain.Transmission.SelectedGear` is 126); if blocked, tell the driver why instead of retrying."
MOVING = "Blocked while `Vehicle.Speed` is above 0."
WEATHER = "Check the weather with `get_weather` first."
SEAT4 = list(SIDES) + ["all"]
SEATDESC = " \"row1_driver_side\" is the driver seat; row 2 is the back seat."
LEVEL = "integer from 0 to 3. 0 is off; 1, 2, 3 set 33, 66, 100 percent."

# ---- Body: windows, sunroof, shades
tool("set_window_position", "Vehicle", "action",
     "Open or close one window, or all four, to a position from 0 (closed) to 100 (fully open). Policy: if air conditioning is on and a window is opened beyond 25, warn about energy waste and ask for confirmation first.",
     {"window": P("str", one_of(SEAT4) + " \"row1_driver_side\" is the driver window."),
      "position": P("int", "integer from 0 to 100, in steps of 5. Default is 100.", False, 100)},
     writes=sel(r"Window\.Position$"))
tool("set_window_child_lock", "Vehicle", "action",
     "Disable or enable the rear passengers' window switches, so only the driver can move the rear windows.",
     {"on": P("bool", "true to disable the rear window switches, false to enable them.")},
     writes=[f"{C}.IsWindowChildLockEngaged"])
tool("get_window_positions", "Vehicle", "retrieve",
     "Return the opening position of all four windows and whether the rear window switches are locked.",
     reads=sel(r"Window\.Position$") + [f"{C}.IsWindowChildLockEngaged"])
tool("set_sunshade_position", "Vehicle", "action",
     "Open or close the sunroof shade from 0 (closed) to 100 (fully open). It cannot close below 100 while the sunroof is open; close the sunroof first.",
     {"position": P("int", "integer from 0 to 100, in steps of 5. Default is 100.", False, 100)},
     writes=[f"{C}.Sunroof.Shade.Position"])
tool("set_sunroof_position", "Vehicle", "action",
     "Open, close, or tilt the sunroof. Opening above 0 is blocked unless the shade is already at 100 or is opened to 100 with `set_sunshade_position` in the same turn; tilting needs no shade. "
     + WEATHER + " If the condition is not \"clear\", \"sunny\", \"partly_cloudy\", or \"cloudy\", get an explicit yes from the driver before opening or tilting.",
     {"position": P("int", "integer from -100 to 100, in steps of 5. 0 closes, 100 opens fully, negative values tilt up with -100 fully tilted. Default is 100.", False, 100)},
     writes=[f"{C}.Sunroof.Position"])
tool("get_sunroof_and_sunshade_position", "Vehicle", "retrieve",
     "Return the sunroof position (negative means tilted) and the sunroof shade position. They are read together because the sunroof can only open when the shade is fully open.",
     reads=[f"{C}.Sunroof.Position", f"{C}.Sunroof.Shade.Position"])
tool("set_rear_window_shade", "Vehicle", "action",
     "Raise or lower the rear window sun shade.",
     {"position": P("int", "integer from 0 to 100, in steps of 10. 0 retracts it, 100 raises it fully. Default is 100.", False, 100)},
     writes=[f"{C}.RearShade.Position"])
tool("get_rear_window_shade_position", "Vehicle", "retrieve",
     "Return how far the rear window sun shade is raised.",
     reads=[f"{C}.RearShade.Position"])

# ---- doors and access
tool("set_door_locks", "Vehicle", "action",
     "Lock or unlock one door or all doors. Unlocking is " + MOVING[0].lower() + MOVING[1:],
     {"door": P("str", one_of(SEAT4) + " Default is \"all\".", False, "all"),
      "locked": P("bool", "true to lock, false to unlock.")},
     writes=sel(r"Door\.Row\d\.\w+\.IsLocked$"))
tool("get_door_status", "Vehicle", "retrieve",
     "Return which doors are locked and whether the rear child safety locks are engaged. Child locks are mechanical switches on the doors, so the assistant can report them but not change them.",
     reads=sel(r"Door\.Row\d\.\w+\.IsLocked$", r"IsChildLockActive$"))
tool("set_trunk", "Vehicle", "action",
     "Open or close the power trunk lid. " + STOPPED,
     {"open": P("bool", "true to open the trunk, false to close it.")},
     writes=["Vehicle.Body.Trunk.Rear.IsOpen"])
tool("set_trunk_lock", "Vehicle", "action",
     "Lock or unlock the trunk separately from the doors, for example to keep valet staff out.",
     {"locked": P("bool", "true to lock the trunk, false to unlock it.")},
     writes=["Vehicle.Body.Trunk.Rear.IsLocked"])
tool("get_trunk_status", "Vehicle", "retrieve",
     "Return whether the trunk lid is open and whether the trunk is locked.",
     reads=["Vehicle.Body.Trunk.Rear.IsOpen", "Vehicle.Body.Trunk.Rear.IsLocked"])
tool("set_fuel_door", "Vehicle", "action",
     "Open or close the fuel filler door for refueling. " + STOPPED,
     {"open": P("bool", "true to open the fuel door, false to close it.")},
     writes=["Vehicle.Powertrain.FuelSystem.IsFuelPortFlapOpen"])
tool("get_fuel_door_status", "Vehicle", "retrieve",
     "Return whether the fuel filler door is open.",
     reads=["Vehicle.Powertrain.FuelSystem.IsFuelPortFlapOpen"])
tool("set_charge_port", "Vehicle", "action",
     "Open or close the charging port door. " + STOPPED,
     {"open": P("bool", "true to open the charge port door, false to close it.")},
     writes=[f"{CHARGE_PORT}.IsFlapOpen"])
tool("set_charging_cable_lock", "Vehicle", "action",
     "Lock or release the charging cable in the port. Only works while a cable is connected; release it before the driver unplugs.",
     {"locked": P("bool", "true to lock the cable, false to release it.")},
     writes=[f"{CHARGE_PORT}.IsChargingCableLocked"])
tool("get_charge_port_status", "Vehicle", "retrieve",
     "Return whether the charge port door is open, whether a cable is connected, and whether the cable is locked.",
     reads=paths(CHARGE_PORT))

# ---- exterior lights
tool("set_low_beams", "Vehicle", "action",
     "Turn the low beam headlights on or off. Turning them off is not allowed while the front fog lights are on.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=[f"{B}.Lights.Beam.Low.IsOn"])
tool("set_high_beams", "Vehicle", "action",
     "Turn the high beam headlights on or off. Turning them on is blocked while the front fog lights are on.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=[f"{B}.Lights.Beam.High.IsOn"])
tool("set_fog_lights", "Vehicle", "action",
     "Turn the front fog lights, the rear fog light, or both on or off. Policy: when turning the front fog lights on, also make sure the low beams are on (`set_low_beams`) and the high beams are off (`set_high_beams`). "
     + WEATHER + " If the condition is not \"fog\", \"heavy_rain\", \"snow\", or \"storm\", get an explicit yes from the driver before turning any fog light on.",
     {"which": P("str", one_of(["front", "rear", "both"])),
      "on": P("bool", "true to turn on, false to turn off.")},
     writes=[f"{B}.Lights.Fog.Front.IsOn", f"{B}.Lights.Fog.Rear.IsOn"])
tool("set_hazard_lights", "Vehicle", "action",
     "Turn the hazard warning lights on or off.",
     {"on": P("bool", "true to start flashing, false to stop.")},
     writes=[f"{B}.Lights.Hazard.IsSignaling"])
tool("get_exterior_lights_status", "Vehicle", "retrieve",
     "Return whether the low beams, high beams, front fog lights, rear fog light, and hazard lights are on.",
     reads=paths(f"{B}.Lights."))

# ---- wipers and mirrors
tool("set_wipers", "Vehicle", "action",
     "Set the front or rear wiper mode, and for the front wiper the interval or rain sensor sensitivity.",
     {"window": P("str", one_of(["front", "rear"])),
      "mode": P("str", one_of(WIPE) + " The rear wiper supports only \"OFF\", \"INTERVAL\", and \"SLOW\"."),
      "intensity": P("int", "integer from 1 to 4. Default is 2. Used only for the front wiper in \"INTERVAL\" or \"RAIN_SENSOR\" mode.", False, 2)},
     writes=sel(r"Wiping\.(Mode|Intensity)$"))
tool("get_wiper_status", "Vehicle", "retrieve",
     "Return the front and rear wiper modes and the front wiper intensity.",
     reads=sel(r"Wiping\.(Mode|Intensity)$"))
tool("set_side_mirrors_folded", "Vehicle", "action",
     "Fold or unfold both exterior mirrors. Folding is " + MOVING[0].lower() + MOVING[1:],
     {"folded": P("bool", "true to fold the mirrors in, false to unfold them.")},
     writes=sel(r"Mirrors\.\w+\.IsFolded$"))
tool("set_mirror_heating", "Vehicle", "action",
     "Turn exterior mirror heating on or off for both mirrors, to clear ice, frost, or fog.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=sel(r"Mirrors\.\w+\.IsHeatingOn$"))
tool("get_side_mirror_status", "Vehicle", "retrieve",
     "Return whether each exterior mirror is folded and whether its heating is on.",
     reads=paths(f"{B}.Mirrors."))

# ---- interior lights
tool("set_reading_light", "Vehicle", "action",
     "Turn the reading light at one seat, or at all seats, on or off.",
     {"seat": P("str", one_of(SEAT4) + SEATDESC),
      "on": P("bool", "true to turn on, false to turn off.")},
     writes=sel(r"Spotlight\..*IsLightOn$"))
tool("get_reading_lights_status", "Vehicle", "retrieve",
     "Return which seats have their reading light on.",
     reads=sel(r"Spotlight\..*IsLightOn$"))
tool("set_ambient_light", "Vehicle", "action",
     "Set the ambient interior lighting in all four zones: on or off, color, and brightness. Colors map to RGB codes: "
     + ", ".join(f"{n} {h}" for n, h in AMBIENT.items()) + ".",
     {"on": P("bool", "true to turn on, false to turn off."),
      "color": P("str", one_of(list(AMBIENT)) + " Default is \"white\". Ignored when on is false.", False, "white"),
      "brightness_pct": P("int", "integer from 10 to 100, in steps of 10. Default is 70. Ignored when on is false.", False, 70)},
     writes=paths(f"{C}.Light.AmbientLight."))
tool("get_ambient_light_status", "Vehicle", "retrieve",
     "Return, for each ambient light zone, whether it is on, its color code, and its brightness.",
     reads=paths(f"{C}.Light.AmbientLight."))

# ---- climate
ZONES = list(STATIONS) + ["row2", "all"]
ZDESC = " \"row1_driver\" is the driver zone; \"row2\" means both rear zones."
tool("set_climate_temperature", "Vehicle", "action",
     "Set the target temperature of one climate zone, both rear zones, or all zones. Policy: if the result leaves more than 3 Celsius between zones, tell the driver.",
     {"zone": P("str", one_of(ZONES) + ZDESC),
      "temperature_c": P("float", "number from 16.0 to 28.0, in steps of 0.5.")},
     writes=sel(r"Station\..*\.Temperature$"))
tool("set_fan_speed", "Vehicle", "action",
     "Set the fan speed of one climate zone or all zones. This switches climate auto mode off.",
     {"zone": P("str", one_of(ZONES) + ZDESC + " Default is \"all\".", False, "all"),
      "level": P("int", "integer from 0 to 5. 0 is off; each level adds 20 percent fan speed.")},
     writes=sel(r"Station\..*\.FanSpeed$") + [f"{H}.IsAutoModeActive"])
tool("set_air_distribution", "Vehicle", "action",
     "Set where a climate zone blows air: up to the windshield, middle to the face, or down to the feet. This switches climate auto mode off.",
     {"zone": P("str", one_of(ZONES) + ZDESC + " Default is \"all\".", False, "all"),
      "direction": P("str", one_of(["UP", "MIDDLE", "DOWN"]))},
     writes=sel(r"Station\..*\.AirDistribution$") + [f"{H}.IsAutoModeActive"])
tool("set_air_conditioning", "Vehicle", "action",
     "Turn the air conditioning compressor on or off. Policy: when turning it on, also close any window open beyond 20 (`set_window_position`) and raise the fan to level 1 if it is off (`set_fan_speed`).",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=[f"{H}.IsAirConditioningActive"])
tool("set_air_recirculation", "Vehicle", "action",
     "Switch between recirculating cabin air and drawing fresh outside air.",
     {"on": P("bool", "true to recirculate cabin air, false for fresh outside air.")},
     writes=[f"{H}.IsRecirculationActive"])
tool("set_defrost", "Vehicle", "action",
     "Turn the front windshield defroster, the rear window defroster, or both on or off. Policy: when turning on the front defroster, also set fan level 2 or higher (`set_fan_speed`), set the front air distribution to \"UP\" (`set_air_distribution`), and turn on air conditioning (`set_air_conditioning`).",
     {"window": P("str", one_of(["front", "rear", "all"])),
      "on": P("bool", "true to turn on, false to turn off.")},
     writes=[f"{H}.IsFrontDefrosterActive", f"{H}.IsRearDefrosterActive"])
tool("set_climate_auto_mode", "Vehicle", "action",
     "Turn climate auto mode on or off. In auto mode the car picks fan speed and air distribution to reach the target temperatures.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=[f"{H}.IsAutoModeActive"])
tool("get_climate_status", "Vehicle", "retrieve",
     "Return the climate settings (auto mode, each zone's temperature, fan speed, and air distribution, air conditioning, recirculation, defrosters) plus the measured cabin temperature and the outside temperature and humidity.",
     reads=paths(f"{H}.") + ["Vehicle.Exterior.AirTemperature", "Vehicle.Exterior.Humidity"])

# ---- seats and steering wheel
tool("set_seat_heating", "Vehicle", "action",
     "Set seat heating for one seat or all seats. On a front seat this replaces any ventilation, because both use the same heating-cooling setting.",
     {"seat": P("str", one_of(SEAT4) + SEATDESC),
      "level": P("int", LEVEL)},
     writes=sel(r"Seat\.Row\d\.\w+\.HeatingCooling$"))
tool("set_seat_ventilation", "Vehicle", "action",
     "Set seat ventilation (cooling) for a front seat. Only the front seats ventilate. This replaces any heating on that seat, because both use the same heating-cooling setting.",
     {"seat": P("str", one_of(FRONT + ["both"]) + " \"row1_driver_side\" is the driver seat."),
      "level": P("int", "integer from 0 to 3. 0 is off; 1, 2, 3 set -33, -66, -100 percent.")},
     writes=[f"{C}.Seat.Row1.DriverSide.HeatingCooling", f"{C}.Seat.Row1.PassengerSide.HeatingCooling"])
tool("set_seat_massage", "Vehicle", "action",
     "Start, change, or stop the massage of a front seat. Only the front seats have massage.",
     {"seat": P("str", one_of(FRONT + ["both"]) + " \"row1_driver_side\" is the driver seat."),
      "program": P("str", one_of(["WAVE", "PULSE", "STRETCH", "LUMBAR"]) + " Default is \"WAVE\".", False, "WAVE"),
      "level": P("int", LEVEL)},
     writes=sel(r"Massage\.(Level|TypeActive)$"))
tool("set_seat_position", "Vehicle", "action",
     "Move a front seat forward or back. Moving the driver seat is " + MOVING[0].lower() + MOVING[1:] + " For relative requests, read the current position with `get_seat_status` first.",
     {"seat": P("str", one_of(FRONT) + " \"row1_driver_side\" is the driver seat."),
      "position_mm": P("int", "integer from 0 to 250, in steps of 10. 0 is fully forward.")},
     writes=sel(r"Row1\.\w+\.Position$"))
tool("set_seat_recline", "Vehicle", "action",
     "Change the backrest recline of a front seat. Changing the driver seat is " + MOVING[0].lower() + MOVING[1:] + " For relative requests, read the current angle with `get_seat_status` first.",
     {"seat": P("str", one_of(FRONT) + " \"row1_driver_side\" is the driver seat."),
      "angle_deg": P("int", "integer from 0 to 40. Degrees back from upright.")},
     writes=sel(r"Backrest\.Recline$"))
tool("recall_seat_memory", "Vehicle", "action",
     "Move the driver seat to a saved memory profile. " + MOVING,
     {"profile": P("int", "integer from 1 to 3.")},
     writes=[f"{C}.Seat.Row1.DriverSide.MemoryProfile", f"{C}.Seat.Row1.DriverSide.Position", f"{C}.Seat.Row1.DriverSide.Backrest.Recline"])
tool("set_steering_wheel_heating", "Vehicle", "action",
     "Set the steering wheel heating level.",
     {"level": P("int", LEVEL)},
     writes=["Vehicle.Chassis.SteeringWheel.HeatingCooling"])
tool("get_seat_status", "Vehicle", "retrieve",
     "Return seat occupancy, each seat's heating or ventilation, front seat massage, front seat position and recline, the last recalled memory profile, and steering wheel heating.",
     reads=paths(f"{C}.Seat.") + ["Vehicle.Chassis.SteeringWheel.HeatingCooling"])

# ---- media
tool("set_media_volume", "Media", "action",
     "Set the audio volume. Setting a volume also unmutes the audio.",
     {"volume_pct": P("int", "integer from 0 to 100.")},
     writes=[f"{M}.Volume", f"{M}.IsMuted"])
tool("set_media_mute", "Media", "action",
     "Mute or unmute the audio without changing the volume.",
     {"muted": P("bool", "true to mute, false to unmute.")},
     writes=[f"{M}.IsMuted"])
tool("set_media_source", "Media", "action",
     "Switch the audio source. Playback continues from the new source.",
     {"source": P("str", one_of(SOURCES) + " \"INTERNET\" is the streaming service.")},
     writes=[f"{M}.Played.Source", f"{M}.Action"])
tool("set_media_playback", "Media", "action",
     "Play or pause the current audio source.",
     {"playing": P("bool", "true to play, false to pause.")},
     writes=[f"{M}.Action"])
tool("skip_media_track", "Media", "action",
     "Skip to the next or previous track on the current source and keep playing. Not available on \"FM\", \"AM\", or \"DAB\".",
     {"direction": P("str", one_of(["next", "previous"]))},
     writes=[f"{M}.Action"])
tool("tune_fm_radio", "Media", "action",
     "Tune the FM radio to a frequency and switch the audio source to FM.",
     {"frequency_mhz": P("float", "number from 87.5 to 108.0, in steps of 0.1.")},
     writes=[f"{M}.Radio.FMFrequency", f"{M}.Played.Source", f"{M}.Action"])
tool("play_media_by_query", "Media", "action",
     "Search the streaming service for a song, artist, album, playlist, or podcast and start playing the best match. Switches the audio source to \"INTERNET\".",
     {"query": P("str", "free text naming what to play.", samples=["Bohemian Rhapsody", "Norah Jones", "lo-fi focus playlist", "the latest episode of a daily news podcast"]),
      "media_type": P("str", one_of(["any", "song", "artist", "album", "playlist", "podcast"]) + " Default is \"any\".", False, "any")},
     writes=[f"{M}.SelectedURI", f"{M}.Played.Source", f"{M}.Action"])
tool("get_media_status", "Media", "retrieve",
     "Return the audio source, the last playback command, the volume, mute state, the tuned FM frequency, and the last item chosen by search.",
     reads=paths(f"{M}."))

# ---- driving, tires, maintenance, trip
tool("get_driving_status", "Vehicle", "retrieve",
     "Return the current speed, the selected gear (126 park, 127 drive, 0 neutral, -1 reverse), and the odometer. Use it to check whether the car is stopped in park before actions that require it.",
     reads=["Vehicle.Speed", "Vehicle.Powertrain.Transmission.SelectedGear", "Vehicle.TraveledDistance"])
tool("get_tire_pressure", "Vehicle", "retrieve",
     "Return the pressure of all four tires in kPa and which tires have a low-pressure warning.",
     reads=sel(r"Tire\.(Pressure|IsPressureLow)$"))
tool("get_maintenance_status", "Vehicle", "retrieve",
     "Return the distance to the next service, whether service is due, the engine oil level, the washer fluid level, and the 12 V battery voltage.",
     reads=["Vehicle.Service.DistanceToService", "Vehicle.Service.IsServiceDue", "Vehicle.Powertrain.CombustionEngine.EngineOil.Level",
            f"{B}.Windshield.Front.WasherFluid.Level", "Vehicle.LowVoltageBattery.CurrentVoltage"])
tool("get_trip_info", "Vehicle", "retrieve",
     "Return the trip meter, trip duration, average speed, and average fuel consumption.",
     reads=["Vehicle.TripMeterReading", "Vehicle.TripDuration", "Vehicle.AverageSpeed", f"{PT}.FuelSystem.AverageConsumption"])
tool("reset_trip_meter", "Vehicle", "action",
     "Reset the trip meter to zero. Ask for confirmation first, because the old trip distance is lost.",
     writes=["Vehicle.TripMeterReading"])
tool("get_vehicle_specs", "Vehicle", "retrieve",
     "Return fixed facts about the car: exterior color, powertrain and hybrid type, fuel tank capacity, usable battery capacity, and maximum AC and DC charging power.",
     reads=["Vehicle.VehicleIdentification.VehicleExteriorColor", f"{PT}.Type", f"{PT}.FuelSystem.HybridType", f"{PT}.FuelSystem.TankCapacity",
            f"{PT}.TractionBattery.NetCapacity", f"{CH}.MaxAcceptedPowerAC", f"{CH}.MaxAcceptedPowerDC"])

# ---- energy
ENERGY = [f"{PT}.FuelSystem.RelativeLevel", f"{PT}.FuelSystem.IsFuelLevelLow", f"{PT}.TractionBattery.StateOfCharge.Displayed",
          f"{PT}.FuelSystem.TankCapacity", f"{PT}.TractionBattery.NetCapacity",
          f"{PT}.RangeExtender.ChargeDepleting.EnergyConsumption", f"{PT}.FuelSystem.AverageConsumption"]
tool("get_energy_status", "Energy", "retrieve",
     "Return the battery level, fuel level and low-fuel warning, the electric, fuel, and combined range in km (computed from the levels and reference consumption), the hybrid mode and how the hybrid is running, the drive mode, regen level, charge target, and whether the engine is running.",
     reads=ENERGY + [f"{PT}.Hybrid.Mode", f"{PT}.Hybrid.ChargeTarget", f"{PT}.Hybrid.RegenLevel", f"{PT}.RangeExtender.OperatingMode",
                     f"{PT}.Transmission.PerformanceMode", f"{PT}.CombustionEngine.IsRunning"])
tool("set_hybrid_mode", "Energy", "action",
     "Choose how the hybrid uses the battery and the engine. \"AUTO\" blends both, \"ELECTRIC\" drives on battery only (blocked when the battery level is below 10), \"HOLD\" saves the battery level for later (for example a city zone at the destination), \"CHARGE\" runs the engine to charge the battery up to `charge_target_pct`. Policy: in \"CHARGE\" mode warn that fuel consumption rises.",
     {"mode": P("str", one_of(["AUTO", "ELECTRIC", "HOLD", "CHARGE"])),
      "charge_target_pct": P("int", "integer from 20 to 80, in steps of 10. Default is 60. Used only when mode is \"CHARGE\".", False, 60)},
     writes=[f"{PT}.Hybrid.Mode", f"{PT}.Hybrid.ChargeTarget", f"{PT}.RangeExtender.OperatingMode", f"{PT}.CombustionEngine.IsRunning"])
tool("set_drive_mode", "Energy", "action",
     "Set the driving mode, which changes throttle response and efficiency.",
     {"mode": P("str", one_of(["NORMAL", "SPORT", "ECONOMY"]))},
     writes=[f"{PT}.Transmission.PerformanceMode"])
tool("set_regen_level", "Energy", "action",
     "Set the regenerative braking strength.",
     {"level": P("int", "integer from 0 to 3. 0 is coasting, 3 is strongest.")},
     writes=[f"{PT}.Hybrid.RegenLevel"])
tool("get_charging_status", "Energy", "retrieve",
     "Return the plug-in charging state: whether it is charging, the charge limit, the charging timer, and the car's maximum AC and DC charging power.",
     reads=[f"{CH}.IsCharging", f"{CH}.ChargeLimit", f"{CH}.Timer.Mode", f"{CH}.Timer.Time", f"{CH}.MaxAcceptedPowerAC", f"{CH}.MaxAcceptedPowerDC"])
tool("set_charge_limit", "Energy", "action",
     "Set the battery level at which plug-in charging stops.",
     {"limit_pct": P("int", "integer from 50 to 100, in steps of 5.")},
     writes=[f"{CH}.ChargeLimit"])
tool("set_charging_timer", "Energy", "action",
     "Set when plug-in charging runs: right away, starting at a time (for example cheaper night power), or finished by a time (for example a morning departure).",
     {"mode": P("str", one_of(["INACTIVE", "START_TIME", "END_TIME"]) + " \"INACTIVE\" charges as soon as the cable is plugged in."),
      "time": P("str", "time as HH:MM on a 24-hour clock, local time. Default is \"\". Required unless mode is \"INACTIVE\".", False, "", samples=["22:00", "06:30"])},
     writes=[f"{CH}.Timer.Mode", f"{CH}.Timer.Time"])
tool("start_stop_charging", "Energy", "action",
     "Start or stop plug-in charging now. Only works while a charging cable is connected (`get_charge_port_status`).",
     {"action": P("str", one_of(["START", "STOP"]))},
     writes=[f"{CH}.IsCharging"])
STATION_PARAMS = {"charging_station_id": P("str", "charging station ID returned by `search_poi_at_location` or `search_poi_along_route`."),
                  "plug_id": P("str", "plug ID of that station, returned in the same search result.")}
CHG_READS = [f"{PT}.TractionBattery.StateOfCharge.Displayed", f"{PT}.TractionBattery.NetCapacity", f"{CH}.MaxAcceptedPowerAC", f"{CH}.MaxAcceptedPowerDC", f"{CH}.ChargeLimit"]
tool("estimate_charging_time", "Energy", "retrieve",
     "Estimate how many minutes charging takes at a given charging station plug, from a start battery level to a target level. The tool looks up the plug's power and AC or DC type, and caps it at the car's maximum.",
     {**STATION_PARAMS,
      "target_soc_pct": P("int", "integer from 1 to 100. Must be above the start level."),
      "start_soc_pct": P("int", "integer from 0 to 99. Use the current battery level from `get_energy_status` unless the driver names another start level.")},
     reads=CHG_READS)
tool("estimate_soc_after_charging", "Energy", "retrieve",
     "Estimate the battery level after charging for a given number of minutes at a given charging station plug.",
     {**STATION_PARAMS,
      "minutes": P("int", "integer from 1 to 720."),
      "start_soc_pct": P("int", "integer from 0 to 99. Use the current battery level from `get_energy_status` unless the driver names another start level.")},
     reads=CHG_READS)
tool("estimate_electric_distance", "Energy", "retrieve",
     "Estimate how many km the car can drive on electric power alone between two battery levels.",
     {"from_soc_pct": P("int", "integer from 1 to 100. Use the current battery level from `get_energy_status` unless the driver names another start level."),
      "to_soc_pct": P("int", "integer from 0 to 99. Must be below the start level. Default is 0.", False, 0)},
     reads=[f"{PT}.TractionBattery.StateOfCharge.Displayed", f"{PT}.TractionBattery.NetCapacity", f"{PT}.RangeExtender.ChargeDepleting.EnergyConsumption"])
tool("estimate_refuel", "Energy", "retrieve",
     "Estimate how many liters fill the tank to a target level, and the fuel range that adds in km.",
     {"target_fuel_pct": P("int", "integer from 1 to 100. Default is 100.", False, 100)},
     reads=[f"{PT}.FuelSystem.RelativeLevel", f"{PT}.FuelSystem.TankCapacity", f"{PT}.FuelSystem.AverageConsumption"])
tool("estimate_route_energy", "Energy", "retrieve",
     "Estimate how much of a route can be driven electrically, how much fuel the rest needs, and whether the car arrives without charging or refueling. The route ID comes from `get_routes` or `get_navigation_status`.",
     {"route_id": P("str", "route ID returned by `get_routes` or `get_navigation_status`.")},
     reads=ENERGY + [f"{PT}.Hybrid.Mode"])

# ---- navigation
POI = ["gas_station", "charging_station", "restaurant", "fast_food", "cafe", "bakery", "supermarket", "parking", "public_toilet", "hotel", "airport", "pharmacy", "hospital", "car_wash"]
FILTERS = ["open_now", "has_available_plug", "has_dc_plug"]
FILTER_DESC = "list of 0 to 3 filters, each " + one_of(FILTERS)[:-1] + ". \"has_available_plug\" and \"has_dc_plug\" apply only to \"charging_station\". Default is an empty list."
tool("get_location_id_by_name", "Navigation", "retrieve",
     "Look up the location ID of a city, address, or named place. Navigation, route, weather, and POI tools need this ID.",
     {"name": P("str", "free text name of the city, address, or place.", samples=["Munich", "Chico", "Sacramento International Airport", "1200 Main Street, Madison"])},
     external=True)
tool("search_poi_at_location", "Navigation", "retrieve",
     "Find points of interest of one category near a location. Results include POI IDs, distance, opening hours, phone number, and for charging stations the station ID and each plug's ID, power in kW, AC or DC type, and availability. The location ID comes from `get_location_id_by_name`.",
     {"location_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "category": P("str", one_of(POI)),
      "filters": P("list", FILTER_DESC, False, [])},
     external=True)
tool("search_poi_along_route", "Navigation", "retrieve",
     "Find points of interest of one category along a route, with the km along the route and the detour time. Results include the same details as `search_poi_at_location`. The route ID comes from `get_routes` or `get_navigation_status`.",
     {"route_id": P("str", "route ID returned by `get_routes` or `get_navigation_status`."),
      "category": P("str", one_of(POI)),
      "filters": P("list", FILTER_DESC, False, []),
      "max_detour_minutes": P("int", "integer from 1 to 30. Default is 10.", False, 10)},
     external=True)
tool("get_routes", "Navigation", "retrieve",
     "Return up to three route options between two locations with route IDs, distance, duration, toll roads, and road types. Respects the avoid-tolls and avoid-highways options. Location IDs come from `get_location_id_by_name`.",
     {"destination_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "start_id": P("str", "location ID returned by `get_location_id_by_name`. Default is \"current\", the car's current location.", False, "current")},
     reads=[f"{N}.RouteOptions.IsTollAvoided", f"{N}.RouteOptions.IsHighwayAvoided"])
tool("convert_route_distance_and_time", "Navigation", "retrieve",
     "On a given route, convert a distance in km into driving time, or a driving time in minutes into distance. The route ID comes from `get_routes` or `get_navigation_status`.",
     {"route_id": P("str", "route ID returned by `get_routes` or `get_navigation_status`."),
      "value": P("float", "number from 0.0 to 2000.0. A distance in km or a time in minutes, as set by `unit`."),
      "unit": P("str", one_of(["km", "minutes"]))},
     external=True)
NAV = [f"{N}.IsGuidanceActive", f"{N}.DestinationSet.Latitude", f"{N}.DestinationSet.Longitude", f"{N}.DestinationSet.LocationId",
       f"{N}.Waypoints.Stop1.LocationId", f"{N}.Waypoints.Stop2.LocationId", f"{N}.Waypoints.Stop3.LocationId", f"{N}.RouteId"]
tool("set_navigation", "Navigation", "action",
     "Start guidance from the current location to a destination, with up to three intermediate stops in order. Use only when guidance is not active; if it is active, use the add, replace, or delete tools instead. Location IDs come from `get_location_id_by_name`, and the route ID of the first leg from `get_routes`.",
     {"destination_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "route_id": P("str", "route ID of the first leg, returned by `get_routes`."),
      "waypoint_ids": P("list", "list of 0 to 3 location IDs from `get_location_id_by_name`, in driving order. Default is an empty list.", False, [])},
     writes=NAV)
tool("add_navigation_waypoint", "Navigation", "action",
     "Insert an intermediate stop into the active route. Only works while guidance is active and fewer than three stops are set. Call one at a time, never in parallel, because stop numbers shift.",
     {"location_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "position": P("int", "integer from 1 to 3. The stop number the new stop gets; later stops move back. Default is 1.", False, 1)},
     writes=NAV)
tool("replace_navigation_waypoint", "Navigation", "action",
     "Replace one intermediate stop of the active route with another location. Only works while guidance is active and that stop exists.",
     {"position": P("int", "integer from 1 to 3. The stop number to replace."),
      "location_id": P("str", "location ID returned by `get_location_id_by_name`.")},
     writes=NAV)
tool("delete_navigation_waypoint", "Navigation", "action",
     "Remove one intermediate stop from the active route. Only works while guidance is active and that stop exists. Call one at a time, never in parallel, because stop numbers shift.",
     {"position": P("int", "integer from 1 to 3. The stop number to remove.")},
     writes=NAV)
tool("replace_navigation_destination", "Navigation", "action",
     "Replace the final destination of the active route and keep the intermediate stops. Only works while guidance is active.",
     {"location_id": P("str", "location ID returned by `get_location_id_by_name`.")},
     writes=NAV)
tool("delete_navigation_destination", "Navigation", "action",
     "Remove the final destination so the last intermediate stop becomes the destination. Only works while guidance is active and at least one intermediate stop exists; otherwise use `cancel_navigation`.",
     writes=NAV)
tool("cancel_navigation", "Navigation", "action",
     "Stop guidance and clear the destination and all stops.",
     writes=NAV)
tool("set_route_options", "Navigation", "action",
     "Set whether route planning avoids toll roads and highways. Applies to the next `get_routes` call; an active route is not recalculated.",
     {"avoid_tolls": P("bool", "true to avoid toll roads, false to allow them."),
      "avoid_highways": P("bool", "true to avoid highways, false to allow them.")},
     writes=[f"{N}.RouteOptions.IsTollAvoided", f"{N}.RouteOptions.IsHighwayAvoided"])
tool("set_voice_guidance", "Navigation", "action",
     "Choose how much spoken navigation guidance plays: every instruction, alerts only, or none.",
     {"mode": P("str", one_of(["UNMUTED", "ALERT_ONLY", "MUTED"]))},
     writes=[f"{N}.Mute"])
tool("set_navigation_volume", "Navigation", "action",
     "Set the volume of the navigation voice, separately from the media volume.",
     {"volume_pct": P("int", "integer from 0 to 100, in steps of 5.")},
     writes=[f"{N}.Volume"])
tool("get_navigation_status", "Navigation", "retrieve",
     "Return whether guidance is active, the destination and its coordinates, intermediate stops, the current route ID, whether the destination is reached, route options, and voice guidance mode and volume.",
     reads=paths(f"{N}."))

# ---- outside-world, communication, preferences, utilities (no vehicle state)
tool("get_weather", "Weather", "retrieve",
     "Return the weather condition, temperature, humidity, and wind for a location at a time today. Only today can be requested. The location ID comes from `get_location_id_by_name`.",
     {"location_id": P("str", "location ID returned by `get_location_id_by_name`, or \"current\" for the car's current location."),
      "time": P("str", "time today as HH:MM on a 24-hour clock, or \"now\". Default is \"now\".", False, "now", samples=["now", "17:30"])},
     external=True)
tool("get_contact_id_by_name", "Communication", "retrieve",
     "Find contacts in the connected phone's address book by name and return their contact IDs.",
     {"name": P("str", "free text first name, last name, or both.", samples=["Alex", "Jordan Lee", "Dr. Patel", "Mom"])},
     external=True)
tool("get_contact_details", "Communication", "retrieve",
     "Return the phone numbers and email addresses of contacts. Contact IDs come from `get_contact_id_by_name`.",
     {"contact_ids": P("list", "list of 1 to 5 contact IDs returned by `get_contact_id_by_name`.")},
     external=True)
tool("call_phone_number", "Communication", "action",
     "Place a hands-free call through the connected phone. The number usually comes from `get_contact_details`.",
     {"phone_number": P("str", "phone number in international format.", samples=["+1 530 555 0142", "+49 89 5550 1234"])},
     external=True)
tool("send_text_message", "Communication", "action",
     "Send a short SMS through the connected phone. Read the message back and get confirmation before sending.",
     {"phone_number": P("str", "phone number in international format, usually from `get_contact_details`.", samples=["+1 530 555 0142"]),
      "message": P("str", "free text message, at most 300 characters.", samples=["Running 15 minutes late, start without me.", "Just parked, see you at the entrance."])},
     external=True)
tool("send_email", "Communication", "action",
     "Send a short email from the driver's connected account. Read the content back and get confirmation before sending. Addresses usually come from `get_contact_details`.",
     {"to": P("list", "list of 1 to 5 email addresses."),
      "subject": P("str", "free text subject line.", samples=["Running late", "Meeting notes"]),
      "body": P("str", "free text message body.", samples=["I'm stuck in traffic and will arrive around 10:20."])},
     external=True)
tool("get_calendar_events", "Communication", "retrieve",
     "Return today's calendar events with start time, duration, topic, location, and attendees. Only today can be requested.",
     {"from_hour": P("int", "integer from 0 to 23, local time. Default is 0.", False, 0)},
     external=True)
tool("get_user_preferences", "Preferences", "retrieve",
     "Return the driver's saved preferences for one category, such as preferred charging or fuel brands, route choices, or climate habits. Check them before choosing between options on the driver's behalf.",
     {"category": P("str", one_of(["points_of_interest", "navigation_and_routing", "climate", "seats", "media", "energy", "communication", "weather"]))},
     external=True)
tool("calculate_math", "Utility", "retrieve",
     "Evaluate an arithmetic expression, for example to add up distances or costs.",
     {"expression": P("str", "free text arithmetic expression using numbers, + - * / and parentheses.", samples=["(42.5 + 17.3) * 1.8", "45 * 0.62"])},
     external=True)
tool("calculate_datetime", "Utility", "retrieve",
     "Add or subtract minutes to a time, for example to work out an arrival time.",
     {"time": P("str", "time as HH:MM on a 24-hour clock, or \"now\".", samples=["now", "14:35"]),
      "add_minutes": P("int", "integer from -1440 to 1440. Negative values subtract.")},
     external=True)

# ------------------------------------------------------------------ negative tools (unchanged from v1)
NEG = json.load(open(HERE.parent / "hybrid_car" / "2026-10-11_hybrid_negative_tools_spec.json"))

# ------------------------------------------------------------------ validate
errors = []
for name, spec in {**TOOLS, **NEG}.items():
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        errors.append(f"bad name {name}")
    assert set(spec) == {"description", "domain", "kind", "parameters", "sample_commands"}
    for pn, p in spec["parameters"].items():
        if not p["required"] and "default" not in p:
            errors.append(f"{name}.{pn} missing default")
        d = p["description"]
        if p["type"] in ("int", "float") and not re.search(r"(integer|number) from -?[\d.]+ to -?[\d.]+", d):
            errors.append(f"{name}.{pn} numeric without range")
        if p["type"] == "str" and "sample_values" not in p and "one of" not in d and "ID" not in d:
            errors.append(f"{name}.{pn} str without enum or samples")
for name in TOOLS:
    t = TOOL_STATE[name]
    if t.get("external"):
        continue
    key = "writes" if TOOLS[name]["kind"] == "action" else "reads"
    if not t.get(key):
        errors.append(f"{name} missing {key}")
    for p in t.get(key, []):
        if p not in STATE:
            errors.append(f"{name}: undefined state {p}")
read = {p for t in TOOL_STATE.values() for p in t.get("reads", [])}
written = {p for t in TOOL_STATE.values() for p in t.get("writes", [])}
for p in written - read:
    errors.append(f"{p} is written but no retrieve tool reads it")
for p in set(STATE) - read - written:
    errors.append(f"{p} is unused")
# VSS conformance: ranges and enums of standard signals must sit inside what VSS allows.
for p, s in STATE.items():
    m = META[p]
    if not m["standard"]:
        continue
    if "allowed" in m and "enum" in s and not set(s["enum"]) <= set(m["allowed"]):
        errors.append(f"{p}: enum {s['enum']} outside VSS allowed {m['allowed']}")
    vals = s.get("enum", []) + [s[k] for k in ("minimum", "maximum") if k in s]
    if vals and isinstance(vals[0], (int, float)):
        if "min" in m and min(vals) < m["min"]:
            errors.append(f"{p}: {min(vals)} below VSS min {m['min']}")
        if "max" in m and max(vals) > m["max"]:
            errors.append(f"{p}: {max(vals)} above VSS max {m['max']}")
    if s["type"] == "str" and "enum" not in s and s["initial"] != "fixed":
        errors.append(f"{p}: free text state must be fixed")
for name in NEG:
    if name in TOOLS:
        errors.append(f"negative tool {name} duplicates a positive tool")
if errors:
    print("\n".join(errors))
    sys.exit(1)

# ------------------------------------------------------------------ write
OUT.mkdir(parents=True, exist_ok=True)
dump = lambda obj: json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
(OUT / f"{PREFIX}_positive_tools_spec.json").write_text(dump(TOOLS))
(OUT / f"{PREFIX}_negative_tools_spec.json").write_text(dump(NEG))
(OUT / f"{PREFIX}_state_inventory.json").write_text(dump({"state": STATE, "tools": TOOL_STATE}))
# Side-car for people and the overview page; not a pipeline input.
(OUT / f"{PREFIX}_vss_mapping.json").write_text(dump({"vss_version": VSS_VERSION, "vss_commit": VSS_COMMIT, "signals": META}))
if VSS_ALL is not None:
    REF_PATH.write_text(dump({"vss_version": VSS_VERSION, "vss_commit": VSS_COMMIT,
                              "signals": {p: VSS_ALL[p] for p in sorted(STATE) if p in VSS_ALL}}))

# Overlay with every extension, in VSS's own .vspec format.
lines = ["# VSS overlay for the plug-in hybrid assistant (v2).",
         f"# Apply on top of VSS {VSS_VERSION} (commit {VSS_COMMIT[:7]}):",
         "#   vspec export json -s spec/VehicleSignalSpecification.vspec -u spec/units.yaml -q spec/quantities.yaml -l <this file> -o out.json",
         ""]
branches = set()
for p in EXT:
    parts = p.split(".")
    for i in range(2, len(parts)):
        b = ".".join(parts[:i])
        if b not in branches and vss_lookup(b) is None and b in ("Vehicle.Powertrain.Hybrid", f"{N}.Waypoints", f"{N}.Waypoints.Stop1", f"{N}.Waypoints.Stop2", f"{N}.Waypoints.Stop3", f"{N}.RouteOptions", f"{M}.Radio"):
            branches.add(b)
            lines += [f"{b}:", "  type: branch", f"  description: {b.split('.')[-1]} signals added by the hybrid assistant overlay.", ""]
    e = EXT[p]
    lines += [f"{p}:", f"  datatype: {e['datatype']}", f"  type: {e['type']}"]
    if "unit" in e:
        lines.append(f"  unit: {e['unit']}")
    s = STATE[p]
    if "enum" in s and e["datatype"] == "string":
        lines.append("  allowed: [" + ", ".join(f"'{v}'" for v in s["enum"]) + "]")
    if "minimum" in s and e["datatype"] != "string":
        lines += [f"  min: {s['minimum']}", f"  max: {s['maximum']}"]
    lines += [f"  description: {e['description']}", ""]
(OUT / f"{PREFIX}_vss_overlay.vspec").write_text("\n".join(lines))

print("positive", len(TOOLS), Counter((t["domain"], t["kind"]) for t in TOOLS.values()))
print("negative", len(NEG), "| state", len(STATE), "standard", sum(m["standard"] for m in META.values()), "extension", len(EXT))
