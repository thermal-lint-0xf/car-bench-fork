"""Generate hybrid-car assistant spec files and validate cross-file consistency."""
import json
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
PREFIX = "2026-10-11_hybrid"

SEATS4 = ["front_left", "front_right", "rear_left", "rear_right"]
FRONT2 = ["front_left", "front_right"]


def one_of(values, quote=True):
    vals = [f'"{v}"' if quote else str(v) for v in values]
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


TOOLS = {}
TOOL_STATE = {}


def tool(name, domain, kind, desc, params=None, writes=None, reads=None, external=False):
    TOOLS[name] = {
        "description": desc,
        "domain": domain,
        "kind": kind,
        "parameters": params or {},
        "sample_commands": [],
    }
    if external:
        TOOL_STATE[name] = {"external": True}
    elif kind == "action":
        TOOL_STATE[name] = {"writes": writes}
    else:
        TOOL_STATE[name] = {"reads": reads}


# ---------------------------------------------------------------- state
STATE = {}


def S(path, type_, desc, initial="random", default=None, minimum=None, maximum=None, step=None, enum=None):
    s = {"type": type_}
    if minimum is not None:
        s["minimum"] = minimum
        s["maximum"] = maximum
    if step is not None:
        s["step"] = step
    if enum is not None:
        s["enum"] = enum
    s["initial"] = initial
    if initial == "fixed":
        s["default"] = default
    s["description"] = desc
    STATE[path] = s


SEAT_WORD = {
    "front_left": "Front-left (driver)",
    "front_right": "Front-right (passenger)",
    "rear_left": "Rear-left",
    "rear_right": "Rear-right",
}

# comfort: windows, roof
for s in SEATS4:
    S(f"vehicle.comfort.window_positions.{s}", "int", f"{SEAT_WORD[s]} window opening in percent, 0 is closed.", minimum=0, maximum=100, step=5)
S("vehicle.comfort.sunroof_position_pct", "int", "Sunroof opening in percent, 0 is closed.", initial="from_weather", minimum=0, maximum=100, step=5)
S("vehicle.comfort.sunshade_position_pct", "int", "Sunshade opening in percent, 0 is closed. Must be 100 whenever the sunroof is above 0.", minimum=0, maximum=100, step=5)

# comfort: seats
for s in SEATS4:
    S(f"vehicle.comfort.seat_occupied.{s}", "bool",
      f"{SEAT_WORD[s]} seat occupancy sensor." + (" The driver seat is always occupied." if s == "front_left" else ""),
      initial="fixed" if s == "front_left" else "random", default=True if s == "front_left" else None)
for s in SEATS4:
    S(f"vehicle.comfort.seat_heating.{s}", "int", f"{SEAT_WORD[s]} seat heating level, 0 off, 3 highest.", initial="from_weather", enum=[0, 1, 2, 3])
for s in FRONT2:
    S(f"vehicle.comfort.seat_ventilation.{s}", "int", f"{SEAT_WORD[s]} seat ventilation level, 0 off, 3 highest.", initial="from_weather", enum=[0, 1, 2, 3])
    S(f"vehicle.comfort.seat_massage_mode.{s}", "str", f"{SEAT_WORD[s]} seat massage program.", enum=["off", "wave", "pulse", "stretch", "lumbar"])
    S(f"vehicle.comfort.seat_massage_intensity.{s}", "int", f"{SEAT_WORD[s]} seat massage intensity, 1 gentle, 3 strong. Ignored while the massage mode is off.", enum=[1, 2, 3])
    S(f"vehicle.comfort.seat_fore_aft_pct.{s}", "int", f"{SEAT_WORD[s]} seat fore-aft position in percent, 0 fully forward, 100 fully back.", minimum=0, maximum=100, step=5)
    S(f"vehicle.comfort.seat_backrest_angle_deg.{s}", "int", f"{SEAT_WORD[s]} backrest angle in degrees from vertical.", minimum=5, maximum=40, step=1)
S("vehicle.comfort.driver_memory_profile", "int", "Last recalled driver seat and mirror memory profile, 0 means no profile recalled.", enum=[0, 1, 2, 3])
S("vehicle.comfort.steering_wheel_heating", "int", "Steering wheel heating level, 0 off, 3 highest.", initial="from_weather", enum=[0, 1, 2, 3])

# comfort: interior lights
for s in SEATS4:
    S(f"vehicle.comfort.reading_light.{s}", "bool", f"{SEAT_WORD[s]} reading light on.")
AMBIENT_COLORS = ["off", "red", "green", "blue", "yellow", "white", "pink", "orange", "purple", "cyan"]
S("vehicle.comfort.ambient_light_color", "str", "Ambient interior light color, \"off\" when the ambient light is off.", enum=AMBIENT_COLORS)
S("vehicle.comfort.ambient_light_brightness_pct", "int", "Ambient light brightness in percent.", minimum=10, maximum=100, step=10)

# climate
S("vehicle.climate.auto_mode", "bool", "Climate auto mode. Manual changes to fan speed or airflow direction switch it off.", initial="fixed", default=True)
for z in ["front_left", "front_right", "rear"]:
    word = {"front_left": "Front-left (driver)", "front_right": "Front-right (passenger)", "rear": "Rear"}[z]
    S(f"vehicle.climate.temperature_c.{z}", "float", f"{word} climate zone target temperature in Celsius.", minimum=16.0, maximum=28.0, step=0.5)
S("vehicle.climate.fan_speed", "int", "Climate fan speed, 0 off, 5 highest.", enum=[0, 1, 2, 3, 4, 5])
AIRFLOW = ["feet", "head", "head_feet", "windshield", "windshield_feet", "windshield_head", "windshield_head_feet"]
S("vehicle.climate.airflow_direction", "str", "Where the fan blows air.", enum=AIRFLOW)
S("vehicle.climate.ac_on", "bool", "Air conditioning compressor on. Usually on when it is hot.", initial="from_weather")
S("vehicle.climate.air_circulation", "str", "Air intake mode.", enum=["auto", "fresh_air", "recirculation"])
S("vehicle.climate.front_defrost", "bool", "Front windshield defrost on. Usually on in snow, fog, or below 3 Celsius.", initial="from_weather")
S("vehicle.climate.rear_defrost", "bool", "Rear window defrost on. Usually on in snow, fog, or below 3 Celsius.", initial="from_weather")

