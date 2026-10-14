# AI-powered cockpit assistant tools VSS

**113 tools** in total: **101 positive** and **12 negative**, over **146 vehicle state values** named after [COVESA VSS](https://github.com/COVESA/vehicle_signal_specification) signals (129 standard, 17 extensions). The spec files are the `2026-10-14_hybrid_vss_*` files in this folder.

Of the 101 positive tools, **52 come from CAR-bench** (32 with the same capability, 20 extended) and **49 are new**.

## Positive tools by domain

| Domain | Action | Retrieve | Total | From CAR-bench | New |
|---|---|---|---|---|---|
| Vehicle (Body, lights, climate, seats, vehicle status) | 35 | 19 | 54 | 26 | 28 |
| Navigation (Routes, stops, places) | 10 | 6 | 16 | 13 | 3 |
| Energy (Hybrid powertrain, charging, fuel) | 6 | 7 | 13 | 4 | 9 |
| Media (Audio and radio) | 7 | 1 | 8 | – | 8 |
| Communication (Calls, texts, email, calendar) | 3 | 3 | 6 | 5 | 1 |
| Utility (Math and time) | – | 2 | 2 | 2 | – |
| Weather (Conditions at a place today) | – | 1 | 1 | 1 | – |
| Preferences (Saved driver preferences) | – | 1 | 1 | 1 | – |
| **Total** | **61** | **40** | **101** | **52** | **49** |

CAR-bench has 57 tools. All of them are covered except `think` and `planning_tool`, which are reasoning scaffolds for the agent rather than features for the driver.

Origin tags used below:

- **CAR-bench**: the same capability as a CAR-bench tool, sometimes renamed or merged from several getters.
- **CAR-bench, extended**: built on a CAR-bench tool, with added parameters, values, or state.
- **New**: not in CAR-bench.

## Positive tools

### Vehicle (54)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `set_window_position` | `window: str`, `position?: int` | action | CAR-bench | `open_close_window` | Open or close one window, or all four, to a position from 0 (closed) to 100 (fully open). |
| `set_window_child_lock` | `on: bool` | action | New | – | Disable or enable the rear passengers' window switches, so only the driver can move the rear windows. |
| `get_window_positions` | – | retrieve | CAR-bench | `get_vehicle_window_positions` | Return the opening position of all four windows and whether the rear window switches are locked. |
| `set_sunshade_position` | `position?: int` | action | CAR-bench | `open_close_sunshade` | Open or close the sunroof shade from 0 (closed) to 100 (fully open). |
| `set_sunroof_position` | `position?: int` | action | CAR-bench, extended | `open_close_sunroof` | Open, close, or tilt the sunroof. Adds tilt, as VSS models it. |
| `get_sunroof_and_sunshade_position` | – | retrieve | CAR-bench | `get_sunroof_and_sunshade_position` | Return the sunroof position (negative means tilted) and the sunroof shade position. |
| `set_rear_window_shade` | `position?: int` | action | New | – | Raise or lower the rear window sun shade. |
| `get_rear_window_shade_position` | – | retrieve | New | – | Return how far the rear window sun shade is raised. |
| `set_door_locks` | `door?: str`, `locked: bool` | action | New | – | Lock or unlock one door or all doors. |
| `get_door_status` | – | retrieve | New | – | Return which doors are locked and whether the rear child safety locks are engaged. |
| `set_trunk` | `open: bool` | action | CAR-bench, extended | `open_close_trunk_door` | Open or close the power trunk lid. Adds the stopped-in-park rule. |
| `set_trunk_lock` | `locked: bool` | action | New | – | Lock or unlock the trunk separately from the doors, for example to keep valet staff out. |
| `get_trunk_status` | – | retrieve | CAR-bench, extended | `get_trunk_door_position` | Return whether the trunk lid is open and whether the trunk is locked. Adds the trunk lock. |
| `set_fuel_door` | `open: bool` | action | New | – | Open or close the fuel filler door for refueling. |
| `get_fuel_door_status` | – | retrieve | New | – | Return whether the fuel filler door is open. |
| `set_charge_port` | `open: bool` | action | New | – | Open or close the charging port door. |
| `set_charging_cable_lock` | `locked: bool` | action | New | – | Lock or release the charging cable in the port. |
| `get_charge_port_status` | – | retrieve | New | – | Return whether the charge port door is open, whether a cable is connected, and whether the cable is locked. |
| `set_low_beams` | `on: bool` | action | CAR-bench | `set_head_lights_low_beams` | Turn the low beam headlights on or off. |
| `set_high_beams` | `on: bool` | action | CAR-bench | `set_head_lights_high_beams` | Turn the high beam headlights on or off. |
| `set_fog_lights` | `which: str`, `on: bool` | action | CAR-bench, extended | `set_fog_lights` | Turn the front fog lights, the rear fog light, or both on or off. Adds the rear fog light. |
| `set_hazard_lights` | `on: bool` | action | New | – | Turn the hazard warning lights on or off. |
| `get_exterior_lights_status` | – | retrieve | CAR-bench, extended | `get_exterior_lights_status` | Return whether the low beams, high beams, front fog lights, rear fog light, and hazard lights are on. Adds the rear fog light and hazard lights. |
| `set_wipers` | `window: str`, `mode: str`, `intensity?: int` | action | New | – | Set the front or rear wiper mode, and for the front wiper the interval or rain sensor sensitivity. |
| `get_wiper_status` | – | retrieve | New | – | Return the front and rear wiper modes and the front wiper intensity. |
| `set_side_mirrors_folded` | `folded: bool` | action | New | – | Fold or unfold both exterior mirrors. |
| `set_mirror_heating` | `on: bool` | action | New | – | Turn exterior mirror heating on or off for both mirrors, to clear ice, frost, or fog. |
| `get_side_mirror_status` | – | retrieve | New | – | Return whether each exterior mirror is folded and whether its heating is on. |
| `set_reading_light` | `seat: str`, `on: bool` | action | CAR-bench | `set_reading_light` | Turn the reading light at one seat, or at all seats, on or off. |
| `get_reading_lights_status` | – | retrieve | CAR-bench | `get_reading_lights_status` | Return which seats have their reading light on. |
| `set_ambient_light` | `on: bool`, `color?: str`, `brightness_pct?: int` | action | CAR-bench, extended | `set_ambient_lights` | Set the ambient interior lighting in all four zones: on or off, color, and brightness. Adds brightness and sets four zones. |
| `get_ambient_light_status` | – | retrieve | CAR-bench, extended | `get_ambient_light_status_and_color` | Return, for each ambient light zone, whether it is on, its color code, and its brightness. Adds brightness. |
| `set_climate_temperature` | `zone: str`, `temperature_c: float` | action | CAR-bench, extended | `set_climate_temperature` | Set the target temperature of one climate zone, both rear zones, or all zones. Adds a rear zone. |
| `set_fan_speed` | `zone?: str`, `level: int` | action | CAR-bench, extended | `set_fan_speed` | Set the fan speed of one climate zone or all zones. Sets each climate zone separately, as VSS models it. |
| `set_air_distribution` | `zone?: str`, `direction: str` | action | CAR-bench, extended | `set_fan_airflow_direction` | Set where a climate zone blows air: up to the windshield, middle to the face, or down to the feet. Uses VSS's per-zone up, middle, and down directions. |
| `set_air_conditioning` | `on: bool` | action | CAR-bench | `set_air_conditioning` | Turn the air conditioning compressor on or off. |
| `set_air_recirculation` | `on: bool` | action | CAR-bench | `set_air_circulation` | Switch between recirculating cabin air and drawing fresh outside air. VSS models it as on or off. |
| `set_defrost` | `window: str`, `on: bool` | action | CAR-bench | `set_window_defrost` | Turn the front windshield defroster, the rear window defroster, or both on or off. |
| `set_climate_auto_mode` | `on: bool` | action | New | – | Turn climate auto mode on or off. |
| `get_climate_status` | – | retrieve | CAR-bench, extended | `get_climate_settings`, `get_temperature_inside_car` | Return the climate settings (auto mode, each zone's temperature, fan speed, and air distribution, air conditioning, recirculation, defrosters) plus the measured cabin temperature and the outside temperature and humidity. Merges two CAR-bench getters and adds auto mode, four zones, and measured cabin and outside temperature and humidity. |
| `set_seat_heating` | `seat: str`, `level: int` | action | CAR-bench, extended | `set_seat_heating` | Set seat heating for one seat or all seats. Adds the rear seats. |
| `set_seat_ventilation` | `seat: str`, `level: int` | action | New | – | Set seat ventilation (cooling) for a front seat. |
| `set_seat_massage` | `seat: str`, `program?: str`, `level: int` | action | New | – | Start, change, or stop the massage of a front seat. |
| `set_seat_position` | `seat: str`, `position_mm: int` | action | New | – | Move a front seat forward or back. |
| `set_seat_recline` | `seat: str`, `angle_deg: int` | action | New | – | Change the backrest recline of a front seat. |
| `recall_seat_memory` | `profile: int` | action | New | – | Move the driver seat to a saved memory profile. |
| `set_steering_wheel_heating` | `level: int` | action | CAR-bench | `set_steering_wheel_heating` | Set the steering wheel heating level. |
| `get_seat_status` | – | retrieve | CAR-bench, extended | `get_seat_heating_level`, `get_seats_occupancy`, `get_steering_wheel_heating_level` | Return seat occupancy, each seat's heating or ventilation, front seat massage, front seat position and recline, the last recalled memory profile, and steering wheel heating. Merges three CAR-bench getters and adds ventilation, massage, and seat position. |
| `get_driving_status` | – | retrieve | New | – | Return the current speed, the selected gear (126 park, 127 drive, 0 neutral, -1 reverse), and the odometer. |
| `get_tire_pressure` | – | retrieve | New | – | Return the pressure of all four tires in kPa and which tires have a low-pressure warning. |
| `get_maintenance_status` | – | retrieve | New | – | Return the distance to the next service, whether service is due, the engine oil level, the washer fluid level, and the 12 V battery voltage. |
| `get_trip_info` | – | retrieve | New | – | Return the trip meter, trip duration, average speed, and average fuel consumption. |
| `reset_trip_meter` | – | action | New | – | Reset the trip meter to zero. |
| `get_vehicle_specs` | – | retrieve | CAR-bench, extended | `get_car_color` | Return fixed facts about the car: exterior color, powertrain and hybrid type, fuel tank capacity, usable battery capacity, and maximum AC and DC charging power. Adds tank, battery, consumption, and charging specs. |

### Navigation (16)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_location_id_by_name` | `name: str` | retrieve | CAR-bench | `get_location_id_by_location_name` | Look up the location ID of a city, address, or named place. |
| `search_poi_at_location` | `location_id: str`, `category: str`, `filters?: list` | retrieve | CAR-bench, extended | `search_poi_at_location` | Find points of interest of one category near a location. Keeps CAR-bench's open-now, available-plug, and DC-plug filters and adds gas stations and other categories. |
| `search_poi_along_route` | `route_id: str`, `category: str`, `filters?: list`, `max_detour_minutes?: int` | retrieve | CAR-bench, extended | `search_poi_along_the_route` | Find points of interest of one category along a route, with the km along the route and the detour time. Keeps CAR-bench's filters and adds gas stations, other categories, and a detour limit. |
| `get_routes` | `destination_id: str`, `start_id?: str` | retrieve | CAR-bench, extended | `get_routes_from_start_to_destination` | Return up to three route options between two locations with route IDs, distance, duration, toll roads, and road types. Respects the avoid-tolls and avoid-highways options. |
| `convert_route_distance_and_time` | `route_id: str`, `value: float`, `unit: str` | retrieve | CAR-bench | `convert_route_distance_and_time` | On a given route, convert a distance in km into driving time, or a driving time in minutes into distance. |
| `set_navigation` | `destination_id: str`, `route_id: str`, `waypoint_ids?: list` | action | CAR-bench | `set_new_navigation` | Start guidance from the current location to a destination, with up to three intermediate stops in order. |
| `add_navigation_waypoint` | `location_id: str`, `position?: int` | action | CAR-bench | `navigation_add_one_waypoint` | Insert an intermediate stop into the active route. |
| `replace_navigation_waypoint` | `position: int`, `location_id: str` | action | CAR-bench | `navigation_replace_one_waypoint` | Replace one intermediate stop of the active route with another location. |
| `delete_navigation_waypoint` | `position: int` | action | CAR-bench | `navigation_delete_waypoint` | Remove one intermediate stop from the active route. |
| `replace_navigation_destination` | `location_id: str` | action | CAR-bench | `navigation_replace_final_destination` | Replace the final destination of the active route and keep the intermediate stops. |
| `delete_navigation_destination` | – | action | CAR-bench | `navigation_delete_destination` | Remove the final destination so the last intermediate stop becomes the destination. |
| `cancel_navigation` | – | action | CAR-bench | `delete_current_navigation` | Stop guidance and clear the destination and all stops. |
| `set_route_options` | `avoid_tolls: bool`, `avoid_highways: bool` | action | New | – | Set whether route planning avoids toll roads and highways. |
| `set_voice_guidance` | `mode: str` | action | New | – | Choose how much spoken navigation guidance plays: every instruction, alerts only, or none. |
| `set_navigation_volume` | `volume_pct: int` | action | New | – | Set the volume of the navigation voice, separately from the media volume. |
| `get_navigation_status` | – | retrieve | CAR-bench, extended | `get_current_navigation_state` | Return whether guidance is active, the destination and its coordinates, intermediate stops, the current route ID, whether the destination is reached, route options, and voice guidance mode and volume. Adds route options and voice guidance. |

### Energy (13)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_energy_status` | – | retrieve | CAR-bench, extended | `get_charging_specs_and_status`, `get_fuel_information` | Return the battery level, fuel level and low-fuel warning, the electric, fuel, and combined range in km (computed from the levels and reference consumption), the hybrid mode and how the hybrid is running, the drive mode, regen level, charge target, and whether the engine is running. Combines battery and fuel for the hybrid and adds hybrid mode, drive mode, and regen. |
| `set_hybrid_mode` | `mode: str`, `charge_target_pct?: int` | action | New | – | Choose how the hybrid uses the battery and the engine. |
| `set_drive_mode` | `mode: str` | action | New | – | Set the driving mode, which changes throttle response and efficiency. |
| `set_regen_level` | `level: int` | action | New | – | Set the regenerative braking strength. |
| `get_charging_status` | – | retrieve | New | – | Return the plug-in charging state: whether it is charging, the charge limit, the charging timer, and the car's maximum AC and DC charging power. |
| `set_charge_limit` | `limit_pct: int` | action | New | – | Set the battery level at which plug-in charging stops. |
| `set_charging_timer` | `mode: str`, `time?: str` | action | New | – | Set when plug-in charging runs: right away, starting at a time (for example cheaper night power), or finished by a time (for example a morning departure). |
| `start_stop_charging` | `action: str` | action | New | – | Start or stop plug-in charging now. |
| `estimate_charging_time` | `charging_station_id: str`, `plug_id: str`, `target_soc_pct: int`, `start_soc_pct: int` | retrieve | CAR-bench | `calculate_charging_time_by_soc` | Estimate how many minutes charging takes at a given charging station plug, from a start battery level to a target level. Takes the charging station and plug IDs, like CAR-bench. |
| `estimate_soc_after_charging` | `charging_station_id: str`, `plug_id: str`, `minutes: int`, `start_soc_pct: int` | retrieve | CAR-bench | `calculate_charging_soc_by_time` | Estimate the battery level after charging for a given number of minutes at a given charging station plug. Takes the charging station and plug IDs, like CAR-bench. |
| `estimate_electric_distance` | `from_soc_pct: int`, `to_soc_pct?: int` | retrieve | CAR-bench | `get_distance_by_soc` | Estimate how many km the car can drive on electric power alone between two battery levels. |
| `estimate_refuel` | `target_fuel_pct?: int` | retrieve | New | – | Estimate how many liters fill the tank to a target level, and the fuel range that adds in km. |
| `estimate_route_energy` | `route_id: str` | retrieve | New | – | Estimate how much of a route can be driven electrically, how much fuel the rest needs, and whether the car arrives without charging or refueling. |

### Media (8)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `set_media_volume` | `volume_pct: int` | action | New | – | Set the audio volume. |
| `set_media_mute` | `muted: bool` | action | New | – | Mute or unmute the audio without changing the volume. |
| `set_media_source` | `source: str` | action | New | – | Switch the audio source. |
| `set_media_playback` | `playing: bool` | action | New | – | Play or pause the current audio source. |
| `skip_media_track` | `direction: str` | action | New | – | Skip to the next or previous track on the current source and keep playing. |
| `tune_fm_radio` | `frequency_mhz: float` | action | New | – | Tune the FM radio to a frequency and switch the audio source to FM. |
| `play_media_by_query` | `query: str`, `media_type?: str` | action | New | – | Search the streaming service for a song, artist, album, playlist, or podcast and start playing the best match. |
| `get_media_status` | – | retrieve | New | – | Return the audio source, the last playback command, the volume, mute state, the tuned FM frequency, and the last item chosen by search. |

### Communication (6)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_contact_id_by_name` | `name: str` | retrieve | CAR-bench | `get_contact_id_by_contact_name` | Find contacts in the connected phone's address book by name and return their contact IDs. |
| `get_contact_details` | `contact_ids: list` | retrieve | CAR-bench | `get_contact_information` | Return the phone numbers and email addresses of contacts. |
| `call_phone_number` | `phone_number: str` | action | CAR-bench | `call_phone_by_number` | Place a hands-free call through the connected phone. |
| `send_text_message` | `phone_number: str`, `message: str` | action | New | – | Send a short SMS through the connected phone. |
| `send_email` | `to: list`, `subject: str`, `body: str` | action | CAR-bench | `send_email` | Send a short email from the driver's connected account. |
| `get_calendar_events` | `from_hour?: int` | retrieve | CAR-bench | `get_entries_from_calendar` | Return today's calendar events with start time, duration, topic, location, and attendees. |

### Utility (2)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `calculate_math` | `expression: str` | retrieve | CAR-bench | `calculate_math` | Evaluate an arithmetic expression, for example to add up distances or costs. |
| `calculate_datetime` | `time: str`, `add_minutes: int` | retrieve | CAR-bench | `calculate_datetime` | Add or subtract minutes to a time, for example to work out an arrival time. |

### Weather (1)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_weather` | `location_id: str`, `time?: str` | retrieve | CAR-bench | `get_weather` | Return the weather condition, temperature, humidity, and wind for a location at a time today. |

### Preferences (1)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_user_preferences` | `category: str` | retrieve | CAR-bench, extended | `get_user_preferences` | Return the driver's saved preferences for one category, such as preferred charging or fuel brands, route choices, or climate habits. Adds seats, media, and energy categories. |

## Negative tools

These 12 tools cover smart-home, phone, and other requests that do not belong in the car. The model should recognize them and decline or pick the right in-car tool. All of them are new.

| Tool | Domain | What it does |
|---|---|---|
| `set_home_thermostat` | SmartHome | Set the target temperature of the home thermostat. |
| `set_home_lights` | SmartHome | Turn lights in a room of the home on or off and set their color. |
| `lock_home_door` | SmartHome | Lock or unlock the smart lock on the home's front door. |
| `play_on_home_speaker` | SmartHome | Play music on a smart speaker at home. |
| `start_home_wallbox_charging` | SmartHome | Start charging on the home wallbox app account. |
| `set_phone_alarm` | Phone | Set an alarm on the user's phone. |
| `set_phone_ringer_volume` | Phone | Change the phone's own ringer volume. |
| `book_flight` | Travel | Search and book a flight ticket. |
| `order_food_delivery` | Shopping | Order food for delivery to a home address. |
| `transfer_money` | Finance | Transfer money from the user's bank account to another account. |
| `create_document` | Productivity | Create a new text document in the user's cloud drive. |
| `post_to_social_media` | Social | Publish a post on the user's social media account. |

## Vehicle state

The 146 state values the tools change and read, named by their [COVESA VSS](https://github.com/COVESA/vehicle_signal_specification) path. 129 are standard VSS signals and 17 are extensions declared in `2026-10-14_hybrid_vss_overlay.vspec`. Each conversation starts from a random but valid state, and every successful action updates it.

### Doors and windows

Door locks, child locks, window positions.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Door.Row1.DriverSide.Window.Position` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `Vehicle.Cabin.Door.Row2.DriverSide.Window.Position` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `Vehicle.Cabin.Door.Row2.PassengerSide.Window.Position` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `Vehicle.Cabin.IsWindowChildLockEngaged` | actuator | boolean | bool | true, false | random | `set_window_child_lock` | `get_window_positions` |
| `Vehicle.Cabin.Door.Row1.DriverSide.IsLocked` | actuator | boolean | bool | true, false | random | `set_door_locks` | `get_door_status` |
| `Vehicle.Cabin.Door.Row1.PassengerSide.IsLocked` | actuator | boolean | bool | true, false | random | `set_door_locks` | `get_door_status` |
| `Vehicle.Cabin.Door.Row2.DriverSide.IsLocked` | actuator | boolean | bool | true, false | random | `set_door_locks` | `get_door_status` |
| `Vehicle.Cabin.Door.Row2.PassengerSide.IsLocked` | actuator | boolean | bool | true, false | random | `set_door_locks` | `get_door_status` |
| `Vehicle.Cabin.Door.Row2.DriverSide.IsChildLockActive` | sensor | boolean | bool | true, false | random | read-only | `get_door_status` |
| `Vehicle.Cabin.Door.Row2.PassengerSide.IsChildLockActive` | sensor | boolean | bool | true, false | random | read-only | `get_door_status` |

### Sunroof and shades

Sunroof, sunroof shade, rear window shade.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Sunroof.Position` | sensor | int8 (percent) | int | -100 to 100, step 5 | from weather | `set_sunroof_position` | `get_sunroof_and_sunshade_position` |
| `Vehicle.Cabin.Sunroof.Shade.Position` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_sunshade_position` | `get_sunroof_and_sunshade_position` |
| `Vehicle.Cabin.RearShade.Position` | actuator | uint8 (percent) | int | 0 to 100, step 10 | random | `set_rear_window_shade` | `get_rear_window_shade_position` |

### Interior lights

Reading lights and ambient light zones.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Light.Spotlight.Row1.DriverSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_reading_light` | `get_reading_lights_status` |
| `Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_reading_light` | `get_reading_lights_status` |
| `Vehicle.Cabin.Light.Spotlight.Row2.DriverSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_reading_light` | `get_reading_lights_status` |
| `Vehicle.Cabin.Light.Spotlight.Row2.PassengerSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_reading_light` | `get_reading_lights_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Color` | actuator | string | str | "#FFFFFF", "#FF0000", "#FF8000", "#FFD700", "#00C853", "#00FFFF", "#0050FF", "#8000FF", "#FF4FA0" | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Intensity` | actuator | uint8 (percent) | int | 10 to 100, step 10 | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row1.PassengerSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row1.PassengerSide.Color` | actuator | string | str | "#FFFFFF", "#FF0000", "#FF8000", "#FFD700", "#00C853", "#00FFFF", "#0050FF", "#8000FF", "#FF4FA0" | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row1.PassengerSide.Intensity` | actuator | uint8 (percent) | int | 10 to 100, step 10 | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row2.DriverSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row2.DriverSide.Color` | actuator | string | str | "#FFFFFF", "#FF0000", "#FF8000", "#FFD700", "#00C853", "#00FFFF", "#0050FF", "#8000FF", "#FF4FA0" | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row2.DriverSide.Intensity` | actuator | uint8 (percent) | int | 10 to 100, step 10 | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row2.PassengerSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row2.PassengerSide.Color` | actuator | string | str | "#FFFFFF", "#FF0000", "#FF8000", "#FFD700", "#00C853", "#00FFFF", "#0050FF", "#8000FF", "#FF4FA0" | random | `set_ambient_light` | `get_ambient_light_status` |
| `Vehicle.Cabin.Light.AmbientLight.Row2.PassengerSide.Intensity` | actuator | uint8 (percent) | int | 10 to 100, step 10 | random | `set_ambient_light` | `get_ambient_light_status` |

### Climate

HVAC zones, air conditioning, defrosters, measured temperatures.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.HVAC.IsAutoModeActive` *(extension)* | actuator | boolean | bool | true, false | fixed: true | `set_fan_speed`, `set_air_distribution`, `set_climate_auto_mode` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature` | actuator | float (Celsius) | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Driver.FanSpeed` | actuator | uint8 (percent) | int | 0, 20, 40, 60, 80, 100 | random | `set_fan_speed` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Driver.AirDistribution` | actuator | string | str | "UP", "MIDDLE", "DOWN" | random | `set_air_distribution` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature` | actuator | float (Celsius) | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Passenger.FanSpeed` | actuator | uint8 (percent) | int | 0, 20, 40, 60, 80, 100 | random | `set_fan_speed` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Passenger.AirDistribution` | actuator | string | str | "UP", "MIDDLE", "DOWN" | random | `set_air_distribution` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Driver.Temperature` | actuator | float (Celsius) | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Driver.FanSpeed` | actuator | uint8 (percent) | int | 0, 20, 40, 60, 80, 100 | random | `set_fan_speed` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Driver.AirDistribution` | actuator | string | str | "UP", "MIDDLE", "DOWN" | random | `set_air_distribution` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Passenger.Temperature` | actuator | float (Celsius) | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Passenger.FanSpeed` | actuator | uint8 (percent) | int | 0, 20, 40, 60, 80, 100 | random | `set_fan_speed` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Passenger.AirDistribution` | actuator | string | str | "UP", "MIDDLE", "DOWN" | random | `set_air_distribution` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.IsAirConditioningActive` | actuator | boolean | bool | true, false | from weather | `set_air_conditioning` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.IsRecirculationActive` | actuator | boolean | bool | true, false | random | `set_air_recirculation` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.IsFrontDefrosterActive` | actuator | boolean | bool | true, false | from weather | `set_defrost` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.IsRearDefrosterActive` | actuator | boolean | bool | true, false | from weather | `set_defrost` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.AmbientAirTemperature` | sensor | float (Celsius) | float | -20.0 to 55.0, step 0.5 | from weather | read-only | `get_climate_status` |
| `Vehicle.Exterior.AirTemperature` | sensor | float (Celsius) | float | -30.0 to 50.0, step 0.5 | from weather | read-only | `get_climate_status` |
| `Vehicle.Exterior.Humidity` | sensor | float (percent) | float | 0.0 to 100.0, step 1.0 | from weather | read-only | `get_climate_status` |

### Seats and steering wheel

Occupancy, heating and cooling, massage, position.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Seat.Row1.DriverSide.OccupancyStatus` | sensor | string | str | "OCCUPIED", "EMPTY" | fixed: "OCCUPIED" | read-only | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.HeatingCooling` | actuator | int8 (percent) | int | -100, -66, -33, 0, 33, 66, 100 | from weather | `set_seat_heating`, `set_seat_ventilation` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.OccupancyStatus` | sensor | string | str | "OCCUPIED", "EMPTY" | random | read-only | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.HeatingCooling` | actuator | int8 (percent) | int | -100, -66, -33, 0, 33, 66, 100 | from weather | `set_seat_heating`, `set_seat_ventilation` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row2.DriverSide.OccupancyStatus` | sensor | string | str | "OCCUPIED", "EMPTY" | random | read-only | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row2.DriverSide.HeatingCooling` | actuator | int8 (percent) | int | 0, 33, 66, 100 | from weather | `set_seat_heating` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row2.PassengerSide.OccupancyStatus` | sensor | string | str | "OCCUPIED", "EMPTY" | random | read-only | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row2.PassengerSide.HeatingCooling` | actuator | int8 (percent) | int | 0, 33, 66, 100 | from weather | `set_seat_heating` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.Massage.Level` | actuator | uint8 (percent) | int | 0, 33, 66, 100 | random | `set_seat_massage` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.Massage.TypeActive` | actuator | string | str | "WAVE", "PULSE", "STRETCH", "LUMBAR" | random | `set_seat_massage` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.Position` | actuator | uint16 (mm) | int | 0 to 250, step 10 | random | `set_seat_position`, `recall_seat_memory` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.Recline` | actuator | float (degrees) | float | 0.0 to 40.0, step 1.0 | random | `set_seat_recline`, `recall_seat_memory` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.Massage.Level` | actuator | uint8 (percent) | int | 0, 33, 66, 100 | random | `set_seat_massage` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.Massage.TypeActive` | actuator | string | str | "WAVE", "PULSE", "STRETCH", "LUMBAR" | random | `set_seat_massage` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.Position` | actuator | uint16 (mm) | int | 0 to 250, step 10 | random | `set_seat_position` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.Recline` | actuator | float (degrees) | float | 0.0 to 40.0, step 1.0 | random | `set_seat_recline` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.MemoryProfile` *(extension)* | actuator | uint8 | int | 0, 1, 2, 3 | random | `recall_seat_memory` | `get_seat_status` |
| `Vehicle.Chassis.SteeringWheel.HeatingCooling` | actuator | int8 (percent) | int | 0, 33, 66, 100 | from weather | `set_steering_wheel_heating` | `get_seat_status` |

### Media

Source, playback, volume, radio.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Infotainment.Media.Played.Source` | actuator | string | str | "FM", "AM", "DAB", "BLUETOOTH", "USB", "INTERNET" | random | `set_media_source`, `tune_fm_radio`, `play_media_by_query` | `get_media_status` |
| `Vehicle.Cabin.Infotainment.Media.Action` | actuator | string | str | "PLAY", "STOP", "SKIP_FORWARD", "SKIP_BACKWARD" | random | `set_media_source`, `set_media_playback`, `skip_media_track`, `tune_fm_radio`, `play_media_by_query` | `get_media_status` |
| `Vehicle.Cabin.Infotainment.Media.Volume` | actuator | uint8 (percent) | int | 0 to 100, step 1 | random | `set_media_volume` | `get_media_status` |
| `Vehicle.Cabin.Infotainment.Media.IsMuted` *(extension)* | actuator | boolean | bool | true, false | random | `set_media_volume`, `set_media_mute` | `get_media_status` |
| `Vehicle.Cabin.Infotainment.Media.Radio.FMFrequency` *(extension)* | actuator | float | float | 87.5 to 108.0, step 0.1 | random | `tune_fm_radio` | `get_media_status` |
| `Vehicle.Cabin.Infotainment.Media.SelectedURI` | actuator | string | str | location or route ID, empty when unset | fixed: "" | `play_media_by_query` | `get_media_status` |

### Navigation

Guidance, destination, stops, route options, voice.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Infotainment.Navigation.IsGuidanceActive` *(extension)* | actuator | boolean | bool | true, false | fixed: false | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.DestinationSet.Latitude` | actuator | double (degrees) | float | -90.0 to 90.0 | fixed: 0.0 | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.DestinationSet.Longitude` | actuator | double (degrees) | float | -180.0 to 180.0 | fixed: 0.0 | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.DestinationSet.LocationId` *(extension)* | actuator | string | str | location or route ID, empty when unset | fixed: "" | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.Waypoints.Stop1.LocationId` *(extension)* | actuator | string | str | location or route ID, empty when unset | fixed: "" | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.Waypoints.Stop2.LocationId` *(extension)* | actuator | string | str | location or route ID, empty when unset | fixed: "" | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.Waypoints.Stop3.LocationId` *(extension)* | actuator | string | str | location or route ID, empty when unset | fixed: "" | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.RouteId` *(extension)* | actuator | string | str | location or route ID, empty when unset | fixed: "" | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.RouteOptions.IsTollAvoided` *(extension)* | actuator | boolean | bool | true, false | random | `set_route_options` | `get_routes`, `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.RouteOptions.IsHighwayAvoided` *(extension)* | actuator | boolean | bool | true, false | random | `set_route_options` | `get_routes`, `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.Mute` | actuator | string | str | "UNMUTED", "ALERT_ONLY", "MUTED" | random | `set_voice_guidance` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.Volume` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_navigation_volume` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.IsDestinationReached` | sensor | boolean | bool | true, false | fixed: false | read-only | `get_navigation_status` |

### Exterior lights

Headlights, fog lights, hazard lights.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Body.Lights.Beam.Low.IsOn` | actuator | boolean | bool | true, false | from weather | `set_low_beams` | `get_exterior_lights_status` |
| `Vehicle.Body.Lights.Beam.High.IsOn` | actuator | boolean | bool | true, false | random | `set_high_beams` | `get_exterior_lights_status` |
| `Vehicle.Body.Lights.Fog.Front.IsOn` | actuator | boolean | bool | true, false | from weather | `set_fog_lights` | `get_exterior_lights_status` |
| `Vehicle.Body.Lights.Fog.Rear.IsOn` | actuator | boolean | bool | true, false | from weather | `set_fog_lights` | `get_exterior_lights_status` |
| `Vehicle.Body.Lights.Hazard.IsSignaling` | actuator | boolean | bool | true, false | fixed: false | `set_hazard_lights` | `get_exterior_lights_status` |

### Wipers and mirrors

Wiper modes, exterior mirrors.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Body.Windshield.Front.Wiping.Mode` | actuator | string | str | "OFF", "SLOW", "MEDIUM", "FAST", "INTERVAL", "RAIN_SENSOR" | from weather | `set_wipers` | `get_wiper_status` |
| `Vehicle.Body.Windshield.Front.Wiping.Intensity` | actuator | uint8 | int | 1, 2, 3, 4 | random | `set_wipers` | `get_wiper_status` |
| `Vehicle.Body.Windshield.Rear.Wiping.Mode` | actuator | string | str | "OFF", "INTERVAL", "SLOW" | from weather | `set_wipers` | `get_wiper_status` |
| `Vehicle.Body.Mirrors.DriverSide.IsFolded` | actuator | boolean | bool | true, false | fixed: false | `set_side_mirrors_folded` | `get_side_mirror_status` |
| `Vehicle.Body.Mirrors.DriverSide.IsHeatingOn` | actuator | boolean | bool | true, false | from weather | `set_mirror_heating` | `get_side_mirror_status` |
| `Vehicle.Body.Mirrors.PassengerSide.IsFolded` | actuator | boolean | bool | true, false | fixed: false | `set_side_mirrors_folded` | `get_side_mirror_status` |
| `Vehicle.Body.Mirrors.PassengerSide.IsHeatingOn` | actuator | boolean | bool | true, false | from weather | `set_mirror_heating` | `get_side_mirror_status` |

### Trunk

Trunk lid and lock.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Body.Trunk.Rear.IsOpen` | actuator | boolean | bool | true, false | fixed: false | `set_trunk` | `get_trunk_status` |
| `Vehicle.Body.Trunk.Rear.IsLocked` | actuator | boolean | bool | true, false | random | `set_trunk_lock` | `get_trunk_status` |

### Driving, tires, and service

Speed, gear, odometer, trip, tire pressure, service, fluids, 12 V battery.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Speed` | sensor | float (km/h) | float | 0.0 to 160.0, step 1.0 | random | read-only | `get_driving_status` |
| `Vehicle.Powertrain.Transmission.SelectedGear` | actuator | int8 | int | 126, 127, 0, -1 | random | read-only | `get_driving_status` |
| `Vehicle.TraveledDistance` | sensor | uint32 (m) | int | 0 to 300000000, step 1000 | random | read-only | `get_driving_status` |
| `Vehicle.TripMeterReading` | actuator | uint32 (m) | int | 0 to 2000000, step 100 | random | `reset_trip_meter` | `get_trip_info` |
| `Vehicle.TripDuration` | sensor | float (s) | float | 0.0 to 86400.0, step 60.0 | random | read-only | `get_trip_info` |
| `Vehicle.AverageSpeed` | sensor | float (km/h) | float | 0.0 to 130.0, step 1.0 | random | read-only | `get_trip_info` |
| `Vehicle.Chassis.Axle.Row1.Wheel.Left.Tire.Pressure` | sensor | uint16 (kPa) | int | 150 to 280, step 5 | random | read-only | `get_tire_pressure` |
| `Vehicle.Chassis.Axle.Row1.Wheel.Left.Tire.IsPressureLow` | sensor | boolean | bool | true, false | random | read-only | `get_tire_pressure` |
| `Vehicle.Chassis.Axle.Row1.Wheel.Right.Tire.Pressure` | sensor | uint16 (kPa) | int | 150 to 280, step 5 | random | read-only | `get_tire_pressure` |
| `Vehicle.Chassis.Axle.Row1.Wheel.Right.Tire.IsPressureLow` | sensor | boolean | bool | true, false | random | read-only | `get_tire_pressure` |
| `Vehicle.Chassis.Axle.Row2.Wheel.Left.Tire.Pressure` | sensor | uint16 (kPa) | int | 150 to 280, step 5 | random | read-only | `get_tire_pressure` |
| `Vehicle.Chassis.Axle.Row2.Wheel.Left.Tire.IsPressureLow` | sensor | boolean | bool | true, false | random | read-only | `get_tire_pressure` |
| `Vehicle.Chassis.Axle.Row2.Wheel.Right.Tire.Pressure` | sensor | uint16 (kPa) | int | 150 to 280, step 5 | random | read-only | `get_tire_pressure` |
| `Vehicle.Chassis.Axle.Row2.Wheel.Right.Tire.IsPressureLow` | sensor | boolean | bool | true, false | random | read-only | `get_tire_pressure` |
| `Vehicle.Service.DistanceToService` | sensor | float (km) | float | 0.0 to 30000.0, step 100.0 | random | read-only | `get_maintenance_status` |
| `Vehicle.Service.IsServiceDue` | sensor | boolean | bool | true, false | random | read-only | `get_maintenance_status` |
| `Vehicle.Powertrain.CombustionEngine.EngineOil.Level` | sensor | string | str | "CRITICALLY_LOW", "LOW", "NORMAL", "HIGH" | random | read-only | `get_maintenance_status` |
| `Vehicle.Body.Windshield.Front.WasherFluid.Level` | sensor | uint8 (percent) | int | 0 to 100, step 5 | random | read-only | `get_maintenance_status` |
| `Vehicle.LowVoltageBattery.CurrentVoltage` | sensor | float (V) | float | 11.0 to 14.8, step 0.1 | random | read-only | `get_maintenance_status` |

### Charging

Charge port, cable, charge limit, timer, charging power.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Powertrain.TractionBattery.Charging.ChargingPort.FrontLeft.IsFlapOpen` | actuator | boolean | bool | true, false | fixed: false | `set_charge_port` | `get_charge_port_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.ChargingPort.FrontLeft.IsChargingCableConnected` | sensor | boolean | bool | true, false | fixed: false | read-only | `get_charge_port_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.ChargingPort.FrontLeft.IsChargingCableLocked` | actuator | boolean | bool | true, false | fixed: false | `set_charging_cable_lock` | `get_charge_port_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.ChargeLimit` | actuator | uint8 (percent) | int | 50 to 100, step 5 | random | `set_charge_limit` | `get_charging_status`, `estimate_charging_time`, `estimate_soc_after_charging` |
| `Vehicle.Powertrain.TractionBattery.Charging.Timer.Mode` | actuator | string | str | "INACTIVE", "START_TIME", "END_TIME" | random | `set_charging_timer` | `get_charging_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.Timer.Time` | actuator | string (iso8601) | str | location or route ID, empty when unset | fixed: "" | `set_charging_timer` | `get_charging_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.IsCharging` | sensor | boolean | bool | true, false | fixed: false | `start_stop_charging` | `get_charging_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.MaxAcceptedPowerAC` *(extension)* | attribute | float (kW) | float | 3.7, 7.4, 11.0 | fixed: 7.4 | read-only | `get_vehicle_specs`, `get_charging_status`, `estimate_charging_time`, `estimate_soc_after_charging` |
| `Vehicle.Powertrain.TractionBattery.Charging.MaxAcceptedPowerDC` *(extension)* | attribute | float (kW) | float | 0.0, 50.0, 80.0 | fixed: 50.0 | read-only | `get_vehicle_specs`, `get_charging_status`, `estimate_charging_time`, `estimate_soc_after_charging` |

### Battery, fuel, and hybrid

Levels, capacities, consumption, hybrid and drive modes.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Powertrain.FuelSystem.IsFuelPortFlapOpen` | actuator | boolean | bool | true, false | fixed: false | `set_fuel_door` | `get_fuel_door_status` |
| `Vehicle.Powertrain.Type` | attribute | string | str | "HYBRID" | fixed: "HYBRID" | read-only | `get_vehicle_specs` |
| `Vehicle.Powertrain.FuelSystem.HybridType` | attribute | string | str | "PHEV" | fixed: "PHEV" | read-only | `get_vehicle_specs` |
| `Vehicle.Powertrain.FuelSystem.TankCapacity` | attribute | float (l) | float | 30.0 to 80.0, step 0.5 | fixed: 45.0 | read-only | `get_vehicle_specs`, `get_energy_status`, `estimate_refuel`, `estimate_route_energy` |
| `Vehicle.Powertrain.TractionBattery.NetCapacity` | sensor | uint16 (kWh) | int | 8 to 40, step 1 | fixed: 18 | read-only | `get_vehicle_specs`, `get_energy_status`, `estimate_charging_time`, `estimate_soc_after_charging`, `estimate_electric_distance`, `estimate_route_energy` |
| `Vehicle.Powertrain.FuelSystem.RelativeLevel` | sensor | uint8 (percent) | int | 0 to 100, step 1 | random | read-only | `get_energy_status`, `estimate_refuel`, `estimate_route_energy` |
| `Vehicle.Powertrain.FuelSystem.IsFuelLevelLow` | sensor | boolean | bool | true, false | random | read-only | `get_energy_status`, `estimate_route_energy` |
| `Vehicle.Powertrain.TractionBattery.StateOfCharge.Displayed` | sensor | float (percent) | float | 0.0 to 100.0, step 1.0 | random | read-only | `get_energy_status`, `estimate_charging_time`, `estimate_soc_after_charging`, `estimate_electric_distance`, `estimate_route_energy` |
| `Vehicle.Powertrain.RangeExtender.ChargeDepleting.EnergyConsumption` | sensor | float (kWh/100km) | float | 12.0 to 25.0, step 0.5 | fixed: 18.0 | read-only | `get_energy_status`, `estimate_electric_distance`, `estimate_route_energy` |
| `Vehicle.Powertrain.FuelSystem.AverageConsumption` | sensor | float (l/100km) | float | 3.0 to 12.0, step 0.1 | random | read-only | `get_trip_info`, `get_energy_status`, `estimate_refuel`, `estimate_route_energy` |
| `Vehicle.Powertrain.CombustionEngine.IsRunning` | sensor | boolean | bool | true, false | random | `set_hybrid_mode` | `get_energy_status` |
| `Vehicle.Powertrain.RangeExtender.OperatingMode` | sensor | string | str | "CHARGE_DEPLETING", "CHARGE_SUSTAINING", "BLENDED" | random | `set_hybrid_mode` | `get_energy_status` |
| `Vehicle.Powertrain.Hybrid.Mode` *(extension)* | actuator | string | str | "AUTO", "ELECTRIC", "HOLD", "CHARGE" | random | `set_hybrid_mode` | `get_energy_status`, `estimate_route_energy` |
| `Vehicle.Powertrain.Hybrid.ChargeTarget` *(extension)* | actuator | uint8 (percent) | int | 20 to 80, step 10 | random | `set_hybrid_mode` | `get_energy_status` |
| `Vehicle.Powertrain.Hybrid.RegenLevel` *(extension)* | actuator | uint8 | int | 0, 1, 2, 3 | random | `set_regen_level` | `get_energy_status` |
| `Vehicle.Powertrain.Transmission.PerformanceMode` | actuator | string | str | "NORMAL", "SPORT", "ECONOMY" | random | `set_drive_mode` | `get_energy_status` |

### Vehicle identity

Fixed facts about the car.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.VehicleIdentification.VehicleExteriorColor` | attribute | string | str | "Black", "White", "Silver", "Gray", "Blue", "Red", "Green" | fixed: "Blue" | read-only | `get_vehicle_specs` |
