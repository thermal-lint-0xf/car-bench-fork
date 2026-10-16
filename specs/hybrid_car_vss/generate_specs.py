"""Generate the hybrid-car assistant spec files (tools vss), with vehicle state named after COVESA VSS signals.

Usage:
    python generate_specs.py OUT_DIR [--vss-json FULL_VSS_EXPORT.json]

Every state value is either a standard VSS signal (checked against vss_reference.json) or an
extension declared in the overlay file this script writes (hybrid_vss_overlay.vspec).
Pass --vss-json with a full `vspec export json` of VSS to refresh vss_reference.json.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1])
PREFIX = "hybrid_vss"
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
# Written to Anthropic's tool-definition guidance
# (https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools#best-practices-for-tool-definitions):
# every description says what the tool does, when to use it and when to use a sibling instead, what each
# parameter means, the caveats, and what it returns. Parameter names carry their meaning and unit
# (percent_open, temperature_celsius, is_locked), and closely related operations share one tool.
TOOLS, TOOL_STATE = {}, {}


def tool(name, domain, kind, desc, params=None, writes=None, reads=None, external=False):
    TOOLS[name] = {"description": desc, "domain": domain, "kind": kind, "parameters": params or {}, "sample_commands": []}
    if external:
        TOOL_STATE[name] = {"external": True}
    elif kind == "action":
        TOOL_STATE[name] = {"writes": writes}
    else:
        TOOL_STATE[name] = {"reads": reads}


STOPPED = ("It only works while the car is stopped in park (`Vehicle.Speed` is 0 and `Vehicle.Powertrain.Transmission.SelectedGear` is 126); "
           "otherwise it returns an error, and the assistant should tell the driver why instead of retrying.")
MOVING = "It returns an error while the car is moving (`Vehicle.Speed` above 0)."
WEATHER = "Check the weather with `get_weather` first."
SEAT4 = list(SIDES) + ["all"]
SEATS = one_of(SEAT4) + " \"row1_driver_side\" is the driver's seat, \"row1_passenger_side\" the front passenger's, and \"row2_...\" the back seat; \"all\" covers all four."
FRONTS = lambda extra: one_of(FRONT + extra) + " \"row1_driver_side\" is the driver's seat."
RETURNS_NEW = "Returns the new value of every setting it changed."

# ---- windows, sunroof, shades
tool("set_window_position", "Vehicle", "action",
     "Opens or closes one side window, or all four, to an exact opening in percent. Use it for any request to open, close, crack, or lower a window; "
     "use `set_sunroof_position` for the roof and `set_rear_window_shade_position` for the rear sun shade. "
     "Policy: if air conditioning is on and a window would open beyond 25 percent, warn about wasted energy and ask for confirmation first. "
     + RETURNS_NEW,
     {"windows": P("str", one_of(SEAT4) + " \"row1_driver_side\" is the driver's window; \"all\" moves all four to the same opening."),
      "percent_open": P("int", "integer from 0 to 100, in steps of 5. 0 is fully closed and 100 fully open; for \"open a bit\" use 20. Default is 100.", False, 100)},
     writes=sel(r"Window\.Position$"))
tool("set_window_child_lock_state", "Vehicle", "action",
     "Enables or disables the rear window child lock, which stops rear passengers from moving their windows with their own switches. "
     "Use it when the driver wants to keep children from opening the rear windows. The driver can still move every window with `set_window_position` while the lock is on. "
     "It does not lock the doors; use `set_door_lock_state` for that. " + RETURNS_NEW,
     {"enabled": P("bool", "true disables the rear window switches, false lets rear passengers use them again.")},
     writes=[f"{C}.IsWindowChildLockEngaged"])
tool("get_window_positions", "Vehicle", "retrieve",
     "Returns the opening of each of the four side windows in percent (0 closed, 100 fully open) and whether the rear window child lock is on. "
     "Use it before relative requests such as \"open it a bit more\", or to answer whether any window is open. "
     "It does not cover the sunroof, the sunroof shade, or the rear window shade; use `get_sunroof_and_shade_position` and `get_rear_window_shade_position`.",
     reads=sel(r"Window\.Position$") + [f"{C}.IsWindowChildLockEngaged"])
tool("set_sunroof_shade_position", "Vehicle", "action",
     "Opens or closes the sliding shade under the glass sunroof, to let light in or block it. "
     "The shade cannot close below 100 percent while the sunroof itself is open, so close the sunroof first with `set_sunroof_position`. "
     "Opening the sunroof needs this shade at 100 percent, so call this first when the driver asks to open the roof. " + RETURNS_NEW,
     {"percent_open": P("int", "integer from 0 to 100, in steps of 5. 0 is fully closed and 100 fully open. Default is 100.", False, 100)},
     writes=[f"{C}.Sunroof.Shade.Position"])
tool("set_sunroof_position", "Vehicle", "action",
     "Slides the glass sunroof open or closed, or tilts its rear edge up for ventilation. "
     "Sliding it open returns an error unless the sunroof shade is at 100 percent or is opened to 100 with `set_sunroof_shade_position` in the same turn; tilting needs no shade. "
     + WEATHER + " If the condition is not \"clear\", \"sunny\", \"partly_cloudy\", or \"cloudy\", get an explicit yes from the driver before sliding or tilting it open. "
     "Returns the new sunroof position, where negative values mean tilted.",
     {"opening_style": P("str", one_of(["slide", "tilt"]) + " \"slide\" moves the glass back; \"tilt\" only raises its rear edge. Default is \"slide\".", False, "slide"),
      "percent_open": P("int", "integer from 0 to 100, in steps of 5. How far to slide or tilt; 0 closes the sunroof in either style. Default is 100.", False, 100)},
     writes=[f"{C}.Sunroof.Position"])
tool("get_sunroof_and_shade_position", "Vehicle", "retrieve",
     "Returns the sunroof position (0 closed, 100 fully slid open, negative values tilted, -100 fully tilted) and the sunroof shade opening in percent. "
     "They come together because the sunroof can only slide open when the shade is fully open. "
     "Use it before opening the sunroof or to answer whether the roof is open. It does not cover the side windows; use `get_window_positions`.",
     reads=[f"{C}.Sunroof.Position", f"{C}.Sunroof.Shade.Position"])
tool("set_rear_window_shade_position", "Vehicle", "action",
     "Raises or lowers the sun shade on the rear window, for example to block low sun or keep the back seat private. "
     "This is the shade behind the rear seats, not the sunroof shade, which `set_sunroof_shade_position` controls. "
     "It works while driving. " + RETURNS_NEW,
     {"percent_raised": P("int", "integer from 0 to 100, in steps of 10. 0 is fully lowered out of sight and 100 fully raised. Default is 100.", False, 100)},
     writes=[f"{C}.RearShade.Position"])
tool("get_rear_window_shade_position", "Vehicle", "retrieve",
     "Returns how far the rear window sun shade is raised, in percent (0 lowered, 100 fully raised). "
     "Use it before relative requests such as \"raise it a bit more\" or to answer whether the shade is up. "
     "It does not cover the sunroof shade; use `get_sunroof_and_shade_position`.",
     reads=[f"{C}.RearShade.Position"])

# ---- doors and access
tool("set_door_lock_state", "Vehicle", "action",
     "Locks or unlocks one door or all four doors. Use it when the driver asks to lock or unlock the car or a single door. "
     "Unlocking " + MOVING[3:] + " "
     "It does not change the trunk lock (`set_trunk_lock_state`) or the rear child safety locks, which are mechanical switches the assistant cannot move. " + RETURNS_NEW,
     {"doors": P("str", one_of(SEAT4) + " \"row1_driver_side\" is the driver's door and \"row2_...\" the back doors; \"all\" covers all four. Default is \"all\".", False, "all"),
      "is_locked": P("bool", "true locks the doors, false unlocks them.")},
     writes=sel(r"Door\.Row\d\.\w+\.IsLocked$"))
tool("get_door_status", "Vehicle", "retrieve",
     "Returns, for each of the four doors, whether it is locked, and for the two rear doors whether the child safety lock is engaged. "
     "Use it to answer whether the car is locked or before unlocking. "
     "Child safety locks are mechanical switches on the door edge, so the assistant can report them but cannot change them; tell the driver to set them by hand. "
     "It does not cover the trunk; use `get_trunk_status`.",
     reads=sel(r"Door\.Row\d\.\w+\.IsLocked$", r"IsChildLockActive$"))
tool("set_trunk_lid_state", "Vehicle", "action",
     "Opens or closes the power trunk lid. " + STOPPED + " "
     "It does not lock or unlock the trunk; use `set_trunk_lock_state` for that. " + RETURNS_NEW,
     {"is_open": P("bool", "true opens the trunk lid, false closes it.")},
     writes=["Vehicle.Body.Trunk.Rear.IsOpen"])
tool("set_trunk_lock_state", "Vehicle", "action",
     "Locks or unlocks the trunk on its own, independently of the doors, for example to keep valet staff out of the trunk. "
     "It does not open the lid; use `set_trunk_lid_state` for that. "
     "Locking the doors with `set_door_lock_state` does not change this setting. " + RETURNS_NEW,
     {"is_locked": P("bool", "true locks the trunk, false unlocks it.")},
     writes=["Vehicle.Body.Trunk.Rear.IsLocked"])
tool("get_trunk_status", "Vehicle", "retrieve",
     "Returns whether the trunk lid is open and whether the trunk is locked. "
     "Use it before opening or closing the trunk, or to answer whether the trunk is open. "
     "It does not cover the doors; use `get_door_status`.",
     reads=["Vehicle.Body.Trunk.Rear.IsOpen", "Vehicle.Body.Trunk.Rear.IsLocked"])
tool("set_fuel_door_state", "Vehicle", "action",
     "Opens or closes the fuel filler door so the driver can refuel. " + STOPPED + " "
     "It is not the charging port door; use `set_charge_port_door_state` for plug-in charging. " + RETURNS_NEW,
     {"is_open": P("bool", "true opens the fuel filler door, false closes it.")},
     writes=["Vehicle.Powertrain.FuelSystem.IsFuelPortFlapOpen"])
tool("get_fuel_door_status", "Vehicle", "retrieve",
     "Returns whether the fuel filler door is open. "
     "Use it before refueling or to answer whether the fuel door was left open. "
     "It does not report the fuel level; use `get_energy_status`.",
     reads=["Vehicle.Powertrain.FuelSystem.IsFuelPortFlapOpen"])
tool("set_charge_port_door_state", "Vehicle", "action",
     "Opens or closes the charging port door on the front-left fender so the driver can plug in. " + STOPPED + " "
     "It is not the fuel filler door; use `set_fuel_door_state` for refueling. " + RETURNS_NEW,
     {"is_open": P("bool", "true opens the charging port door, false closes it.")},
     writes=[f"{CHARGE_PORT}.IsFlapOpen"])
tool("set_charging_cable_lock_state", "Vehicle", "action",
     "Locks the charging cable into the port or releases it. "
     "Release it before the driver unplugs; lock it to stop someone else pulling the cable at a public charger. "
     "It returns an error when no cable is connected (`get_charge_port_status`). " + RETURNS_NEW,
     {"is_locked": P("bool", "true locks the cable in the port, false releases it.")},
     writes=[f"{CHARGE_PORT}.IsChargingCableLocked"])
tool("get_charge_port_status", "Vehicle", "retrieve",
     "Returns whether the charging port door is open, whether a charging cable is plugged in, and whether the cable is locked. "
     "Use it before starting charging or releasing the cable. "
     "It does not report the battery level or charging progress; use `get_energy_status` and `get_charging_status`.",
     reads=paths(CHARGE_PORT))

# ---- exterior lights
tool("set_headlight_beam_state", "Vehicle", "action",
     "Turns the low beam or the high beam headlights on or off. "
     "Turning the high beams on returns an error while the front fog lights are on, and turning the low beams off returns an error while the front fog lights are on. "
     "Use `set_fog_light_state` for fog lights and `set_hazard_lights_state` for hazard lights. " + RETURNS_NEW,
     {"beam": P("str", one_of(["low", "high"]) + " \"low\" is the normal driving light; \"high\" is the long-range main beam."),
      "enabled": P("bool", "true turns the beam on, false turns it off.")},
     writes=[f"{B}.Lights.Beam.Low.IsOn", f"{B}.Lights.Beam.High.IsOn"])
tool("set_fog_light_state", "Vehicle", "action",
     "Turns the front fog lights, the rear fog light, or both on or off. "
     "Policy: when turning the front fog lights on, also make sure the low beams are on and the high beams are off with `set_headlight_beam_state`. "
     + WEATHER + " If the condition is not \"fog\", \"heavy_rain\", \"snow\", or \"storm\", get an explicit yes from the driver before turning any fog light on. " + RETURNS_NEW,
     {"fog_lights": P("str", one_of(["front", "rear", "both"])),
      "enabled": P("bool", "true turns the chosen fog lights on, false turns them off.")},
     writes=[f"{B}.Lights.Fog.Front.IsOn", f"{B}.Lights.Fog.Rear.IsOn"])
tool("set_hazard_lights_state", "Vehicle", "action",
     "Starts or stops the hazard warning lights, which flash all turn signals at once. "
     "Use it when the driver asks for hazards, for example after stopping on the shoulder or at the end of a traffic jam. "
     "It does not change the headlights or fog lights. " + RETURNS_NEW,
     {"enabled": P("bool", "true starts flashing, false stops it.")},
     writes=[f"{B}.Lights.Hazard.IsSignaling"])
tool("get_exterior_lights_status", "Vehicle", "retrieve",
     "Returns whether the low beams, high beams, front fog lights, rear fog light, and hazard lights are on. "
     "Use it before changing any exterior light, because the fog lights restrict the headlight beams. "
     "It does not cover interior lights; use `get_reading_lights_status` and `get_ambient_light_status`.",
     reads=paths(f"{B}.Lights."))

# ---- wipers and mirrors
tool("set_wiper_mode", "Vehicle", "action",
     "Sets the mode of the front or the rear windshield wiper, and for the front wiper how often it wipes in interval or rain-sensor mode. "
     "Use it for requests to start, stop, speed up, or slow down the wipers. The rear wiper supports only \"OFF\", \"INTERVAL\", and \"SLOW\" and returns an error for other modes. "
     "It does not spray washer fluid. " + RETURNS_NEW,
     {"wiper": P("str", one_of(["front", "rear"])),
      "wiper_mode": P("str", one_of(WIPE) + " \"RAIN_SENSOR\" wipes automatically when rain is detected."),
      "interval_level": P("int", "integer from 1 to 4. How often the front wiper wipes in \"INTERVAL\" mode, or how sensitive it is in \"RAIN_SENSOR\" mode; 4 is most frequent. Default is 2. Ignored for other modes and for the rear wiper.", False, 2)},
     writes=sel(r"Wiping\.(Mode|Intensity)$"))
tool("get_wiper_status", "Vehicle", "retrieve",
     "Returns the front and rear wiper modes and the front wiper interval level. "
     "Use it before relative requests such as \"wipe faster\". "
     "It does not report the washer fluid level; use `get_maintenance_status`.",
     reads=sel(r"Wiping\.(Mode|Intensity)$"))
tool("set_side_mirror_fold_state", "Vehicle", "action",
     "Folds both exterior side mirrors in against the car, or unfolds them for driving. "
     "Use it for tight parking spots or car washes. Folding " + MOVING[3:] + " " + RETURNS_NEW,
     {"is_folded": P("bool", "true folds both mirrors in, false unfolds them.")},
     writes=sel(r"Mirrors\.\w+\.IsFolded$"))
tool("set_side_mirror_heating_state", "Vehicle", "action",
     "Turns heating on or off in both exterior side mirrors, to clear ice, frost, or fog from the glass. "
     "Use it in cold or damp weather or when the driver says the mirrors are fogged. "
     "It does not defrost the windshield; use `set_defroster_state`. " + RETURNS_NEW,
     {"enabled": P("bool", "true turns mirror heating on, false turns it off.")},
     writes=sel(r"Mirrors\.\w+\.IsHeatingOn$"))
tool("get_side_mirror_status", "Vehicle", "retrieve",
     "Returns, for the driver-side and passenger-side mirrors, whether each is folded and whether its heating is on. "
     "Use it before folding the mirrors or to answer whether mirror heating is on. "
     "It does not return mirror angles.",
     reads=paths(f"{B}.Mirrors."))

# ---- interior lights
tool("set_reading_light_state", "Vehicle", "action",
     "Turns the reading light above one seat, or above all seats, on or off. "
     "Use it for requests to switch on a light to read or find something; use `set_ambient_light` for the mood lighting along the doors and dashboard. "
     "When the driver says only \"my light\", use \"row1_driver_side\". " + RETURNS_NEW,
     {"seats": P("str", SEATS),
      "enabled": P("bool", "true turns the reading light on, false turns it off.")},
     writes=sel(r"Spotlight\..*IsLightOn$"))
tool("get_reading_lights_status", "Vehicle", "retrieve",
     "Returns, for each of the four seats, whether its reading light is on. "
     "Use it to answer which lights are on or before turning them off. "
     "It does not cover the ambient light; use `get_ambient_light_status`.",
     reads=sel(r"Spotlight\..*IsLightOn$"))
tool("set_ambient_light", "Vehicle", "action",
     "Turns the ambient mood lighting on or off and sets its color and brightness in all four zones at once. "
     "Use it for requests about the cabin's mood or accent lighting; use `set_reading_light_state` for lights to read by. "
     "Colors are stored as RGB codes: " + ", ".join(f"{n} {h}" for n, h in AMBIENT.items()) + ". " + RETURNS_NEW,
     {"enabled": P("bool", "true turns the ambient light on, false turns it off."),
      "color": P("str", one_of(list(AMBIENT)) + " Default is \"white\". Ignored when enabled is false.", False, "white"),
      "brightness_percent": P("int", "integer from 10 to 100, in steps of 10. Default is 70. Ignored when enabled is false.", False, 70)},
     writes=paths(f"{C}.Light.AmbientLight."))
tool("get_ambient_light_status", "Vehicle", "retrieve",
     "Returns, for each of the four ambient light zones, whether it is on, its color as an RGB code, and its brightness in percent. "
     "Use it before relative requests such as \"make it a bit brighter\". "
     "It does not cover the reading lights; use `get_reading_lights_status`.",
     reads=paths(f"{C}.Light.AmbientLight."))

# ---- climate
ZONES = list(STATIONS) + ["row2", "all"]
ZONEDESC = one_of(ZONES) + " \"row1_driver\" is the driver's zone, \"row1_passenger\" the front passenger's, \"row2\" both back-seat zones, and \"all\" every zone."
AIRFLOW = {"windshield": "UP", "face": "MIDDLE", "feet": "DOWN"}
tool("set_climate_temperature", "Vehicle", "action",
     "Sets the target cabin temperature for one climate zone, both back-seat zones, or every zone. "
     "Use it for requests to make it warmer or colder; for a relative request, read the current target with `get_climate_status` and change it by 1 to 2 degrees. "
     "Policy: if the result leaves more than 3 degrees between zones, tell the driver. "
     "It does not turn air conditioning on or change the fan. " + RETURNS_NEW,
     {"zones": P("str", ZONEDESC),
      "temperature_celsius": P("float", "number from 16.0 to 28.0, in steps of 0.5.")},
     writes=sel(r"Station\..*\.Temperature$"))
tool("set_fan_speed", "Vehicle", "action",
     "Sets how hard the climate fan blows in one zone or in every zone. "
     "Use it for requests about airflow strength such as \"more air\" or \"turn the fan down\". Setting a fan level switches climate auto mode off. "
     "It does not change temperature or direction; use `set_climate_temperature` and `set_airflow_direction`. " + RETURNS_NEW,
     {"zones": P("str", ZONEDESC + " Default is \"all\".", False, "all"),
      "fan_level": P("int", "integer from 0 to 5. 0 turns the fan off and 5 is the strongest; each level is 20 percent fan speed.")},
     writes=sel(r"Station\..*\.FanSpeed$") + [f"{H}.IsAutoModeActive"])
tool("set_airflow_direction", "Vehicle", "action",
     "Sets where the climate air comes out in one zone or in every zone: onto the windshield, at the face, or at the feet. "
     "Use it for requests such as \"blow on my feet\" or \"air on the windshield\". Setting a direction switches climate auto mode off. "
     "To clear a fogged windshield, prefer `set_defroster_state`, which also handles fan and air conditioning. " + RETURNS_NEW,
     {"zones": P("str", ZONEDESC + " Default is \"all\".", False, "all"),
      "airflow_direction": P("str", one_of(list(AIRFLOW)) + " These are stored as the VSS values \"UP\", \"MIDDLE\", and \"DOWN\".")},
     writes=sel(r"Station\..*\.AirDistribution$") + [f"{H}.IsAutoModeActive"])
tool("set_air_conditioning_state", "Vehicle", "action",
     "Turns the air conditioning compressor on or off. AC cools and dries the air; the temperature itself comes from `set_climate_temperature`. "
     "Policy: when turning AC on, also close any window open beyond 20 percent with `set_window_position` and raise the fan to level 1 with `set_fan_speed` if it is off. "
     "Turning AC off saves energy and battery range. " + RETURNS_NEW,
     {"enabled": P("bool", "true turns air conditioning on, false turns it off.")},
     writes=[f"{H}.IsAirConditioningActive"])
tool("set_air_recirculation_state", "Vehicle", "action",
     "Switches between recirculating the cabin air and drawing in fresh outside air. "
     "Use recirculation when the driver mentions bad smells, exhaust, or dust outside, or to cool down faster; use fresh air when the windows fog up or the air feels stale. "
     "It does not change fan speed or temperature. " + RETURNS_NEW,
     {"enabled": P("bool", "true recirculates cabin air, false draws in fresh outside air.")},
     writes=[f"{H}.IsRecirculationActive"])
tool("set_defroster_state", "Vehicle", "action",
     "Turns the front windshield defroster, the rear window defroster, or both on or off, to clear fog, frost, or ice from the glass. "
     "Policy: when turning on the front defroster, also set fan level 2 or higher with `set_fan_speed`, set the front zones' airflow to \"windshield\" with `set_airflow_direction`, and turn on air conditioning with `set_air_conditioning_state`. "
     "It does not heat the side mirrors; use `set_side_mirror_heating_state`. " + RETURNS_NEW,
     {"defrosters": P("str", one_of(["front", "rear", "both"])),
      "enabled": P("bool", "true turns the chosen defrosters on, false turns them off.")},
     writes=[f"{H}.IsFrontDefrosterActive", f"{H}.IsRearDefrosterActive"])
tool("set_climate_auto_mode_state", "Vehicle", "action",
     "Turns climate auto mode on or off. In auto mode the car chooses fan speed and airflow direction to reach the target temperatures. "
     "Use it when the driver asks the car to handle the climate itself, or to undo manual fan and airflow changes. "
     "It does not change target temperatures or air conditioning. " + RETURNS_NEW,
     {"enabled": P("bool", "true turns auto mode on, false keeps the current manual fan and airflow settings.")},
     writes=[f"{H}.IsAutoModeActive"])
tool("get_climate_status", "Vehicle", "retrieve",
     "Returns the whole climate setup: auto mode, each zone's target temperature, fan speed in percent, and airflow direction, plus air conditioning, recirculation, and both defrosters. "
     "It also returns the measured cabin temperature and the outside temperature and humidity. "
     "Use it before any relative climate request or to answer how warm it is inside or outside. It does not cover seat or steering wheel heating; use `get_seat_status`.",
     reads=paths(f"{H}.") + ["Vehicle.Exterior.AirTemperature", "Vehicle.Exterior.Humidity"])

# ---- seats and steering wheel
tool("set_seat_heating_cooling", "Vehicle", "action",
     "Heats or ventilates (cools) one seat or all seats, or turns both off. "
     "Heating and ventilation share one setting per seat, so a seat never heats and cools at once; choosing one replaces the other. "
     "Only the front seats ventilate, so \"ventilate\" returns an error for back seats. Use `set_steering_wheel_heating_level` for the steering wheel. " + RETURNS_NEW,
     {"seats": P("str", SEATS),
      "climate_mode": P("str", one_of(["heat", "ventilate", "off"])),
      "intensity_level": P("int", "integer from 1 to 3. 1 is gentle and 3 the strongest; levels are stored as 33, 66, and 100 percent, negative when ventilating. Default is 2. Ignored when climate_mode is \"off\".", False, 2)},
     writes=sel(r"Seat\.Row\d\.\w+\.HeatingCooling$"))
tool("set_seat_massage", "Vehicle", "action",
     "Starts, changes, or stops the massage in one or both front seats. Only the front seats have massage. "
     "Use it when the driver or front passenger asks for a massage or says their back is tired. "
     "Massage works while driving. " + RETURNS_NEW,
     {"seats": P("str", FRONTS(["both"])),
      "massage_program": P("str", one_of(["WAVE", "PULSE", "STRETCH", "LUMBAR"]) + " \"LUMBAR\" targets the lower back. Default is \"WAVE\".", False, "WAVE"),
      "intensity_level": P("int", "integer from 0 to 3. 0 stops the massage and 3 is the strongest; levels are stored as 0, 33, 66, and 100 percent.")},
     writes=sel(r"Massage\.(Level|TypeActive)$"))
tool("set_seat_fore_aft_position", "Vehicle", "action",
     "Moves a front seat forward or backward along its rail. "
     "For a relative request such as \"move my seat back a bit\", read the current position with `get_seat_status` and move it by about 30 mm. "
     "Moving the driver's seat " + MOVING[3:] + " To restore a saved driver position, use `recall_driver_seat_memory`. " + RETURNS_NEW,
     {"seats": P("str", FRONTS([])),
      "distance_from_front_mm": P("int", "integer from 0 to 250, in steps of 10. 0 is the seat's frontmost position; larger values move it back.")},
     writes=sel(r"Row1\.\w+\.Position$"))
tool("set_seat_recline", "Vehicle", "action",
     "Changes how far a front seat's backrest leans back. "
     "For a relative request such as \"lean back a little\", read the current angle with `get_seat_status` and change it by about 5 degrees. "
     "Changing the driver's seat " + MOVING[3:] + " " + RETURNS_NEW,
     {"seats": P("str", FRONTS([])),
      "recline_degrees": P("int", "integer from 0 to 40. Degrees back from upright; 0 is upright and about 25 is a relaxed position.")},
     writes=sel(r"Backrest\.Recline$"))
tool("recall_driver_seat_memory", "Vehicle", "action",
     "Moves the driver's seat to one of three saved memory positions, setting both its fore-aft position and recline. "
     "Use it when the driver asks for \"my seat position\" or names a profile number. " + MOVING + " "
     "It does not save a new memory position. Returns the recalled profile and the new seat position and recline.",
     {"profile_number": P("int", "integer from 1 to 3.")},
     writes=[f"{C}.Seat.Row1.DriverSide.MemoryProfile", f"{C}.Seat.Row1.DriverSide.Position", f"{C}.Seat.Row1.DriverSide.Backrest.Recline"])
tool("set_steering_wheel_heating_level", "Vehicle", "action",
     "Sets the steering wheel heating level, or turns it off. "
     "Use it when the driver says their hands or the wheel are cold. The wheel only heats; it cannot cool. " + RETURNS_NEW,
     {"heating_level": P("int", "integer from 0 to 3. 0 is off and 3 the warmest; levels are stored as 0, 33, 66, and 100 percent.")},
     writes=["Vehicle.Chassis.SteeringWheel.HeatingCooling"])
tool("get_seat_status", "Vehicle", "retrieve",
     "Returns each seat's occupancy and heating or ventilation level (positive values heat, negative values cool), the front seats' massage program and level, fore-aft position, and recline, the last recalled driver memory profile, and the steering wheel heating level. "
     "Use it before any relative seat request, or to check which seats are occupied before turning on heating for passengers. "
     "It does not cover cabin air temperature; use `get_climate_status`.",
     reads=paths(f"{C}.Seat.") + ["Vehicle.Chassis.SteeringWheel.HeatingCooling"])

# ---- media
tool("set_media_volume", "Media", "action",
     "Sets the volume of music, radio, and podcasts. Setting any volume also unmutes the audio. "
     "For a relative request such as \"a bit louder\", read the current volume with `get_media_status` and change it by about 10. "
     "It does not change the navigation voice; use `set_navigation_voice_volume`. " + RETURNS_NEW,
     {"volume_percent": P("int", "integer from 0 to 100.")},
     writes=[f"{M}.Volume", f"{M}.IsMuted"])
tool("set_media_mute_state", "Media", "action",
     "Mutes or unmutes music, radio, and podcasts while keeping the volume setting. "
     "Use it for quick silence, for example during a phone call or a conversation, so the previous volume comes back on unmute. "
     "It does not pause playback; use `control_media_playback`. " + RETURNS_NEW,
     {"is_muted": P("bool", "true mutes the audio, false unmutes it at the previous volume.")},
     writes=[f"{M}.IsMuted"])
tool("set_media_source", "Media", "action",
     "Switches the audio source, for example from FM radio to the phone over Bluetooth, and keeps playing. "
     "Use it when the driver names a source. To play a specific song or artist, use `play_media_by_query`; to tune a radio station, use `tune_fm_radio`. "
     + RETURNS_NEW,
     {"media_source": P("str", one_of(SOURCES) + " \"INTERNET\" is the built-in streaming service and \"BLUETOOTH\" the connected phone.")},
     writes=[f"{M}.Played.Source", f"{M}.Action"])
tool("control_media_playback", "Media", "action",
     "Plays, pauses, or skips forward or back on the current audio source. "
     "Use it for requests such as \"pause\", \"resume\", \"next song\", or \"go back one track\". Skipping returns an error on \"FM\", \"AM\", and \"DAB\" radio, which have no tracks. "
     "It does not change the source or volume. " + RETURNS_NEW,
     {"playback_command": P("str", one_of(["play", "pause", "next_track", "previous_track"]) + " Skipping keeps playback running.")},
     writes=[f"{M}.Action"])
tool("tune_fm_radio", "Media", "action",
     "Tunes the FM radio to a frequency and switches the audio source to FM. "
     "Use it when the driver names an FM frequency; if they name a station instead, ask for its frequency. "
     "It does not tune AM or DAB. " + RETURNS_NEW,
     {"frequency_mhz": P("float", "number from 87.5 to 108.0, in steps of 0.1.")},
     writes=[f"{M}.Radio.FMFrequency", f"{M}.Played.Source", f"{M}.Action"])
tool("play_media_by_query", "Media", "action",
     "Searches the built-in streaming service for a song, artist, album, playlist, or podcast and starts playing the best match. "
     "It switches the audio source to \"INTERNET\". Use it whenever the driver names what to hear rather than a source or a radio frequency. "
     "Returns the identifier of the item it started playing; if nothing matches, it returns an error and playback continues unchanged.",
     {"search_query": P("str", "free text naming what to play, as the driver said it.", samples=["Bohemian Rhapsody", "Norah Jones", "lo-fi focus playlist", "the latest episode of a daily news podcast"]),
      "media_type": P("str", one_of(["any", "song", "artist", "album", "playlist", "podcast"]) + " Narrow it when the driver says which kind; \"any\" lets the service decide. Default is \"any\".", False, "any")},
     writes=[f"{M}.SelectedURI", f"{M}.Played.Source", f"{M}.Action"])
tool("get_media_status", "Media", "retrieve",
     "Returns the audio source, whether it is playing or paused, the volume in percent, whether it is muted, the tuned FM frequency, and the identifier of the last item chosen by search. "
     "Use it before relative volume requests or to answer what is playing. "
     "It does not return the navigation voice volume; use `get_navigation_status`.",
     reads=paths(f"{M}."))

# ---- driving, tires, maintenance, trip
tool("get_driving_status", "Vehicle", "retrieve",
     "Returns the current speed in km/h, the selected gear (126 park, 127 drive, 0 neutral, -1 reverse), and the odometer in meters. "
     "Use it to check whether the car is stopped in park before actions that need it, such as opening the trunk, fuel door, or charge port. "
     "It does not return trip figures; use `get_trip_info`.",
     reads=["Vehicle.Speed", "Vehicle.Powertrain.Transmission.SelectedGear", "Vehicle.TraveledDistance"])
tool("get_tire_pressure", "Vehicle", "retrieve",
     "Returns each tire's pressure in kPa and whether it has a low-pressure warning (below 200 kPa; 230 to 250 is recommended). "
     "Use it when the driver asks about the tires or a tire warning. "
     "It does not return tire temperature or tread depth.",
     reads=sel(r"Tire\.(Pressure|IsPressureLow)$"))
tool("get_maintenance_status", "Vehicle", "retrieve",
     "Returns the distance to the next scheduled service in km and whether service is due, the engine oil level, the washer fluid level in percent, and the 12 V battery voltage. "
     "Use it for questions about service, warning lights, oil, washer fluid, or a weak starter battery. "
     "It does not report tire pressure (`get_tire_pressure`) or fuel and battery range (`get_energy_status`).",
     reads=["Vehicle.Service.DistanceToService", "Vehicle.Service.IsServiceDue", "Vehicle.Powertrain.CombustionEngine.EngineOil.Level",
            f"{B}.Windshield.Front.WasherFluid.Level", "Vehicle.LowVoltageBattery.CurrentVoltage"])
tool("get_trip_info", "Vehicle", "retrieve",
     "Returns the trip meter in meters, the trip duration in seconds, the average speed in km/h, and the average fuel consumption in liters per 100 km. "
     "Use it for questions about the current trip, such as how far or how long the driver has driven. "
     "It does not return the odometer; use `get_driving_status`.",
     reads=["Vehicle.TripMeterReading", "Vehicle.TripDuration", "Vehicle.AverageSpeed", f"{PT}.FuelSystem.AverageConsumption"])
tool("reset_trip_meter", "Vehicle", "action",
     "Resets the trip meter to zero to start measuring a new trip. "
     "The old trip distance is lost, so ask the driver to confirm first. "
     "It does not reset the odometer or the average fuel consumption. Returns the new trip meter reading, which is 0.",
     writes=["Vehicle.TripMeterReading"])
tool("get_vehicle_specs", "Vehicle", "retrieve",
     "Returns fixed facts about this car: exterior color, powertrain type (hybrid) and hybrid type (plug-in), fuel tank capacity in liters, usable battery capacity in kWh, and maximum AC and DC charging power in kW. "
     "Use it for questions about what the car is or can do, or before estimates that depend on capacities. "
     "It does not return current levels; use `get_energy_status`.",
     reads=["Vehicle.VehicleIdentification.VehicleExteriorColor", f"{PT}.Type", f"{PT}.FuelSystem.HybridType", f"{PT}.FuelSystem.TankCapacity",
            f"{PT}.TractionBattery.NetCapacity", f"{CH}.MaxAcceptedPowerAC", f"{CH}.MaxAcceptedPowerDC"])

# ---- energy
ENERGY = [f"{PT}.FuelSystem.RelativeLevel", f"{PT}.FuelSystem.IsFuelLevelLow", f"{PT}.TractionBattery.StateOfCharge.Displayed",
          f"{PT}.FuelSystem.TankCapacity", f"{PT}.TractionBattery.NetCapacity",
          f"{PT}.RangeExtender.ChargeDepleting.EnergyConsumption", f"{PT}.FuelSystem.AverageConsumption"]
tool("get_energy_status", "Energy", "retrieve",
     "Returns the battery level and fuel level in percent, the low-fuel warning, and the electric, fuel, and combined range in km, computed from those levels and the reference consumption. "
     "It also returns the hybrid mode and how the hybrid is currently running, the drive mode, the regenerative braking level, the hybrid charge target, and whether the engine is running. "
     "Use it for any question about range, battery, fuel, or driving modes, and before changing a mode. It does not return plug-in charging settings; use `get_charging_status`.",
     reads=ENERGY + [f"{PT}.Hybrid.Mode", f"{PT}.Hybrid.ChargeTarget", f"{PT}.Hybrid.RegenLevel", f"{PT}.RangeExtender.OperatingMode",
                     f"{PT}.Transmission.PerformanceMode", f"{PT}.CombustionEngine.IsRunning"])
tool("set_hybrid_mode", "Energy", "action",
     "Chooses how the plug-in hybrid uses its battery and engine. "
     "\"AUTO\" blends both; \"ELECTRIC\" drives on the battery only and returns an error when the battery is below 10 percent; \"HOLD\" saves the current battery level for later, for example for a low-emission zone at the destination; \"CHARGE\" runs the engine to charge the battery up to `charge_target_percent`. "
     "Policy: when choosing \"CHARGE\", warn that fuel consumption rises. Returns the new hybrid mode, charge target, and whether the engine is running.",
     {"hybrid_mode": P("str", one_of(["AUTO", "ELECTRIC", "HOLD", "CHARGE"])),
      "charge_target_percent": P("int", "integer from 20 to 80, in steps of 10. The battery level the engine charges up to. Default is 60. Used only when hybrid_mode is \"CHARGE\".", False, 60)},
     writes=[f"{PT}.Hybrid.Mode", f"{PT}.Hybrid.ChargeTarget", f"{PT}.RangeExtender.OperatingMode", f"{PT}.CombustionEngine.IsRunning"])
tool("set_drive_mode", "Energy", "action",
     "Sets the drive mode, which changes throttle response, gear shifts, and efficiency. "
     "Use \"ECONOMY\" when the driver wants to save fuel or battery, \"SPORT\" for sharper response, and \"NORMAL\" to go back to the default. "
     "It does not change how the hybrid uses battery and engine; use `set_hybrid_mode`. " + RETURNS_NEW,
     {"drive_mode": P("str", one_of(["NORMAL", "SPORT", "ECONOMY"]))},
     writes=[f"{PT}.Transmission.PerformanceMode"])
tool("set_regen_braking_level", "Energy", "action",
     "Sets how strongly the car slows down and recovers energy when the driver lifts off the accelerator. "
     "Higher levels recover more energy and allow near one-pedal driving; level 0 lets the car coast. "
     "It does not affect the brake pedal. " + RETURNS_NEW,
     {"regen_level": P("int", "integer from 0 to 3. 0 coasts freely and 3 slows down the most.")},
     writes=[f"{PT}.Hybrid.RegenLevel"])
tool("get_charging_status", "Energy", "retrieve",
     "Returns whether the battery is charging from a cable, the charge limit in percent, the charging timer mode and time, and the car's maximum AC and DC charging power in kW. "
     "Use it before changing charging settings or to answer whether the car is charging. "
     "It does not return the battery level (`get_energy_status`) or the cable state (`get_charge_port_status`).",
     reads=[f"{CH}.IsCharging", f"{CH}.ChargeLimit", f"{CH}.Timer.Mode", f"{CH}.Timer.Time", f"{CH}.MaxAcceptedPowerAC", f"{CH}.MaxAcceptedPowerDC"])
tool("set_charge_limit", "Energy", "action",
     "Sets the battery level at which plug-in charging stops. "
     "A limit of about 80 percent is gentler on the battery for daily use; 100 percent gives full range before a long trip. "
     "It does not start charging; use `set_charging_state`. " + RETURNS_NEW,
     {"charge_limit_percent": P("int", "integer from 50 to 100, in steps of 5.")},
     writes=[f"{CH}.ChargeLimit"])
tool("set_charging_timer", "Energy", "action",
     "Sets when plug-in charging runs: right away, starting at a time of day (for example cheaper night power), or finishing by a time of day (for example a morning departure). "
     "Use it for scheduling requests; use `set_charging_state` to start or stop charging immediately. "
     "Times are local and apply to the next charging session. " + RETURNS_NEW,
     {"timer_mode": P("str", one_of(["INACTIVE", "START_TIME", "END_TIME"]) + " \"INACTIVE\" charges as soon as the cable is plugged in; \"START_TIME\" waits until timer_time; \"END_TIME\" finishes by timer_time."),
      "timer_time": P("str", "time of day as HH:MM on a 24-hour clock, local time. Default is \"\". Required unless timer_mode is \"INACTIVE\".", False, "", samples=["22:00", "06:30"])},
     writes=[f"{CH}.Timer.Mode", f"{CH}.Timer.Time"])
tool("set_charging_state", "Energy", "action",
     "Starts or stops plug-in charging immediately, overriding the charging timer for this session. "
     "It returns an error when no cable is connected; check with `get_charge_port_status`. "
     "Charging stops on its own at the charge limit. Returns whether the car is now charging.",
     {"is_charging": P("bool", "true starts charging now, false stops it.")},
     writes=[f"{CH}.IsCharging"])
STATION_PARAMS = {"charging_station_id": P("str", "charging station ID returned by `search_poi_at_location` or `search_poi_along_route` with category \"charging_station\"."),
                  "plug_id": P("str", "ID of one plug at that station, returned in the same search result; the plug decides the charging power and whether it is AC or DC.")}
CHG_READS = [f"{PT}.TractionBattery.StateOfCharge.Displayed", f"{PT}.TractionBattery.NetCapacity", f"{CH}.MaxAcceptedPowerAC", f"{CH}.MaxAcceptedPowerDC", f"{CH}.ChargeLimit"]
START_BATT = P("int", "integer from 0 to 99. The battery level charging starts from; use the current level from `get_energy_status` unless the driver names another.")
tool("estimate_charging_time", "Energy", "retrieve",
     "Estimates how many minutes it takes to charge from one battery level to another at a specific charging station plug. "
     "It looks up the plug's power and AC or DC type, caps the power at what this car accepts, and follows the car's charging curve. "
     "Use it when the driver asks how long charging will take; use `estimate_battery_after_charging` when they ask what level a given time gets them. Returns the estimated minutes and the charging power used.",
     {**STATION_PARAMS,
      "start_battery_percent": START_BATT,
      "target_battery_percent": P("int", "integer from 1 to 100. Must be above start_battery_percent; levels above the charge limit are capped to it.")},
     reads=CHG_READS)
tool("estimate_battery_after_charging", "Energy", "retrieve",
     "Estimates the battery level after charging for a given number of minutes at a specific charging station plug. "
     "It looks up the plug's power and AC or DC type, caps the power at what this car accepts, and stops at the charge limit. "
     "Use it when the driver asks what a stop of a certain length gets them; use `estimate_charging_time` for the reverse question. Returns the estimated battery level in percent.",
     {**STATION_PARAMS,
      "start_battery_percent": START_BATT,
      "charging_minutes": P("int", "integer from 1 to 720.")},
     reads=CHG_READS)
tool("estimate_electric_distance", "Energy", "retrieve",
     "Estimates how many km the car can drive on electric power alone between two battery levels, using the usable battery capacity and the reference consumption. "
     "Use it for questions such as \"how far can I go on electric only?\". "
     "It ignores the fuel tank; for a whole route with fuel included, use `estimate_route_energy`. Returns the distance in km.",
     {"start_battery_percent": P("int", "integer from 1 to 100. Use the current level from `get_energy_status` unless the driver names another."),
      "end_battery_percent": P("int", "integer from 0 to 99. Must be below start_battery_percent. Default is 0.", False, 0)},
     reads=[f"{PT}.TractionBattery.StateOfCharge.Displayed", f"{PT}.TractionBattery.NetCapacity", f"{PT}.RangeExtender.ChargeDepleting.EnergyConsumption"])
tool("estimate_refuel", "Energy", "retrieve",
     "Estimates how many liters fill the tank to a target level and how many km of fuel range that adds. "
     "Use it when the driver asks how much fuel to buy or how far a fill-up gets them. "
     "It does not find gas stations; use `search_poi_at_location` or `search_poi_along_route` with category \"gas_station\". Returns liters and added range in km.",
     {"target_fuel_percent": P("int", "integer from 1 to 100. Default is 100, a full tank.", False, 100)},
     reads=[f"{PT}.FuelSystem.RelativeLevel", f"{PT}.FuelSystem.TankCapacity", f"{PT}.FuelSystem.AverageConsumption"])
tool("estimate_route_energy", "Energy", "retrieve",
     "Estimates, for a route, how many km can be driven electrically, how many liters of fuel the rest needs, and whether the car arrives without charging or refueling. "
     "Use it before long trips or when the driver asks whether they will make it. It takes the current hybrid mode into account, for example \"HOLD\" saves battery. "
     "Returns electric km, fuel liters, and whether a stop is needed.",
     {"route_id": P("str", "route ID returned by `get_routes` or `get_navigation_status`.")},
     reads=ENERGY + [f"{PT}.Hybrid.Mode"])

# ---- navigation
POI = ["gas_station", "charging_station", "restaurant", "fast_food", "cafe", "bakery", "supermarket", "parking", "public_toilet", "hotel", "airport", "pharmacy", "hospital", "car_wash"]
FILTERS = ["open_now", "has_available_plug", "has_dc_plug"]
FILTER_DESC = "list of 0 to 3 filters, each " + one_of(FILTERS)[:-1] + ". \"has_available_plug\" and \"has_dc_plug\" apply only to \"charging_station\". Default is an empty list."
POI_RETURNS = ("Returns up to 10 results; each has its POI ID, name, location ID, distance, opening hours, and phone number; charging stations also list each plug's ID, power in kW, AC or DC type, and whether it is free. "
               "Results do not include prices or reviews.")
tool("get_location_id_by_name", "Navigation", "retrieve",
     "Looks up the location ID of a city, street address, or named place. "
     "Call it first whenever the driver names a place, because navigation, route, weather, and POI tools only accept location IDs. "
     "If several places match, it returns all of them with their city so the assistant can ask which one. Returns location IDs, names, and coordinates.",
     {"place_name": P("str", "free text name of the city, address, or place, as the driver said it.", samples=["Munich", "Chico", "Sacramento International Airport", "1200 Main Street, Madison"])},
     external=True)
tool("search_poi_at_location", "Navigation", "retrieve",
     "Finds points of interest of one category near a location, sorted by distance. "
     "Use it for requests such as \"find a pharmacy near the hotel\" or \"is there a charger in town\"; for places on the way to the destination, use `search_poi_along_route`. "
     + POI_RETURNS,
     {"location_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "poi_category": P("str", one_of(POI)),
      "filters": P("list", FILTER_DESC, False, [])},
     external=True)
tool("search_poi_along_route", "Navigation", "retrieve",
     "Finds points of interest of one category along a route, with how many km along the route each one is and the extra driving time of the detour. "
     "Use it for stops on the way, such as \"find a charger on the way\" or \"a gas station before we run out\"; for places around one location, use `search_poi_at_location`. "
     + POI_RETURNS,
     {"route_id": P("str", "route ID returned by `get_routes` or `get_navigation_status`."),
      "poi_category": P("str", one_of(POI)),
      "filters": P("list", FILTER_DESC, False, []),
      "max_detour_minutes": P("int", "integer from 1 to 30. Leave out places that add more extra driving time than this. Default is 10.", False, 10)},
     external=True)
tool("get_routes", "Navigation", "retrieve",
     "Returns up to three route options between two locations, each with its route ID, distance in km, duration, whether it uses toll roads, and the main roads it takes. "
     "Call it before `start_navigation`, and present the options so the driver can choose. It respects the avoid-tolls and avoid-highways settings from `set_route_preferences`. "
     "It does not start guidance.",
     {"destination_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "start_location_id": P("str", "location ID returned by `get_location_id_by_name`. Default is \"current\", the car's current location.", False, "current")},
     reads=[f"{N}.RouteOptions.IsTollAvoided", f"{N}.RouteOptions.IsHighwayAvoided"])
tool("convert_route_distance_and_time", "Navigation", "retrieve",
     "Converts, on a given route, a distance into the driving time it takes, or a driving time into the distance covered. "
     "Use it for questions such as \"where will I be in 30 minutes?\" or \"how long until the charger 40 km ahead?\". "
     "It uses the speeds of the roads on that route. Returns the converted value.",
     {"route_id": P("str", "route ID returned by `get_routes` or `get_navigation_status`."),
      "amount": P("float", "number from 0.0 to 2000.0. The distance or time to convert, in the unit given by amount_unit."),
      "amount_unit": P("str", one_of(["km", "minutes"]) + " \"km\" converts a distance into minutes; \"minutes\" converts a time into km.")},
     external=True)
NAV = [f"{N}.IsGuidanceActive", f"{N}.DestinationSet.Latitude", f"{N}.DestinationSet.Longitude", f"{N}.DestinationSet.LocationId",
       f"{N}.Waypoints.Stop1.LocationId", f"{N}.Waypoints.Stop2.LocationId", f"{N}.Waypoints.Stop3.LocationId", f"{N}.RouteId"]
tool("start_navigation", "Navigation", "action",
     "Starts turn-by-turn guidance from the current location to a destination, optionally through up to three intermediate stops in order. "
     "Use it only when guidance is not active; to change an active route, use `update_navigation_waypoint` or `update_navigation_destination`, which do not restart guidance. "
     "Get location IDs from `get_location_id_by_name` and the route ID of the first leg from `get_routes`. Returns the destination, stops, and active route ID.",
     {"destination_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "first_leg_route_id": P("str", "route ID of the first leg, returned by `get_routes` for the current location to the first stop, or to the destination when there are no stops."),
      "stop_location_ids": P("list", "list of 0 to 3 location IDs from `get_location_id_by_name`, in driving order. Default is an empty list.", False, [])},
     writes=NAV)
tool("update_navigation_waypoint", "Navigation", "action",
     "Adds, replaces, or removes one intermediate stop on the active route without restarting guidance. "
     "It returns an error when guidance is not active, when adding a fourth stop, or when the stop number does not exist. "
     "Change one stop per call and never call it in parallel, because stop numbers shift after each change. Returns the updated list of stops and the new route ID.",
     {"waypoint_operation": P("str", one_of(["add", "replace", "remove"])),
      "stop_number": P("int", "integer from 1 to 3. For \"add\", the number the new stop takes, with later stops moving back; for \"replace\" and \"remove\", the stop to change."),
      "location_id": P("str", "location ID returned by `get_location_id_by_name`. Required for \"add\" and \"replace\"; leave it empty for \"remove\". Default is \"\".", False, "")},
     writes=NAV)
tool("update_navigation_destination", "Navigation", "action",
     "Replaces the final destination of the active route, or removes it so the last intermediate stop becomes the destination, without restarting guidance. "
     "It returns an error when guidance is not active, or when removing the destination with no intermediate stop left; use `cancel_navigation` to end guidance instead. "
     "Intermediate stops are kept. Returns the updated destination, stops, and route ID.",
     {"destination_operation": P("str", one_of(["replace", "remove"])),
      "location_id": P("str", "location ID returned by `get_location_id_by_name`. Required for \"replace\"; leave it empty for \"remove\". Default is \"\".", False, "")},
     writes=NAV)
tool("cancel_navigation", "Navigation", "action",
     "Stops guidance and clears the destination and all intermediate stops. "
     "Use it when the driver wants no route at all; to change only part of the route, use `update_navigation_waypoint` or `update_navigation_destination`. "
     "Route preferences and voice settings are kept. Returns confirmation that guidance is off.",
     writes=NAV)
tool("set_route_preferences", "Navigation", "action",
     "Sets whether route planning avoids toll roads and whether it avoids highways. "
     "The preferences apply to the next `get_routes` call; an active route is not recalculated, so call `get_routes` again if the driver wants the current trip changed. "
     "Avoiding highways usually makes trips much longer. " + RETURNS_NEW,
     {"avoid_tolls": P("bool", "true avoids toll roads, false allows them."),
      "avoid_highways": P("bool", "true avoids highways, false allows them.")},
     writes=[f"{N}.RouteOptions.IsTollAvoided", f"{N}.RouteOptions.IsHighwayAvoided"])
tool("set_navigation_voice_guidance", "Navigation", "action",
     "Chooses how much the navigation voice speaks: every turn instruction, only alerts such as hazards and speed cameras, or nothing. "
     "Use it when the driver finds the voice too chatty or wants it back. "
     "It does not change its loudness; use `set_navigation_voice_volume`. " + RETURNS_NEW,
     {"guidance_level": P("str", one_of(["UNMUTED", "ALERT_ONLY", "MUTED"]) + " \"UNMUTED\" speaks every instruction and \"MUTED\" is silent.")},
     writes=[f"{N}.Mute"])
tool("set_navigation_voice_volume", "Navigation", "action",
     "Sets the loudness of the navigation voice, separately from music and radio. "
     "Use it when the driver says the directions are too loud or too quiet. "
     "It does not change the media volume (`set_media_volume`) and does not unmute a muted voice (`set_navigation_voice_guidance`). " + RETURNS_NEW,
     {"volume_percent": P("int", "integer from 0 to 100, in steps of 5.")},
     writes=[f"{N}.Volume"])
tool("get_navigation_status", "Navigation", "retrieve",
     "Returns whether guidance is active, the destination's location ID and coordinates, the intermediate stops in order, the route ID being followed, and whether the destination is reached. "
     "It also returns the route preferences and the voice guidance level and volume. "
     "Use it before changing an active route or to answer where the car is heading. It does not return arrival time or distance left; use `convert_route_distance_and_time` with the route ID.",
     reads=paths(f"{N}."))

# ---- outside-world, communication, preferences, utilities (no vehicle state)
tool("get_weather", "Weather", "retrieve",
     "Returns the weather condition, temperature in Celsius, humidity, and wind speed for a location at a time today. "
     "Use it before opening the sunroof or turning on fog lights, and for any weather question. Only today can be requested; it returns an error for other days. "
     "Returns one forecast for the requested time.",
     {"location_id": P("str", "location ID returned by `get_location_id_by_name`, or \"current\" for the car's current location."),
      "time_of_day": P("str", "time today as HH:MM on a 24-hour clock, or \"now\". Default is \"now\".", False, "now", samples=["now", "17:30"])},
     external=True)
tool("get_contact_id_by_name", "Communication", "retrieve",
     "Finds contacts in the connected phone's address book by name and returns their contact IDs and full names. "
     "Call it before `get_contact_details` whenever the driver names a person. If several contacts match, ask the driver which one. "
     "It does not return phone numbers or email addresses.",
     {"contact_name": P("str", "free text first name, last name, nickname, or both names.", samples=["Alex", "Jordan Lee", "Dr. Patel", "Mom"])},
     external=True)
tool("get_contact_details", "Communication", "retrieve",
     "Returns the phone numbers and email addresses saved for one or more contacts. "
     "Use it after `get_contact_id_by_name` and before calling, texting, or emailing someone. "
     "It does not return the contact's location or calendar.",
     {"contact_ids": P("list", "list of 1 to 5 contact IDs returned by `get_contact_id_by_name`.")},
     external=True)
tool("call_phone_number", "Communication", "action",
     "Places a hands-free call through the connected phone. "
     "Look the number up with `get_contact_details` when the driver names a person, and confirm the person when several numbers exist. "
     "It does not send texts; use `send_text_message`. Returns whether the call was placed.",
     {"phone_number": P("str", "phone number in international format.", samples=["+1 530 555 0142", "+49 89 5550 1234"])},
     external=True)
tool("send_text_message", "Communication", "action",
     "Sends a short SMS through the connected phone. "
     "Read the message back to the driver and get confirmation before sending, because a sent message cannot be recalled. "
     "Use `send_email` for longer messages or email addresses. Returns whether the message was sent.",
     {"phone_number": P("str", "phone number in international format, usually from `get_contact_details`.", samples=["+1 530 555 0142"]),
      "message_text": P("str", "free text message, at most 300 characters.", samples=["Running 15 minutes late, start without me.", "Just parked, see you at the entrance."])},
     external=True)
tool("send_email", "Communication", "action",
     "Sends a short email from the driver's connected account. "
     "Read the subject and body back and get confirmation before sending, because a sent email cannot be recalled. "
     "Addresses usually come from `get_contact_details`. Returns whether the email was sent.",
     {"recipient_emails": P("list", "list of 1 to 5 email addresses."),
      "subject": P("str", "free text subject line.", samples=["Running late", "Meeting notes"]),
      "body": P("str", "free text message body.", samples=["I'm stuck in traffic and will arrive around 10:20."])},
     external=True)
tool("get_calendar_events", "Communication", "retrieve",
     "Returns today's calendar events from a given hour onward, each with start time, duration, topic, location, and attendees. "
     "Use it when the driver asks about their schedule or the next meeting, and to plan a route to a meeting location. "
     "Only today can be requested; it cannot create or change events.",
     {"start_hour": P("int", "integer from 0 to 23, local time. Events starting before this hour are left out. Default is 0.", False, 0)},
     external=True)
tool("get_user_preferences", "Preferences", "retrieve",
     "Returns the driver's saved preferences for one category, such as preferred charging and fuel brands, route choices, or usual climate settings. "
     "Check them before choosing between options on the driver's behalf, for example which of several chargers to suggest. "
     "It cannot change preferences.",
     {"preference_category": P("str", one_of(["points_of_interest", "navigation_and_routing", "climate", "seats", "media", "energy", "communication", "weather"]))},
     external=True)
tool("calculate_math", "Utility", "retrieve",
     "Evaluates an arithmetic expression and returns the exact result. "
     "Use it instead of mental math whenever an answer depends on a calculation, such as adding distances, splitting costs, or converting units. "
     "It supports numbers, + - * /, and parentheses only.",
     {"expression": P("str", "free text arithmetic expression using numbers, + - * / and parentheses.", samples=["(42.5 + 17.3) * 1.8", "45 * 0.62"])},
     external=True)
tool("calculate_datetime", "Utility", "retrieve",
     "Adds or subtracts minutes to a time of day and returns the resulting time, rolling over midnight when needed. "
     "Use it to work out arrival times, departure times, or how long until an event. "
     "It works with times of day only, not dates.",
     {"start_time": P("str", "time as HH:MM on a 24-hour clock, or \"now\".", samples=["now", "14:35"]),
      "minutes_to_add": P("int", "integer from -1440 to 1440. Negative values subtract.")},
     external=True)

# ------------------------------------------------------------------ negative tools
# Visible to the assistant but wrong for in-car requests: they control the home, the phone itself, or
# services the car does not offer. Their descriptions state that plainly so the model learns to decline.
NEG = {}


def neg(name, domain, desc, params=None):
    NEG[name] = {"description": desc, "domain": domain, "kind": "action", "parameters": params or {}, "sample_commands": []}


NOT_CAR = "It controls nothing in the car; for the car's own {what}, use {tool}."
neg("set_home_thermostat", "SmartHome",
    "Sets the target temperature of the thermostat in the driver's home. Use it only when the driver explicitly asks about the temperature at home. "
    + NOT_CAR.format(what="cabin temperature", tool="`set_climate_temperature`") + " Returns the new home target temperature.",
    {"temperature_celsius": P("float", "number from 10.0 to 30.0, in steps of 0.5.")})
neg("set_home_lights", "SmartHome",
    "Turns the lights in one room of the driver's home on or off and sets their color. Use it only when the driver explicitly asks about lights at home. "
    + NOT_CAR.format(what="interior lights", tool="`set_reading_light_state` or `set_ambient_light`") + " Returns the room's new light state.",
    {"room": P("str", one_of(["living_room", "bedroom", "kitchen", "garden"])),
     "enabled": P("bool", "true turns the lights on, false turns them off."),
     "color": P("str", one_of(["warm_white", "cool_white", "red", "blue", "green"]) + " Default is \"warm_white\".", False, "warm_white")})
neg("set_home_door_lock_state", "SmartHome",
    "Locks or unlocks the smart lock on the front door of the driver's home. Use it only when the driver explicitly asks about the door at home. "
    + NOT_CAR.format(what="doors", tool="`set_door_lock_state`") + " Returns the new lock state of the home door.",
    {"is_locked": P("bool", "true locks the home door, false unlocks it.")})
neg("play_on_home_speaker", "SmartHome",
    "Plays music on a smart speaker in a room of the driver's home. Use it only when the driver wants music playing at home. "
    + NOT_CAR.format(what="audio", tool="`play_media_by_query`") + " Returns what started playing.",
    {"search_query": P("str", "free text naming what to play.", samples=["jazz for dinner"]),
     "room": P("str", one_of(["living_room", "bedroom", "kitchen"]))})
neg("start_home_wallbox_charging", "SmartHome",
    "Starts a charging session through the home wallbox's own app account, at a chosen current. It only works for a car plugged in at home. "
    + NOT_CAR.format(what="charging", tool="`set_charging_state` and `set_charging_timer`") + " Returns whether the wallbox started.",
    {"max_current_amps": P("int", "integer from 6 to 32.")})
neg("set_phone_alarm", "Phone",
    "Sets a wake-up alarm on the driver's phone. Use it only when the driver explicitly asks for a phone alarm. "
    "The car has no alarm clock; for time calculations use `calculate_datetime`. Returns the alarm time.",
    {"alarm_time": P("str", "time as HH:MM on a 24-hour clock.", samples=["06:30"])})
neg("set_phone_ringer_volume", "Phone",
    "Changes the ringer volume of the phone itself, not the car's speakers. Use it only when the driver explicitly asks about the phone's ringer. "
    + NOT_CAR.format(what="audio volume", tool="`set_media_volume`") + " Returns the new ringer level.",
    {"ringer_level": P("int", "integer from 0 to 10.")})
neg("book_flight", "Travel",
    "Searches and books a flight ticket with the driver's travel account. It is a purchase outside the car and should not be made while driving. "
    "For directions to an airport, use `get_location_id_by_name` and `get_routes`. Returns the booking confirmation.",
    {"origin_airport": P("str", "free text city or airport code.", samples=["SFO"]),
     "destination_airport": P("str", "free text city or airport code.", samples=["ORD"]),
     "travel_date": P("str", "date as YYYY-MM-DD.", samples=["2026-11-02"])})
neg("order_food_delivery", "Shopping",
    "Orders food for delivery to a home address. It is a purchase outside the car. "
    "To find somewhere to eat on the way, use `search_poi_along_route` with category \"restaurant\". Returns the order confirmation.",
    {"restaurant_name": P("str", "free text restaurant name.", samples=["Corner Noodle House"]),
     "menu_items": P("list", "list of 1 to 10 free text item names.")})
neg("transfer_money", "Finance",
    "Transfers money from the driver's bank account to another account. It is a financial transaction outside the car and should not be made by voice while driving. "
    "The car offers no payment or banking features. Returns the transfer confirmation.",
    {"recipient": P("str", "free text recipient name or account number.", samples=["Savings account"]),
     "amount": P("float", "number from 0.01 to 10000.0.")})
neg("create_document", "Productivity",
    "Creates a new text document in the driver's cloud drive. It is office work outside the car. "
    "To send a short note to someone, use `send_text_message` or `send_email`. Returns the new document's ID.",
    {"document_title": P("str", "free text document title.", samples=["Trip notes"]),
     "document_text": P("str", "free text document content.", samples=["Packing list: charger cable, snacks"])})
neg("post_to_social_media", "Social",
    "Publishes a post on the driver's social media account. It is public, cannot be recalled, and is outside the car. "
    "To message one person, use `send_text_message`. Returns the post's link.",
    {"post_text": P("str", "free text post content.", samples=["Road trip day!"])})

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
VAGUE = {"on", "open", "position", "level", "mode", "value", "time", "which", "action", "name", "window", "seat", "door", "zone", "unit", "query", "category", "direction", "locked", "folded", "muted", "playing"}
for name, spec in {**TOOLS, **NEG}.items():
    if len(re.findall(r"[.!?](?:\s|$)", spec["description"])) < 3:
        errors.append(f"{name}: description shorter than three sentences")
    if "return" not in spec["description"].lower():
        errors.append(f"{name}: description does not say what it returns")
    for pn in spec["parameters"]:
        if pn in VAGUE:
            errors.append(f"{name}.{pn}: parameter name too vague")
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
(OUT / f"{PREFIX}_signal_mapping.json").write_text(dump({"vss_version": VSS_VERSION, "vss_commit": VSS_COMMIT, "signals": META}))
if VSS_ALL is not None:
    REF_PATH.write_text(dump({"vss_version": VSS_VERSION, "vss_commit": VSS_COMMIT,
                              "signals": {p: VSS_ALL[p] for p in sorted(STATE) if p in VSS_ALL}}))

# Overlay with every extension, in VSS's own .vspec format.
lines = ["# VSS overlay for the plug-in hybrid assistant (tools vss).",
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
(OUT / f"{PREFIX}_overlay.vspec").write_text("\n".join(lines))

print("positive", len(TOOLS), Counter((t["domain"], t["kind"]) for t in TOOLS.values()))
print("negative", len(NEG), "| state", len(STATE), "standard", sum(m["standard"] for m in META.values()), "extension", len(EXT))