# visibility
S("vehicle.visibility.low_beams", "bool", "Low beam headlights on. On at night, in rain, snow, fog, or storm.", initial="from_weather")
S("vehicle.visibility.high_beams", "bool", "High beam headlights on. Always off while fog lights are on.")
S("vehicle.visibility.fog_lights", "bool", "Front fog lights on. Usually on only in fog, heavy rain, or snow.", initial="from_weather")
S("vehicle.visibility.wiper_speed", "int", "Front wiper speed, 0 off, 3 fastest. Should be above 0 when it rains or snows.", initial="from_weather", enum=[0, 1, 2, 3])
S("vehicle.visibility.rear_wiper", "bool", "Rear wiper on. Usually on in rain or snow.", initial="from_weather")
S("vehicle.visibility.mirrors_folded", "bool", "Side mirrors folded in.", initial="fixed", default=False)
S("vehicle.visibility.mirror_heating", "bool", "Side mirror heating on. Usually on in snow, fog, or below 3 Celsius.", initial="from_weather")

# access (new)
S("vehicle.access.doors_locked", "bool", "All doors locked.")
for s in ["rear_left", "rear_right"]:
    S(f"vehicle.access.child_lock.{s}", "bool", f"{SEAT_WORD[s]} door child safety lock engaged.")
S("vehicle.access.trunk_open", "bool", "Trunk lid open. Can only be true while the car is stopped in park.", initial="fixed", default=False)
S("vehicle.access.fuel_door_open", "bool", "Fuel filler door open. Can only be true while the car is stopped in park.", initial="fixed", default=False)
S("vehicle.access.charge_port_open", "bool", "Charging port door open. Can only be true while the car is stopped in park.", initial="fixed", default=False)

# media (new)
S("vehicle.media.source", "str", "Active audio source.", enum=["fm_radio", "dab_radio", "bluetooth", "usb", "streaming"])
S("vehicle.media.playing", "bool", "Audio is playing rather than paused.")
S("vehicle.media.volume", "int", "Audio volume, 0 silent, 30 loudest.", minimum=0, maximum=30, step=1)
S("vehicle.media.muted", "bool", "Audio muted.")
S("vehicle.media.fm_frequency_mhz", "float", "Tuned FM radio frequency in MHz.", minimum=87.5, maximum=108.0, step=0.1)

# telemetry (read-only)
S("vehicle.telemetry.speed_kph", "int", "Current vehicle speed in km/h. 0 means the car is stopped.", minimum=0, maximum=160, step=1)
S("vehicle.telemetry.gear", "str", "Selected gear. \"P\" park, \"R\" reverse, \"N\" neutral, \"D\" drive. Speed is 0 whenever the gear is \"P\".", enum=["P", "R", "N", "D"])
S("vehicle.telemetry.outside_temp_c", "float", "Outside air temperature in Celsius, taken from the weather of the current city.", initial="from_weather", minimum=-30.0, maximum=50.0, step=0.5)
S("vehicle.telemetry.cabin_temp_c", "float", "Measured cabin air temperature in Celsius. Drifts toward the outside temperature when climate is off.", initial="from_weather", minimum=-20.0, maximum=55.0, step=0.5)
for s in SEATS4:
    S(f"vehicle.telemetry.tire_pressure_kpa.{s}", "int", f"{SEAT_WORD[s].split(' ')[0]} tire pressure in kPa. Recommended 230 to 250, below 200 is a low-pressure warning.", minimum=150, maximum=280, step=5)
S("vehicle.telemetry.odometer_km", "int", "Total distance driven in km.", minimum=0, maximum=300000, step=1)
S("vehicle.telemetry.oil_life_pct", "int", "Remaining combustion engine oil life in percent.", minimum=0, maximum=100, step=1)
S("vehicle.telemetry.washer_fluid_pct", "int", "Windshield washer fluid level in percent.", minimum=0, maximum=100, step=5)
S("vehicle.telemetry.next_service_km", "int", "Distance until the next scheduled service in km. Negative values are not used; 0 means service is due now.", minimum=0, maximum=30000, step=100)
S("vehicle.telemetry.trip_distance_km", "float", "Distance since the trip computer was last reset, in km.", minimum=0.0, maximum=2000.0, step=0.1)
S("vehicle.telemetry.trip_avg_fuel_l_per_100km", "float", "Average fuel consumption since the last trip reset, in liters per 100 km.", minimum=0.0, maximum=15.0, step=0.1)
S("vehicle.telemetry.trip_avg_energy_kwh_per_100km", "float", "Average electric energy consumption since the last trip reset, in kWh per 100 km.", minimum=0.0, maximum=30.0, step=0.1)
S("vehicle.telemetry.trip_electric_share_pct", "int", "Share of trip distance driven on electric power only, in percent.", minimum=0, maximum=100, step=1)

# powertrain (new): plug-in hybrid
S("vehicle.powertrain.fuel_level_pct", "int", "Fuel tank level in percent of tank capacity.", minimum=0, maximum=100, step=1)
S("vehicle.powertrain.battery_soc_pct", "int", "High-voltage battery state of charge in percent.", minimum=0, maximum=100, step=1)
S("vehicle.powertrain.fuel_tank_capacity_l", "float", "Fuel tank capacity in liters.", initial="fixed", default=45.0, minimum=30.0, maximum=80.0, step=0.5)
S("vehicle.powertrain.battery_usable_capacity_kwh", "float", "Usable high-voltage battery capacity in kWh.", initial="fixed", default=18.0, minimum=8.0, maximum=40.0, step=0.5)
S("vehicle.powertrain.electric_consumption_kwh_per_100km", "float", "Reference electric energy consumption used for electric range estimates, in kWh per 100 km.", initial="fixed", default=18.0, minimum=12.0, maximum=25.0, step=0.5)
S("vehicle.powertrain.fuel_consumption_l_per_100km", "float", "Reference fuel consumption with the engine running, used for fuel range estimates, in liters per 100 km.", initial="fixed", default=6.0, minimum=3.0, maximum=12.0, step=0.1)
S("vehicle.powertrain.max_ac_charging_kw", "float", "Maximum AC charging power the car accepts, in kW.", initial="fixed", default=7.4, enum=[3.7, 7.4, 11.0])
S("vehicle.powertrain.max_dc_charging_kw", "float", "Maximum DC fast charging power the car accepts, in kW.", initial="fixed", default=50.0, enum=[0.0, 50.0, 80.0])
S("vehicle.powertrain.drive_mode", "str", "Driving dynamics mode.", enum=["eco", "comfort", "sport"])
S("vehicle.powertrain.hybrid_mode", "str", "How the hybrid system uses battery and engine. \"auto\" blends both, \"electric\" drives on battery only, \"hold\" keeps the current battery charge for later, \"charge\" uses the engine to charge the battery up to the charge target.", enum=["auto", "electric", "hold", "charge"])
S("vehicle.powertrain.battery_charge_target_pct", "int", "Battery level the engine charges up to while the hybrid mode is \"charge\".", minimum=20, maximum=80, step=10)
S("vehicle.powertrain.regen_level", "int", "Regenerative braking strength, 0 coasting, 3 strongest (one-pedal feel).", enum=[0, 1, 2, 3])
S("vehicle.powertrain.engine_running", "bool", "Combustion engine currently running. False whenever the hybrid mode is \"electric\".")
S("vehicle.powertrain.plugged_in", "bool", "Charging cable connected. Always false while driving.", initial="fixed", default=False)
S("vehicle.powertrain.charge_limit_pct", "int", "Maximum battery level plug-in charging stops at.", minimum=50, maximum=100, step=5)
S("vehicle.powertrain.scheduled_charging_enabled", "bool", "Delayed plug-in charging is enabled, so charging starts at the scheduled hour instead of immediately.")
S("vehicle.powertrain.scheduled_charging_start_hour", "int", "Hour of day (local time, 24-hour clock) delayed charging starts.", minimum=0, maximum=23, step=1)

# info
S("vehicle.info.exterior_color", "str", "Exterior paint color of the car.", initial="fixed", default="blue", enum=["black", "white", "silver", "gray", "blue", "red", "green"])

# navigation
S("navigation.active", "bool", "A route is set and guidance is running.", initial="fixed", default=False)
S("navigation.destination_id", "str", "Location ID of the final destination, empty when no route is set.", initial="fixed", default="")
for i in (1, 2, 3):
    S(f"navigation.waypoint_{i}_id", "str", f"Location ID of intermediate stop {i} in driving order, empty when unused. Stops are always filled from 1 upward without gaps.", initial="fixed", default="")
S("navigation.route_id", "str", "Route ID of the route currently being followed to the next stop, empty when no route is set.", initial="fixed", default="")
S("navigation.avoid_tolls", "bool", "Route planning avoids toll roads.")
S("navigation.avoid_highways", "bool", "Route planning avoids highways.")
S("navigation.voice_guidance_on", "bool", "Spoken turn-by-turn guidance on.")


def paths(prefix):
    return [p for p in STATE if p.startswith(prefix)]


STOPPED_RULE = "Blocked unless the car is stopped in park (`vehicle.telemetry.speed_kph` is 0 and `vehicle.telemetry.gear` is \"P\"); if blocked, tell the driver why instead of retrying."
WEATHER_CHECK = "Check the weather with `get_weather` first."

# ======================================================== vehicle: body
tool("set_window_position", "Vehicle", "action",
     "Open or close one window, or all four, to a position from 0 (closed) to 100 (fully open). Policy: if air conditioning is on and a window is opened beyond 25, warn about energy waste and ask for confirmation first.",
     {"window": P("str", one_of(SEATS4 + ["all"]) + " \"front_left\" is the driver window."),
      "position": P("int", "integer from 0 to 100, in steps of 5. Default is 100.", False, 100)},
     writes=paths("vehicle.comfort.window_positions."))
tool("set_sunshade_position", "Vehicle", "action",
     "Open or close the sunroof sunshade to a position from 0 (closed) to 100 (fully open). The sunshade cannot close below 100 while the sunroof is open; close the sunroof first.",
     {"position": P("int", "integer from 0 to 100, in steps of 5. Default is 100.", False, 100)},
     writes=["vehicle.comfort.sunshade_position_pct"])
tool("set_sunroof_position", "Vehicle", "action",
     "Open or close the sunroof to a position from 0 (closed) to 100 (fully open). Opening is blocked unless the sunshade is already at 100 or is opened to 100 with `set_sunshade_position` in the same turn. "
     + WEATHER_CHECK + " If the condition is not \"clear\", \"sunny\", \"partly_cloudy\", or \"cloudy\", get an explicit yes from the driver before opening.",
     {"position": P("int", "integer from 0 to 100, in steps of 5. Default is 100.", False, 100)},
     writes=["vehicle.comfort.sunroof_position_pct"])
tool("get_window_and_roof_status", "Vehicle", "retrieve",
     "Return the position of all four windows, the sunroof, and the sunshade.",
     reads=paths("vehicle.comfort.window_positions.") + ["vehicle.comfort.sunroof_position_pct", "vehicle.comfort.sunshade_position_pct"])

tool("set_door_locks", "Vehicle", "action",
     "Lock or unlock all doors. Unlocking is blocked while `vehicle.telemetry.speed_kph` is above 0.",
     {"locked": P("bool", "true to lock all doors, false to unlock them.")},
     writes=["vehicle.access.doors_locked"])
tool("set_child_lock", "Vehicle", "action",
     "Engage or release the child safety lock on a rear door, so it cannot be opened from inside.",
     {"door": P("str", one_of(["rear_left", "rear_right", "both"])),
      "on": P("bool", "true to engage the child lock, false to release it.")},
     writes=["vehicle.access.child_lock.rear_left", "vehicle.access.child_lock.rear_right"])
tool("set_trunk", "Vehicle", "action",
     "Open or close the power trunk lid. " + STOPPED_RULE,
     {"open": P("bool", "true to open the trunk, false to close it.")},
     writes=["vehicle.access.trunk_open"])
tool("set_fuel_door", "Vehicle", "action",
     "Open or close the fuel filler door for refueling. " + STOPPED_RULE,
     {"open": P("bool", "true to open the fuel door, false to close it.")},
     writes=["vehicle.access.fuel_door_open"])
tool("set_charge_port", "Vehicle", "action",
     "Open or close the charging port door for plug-in charging. " + STOPPED_RULE,
     {"open": P("bool", "true to open the charge port door, false to close it.")},
     writes=["vehicle.access.charge_port_open"])
tool("get_door_lock_status", "Vehicle", "retrieve",
     "Return whether the doors are locked.",
     reads=["vehicle.access.doors_locked"])
tool("get_child_lock_status", "Vehicle", "retrieve",
     "Return whether the child safety lock is engaged on each rear door.",
     reads=["vehicle.access.child_lock.rear_left", "vehicle.access.child_lock.rear_right"])
tool("get_trunk_status", "Vehicle", "retrieve",
     "Return whether the trunk lid is open or closed.",
     reads=["vehicle.access.trunk_open"])
tool("get_fuel_door_status", "Vehicle", "retrieve",
     "Return whether the fuel filler door is open or closed.",
     reads=["vehicle.access.fuel_door_open"])
tool("get_charge_port_status", "Vehicle", "retrieve",
     "Return whether the charging port door is open or closed.",
     reads=["vehicle.access.charge_port_open"])

# ======================================================== vehicle: lights & visibility
tool("set_low_beams", "Vehicle", "action",
     "Turn the low beam headlights on or off. Turning them off is not allowed while the fog lights are on.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=["vehicle.visibility.low_beams"])
tool("set_high_beams", "Vehicle", "action",
     "Turn the high beam headlights on or off. Turning them on is blocked while the fog lights are on.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=["vehicle.visibility.high_beams"])
tool("set_fog_lights", "Vehicle", "action",
     "Turn the front fog lights on or off. Policy: when turning them on, also make sure the low beams are on (`set_low_beams`) and the high beams are off (`set_high_beams`). "
     + WEATHER_CHECK + " If the condition is not \"fog\", \"heavy_rain\", \"snow\", or \"storm\", get an explicit yes from the driver before turning them on.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=["vehicle.visibility.fog_lights"])
tool("set_wiper_speed", "Vehicle", "action",
     "Set the front windshield wiper speed.",
     {"speed": P("int", "integer from 0 to 3. 0 is off and 3 is fastest.")},
     writes=["vehicle.visibility.wiper_speed"])
tool("set_rear_wiper", "Vehicle", "action",
     "Turn the rear window wiper on or off.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=["vehicle.visibility.rear_wiper"])
tool("set_side_mirrors_folded", "Vehicle", "action",
     "Fold or unfold both side mirrors. Folding is blocked while `vehicle.telemetry.speed_kph` is above 0.",
     {"folded": P("bool", "true to fold the mirrors in, false to unfold them.")},
     writes=["vehicle.visibility.mirrors_folded"])
tool("set_mirror_heating", "Vehicle", "action",
     "Turn side mirror heating on or off, to clear ice, frost, or fog from the mirrors.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=["vehicle.visibility.mirror_heating"])
tool("get_visibility_status", "Vehicle", "retrieve",
     "Return the state of the low beams, high beams, fog lights, front and rear wipers, side mirror folding, and mirror heating.",
     reads=paths("vehicle.visibility."))

tool("set_reading_light", "Vehicle", "action",
     "Turn the reading light at one seat, or at all seats, on or off.",
     {"seat": P("str", one_of(SEATS4 + ["all"]) + " \"front_left\" is the driver seat."),
      "on": P("bool", "true to turn on, false to turn off.")},
     writes=paths("vehicle.comfort.reading_light."))
tool("set_ambient_light", "Vehicle", "action",
     "Set the ambient interior lighting color and brightness, or turn it off with color \"off\".",
     {"color": P("str", one_of(AMBIENT_COLORS)),
      "brightness_pct": P("int", "integer from 10 to 100, in steps of 10. Default is 70. Ignored when color is \"off\".", False, 70)},
     writes=["vehicle.comfort.ambient_light_color", "vehicle.comfort.ambient_light_brightness_pct"])
tool("get_interior_lights_status", "Vehicle", "retrieve",
     "Return which reading lights are on and the ambient light color and brightness.",
     reads=paths("vehicle.comfort.reading_light.") + ["vehicle.comfort.ambient_light_color", "vehicle.comfort.ambient_light_brightness_pct"])

# ======================================================== vehicle: climate
tool("set_climate_temperature", "Vehicle", "action",
     "Set the target temperature of one climate zone or all zones. Policy: if the result leaves more than 3 Celsius between zones, tell the driver.",
     {"zone": P("str", one_of(["front_left", "front_right", "rear", "all"]) + " \"front_left\" is the driver zone."),
      "temperature_c": P("float", "number from 16.0 to 28.0, in steps of 0.5.")},
     writes=paths("vehicle.climate.temperature_c."))
tool("set_fan_speed", "Vehicle", "action",
     "Set the climate fan speed. This switches climate auto mode off.",
     {"speed": P("int", "integer from 0 to 5. 0 is off.")},
     writes=["vehicle.climate.fan_speed", "vehicle.climate.auto_mode"])
tool("set_airflow_direction", "Vehicle", "action",
     "Set where the climate fan blows air. This switches climate auto mode off.",
     {"direction": P("str", one_of(AIRFLOW))},
     writes=["vehicle.climate.airflow_direction", "vehicle.climate.auto_mode"])
tool("set_air_conditioning", "Vehicle", "action",
     "Turn the air conditioning compressor on or off. Policy: when turning it on, also close any window open beyond 20 (`set_window_position`) and raise the fan speed to 1 if it is 0 (`set_fan_speed`).",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=["vehicle.climate.ac_on"])
tool("set_air_circulation", "Vehicle", "action",
     "Set the air intake mode: automatic, fresh outside air, or recirculated cabin air.",
     {"mode": P("str", one_of(["auto", "fresh_air", "recirculation"]))},
     writes=["vehicle.climate.air_circulation"])
tool("set_defrost", "Vehicle", "action",
     "Turn the front windshield defrost, the rear window defrost, or both on or off. Policy: when turning on front defrost, also raise the fan speed to at least 2 (`set_fan_speed`), set an airflow direction that includes the windshield (`set_airflow_direction`), and turn on air conditioning (`set_air_conditioning`).",
     {"window": P("str", one_of(["front", "rear", "all"])),
      "on": P("bool", "true to turn on, false to turn off.")},
     writes=["vehicle.climate.front_defrost", "vehicle.climate.rear_defrost"])
tool("set_climate_auto_mode", "Vehicle", "action",
     "Turn climate auto mode on or off. In auto mode the car picks fan speed and airflow direction to reach the target temperatures.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=["vehicle.climate.auto_mode"])
tool("get_climate_status", "Vehicle", "retrieve",
     "Return the climate settings (auto mode, zone temperatures, fan speed, airflow direction, air conditioning, air circulation, defrost) plus the measured cabin and outside temperatures.",
     reads=paths("vehicle.climate.") + ["vehicle.telemetry.cabin_temp_c", "vehicle.telemetry.outside_temp_c"])

# ======================================================== vehicle: seats
tool("set_seat_heating", "Vehicle", "action",
     "Set the seat heating level for one seat or all seats. Policy: a seat cannot heat and ventilate at once, so setting heating above 0 on a front seat also needs that seat's ventilation set to 0 (`set_seat_ventilation`).",
     {"seat": P("str", one_of(SEATS4 + ["all"]) + " \"front_left\" is the driver seat."),
      "level": P("int", "integer from 0 to 3. 0 is off.")},
     writes=paths("vehicle.comfort.seat_heating."))
tool("set_seat_ventilation", "Vehicle", "action",
     "Set the seat ventilation (cooling) level for a front seat. Only the front seats have ventilation. Policy: setting ventilation above 0 also needs that seat's heating set to 0 (`set_seat_heating`).",
     {"seat": P("str", one_of(FRONT2 + ["both"]) + " \"front_left\" is the driver seat."),
      "level": P("int", "integer from 0 to 3. 0 is off.")},
     writes=paths("vehicle.comfort.seat_ventilation."))
tool("set_seat_massage", "Vehicle", "action",
     "Start, change, or stop the massage program of a front seat. Only the front seats have massage.",
     {"seat": P("str", one_of(FRONT2 + ["both"]) + " \"front_left\" is the driver seat."),
      "mode": P("str", one_of(["off", "wave", "pulse", "stretch", "lumbar"])),
      "intensity": P("int", "integer from 1 to 3. Default is 2. Ignored when mode is \"off\".", False, 2)},
     writes=paths("vehicle.comfort.seat_massage_mode.") + paths("vehicle.comfort.seat_massage_intensity."))
tool("set_seat_fore_aft", "Vehicle", "action",
     "Move a front seat forward or back. Moving the driver seat (\"front_left\") is blocked while `vehicle.telemetry.speed_kph` is above 0. For relative requests, read the current position with `get_seat_status` first.",
     {"seat": P("str", one_of(FRONT2) + " \"front_left\" is the driver seat."),
      "position_pct": P("int", "integer from 0 to 100, in steps of 5. 0 is fully forward, 100 fully back.")},
     writes=["vehicle.comfort.seat_fore_aft_pct.front_left", "vehicle.comfort.seat_fore_aft_pct.front_right"])
tool("set_seat_backrest", "Vehicle", "action",
     "Change the backrest angle of a front seat. Changing the driver seat (\"front_left\") is blocked while `vehicle.telemetry.speed_kph` is above 0. For relative requests, read the current angle with `get_seat_status` first.",
     {"seat": P("str", one_of(FRONT2) + " \"front_left\" is the driver seat."),
      "angle_deg": P("int", "integer from 5 to 40. Degrees from vertical.")},
     writes=["vehicle.comfort.seat_backrest_angle_deg.front_left", "vehicle.comfort.seat_backrest_angle_deg.front_right"])
tool("recall_driver_memory_profile", "Vehicle", "action",
     "Move the driver seat to a saved memory profile. " + "Blocked while `vehicle.telemetry.speed_kph` is above 0.",
     {"profile": P("int", "integer from 1 to 3.")},
     writes=["vehicle.comfort.driver_memory_profile", "vehicle.comfort.seat_fore_aft_pct.front_left", "vehicle.comfort.seat_backrest_angle_deg.front_left"])
tool("set_steering_wheel_heating", "Vehicle", "action",
     "Set the steering wheel heating level.",
     {"level": P("int", "integer from 0 to 3. 0 is off.")},
     writes=["vehicle.comfort.steering_wheel_heating"])
tool("get_seat_status", "Vehicle", "retrieve",
     "Return seat occupancy, seat heating, ventilation, massage, front seat positions, the last recalled driver memory profile, and steering wheel heating.",
     reads=paths("vehicle.comfort.seat_") + ["vehicle.comfort.driver_memory_profile", "vehicle.comfort.steering_wheel_heating"])

# ======================================================== media
tool("set_media_volume", "Media", "action",
     "Set the audio volume. Setting a volume also unmutes the audio.",
     {"volume": P("int", "integer from 0 to 30.")},
     writes=["vehicle.media.volume", "vehicle.media.muted"])
tool("set_media_mute", "Media", "action",
     "Mute or unmute the audio without changing the volume.",
     {"muted": P("bool", "true to mute, false to unmute.")},
     writes=["vehicle.media.muted"])
tool("set_media_source", "Media", "action",
     "Switch the audio source. Playback continues from the new source.",
     {"source": P("str", one_of(["fm_radio", "dab_radio", "bluetooth", "usb", "streaming"]))},
     writes=["vehicle.media.source", "vehicle.media.playing"])
tool("set_media_playback", "Media", "action",
     "Play or pause the current audio source.",
     {"playing": P("bool", "true to play, false to pause.")},
     writes=["vehicle.media.playing"])
tool("skip_media_track", "Media", "action",
     "Skip to the next or previous track on the current source and keep playing. Not available on \"fm_radio\" or \"dab_radio\".",
     {"direction": P("str", one_of(["next", "previous"]))},
     writes=["vehicle.media.playing"])
tool("tune_fm_radio", "Media", "action",
     "Tune the FM radio to a frequency and switch the audio source to FM radio.",
     {"frequency_mhz": P("float", "number from 87.5 to 108.0, in steps of 0.1.")},
     writes=["vehicle.media.fm_frequency_mhz", "vehicle.media.source", "vehicle.media.playing"])
tool("play_media_by_query", "Media", "action",
     "Search the streaming service for a song, artist, album, playlist, or podcast and start playing the best match. Switches the audio source to streaming.",
     {"query": P("str", "free text naming what to play.", samples=["Bohemian Rhapsody", "Norah Jones", "lo-fi focus playlist", "the latest episode of a daily news podcast"]),
      "media_type": P("str", one_of(["any", "song", "artist", "album", "playlist", "podcast"]) + " Default is \"any\".", False, "any")},
     writes=["vehicle.media.source", "vehicle.media.playing"])
tool("get_media_status", "Media", "retrieve",
     "Return the audio source, whether it is playing, the volume, mute state, and the tuned FM frequency.",
     reads=paths("vehicle.media."))

# ======================================================== telemetry & maintenance
tool("get_driving_status", "Vehicle", "retrieve",
     "Return the current speed, selected gear, and odometer. Use it to check whether the car is stopped in park before actions that require it.",
     reads=["vehicle.telemetry.speed_kph", "vehicle.telemetry.gear", "vehicle.telemetry.odometer_km"])
tool("get_tire_pressure", "Vehicle", "retrieve",
     "Return the pressure of all four tires in kPa and flag any tire below 200 kPa as low.",
     reads=paths("vehicle.telemetry.tire_pressure_kpa."))
tool("get_maintenance_status", "Vehicle", "retrieve",
     "Return engine oil life, washer fluid level, and the distance until the next scheduled service.",
     reads=["vehicle.telemetry.oil_life_pct", "vehicle.telemetry.washer_fluid_pct", "vehicle.telemetry.next_service_km", "vehicle.telemetry.odometer_km"])
tool("get_trip_info", "Vehicle", "retrieve",
     "Return the trip computer: distance since last reset, average fuel and electric consumption, and the share driven electrically.",
     reads=paths("vehicle.telemetry.trip_"))
tool("reset_trip_computer", "Vehicle", "action",
     "Reset the trip computer to zero. Ask for confirmation first, because the old trip values are lost.",
     writes=paths("vehicle.telemetry.trip_"))
tool("get_vehicle_specs", "Vehicle", "retrieve",
     "Return fixed facts about the car: exterior color, fuel tank capacity, usable battery capacity, reference consumption figures, and maximum AC and DC charging power.",
     reads=["vehicle.info.exterior_color", "vehicle.powertrain.fuel_tank_capacity_l", "vehicle.powertrain.battery_usable_capacity_kwh",
            "vehicle.powertrain.electric_consumption_kwh_per_100km", "vehicle.powertrain.fuel_consumption_l_per_100km",
            "vehicle.powertrain.max_ac_charging_kw", "vehicle.powertrain.max_dc_charging_kw"])

# ======================================================== hybrid powertrain & charging
ENERGY_READS = ["vehicle.powertrain.fuel_level_pct", "vehicle.powertrain.battery_soc_pct", "vehicle.powertrain.fuel_tank_capacity_l",
                "vehicle.powertrain.battery_usable_capacity_kwh", "vehicle.powertrain.electric_consumption_kwh_per_100km",
                "vehicle.powertrain.fuel_consumption_l_per_100km"]
tool("get_energy_status", "Energy", "retrieve",
     "Return the battery level, fuel level, estimated electric range, fuel range, and combined range in km, plus the current hybrid mode, drive mode, regen level, charge target, and whether the engine is running.",
     reads=ENERGY_READS + ["vehicle.powertrain.hybrid_mode", "vehicle.powertrain.drive_mode", "vehicle.powertrain.regen_level",
                           "vehicle.powertrain.battery_charge_target_pct", "vehicle.powertrain.engine_running"])
tool("set_hybrid_mode", "Energy", "action",
     "Choose how the hybrid system uses the battery and the engine. \"auto\" blends both, \"electric\" drives on battery only (blocked when `vehicle.powertrain.battery_soc_pct` is below 10), \"hold\" saves the current battery charge for later (for example a city zone at the destination), \"charge\" runs the engine to charge the battery up to `charge_target_pct`. Policy: in \"charge\" mode warn that fuel consumption rises.",
     {"mode": P("str", one_of(["auto", "electric", "hold", "charge"])),
      "charge_target_pct": P("int", "integer from 20 to 80, in steps of 10. Default is 60. Used only when mode is \"charge\".", False, 60)},
     writes=["vehicle.powertrain.hybrid_mode", "vehicle.powertrain.battery_charge_target_pct", "vehicle.powertrain.engine_running"])
tool("set_drive_mode", "Energy", "action",
     "Set the driving dynamics mode, which changes throttle response and efficiency.",
     {"mode": P("str", one_of(["eco", "comfort", "sport"]))},
     writes=["vehicle.powertrain.drive_mode"])
tool("set_regen_level", "Energy", "action",
     "Set the regenerative braking strength.",
     {"level": P("int", "integer from 0 to 3. 0 is coasting, 3 is strongest.")},
     writes=["vehicle.powertrain.regen_level"])
tool("get_charging_settings", "Energy", "retrieve",
     "Return the plug-in charging settings: whether a cable is connected, the charge limit, and the delayed charging schedule.",
     reads=["vehicle.powertrain.plugged_in", "vehicle.powertrain.charge_limit_pct",
            "vehicle.powertrain.scheduled_charging_enabled", "vehicle.powertrain.scheduled_charging_start_hour",
            "vehicle.powertrain.max_ac_charging_kw", "vehicle.powertrain.max_dc_charging_kw"])
tool("set_charge_limit", "Energy", "action",
     "Set the battery level at which plug-in charging stops.",
     {"limit_pct": P("int", "integer from 50 to 100, in steps of 5.")},
     writes=["vehicle.powertrain.charge_limit_pct"])
tool("set_scheduled_charging", "Energy", "action",
     "Turn delayed plug-in charging on or off and set the hour it starts, for example to use cheaper night-time electricity.",
     {"enabled": P("bool", "true to delay charging until the start hour, false to charge as soon as the cable is plugged in."),
      "start_hour": P("int", "integer from 0 to 23, local time on a 24-hour clock. Default is 22. Used only when enabled is true.", False, 22)},
     writes=["vehicle.powertrain.scheduled_charging_enabled", "vehicle.powertrain.scheduled_charging_start_hour"])
tool("estimate_charging_time", "Energy", "retrieve",
     "Estimate how many minutes plug-in charging takes from a start battery level to a target level at a given charger. The charging power is capped by the car's maximum AC or DC power. Charger power and type come from the charging plugs returned by `search_poi_at_location` or `search_poi_along_route`.",
     {"charger_power_kw": P("float", "number from 2.3 to 350.0. Rated power of the charger plug."),
      "charger_type": P("str", one_of(["ac", "dc"])),
      "target_soc_pct": P("int", "integer from 1 to 100. Must be above the start level."),
      "start_soc_pct": P("int", "integer from 0 to 99. Use the current battery level from `get_energy_status` unless the driver names another start level.")},
     reads=["vehicle.powertrain.battery_soc_pct", "vehicle.powertrain.battery_usable_capacity_kwh",
            "vehicle.powertrain.max_ac_charging_kw", "vehicle.powertrain.max_dc_charging_kw", "vehicle.powertrain.charge_limit_pct"])
tool("estimate_soc_after_charging", "Energy", "retrieve",
     "Estimate the battery level after charging for a given number of minutes at a given charger. Charger power and type come from `search_poi_at_location` or `search_poi_along_route`.",
     {"charger_power_kw": P("float", "number from 2.3 to 350.0. Rated power of the charger plug."),
      "charger_type": P("str", one_of(["ac", "dc"])),
      "minutes": P("int", "integer from 1 to 720."),
      "start_soc_pct": P("int", "integer from 0 to 99. Use the current battery level from `get_energy_status` unless the driver names another start level.")},
     reads=["vehicle.powertrain.battery_soc_pct", "vehicle.powertrain.battery_usable_capacity_kwh",
            "vehicle.powertrain.max_ac_charging_kw", "vehicle.powertrain.max_dc_charging_kw", "vehicle.powertrain.charge_limit_pct"])
tool("estimate_electric_distance", "Energy", "retrieve",
     "Estimate how many km the car can drive on electric power alone between two battery levels.",
     {"from_soc_pct": P("int", "integer from 1 to 100. Use the current battery level from `get_energy_status` unless the driver names another start level."),
      "to_soc_pct": P("int", "integer from 0 to 99. Must be below the start level. Default is 0.", False, 0)},
     reads=["vehicle.powertrain.battery_soc_pct", "vehicle.powertrain.battery_usable_capacity_kwh", "vehicle.powertrain.electric_consumption_kwh_per_100km"])
tool("estimate_refuel", "Energy", "retrieve",
     "Estimate how many liters are needed to fill the tank to a target level, and the added fuel range in km.",
     {"target_fuel_pct": P("int", "integer from 1 to 100. Default is 100.", False, 100)},
     reads=["vehicle.powertrain.fuel_level_pct", "vehicle.powertrain.fuel_tank_capacity_l", "vehicle.powertrain.fuel_consumption_l_per_100km"])
tool("estimate_route_energy", "Energy", "retrieve",
     "Estimate how much of a route can be driven electrically, how much fuel the rest needs, and whether the car reaches the end without charging or refueling. The route ID comes from `get_routes` or `get_navigation_status`.",
     {"route_id": P("str", "route ID returned by `get_routes` or `get_navigation_status`.")},
     reads=ENERGY_READS + ["vehicle.powertrain.hybrid_mode"])

# ======================================================== navigation
POI_CATEGORIES = ["gas_station", "charging_station", "restaurant", "fast_food", "cafe", "bakery", "supermarket", "parking", "public_toilet", "hotel", "airport", "pharmacy", "hospital", "car_wash"]
tool("get_location_id_by_name", "Navigation", "retrieve",
     "Look up the location ID of a city, address, or named place. Navigation, route, weather, and POI tools need this ID.",
     {"name": P("str", "free text name of the city, address, or place.", samples=["Munich", "Chico", "Sacramento International Airport", "1200 Main Street, Madison"])},
     external=True)
tool("search_poi_at_location", "Navigation", "retrieve",
     "Find points of interest of one category near a location. Results include POI IDs, distance, opening hours, phone number, and, for charging stations, the plugs with their power in kW and AC or DC type. The location ID comes from `get_location_id_by_name`.",
     {"location_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "category": P("str", one_of(POI_CATEGORIES)),
      "open_now_only": P("bool", "true to return only places open right now. Default is false.", False, False)},
     external=True)
tool("search_poi_along_route", "Navigation", "retrieve",
     "Find points of interest of one category along a route, with the km along the route and the detour time. Results include the same details as `search_poi_at_location`. The route ID comes from `get_routes` or `get_navigation_status`.",
     {"route_id": P("str", "route ID returned by `get_routes` or `get_navigation_status`."),
      "category": P("str", one_of(POI_CATEGORIES)),
      "max_detour_minutes": P("int", "integer from 1 to 30. Default is 10.", False, 10)},
     external=True)
tool("get_routes", "Navigation", "retrieve",
     "Return up to three route options between two locations with route IDs, distance, duration, toll roads, and road types. Respects the current avoid-tolls and avoid-highways options. Location IDs come from `get_location_id_by_name`.",
     {"destination_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "start_id": P("str", "location ID returned by `get_location_id_by_name`. Default is \"current\", the car's current location.", False, "current")},
     reads=["navigation.avoid_tolls", "navigation.avoid_highways"])
tool("convert_route_distance_and_time", "Navigation", "retrieve",
     "On a given route, convert a distance in km into driving time, or a driving time in minutes into distance. The route ID comes from `get_routes` or `get_navigation_status`.",
     {"route_id": P("str", "route ID returned by `get_routes` or `get_navigation_status`."),
      "value": P("float", "number from 0.0 to 2000.0. A distance in km or a time in minutes, as set by `unit`."),
      "unit": P("str", one_of(["km", "minutes"]))},
     external=True)
NAV_STOPS = ["navigation.active", "navigation.destination_id", "navigation.waypoint_1_id", "navigation.waypoint_2_id", "navigation.waypoint_3_id", "navigation.route_id"]
tool("set_navigation", "Navigation", "action",
     "Start guidance from the current location to a destination, with up to three intermediate stops in order. Use only when navigation is not active; if it is active, use the add, replace, or delete tools instead. Location IDs come from `get_location_id_by_name`, and the route ID of the first leg from `get_routes`.",
     {"destination_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "route_id": P("str", "route ID of the first leg, returned by `get_routes`."),
      "waypoint_ids": P("list", "list of 0 to 3 location IDs from `get_location_id_by_name`, in driving order. Default is an empty list.", False, [])},
     writes=NAV_STOPS)
tool("add_navigation_waypoint", "Navigation", "action",
     "Insert an intermediate stop into the active route. Only works while navigation is active and fewer than three stops are set. Call one at a time, never in parallel, because stop numbers shift.",
     {"location_id": P("str", "location ID returned by `get_location_id_by_name`."),
      "position": P("int", "integer from 1 to 3. The stop number the new stop gets; later stops move back. Default is 1.", False, 1)},
     writes=NAV_STOPS)
tool("replace_navigation_waypoint", "Navigation", "action",
     "Replace one intermediate stop of the active route with another location. Only works while navigation is active and that stop exists.",
     {"position": P("int", "integer from 1 to 3. The stop number to replace."),
      "location_id": P("str", "location ID returned by `get_location_id_by_name`.")},
     writes=NAV_STOPS)
tool("delete_navigation_waypoint", "Navigation", "action",
     "Remove one intermediate stop from the active route. Only works while navigation is active and that stop exists. Call one at a time, never in parallel, because stop numbers shift.",
     {"position": P("int", "integer from 1 to 3. The stop number to remove.")},
     writes=NAV_STOPS)
tool("replace_navigation_destination", "Navigation", "action",
     "Replace the final destination of the active route and keep the intermediate stops. Only works while navigation is active.",
     {"location_id": P("str", "location ID returned by `get_location_id_by_name`.")},
     writes=NAV_STOPS)
tool("delete_navigation_destination", "Navigation", "action",
     "Remove the final destination so the last intermediate stop becomes the destination. Only works while navigation is active and at least one intermediate stop exists; otherwise use `cancel_navigation`.",
     writes=NAV_STOPS)
tool("cancel_navigation", "Navigation", "action",
     "Stop guidance and clear the destination and all stops.",
     writes=NAV_STOPS)
tool("set_route_options", "Navigation", "action",
     "Set whether route planning avoids toll roads and highways. Applies to the next `get_routes` call; an active route is not recalculated.",
     {"avoid_tolls": P("bool", "true to avoid toll roads, false to allow them."),
      "avoid_highways": P("bool", "true to avoid highways, false to allow them.")},
     writes=["navigation.avoid_tolls", "navigation.avoid_highways"])
tool("set_voice_guidance", "Navigation", "action",
     "Turn spoken turn-by-turn navigation guidance on or off.",
     {"on": P("bool", "true to turn on, false to turn off.")},
     writes=["navigation.voice_guidance_on"])
tool("get_navigation_status", "Navigation", "retrieve",
     "Return whether guidance is active, the destination, intermediate stops, current route ID, route options, and voice guidance state.",
     reads=paths("navigation."))

# ======================================================== weather, communication, preferences, utilities
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
     "Add or subtract hours and minutes to a time, for example to work out an arrival time.",
     {"time": P("str", "time as HH:MM on a 24-hour clock, or \"now\".", samples=["now", "14:35"]),
      "add_minutes": P("int", "integer from -1440 to 1440. Negative values subtract.")},
     external=True)

# ======================================================== negative tools
NEG = {}


def neg(name, domain, kind, desc, params=None):
    NEG[name] = {"description": desc, "domain": domain, "kind": kind, "parameters": params or {}, "sample_commands": []}


neg("set_home_thermostat", "SmartHome", "action",
    "Set the target temperature of the home thermostat.",
    {"temperature_c": P("float", "number from 10.0 to 30.0, in steps of 0.5.")})
neg("set_home_lights", "SmartHome", "action",
    "Turn lights in a room of the home on or off and set their color.",
    {"room": P("str", one_of(["living_room", "bedroom", "kitchen", "garden"])),
     "on": P("bool", "true to turn on, false to turn off."),
     "color": P("str", one_of(["warm_white", "cool_white", "red", "blue", "green"]) + " Default is \"warm_white\".", False, "warm_white")})
neg("lock_home_door", "SmartHome", "action",
    "Lock or unlock the smart lock on the home's front door.",
    {"locked": P("bool", "true to lock, false to unlock.")})
neg("play_on_home_speaker", "SmartHome", "action",
    "Play music on a smart speaker at home.",
    {"query": P("str", "free text naming what to play.", samples=["jazz for dinner"]),
     "room": P("str", one_of(["living_room", "bedroom", "kitchen"]))})
neg("start_home_wallbox_charging", "SmartHome", "action",
    "Start charging on the home wallbox app account. This controls the home charger's own app, not the car.",
    {"max_current_a": P("int", "integer from 6 to 32.")})
neg("set_phone_alarm", "Phone", "action",
    "Set an alarm on the user's phone.",
    {"time": P("str", "time as HH:MM on a 24-hour clock.", samples=["06:30"])})
neg("set_phone_ringer_volume", "Phone", "action",
    "Change the phone's own ringer volume.",
    {"level": P("int", "integer from 0 to 10.")})
neg("book_flight", "Travel", "action",
    "Search and book a flight ticket.",
    {"origin": P("str", "free text city or airport code.", samples=["SFO"]),
     "destination": P("str", "free text city or airport code.", samples=["ORD"]),
     "date": P("str", "date as YYYY-MM-DD.", samples=["2026-11-02"])})
neg("order_food_delivery", "Shopping", "action",
    "Order food for delivery to a home address.",
    {"restaurant": P("str", "free text restaurant name.", samples=["Corner Noodle House"]),
     "items": P("list", "list of 1 to 10 free text item names.")})
neg("transfer_money", "Finance", "action",
    "Transfer money from the user's bank account to another account.",
    {"recipient": P("str", "free text recipient name or account number.", samples=["Savings account"]),
     "amount": P("float", "number from 0.01 to 10000.0.")})
neg("create_document", "Productivity", "action",
    "Create a new text document in the user's cloud drive.",
    {"title": P("str", "free text document title.", samples=["Trip notes"]),
     "content": P("str", "free text document content.", samples=["Packing list: charger cable, snacks"])})
neg("post_to_social_media", "Social", "action",
    "Publish a post on the user's social media account.",
    {"text": P("str", "free text post content.", samples=["Road trip day!"])})

# ======================================================== validate
errors = []
inv_tools = TOOL_STATE
for name, spec in {**TOOLS, **NEG}.items():
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        errors.append(f"bad name {name}")
    assert set(spec) == {"description", "domain", "kind", "parameters", "sample_commands"}
    assert spec["kind"] in ("action", "retrieve")
    for pn, p in spec["parameters"].items():
        assert p["type"] in ("str", "int", "float", "bool", "list", "dict"), (name, pn)
        if not p["required"] and "default" not in p:
            errors.append(f"{name}.{pn} missing default")
        d = p["description"]
        if p["type"] in ("int", "float") and not re.search(r"(integer|number) from -?[\d.]+ to -?[\d.]+", d):
            errors.append(f"{name}.{pn} numeric without range")
        if p["type"] == "str" and "sample_values" not in p and "one of" not in d and "ID" not in d and "time as" not in d and "date as" not in d:
            errors.append(f"{name}.{pn} str without enum or samples")
for name in TOOLS:
    if name not in inv_tools:
        errors.append(f"{name} missing in inventory tools")
    t = inv_tools[name]
    if t.get("external"):
        continue
    key = "writes" if TOOLS[name]["kind"] == "action" else "reads"
    if key not in t or not t[key]:
        errors.append(f"{name} missing {key}")
    for p in t.get(key, []):
        if p not in STATE:
            errors.append(f"{name}: undefined state {p}")
read_paths = {p for t in inv_tools.values() for p in t.get("reads", [])}
written = {p for t in inv_tools.values() for p in t.get("writes", [])}
for p in written - read_paths:
    errors.append(f"state {p} is written but no retrieve tool reads it")
for p in set(STATE) - read_paths - written:
    errors.append(f"state {p} is unused")
for p, s in STATE.items():
    if s["type"] in ("int", "float") and "enum" not in s and "minimum" not in s:
        errors.append(f"state {p} numeric without bounds")
    if s["type"] == "str" and "enum" not in s and s["initial"] != "fixed":
        errors.append(f"state {p} free str must be fixed")
    if s["initial"] == "from_weather" and "Usually" not in s["description"] and "weather" not in s["description"] and "Should" not in s["description"]:
        pass
for name in NEG:
    if name in TOOLS:
        errors.append(f"negative tool {name} duplicates a positive tool")
if errors:
    print("\n".join(errors))
    sys.exit(1)

OUT.mkdir(parents=True, exist_ok=True)
(OUT / f"{PREFIX}_positive_tools_spec.json").write_text(json.dumps(TOOLS, indent=2, ensure_ascii=False) + "\n")
(OUT / f"{PREFIX}_negative_tools_spec.json").write_text(json.dumps(NEG, indent=2, ensure_ascii=False) + "\n")
(OUT / f"{PREFIX}_state_inventory.json").write_text(json.dumps({"state": STATE, "tools": inv_tools}, indent=2, ensure_ascii=False) + "\n")

from collections import Counter
print("positive", len(TOOLS), Counter((t["domain"], t["kind"]) for t in TOOLS.values()))
print("negative", len(NEG))
print("state", len(STATE), Counter(p.split(".")[1] if p.startswith("vehicle") else p.split(".")[0] for p in STATE))
print("external", sum(1 for t in inv_tools.values() if t.get("external")))
