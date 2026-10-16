# AI-powered cockpit assistant tools VSS

**107 tools** in total: **95 positive** and **12 negative**, over **146 vehicle state values** named after [COVESA VSS](https://github.com/COVESA/vehicle_signal_specification) signals (129 standard, 17 extensions). The spec files are the `hybrid_vss_*` files in this folder.

Of the 95 positive tools, **48 come from CAR-bench** (28 with the same capability, 20 extended) and **47 are new**.

## Positive tools by domain

| Domain | Action | Retrieve | Total | From CAR-bench | New |
|---|---|---|---|---|---|
| Vehicle (Body, lights, climate, seats, vehicle status) | 33 | 19 | 52 | 25 | 27 |
| Navigation (Routes, stops, places) | 7 | 6 | 13 | 10 | 3 |
| Energy (Hybrid powertrain, charging, fuel) | 6 | 7 | 13 | 4 | 9 |
| Media (Audio and radio) | 6 | 1 | 7 | – | 7 |
| Communication (Calls, texts, email, calendar) | 3 | 3 | 6 | 5 | 1 |
| Utility (Math and time) | – | 2 | 2 | 2 | – |
| Weather (Conditions at a place today) | – | 1 | 1 | 1 | – |
| Preferences (Saved driver preferences) | – | 1 | 1 | 1 | – |
| **Total** | **55** | **40** | **95** | **48** | **47** |

CAR-bench has 57 tools. All of them are covered except `think` and `planning_tool`, which are reasoning scaffolds for the agent rather than features for the driver.

Origin tags used below:

- **CAR-bench**: the same capability as a CAR-bench tool, sometimes renamed or merged from several getters.
- **CAR-bench, extended**: built on a CAR-bench tool, with added parameters, values, or state.
- **New**: not in CAR-bench.

## Positive tools

### Vehicle (52)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `set_window_position` | `windows: str`, `percent_open?: int` | action | CAR-bench | `open_close_window` | Opens or closes one side window, or all four, to an exact opening in percent. |
| `set_window_child_lock_state` | `enabled: bool` | action | New | – | Enables or disables the rear window child lock, which stops rear passengers from moving their windows with their own switches. |
| `get_window_positions` | – | retrieve | CAR-bench | `get_vehicle_window_positions` | Returns the opening of each of the four side windows in percent (0 closed, 100 fully open) and whether the rear window child lock is on. |
| `set_sunroof_shade_position` | `percent_open?: int` | action | CAR-bench | `open_close_sunshade` | Opens or closes the sliding shade under the glass sunroof, to let light in or block it. |
| `set_sunroof_position` | `opening_style?: str`, `percent_open?: int` | action | CAR-bench, extended | `open_close_sunroof` | Slides the glass sunroof open or closed, or tilts its rear edge up for ventilation. Adds tilt, as VSS models it. |
| `get_sunroof_and_shade_position` | – | retrieve | CAR-bench | `get_sunroof_and_sunshade_position` | Returns the sunroof position (0 closed, 100 fully slid open, negative values tilted, -100 fully tilted) and the sunroof shade opening in percent. |
| `set_rear_window_shade_position` | `percent_raised?: int` | action | New | – | Raises or lowers the sun shade on the rear window, for example to block low sun or keep the back seat private. |
| `get_rear_window_shade_position` | – | retrieve | New | – | Returns how far the rear window sun shade is raised, in percent (0 lowered, 100 fully raised). |
| `set_door_lock_state` | `doors?: str`, `is_locked: bool` | action | New | – | Locks or unlocks one door or all four doors. |
| `get_door_status` | – | retrieve | New | – | Returns, for each of the four doors, whether it is locked, and for the two rear doors whether the child safety lock is engaged. |
| `set_trunk_lid_state` | `is_open: bool` | action | CAR-bench, extended | `open_close_trunk_door` | Opens or closes the power trunk lid. Adds the stopped-in-park rule. |
| `set_trunk_lock_state` | `is_locked: bool` | action | New | – | Locks or unlocks the trunk on its own, independently of the doors, for example to keep valet staff out of the trunk. |
| `get_trunk_status` | – | retrieve | CAR-bench, extended | `get_trunk_door_position` | Returns whether the trunk lid is open and whether the trunk is locked. Adds the trunk lock. |
| `set_fuel_door_state` | `is_open: bool` | action | New | – | Opens or closes the fuel filler door so the driver can refuel. |
| `get_fuel_door_status` | – | retrieve | New | – | Returns whether the fuel filler door is open. |
| `set_charge_port_door_state` | `is_open: bool` | action | New | – | Opens or closes the charging port door on the front-left fender so the driver can plug in. |
| `set_charging_cable_lock_state` | `is_locked: bool` | action | New | – | Locks the charging cable into the port or releases it. |
| `get_charge_port_status` | – | retrieve | New | – | Returns whether the charging port door is open, whether a charging cable is plugged in, and whether the cable is locked. |
| `set_headlight_beam_state` | `beam: str`, `enabled: bool` | action | CAR-bench | `set_head_lights_low_beams`, `set_head_lights_high_beams` | Turns the low beam or the high beam headlights on or off. Merges CAR-bench's low beam and high beam setters into one tool. |
| `set_fog_light_state` | `fog_lights: str`, `enabled: bool` | action | CAR-bench, extended | `set_fog_lights` | Turns the front fog lights, the rear fog light, or both on or off. Adds the rear fog light. |
| `set_hazard_lights_state` | `enabled: bool` | action | New | – | Starts or stops the hazard warning lights, which flash all turn signals at once. |
| `get_exterior_lights_status` | – | retrieve | CAR-bench, extended | `get_exterior_lights_status` | Returns whether the low beams, high beams, front fog lights, rear fog light, and hazard lights are on. Adds the rear fog light and hazard lights. |
| `set_wiper_mode` | `wiper: str`, `wiper_mode: str`, `interval_level?: int` | action | New | – | Sets the mode of the front or the rear windshield wiper, and for the front wiper how often it wipes in interval or rain-sensor mode. |
| `get_wiper_status` | – | retrieve | New | – | Returns the front and rear wiper modes and the front wiper interval level. |
| `set_side_mirror_fold_state` | `is_folded: bool` | action | New | – | Folds both exterior side mirrors in against the car, or unfolds them for driving. |
| `set_side_mirror_heating_state` | `enabled: bool` | action | New | – | Turns heating on or off in both exterior side mirrors, to clear ice, frost, or fog from the glass. |
| `get_side_mirror_status` | – | retrieve | New | – | Returns, for the driver-side and passenger-side mirrors, whether each is folded and whether its heating is on. |
| `set_reading_light_state` | `seats: str`, `enabled: bool` | action | CAR-bench | `set_reading_light` | Turns the reading light above one seat, or above all seats, on or off. |
| `get_reading_lights_status` | – | retrieve | CAR-bench | `get_reading_lights_status` | Returns, for each of the four seats, whether its reading light is on. |
| `set_ambient_light` | `enabled: bool`, `color?: str`, `brightness_percent?: int` | action | CAR-bench, extended | `set_ambient_lights` | Turns the ambient mood lighting on or off and sets its color and brightness in all four zones at once. Adds brightness and sets four zones. |
| `get_ambient_light_status` | – | retrieve | CAR-bench, extended | `get_ambient_light_status_and_color` | Returns, for each of the four ambient light zones, whether it is on, its color as an RGB code, and its brightness in percent. Adds brightness. |
| `set_climate_temperature` | `zones: str`, `temperature_celsius: float` | action | CAR-bench, extended | `set_climate_temperature` | Sets the target cabin temperature for one climate zone, both back-seat zones, or every zone. Adds a rear zone. |
| `set_fan_speed` | `zones?: str`, `fan_level: int` | action | CAR-bench, extended | `set_fan_speed` | Sets how hard the climate fan blows in one zone or in every zone. Sets each climate zone separately, as VSS models it. |
| `set_airflow_direction` | `zones?: str`, `airflow_direction: str` | action | CAR-bench, extended | `set_fan_airflow_direction` | Sets where the climate air comes out in one zone or in every zone: onto the windshield, at the face, or at the feet. Uses VSS's per-zone up, middle, and down directions. |
| `set_air_conditioning_state` | `enabled: bool` | action | CAR-bench | `set_air_conditioning` | Turns the air conditioning compressor on or off. |
| `set_air_recirculation_state` | `enabled: bool` | action | CAR-bench | `set_air_circulation` | Switches between recirculating the cabin air and drawing in fresh outside air. VSS models it as on or off. |
| `set_defroster_state` | `defrosters: str`, `enabled: bool` | action | CAR-bench | `set_window_defrost` | Turns the front windshield defroster, the rear window defroster, or both on or off, to clear fog, frost, or ice from the glass. |
| `set_climate_auto_mode_state` | `enabled: bool` | action | New | – | Turns climate auto mode on or off. |
| `get_climate_status` | – | retrieve | CAR-bench, extended | `get_climate_settings`, `get_temperature_inside_car` | Returns the whole climate setup: auto mode, each zone's target temperature, fan speed in percent, and airflow direction, plus air conditioning, recirculation, and both defrosters. Merges two CAR-bench getters and adds auto mode, four zones, and measured cabin and outside temperature and humidity. |
| `set_seat_heating_cooling` | `seats: str`, `climate_mode: str`, `intensity_level?: int` | action | CAR-bench, extended | `set_seat_heating` | Heats or ventilates (cools) one seat or all seats, or turns both off. Adds the rear seats and ventilation, which share one VSS heating-cooling value. |
| `set_seat_massage` | `seats: str`, `massage_program?: str`, `intensity_level: int` | action | New | – | Starts, changes, or stops the massage in one or both front seats. |
| `set_seat_fore_aft_position` | `seats: str`, `distance_from_front_mm: int` | action | New | – | Moves a front seat forward or backward along its rail. |
| `set_seat_recline` | `seats: str`, `recline_degrees: int` | action | New | – | Changes how far a front seat's backrest leans back. |
| `recall_driver_seat_memory` | `profile_number: int` | action | New | – | Moves the driver's seat to one of three saved memory positions, setting both its fore-aft position and recline. |
| `set_steering_wheel_heating_level` | `heating_level: int` | action | CAR-bench | `set_steering_wheel_heating` | Sets the steering wheel heating level, or turns it off. |
| `get_seat_status` | – | retrieve | CAR-bench, extended | `get_seat_heating_level`, `get_seats_occupancy`, `get_steering_wheel_heating_level` | Returns each seat's occupancy and heating or ventilation level (positive values heat, negative values cool), the front seats' massage program and level, fore-aft position, and recline, the last recalled driver memory profile, and the steering wheel heating level. Merges three CAR-bench getters and adds ventilation, massage, and seat position. |
| `get_driving_status` | – | retrieve | New | – | Returns the current speed in km/h, the selected gear (126 park, 127 drive, 0 neutral, -1 reverse), and the odometer in meters. |
| `get_tire_pressure` | – | retrieve | New | – | Returns each tire's pressure in kPa and whether it has a low-pressure warning (below 200 kPa; 230 to 250 is recommended). |
| `get_maintenance_status` | – | retrieve | New | – | Returns the distance to the next scheduled service in km and whether service is due, the engine oil level, the washer fluid level in percent, and the 12 V battery voltage. |
| `get_trip_info` | – | retrieve | New | – | Returns the trip meter in meters, the trip duration in seconds, the average speed in km/h, and the average fuel consumption in liters per 100 km. |
| `reset_trip_meter` | – | action | New | – | Resets the trip meter to zero to start measuring a new trip. |
| `get_vehicle_specs` | – | retrieve | CAR-bench, extended | `get_car_color` | Returns fixed facts about this car: exterior color, powertrain type (hybrid) and hybrid type (plug-in), fuel tank capacity in liters, usable battery capacity in kWh, and maximum AC and DC charging power in kW. Adds tank, battery, consumption, and charging specs. |

### Navigation (13)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_location_id_by_name` | `place_name: str` | retrieve | CAR-bench | `get_location_id_by_location_name` | Looks up the location ID of a city, street address, or named place. |
| `search_poi_at_location` | `location_id: str`, `poi_category: str`, `filters?: list` | retrieve | CAR-bench, extended | `search_poi_at_location` | Finds points of interest of one category near a location, sorted by distance. Keeps CAR-bench's open-now, available-plug, and DC-plug filters and adds gas stations and other categories. |
| `search_poi_along_route` | `route_id: str`, `poi_category: str`, `filters?: list`, `max_detour_minutes?: int` | retrieve | CAR-bench, extended | `search_poi_along_the_route` | Finds points of interest of one category along a route, with how many km along the route each one is and the extra driving time of the detour. Keeps CAR-bench's filters and adds gas stations, other categories, and a detour limit. |
| `get_routes` | `destination_id: str`, `start_location_id?: str` | retrieve | CAR-bench, extended | `get_routes_from_start_to_destination` | Returns up to three route options between two locations, each with its route ID, distance in km, duration, whether it uses toll roads, and the main roads it takes. Respects the avoid-tolls and avoid-highways options. |
| `convert_route_distance_and_time` | `route_id: str`, `amount: float`, `amount_unit: str` | retrieve | CAR-bench | `convert_route_distance_and_time` | Converts, on a given route, a distance into the driving time it takes, or a driving time into the distance covered. |
| `start_navigation` | `destination_id: str`, `first_leg_route_id: str`, `stop_location_ids?: list` | action | CAR-bench | `set_new_navigation` | Starts turn-by-turn guidance from the current location to a destination, optionally through up to three intermediate stops in order. |
| `update_navigation_waypoint` | `waypoint_operation: str`, `stop_number: int`, `location_id?: str` | action | CAR-bench | `navigation_add_one_waypoint`, `navigation_replace_one_waypoint`, `navigation_delete_waypoint` | Adds, replaces, or removes one intermediate stop on the active route without restarting guidance. Merges CAR-bench's add, replace, and delete waypoint tools into one tool. |
| `update_navigation_destination` | `destination_operation: str`, `location_id?: str` | action | CAR-bench | `navigation_replace_final_destination`, `navigation_delete_destination` | Replaces the final destination of the active route, or removes it so the last intermediate stop becomes the destination, without restarting guidance. Merges CAR-bench's replace and delete destination tools into one tool. |
| `cancel_navigation` | – | action | CAR-bench | `delete_current_navigation` | Stops guidance and clears the destination and all intermediate stops. |
| `set_route_preferences` | `avoid_tolls: bool`, `avoid_highways: bool` | action | New | – | Sets whether route planning avoids toll roads and whether it avoids highways. |
| `set_navigation_voice_guidance` | `guidance_level: str` | action | New | – | Chooses how much the navigation voice speaks: every turn instruction, only alerts such as hazards and speed cameras, or nothing. |
| `set_navigation_voice_volume` | `volume_percent: int` | action | New | – | Sets the loudness of the navigation voice, separately from music and radio. |
| `get_navigation_status` | – | retrieve | CAR-bench, extended | `get_current_navigation_state` | Returns whether guidance is active, the destination's location ID and coordinates, the intermediate stops in order, the route ID being followed, and whether the destination is reached. Adds route options and voice guidance. |

### Energy (13)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_energy_status` | – | retrieve | CAR-bench, extended | `get_charging_specs_and_status`, `get_fuel_information` | Returns the battery level and fuel level in percent, the low-fuel warning, and the electric, fuel, and combined range in km, computed from those levels and the reference consumption. Combines battery and fuel for the hybrid and adds hybrid mode, drive mode, and regen. |
| `set_hybrid_mode` | `hybrid_mode: str`, `charge_target_percent?: int` | action | New | – | Chooses how the plug-in hybrid uses its battery and engine. |
| `set_drive_mode` | `drive_mode: str` | action | New | – | Sets the drive mode, which changes throttle response, gear shifts, and efficiency. |
| `set_regen_braking_level` | `regen_level: int` | action | New | – | Sets how strongly the car slows down and recovers energy when the driver lifts off the accelerator. |
| `get_charging_status` | – | retrieve | New | – | Returns whether the battery is charging from a cable, the charge limit in percent, the charging timer mode and time, and the car's maximum AC and DC charging power in kW. |
| `set_charge_limit` | `charge_limit_percent: int` | action | New | – | Sets the battery level at which plug-in charging stops. |
| `set_charging_timer` | `timer_mode: str`, `timer_time?: str` | action | New | – | Sets when plug-in charging runs: right away, starting at a time of day (for example cheaper night power), or finishing by a time of day (for example a morning departure). |
| `set_charging_state` | `is_charging: bool` | action | New | – | Starts or stops plug-in charging immediately, overriding the charging timer for this session. |
| `estimate_charging_time` | `charging_station_id: str`, `plug_id: str`, `start_battery_percent: int`, `target_battery_percent: int` | retrieve | CAR-bench | `calculate_charging_time_by_soc` | Estimates how many minutes it takes to charge from one battery level to another at a specific charging station plug. Takes the charging station and plug IDs, like CAR-bench. |
| `estimate_battery_after_charging` | `charging_station_id: str`, `plug_id: str`, `start_battery_percent: int`, `charging_minutes: int` | retrieve | CAR-bench | `calculate_charging_soc_by_time` | Estimates the battery level after charging for a given number of minutes at a specific charging station plug. Takes the charging station and plug IDs, like CAR-bench. |
| `estimate_electric_distance` | `start_battery_percent: int`, `end_battery_percent?: int` | retrieve | CAR-bench | `get_distance_by_soc` | Estimates how many km the car can drive on electric power alone between two battery levels, using the usable battery capacity and the reference consumption. |
| `estimate_refuel` | `target_fuel_percent?: int` | retrieve | New | – | Estimates how many liters fill the tank to a target level and how many km of fuel range that adds. |
| `estimate_route_energy` | `route_id: str` | retrieve | New | – | Estimates, for a route, how many km can be driven electrically, how many liters of fuel the rest needs, and whether the car arrives without charging or refueling. |

### Media (7)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `set_media_volume` | `volume_percent: int` | action | New | – | Sets the volume of music, radio, and podcasts. |
| `set_media_mute_state` | `is_muted: bool` | action | New | – | Mutes or unmutes music, radio, and podcasts while keeping the volume setting. |
| `set_media_source` | `media_source: str` | action | New | – | Switches the audio source, for example from FM radio to the phone over Bluetooth, and keeps playing. |
| `control_media_playback` | `playback_command: str` | action | New | – | Plays, pauses, or skips forward or back on the current audio source. |
| `tune_fm_radio` | `frequency_mhz: float` | action | New | – | Tunes the FM radio to a frequency and switches the audio source to FM. |
| `play_media_by_query` | `search_query: str`, `media_type?: str` | action | New | – | Searches the built-in streaming service for a song, artist, album, playlist, or podcast and starts playing the best match. |
| `get_media_status` | – | retrieve | New | – | Returns the audio source, whether it is playing or paused, the volume in percent, whether it is muted, the tuned FM frequency, and the identifier of the last item chosen by search. |

### Communication (6)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_contact_id_by_name` | `contact_name: str` | retrieve | CAR-bench | `get_contact_id_by_contact_name` | Finds contacts in the connected phone's address book by name and returns their contact IDs and full names. |
| `get_contact_details` | `contact_ids: list` | retrieve | CAR-bench | `get_contact_information` | Returns the phone numbers and email addresses saved for one or more contacts. |
| `call_phone_number` | `phone_number: str` | action | CAR-bench | `call_phone_by_number` | Places a hands-free call through the connected phone. |
| `send_text_message` | `phone_number: str`, `message_text: str` | action | New | – | Sends a short SMS through the connected phone. |
| `send_email` | `recipient_emails: list`, `subject: str`, `body: str` | action | CAR-bench | `send_email` | Sends a short email from the driver's connected account. |
| `get_calendar_events` | `start_hour?: int` | retrieve | CAR-bench | `get_entries_from_calendar` | Returns today's calendar events from a given hour onward, each with start time, duration, topic, location, and attendees. |

### Utility (2)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `calculate_math` | `expression: str` | retrieve | CAR-bench | `calculate_math` | Evaluates an arithmetic expression and returns the exact result. |
| `calculate_datetime` | `start_time: str`, `minutes_to_add: int` | retrieve | CAR-bench | `calculate_datetime` | Adds or subtracts minutes to a time of day and returns the resulting time, rolling over midnight when needed. |

### Weather (1)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_weather` | `location_id: str`, `time_of_day?: str` | retrieve | CAR-bench | `get_weather` | Returns the weather condition, temperature in Celsius, humidity, and wind speed for a location at a time today. |

### Preferences (1)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_user_preferences` | `preference_category: str` | retrieve | CAR-bench, extended | `get_user_preferences` | Returns the driver's saved preferences for one category, such as preferred charging and fuel brands, route choices, or usual climate settings. Adds seats, media, and energy categories. |

## Negative tools

These 12 tools cover smart-home, phone, and other requests that do not belong in the car. The model should recognize them and decline or pick the right in-car tool. All of them are new.

| Tool | Domain | What it does |
|---|---|---|
| `set_home_thermostat` | SmartHome | Sets the target temperature of the thermostat in the driver's home. |
| `set_home_lights` | SmartHome | Turns the lights in one room of the driver's home on or off and sets their color. |
| `set_home_door_lock_state` | SmartHome | Locks or unlocks the smart lock on the front door of the driver's home. |
| `play_on_home_speaker` | SmartHome | Plays music on a smart speaker in a room of the driver's home. |
| `start_home_wallbox_charging` | SmartHome | Starts a charging session through the home wallbox's own app account, at a chosen current. |
| `set_phone_alarm` | Phone | Sets a wake-up alarm on the driver's phone. |
| `set_phone_ringer_volume` | Phone | Changes the ringer volume of the phone itself, not the car's speakers. |
| `book_flight` | Travel | Searches and books a flight ticket with the driver's travel account. |
| `order_food_delivery` | Shopping | Orders food for delivery to a home address. |
| `transfer_money` | Finance | Transfers money from the driver's bank account to another account. |
| `create_document` | Productivity | Creates a new text document in the driver's cloud drive. |
| `post_to_social_media` | Social | Publishes a post on the driver's social media account. |

## Vehicle state

The 146 state values the tools change and read, named by their [COVESA VSS](https://github.com/COVESA/vehicle_signal_specification) path. 129 are standard VSS signals and 17 are extensions declared in `hybrid_vss_overlay.vspec`. Each conversation starts from a random but valid state, and every successful action updates it.

### Doors and windows

Door locks, child locks, window positions.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Door.Row1.DriverSide.Window.Position` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `Vehicle.Cabin.Door.Row2.DriverSide.Window.Position` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `Vehicle.Cabin.Door.Row2.PassengerSide.Window.Position` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `Vehicle.Cabin.IsWindowChildLockEngaged` | actuator | boolean | bool | true, false | random | `set_window_child_lock_state` | `get_window_positions` |
| `Vehicle.Cabin.Door.Row1.DriverSide.IsLocked` | actuator | boolean | bool | true, false | random | `set_door_lock_state` | `get_door_status` |
| `Vehicle.Cabin.Door.Row1.PassengerSide.IsLocked` | actuator | boolean | bool | true, false | random | `set_door_lock_state` | `get_door_status` |
| `Vehicle.Cabin.Door.Row2.DriverSide.IsLocked` | actuator | boolean | bool | true, false | random | `set_door_lock_state` | `get_door_status` |
| `Vehicle.Cabin.Door.Row2.PassengerSide.IsLocked` | actuator | boolean | bool | true, false | random | `set_door_lock_state` | `get_door_status` |
| `Vehicle.Cabin.Door.Row2.DriverSide.IsChildLockActive` | sensor | boolean | bool | true, false | random | read-only | `get_door_status` |
| `Vehicle.Cabin.Door.Row2.PassengerSide.IsChildLockActive` | sensor | boolean | bool | true, false | random | read-only | `get_door_status` |

### Sunroof and shades

Sunroof, sunroof shade, rear window shade.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Sunroof.Position` | sensor | int8 (percent) | int | -100 to 100, step 5 | from weather | `set_sunroof_position` | `get_sunroof_and_shade_position` |
| `Vehicle.Cabin.Sunroof.Shade.Position` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_sunroof_shade_position` | `get_sunroof_and_shade_position` |
| `Vehicle.Cabin.RearShade.Position` | actuator | uint8 (percent) | int | 0 to 100, step 10 | random | `set_rear_window_shade_position` | `get_rear_window_shade_position` |

### Interior lights

Reading lights and ambient light zones.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Light.Spotlight.Row1.DriverSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_reading_light_state` | `get_reading_lights_status` |
| `Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_reading_light_state` | `get_reading_lights_status` |
| `Vehicle.Cabin.Light.Spotlight.Row2.DriverSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_reading_light_state` | `get_reading_lights_status` |
| `Vehicle.Cabin.Light.Spotlight.Row2.PassengerSide.IsLightOn` | actuator | boolean | bool | true, false | random | `set_reading_light_state` | `get_reading_lights_status` |
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
| `Vehicle.Cabin.HVAC.IsAutoModeActive` *(extension)* | actuator | boolean | bool | true, false | fixed: true | `set_fan_speed`, `set_airflow_direction`, `set_climate_auto_mode_state` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature` | actuator | float (Celsius) | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Driver.FanSpeed` | actuator | uint8 (percent) | int | 0, 20, 40, 60, 80, 100 | random | `set_fan_speed` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Driver.AirDistribution` | actuator | string | str | "UP", "MIDDLE", "DOWN" | random | `set_airflow_direction` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature` | actuator | float (Celsius) | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Passenger.FanSpeed` | actuator | uint8 (percent) | int | 0, 20, 40, 60, 80, 100 | random | `set_fan_speed` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row1.Passenger.AirDistribution` | actuator | string | str | "UP", "MIDDLE", "DOWN" | random | `set_airflow_direction` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Driver.Temperature` | actuator | float (Celsius) | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Driver.FanSpeed` | actuator | uint8 (percent) | int | 0, 20, 40, 60, 80, 100 | random | `set_fan_speed` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Driver.AirDistribution` | actuator | string | str | "UP", "MIDDLE", "DOWN" | random | `set_airflow_direction` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Passenger.Temperature` | actuator | float (Celsius) | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Passenger.FanSpeed` | actuator | uint8 (percent) | int | 0, 20, 40, 60, 80, 100 | random | `set_fan_speed` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.Station.Row2.Passenger.AirDistribution` | actuator | string | str | "UP", "MIDDLE", "DOWN" | random | `set_airflow_direction` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.IsAirConditioningActive` | actuator | boolean | bool | true, false | from weather | `set_air_conditioning_state` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.IsRecirculationActive` | actuator | boolean | bool | true, false | random | `set_air_recirculation_state` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.IsFrontDefrosterActive` | actuator | boolean | bool | true, false | from weather | `set_defroster_state` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.IsRearDefrosterActive` | actuator | boolean | bool | true, false | from weather | `set_defroster_state` | `get_climate_status` |
| `Vehicle.Cabin.HVAC.AmbientAirTemperature` | sensor | float (Celsius) | float | -20.0 to 55.0, step 0.5 | from weather | read-only | `get_climate_status` |
| `Vehicle.Exterior.AirTemperature` | sensor | float (Celsius) | float | -30.0 to 50.0, step 0.5 | from weather | read-only | `get_climate_status` |
| `Vehicle.Exterior.Humidity` | sensor | float (percent) | float | 0.0 to 100.0, step 1.0 | from weather | read-only | `get_climate_status` |

### Seats and steering wheel

Occupancy, heating and cooling, massage, position.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Seat.Row1.DriverSide.OccupancyStatus` | sensor | string | str | "OCCUPIED", "EMPTY" | fixed: "OCCUPIED" | read-only | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.HeatingCooling` | actuator | int8 (percent) | int | -100, -66, -33, 0, 33, 66, 100 | from weather | `set_seat_heating_cooling` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.OccupancyStatus` | sensor | string | str | "OCCUPIED", "EMPTY" | random | read-only | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.HeatingCooling` | actuator | int8 (percent) | int | -100, -66, -33, 0, 33, 66, 100 | from weather | `set_seat_heating_cooling` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row2.DriverSide.OccupancyStatus` | sensor | string | str | "OCCUPIED", "EMPTY" | random | read-only | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row2.DriverSide.HeatingCooling` | actuator | int8 (percent) | int | 0, 33, 66, 100 | from weather | `set_seat_heating_cooling` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row2.PassengerSide.OccupancyStatus` | sensor | string | str | "OCCUPIED", "EMPTY" | random | read-only | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row2.PassengerSide.HeatingCooling` | actuator | int8 (percent) | int | 0, 33, 66, 100 | from weather | `set_seat_heating_cooling` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.Massage.Level` | actuator | uint8 (percent) | int | 0, 33, 66, 100 | random | `set_seat_massage` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.Massage.TypeActive` | actuator | string | str | "WAVE", "PULSE", "STRETCH", "LUMBAR" | random | `set_seat_massage` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.Position` | actuator | uint16 (mm) | int | 0 to 250, step 10 | random | `set_seat_fore_aft_position`, `recall_driver_seat_memory` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.Recline` | actuator | float (degrees) | float | 0.0 to 40.0, step 1.0 | random | `set_seat_recline`, `recall_driver_seat_memory` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.Massage.Level` | actuator | uint8 (percent) | int | 0, 33, 66, 100 | random | `set_seat_massage` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.Massage.TypeActive` | actuator | string | str | "WAVE", "PULSE", "STRETCH", "LUMBAR" | random | `set_seat_massage` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.Position` | actuator | uint16 (mm) | int | 0 to 250, step 10 | random | `set_seat_fore_aft_position` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.Recline` | actuator | float (degrees) | float | 0.0 to 40.0, step 1.0 | random | `set_seat_recline` | `get_seat_status` |
| `Vehicle.Cabin.Seat.Row1.DriverSide.MemoryProfile` *(extension)* | actuator | uint8 | int | 0, 1, 2, 3 | random | `recall_driver_seat_memory` | `get_seat_status` |
| `Vehicle.Chassis.SteeringWheel.HeatingCooling` | actuator | int8 (percent) | int | 0, 33, 66, 100 | from weather | `set_steering_wheel_heating_level` | `get_seat_status` |

### Media

Source, playback, volume, radio.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Infotainment.Media.Played.Source` | actuator | string | str | "FM", "AM", "DAB", "BLUETOOTH", "USB", "INTERNET" | random | `set_media_source`, `tune_fm_radio`, `play_media_by_query` | `get_media_status` |
| `Vehicle.Cabin.Infotainment.Media.Action` | actuator | string | str | "PLAY", "STOP", "SKIP_FORWARD", "SKIP_BACKWARD" | random | `set_media_source`, `control_media_playback`, `tune_fm_radio`, `play_media_by_query` | `get_media_status` |
| `Vehicle.Cabin.Infotainment.Media.Volume` | actuator | uint8 (percent) | int | 0 to 100, step 1 | random | `set_media_volume` | `get_media_status` |
| `Vehicle.Cabin.Infotainment.Media.IsMuted` *(extension)* | actuator | boolean | bool | true, false | random | `set_media_volume`, `set_media_mute_state` | `get_media_status` |
| `Vehicle.Cabin.Infotainment.Media.Radio.FMFrequency` *(extension)* | actuator | float | float | 87.5 to 108.0, step 0.1 | random | `tune_fm_radio` | `get_media_status` |
| `Vehicle.Cabin.Infotainment.Media.SelectedURI` | actuator | string | str | location or route ID, empty when unset | fixed: "" | `play_media_by_query` | `get_media_status` |

### Navigation

Guidance, destination, stops, route options, voice.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Cabin.Infotainment.Navigation.IsGuidanceActive` *(extension)* | actuator | boolean | bool | true, false | fixed: false | `start_navigation`, `update_navigation_waypoint`, `update_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.DestinationSet.Latitude` | actuator | double (degrees) | float | -90.0 to 90.0 | fixed: 0.0 | `start_navigation`, `update_navigation_waypoint`, `update_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.DestinationSet.Longitude` | actuator | double (degrees) | float | -180.0 to 180.0 | fixed: 0.0 | `start_navigation`, `update_navigation_waypoint`, `update_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.DestinationSet.LocationId` *(extension)* | actuator | string | str | location or route ID, empty when unset | fixed: "" | `start_navigation`, `update_navigation_waypoint`, `update_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.Waypoints.Stop1.LocationId` *(extension)* | actuator | string | str | location or route ID, empty when unset | fixed: "" | `start_navigation`, `update_navigation_waypoint`, `update_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.Waypoints.Stop2.LocationId` *(extension)* | actuator | string | str | location or route ID, empty when unset | fixed: "" | `start_navigation`, `update_navigation_waypoint`, `update_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.Waypoints.Stop3.LocationId` *(extension)* | actuator | string | str | location or route ID, empty when unset | fixed: "" | `start_navigation`, `update_navigation_waypoint`, `update_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.RouteId` *(extension)* | actuator | string | str | location or route ID, empty when unset | fixed: "" | `start_navigation`, `update_navigation_waypoint`, `update_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.RouteOptions.IsTollAvoided` *(extension)* | actuator | boolean | bool | true, false | random | `set_route_preferences` | `get_routes`, `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.RouteOptions.IsHighwayAvoided` *(extension)* | actuator | boolean | bool | true, false | random | `set_route_preferences` | `get_routes`, `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.Mute` | actuator | string | str | "UNMUTED", "ALERT_ONLY", "MUTED" | random | `set_navigation_voice_guidance` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.Volume` | actuator | uint8 (percent) | int | 0 to 100, step 5 | random | `set_navigation_voice_volume` | `get_navigation_status` |
| `Vehicle.Cabin.Infotainment.Navigation.IsDestinationReached` | sensor | boolean | bool | true, false | fixed: false | read-only | `get_navigation_status` |

### Exterior lights

Headlights, fog lights, hazard lights.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Body.Lights.Beam.Low.IsOn` | actuator | boolean | bool | true, false | from weather | `set_headlight_beam_state` | `get_exterior_lights_status` |
| `Vehicle.Body.Lights.Beam.High.IsOn` | actuator | boolean | bool | true, false | random | `set_headlight_beam_state` | `get_exterior_lights_status` |
| `Vehicle.Body.Lights.Fog.Front.IsOn` | actuator | boolean | bool | true, false | from weather | `set_fog_light_state` | `get_exterior_lights_status` |
| `Vehicle.Body.Lights.Fog.Rear.IsOn` | actuator | boolean | bool | true, false | from weather | `set_fog_light_state` | `get_exterior_lights_status` |
| `Vehicle.Body.Lights.Hazard.IsSignaling` | actuator | boolean | bool | true, false | fixed: false | `set_hazard_lights_state` | `get_exterior_lights_status` |

### Wipers and mirrors

Wiper modes, exterior mirrors.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Body.Windshield.Front.Wiping.Mode` | actuator | string | str | "OFF", "SLOW", "MEDIUM", "FAST", "INTERVAL", "RAIN_SENSOR" | from weather | `set_wiper_mode` | `get_wiper_status` |
| `Vehicle.Body.Windshield.Front.Wiping.Intensity` | actuator | uint8 | int | 1, 2, 3, 4 | random | `set_wiper_mode` | `get_wiper_status` |
| `Vehicle.Body.Windshield.Rear.Wiping.Mode` | actuator | string | str | "OFF", "INTERVAL", "SLOW" | from weather | `set_wiper_mode` | `get_wiper_status` |
| `Vehicle.Body.Mirrors.DriverSide.IsFolded` | actuator | boolean | bool | true, false | fixed: false | `set_side_mirror_fold_state` | `get_side_mirror_status` |
| `Vehicle.Body.Mirrors.DriverSide.IsHeatingOn` | actuator | boolean | bool | true, false | from weather | `set_side_mirror_heating_state` | `get_side_mirror_status` |
| `Vehicle.Body.Mirrors.PassengerSide.IsFolded` | actuator | boolean | bool | true, false | fixed: false | `set_side_mirror_fold_state` | `get_side_mirror_status` |
| `Vehicle.Body.Mirrors.PassengerSide.IsHeatingOn` | actuator | boolean | bool | true, false | from weather | `set_side_mirror_heating_state` | `get_side_mirror_status` |

### Trunk

Trunk lid and lock.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Body.Trunk.Rear.IsOpen` | actuator | boolean | bool | true, false | fixed: false | `set_trunk_lid_state` | `get_trunk_status` |
| `Vehicle.Body.Trunk.Rear.IsLocked` | actuator | boolean | bool | true, false | random | `set_trunk_lock_state` | `get_trunk_status` |

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
| `Vehicle.Powertrain.TractionBattery.Charging.ChargingPort.FrontLeft.IsFlapOpen` | actuator | boolean | bool | true, false | fixed: false | `set_charge_port_door_state` | `get_charge_port_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.ChargingPort.FrontLeft.IsChargingCableConnected` | sensor | boolean | bool | true, false | fixed: false | read-only | `get_charge_port_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.ChargingPort.FrontLeft.IsChargingCableLocked` | actuator | boolean | bool | true, false | fixed: false | `set_charging_cable_lock_state` | `get_charge_port_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.ChargeLimit` | actuator | uint8 (percent) | int | 50 to 100, step 5 | random | `set_charge_limit` | `get_charging_status`, `estimate_charging_time`, `estimate_battery_after_charging` |
| `Vehicle.Powertrain.TractionBattery.Charging.Timer.Mode` | actuator | string | str | "INACTIVE", "START_TIME", "END_TIME" | random | `set_charging_timer` | `get_charging_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.Timer.Time` | actuator | string (iso8601) | str | location or route ID, empty when unset | fixed: "" | `set_charging_timer` | `get_charging_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.IsCharging` | sensor | boolean | bool | true, false | fixed: false | `set_charging_state` | `get_charging_status` |
| `Vehicle.Powertrain.TractionBattery.Charging.MaxAcceptedPowerAC` *(extension)* | attribute | float (kW) | float | 3.7, 7.4, 11.0 | fixed: 7.4 | read-only | `get_vehicle_specs`, `get_charging_status`, `estimate_charging_time`, `estimate_battery_after_charging` |
| `Vehicle.Powertrain.TractionBattery.Charging.MaxAcceptedPowerDC` *(extension)* | attribute | float (kW) | float | 0.0, 50.0, 80.0 | fixed: 50.0 | read-only | `get_vehicle_specs`, `get_charging_status`, `estimate_charging_time`, `estimate_battery_after_charging` |

### Battery, fuel, and hybrid

Levels, capacities, consumption, hybrid and drive modes.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.Powertrain.FuelSystem.IsFuelPortFlapOpen` | actuator | boolean | bool | true, false | fixed: false | `set_fuel_door_state` | `get_fuel_door_status` |
| `Vehicle.Powertrain.Type` | attribute | string | str | "HYBRID" | fixed: "HYBRID" | read-only | `get_vehicle_specs` |
| `Vehicle.Powertrain.FuelSystem.HybridType` | attribute | string | str | "PHEV" | fixed: "PHEV" | read-only | `get_vehicle_specs` |
| `Vehicle.Powertrain.FuelSystem.TankCapacity` | attribute | float (l) | float | 30.0 to 80.0, step 0.5 | fixed: 45.0 | read-only | `get_vehicle_specs`, `get_energy_status`, `estimate_refuel`, `estimate_route_energy` |
| `Vehicle.Powertrain.TractionBattery.NetCapacity` | sensor | uint16 (kWh) | int | 8 to 40, step 1 | fixed: 18 | read-only | `get_vehicle_specs`, `get_energy_status`, `estimate_charging_time`, `estimate_battery_after_charging`, `estimate_electric_distance`, `estimate_route_energy` |
| `Vehicle.Powertrain.FuelSystem.RelativeLevel` | sensor | uint8 (percent) | int | 0 to 100, step 1 | random | read-only | `get_energy_status`, `estimate_refuel`, `estimate_route_energy` |
| `Vehicle.Powertrain.FuelSystem.IsFuelLevelLow` | sensor | boolean | bool | true, false | random | read-only | `get_energy_status`, `estimate_route_energy` |
| `Vehicle.Powertrain.TractionBattery.StateOfCharge.Displayed` | sensor | float (percent) | float | 0.0 to 100.0, step 1.0 | random | read-only | `get_energy_status`, `estimate_charging_time`, `estimate_battery_after_charging`, `estimate_electric_distance`, `estimate_route_energy` |
| `Vehicle.Powertrain.RangeExtender.ChargeDepleting.EnergyConsumption` | sensor | float (kWh/100km) | float | 12.0 to 25.0, step 0.5 | fixed: 18.0 | read-only | `get_energy_status`, `estimate_electric_distance`, `estimate_route_energy` |
| `Vehicle.Powertrain.FuelSystem.AverageConsumption` | sensor | float (l/100km) | float | 3.0 to 12.0, step 0.1 | random | read-only | `get_trip_info`, `get_energy_status`, `estimate_refuel`, `estimate_route_energy` |
| `Vehicle.Powertrain.CombustionEngine.IsRunning` | sensor | boolean | bool | true, false | random | `set_hybrid_mode` | `get_energy_status` |
| `Vehicle.Powertrain.RangeExtender.OperatingMode` | sensor | string | str | "CHARGE_DEPLETING", "CHARGE_SUSTAINING", "BLENDED" | random | `set_hybrid_mode` | `get_energy_status` |
| `Vehicle.Powertrain.Hybrid.Mode` *(extension)* | actuator | string | str | "AUTO", "ELECTRIC", "HOLD", "CHARGE" | random | `set_hybrid_mode` | `get_energy_status`, `estimate_route_energy` |
| `Vehicle.Powertrain.Hybrid.ChargeTarget` *(extension)* | actuator | uint8 (percent) | int | 20 to 80, step 10 | random | `set_hybrid_mode` | `get_energy_status` |
| `Vehicle.Powertrain.Hybrid.RegenLevel` *(extension)* | actuator | uint8 | int | 0, 1, 2, 3 | random | `set_regen_braking_level` | `get_energy_status` |
| `Vehicle.Powertrain.Transmission.PerformanceMode` | actuator | string | str | "NORMAL", "SPORT", "ECONOMY" | random | `set_drive_mode` | `get_energy_status` |

### Vehicle identity

Fixed facts about the car.

| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|---|---|
| `Vehicle.VehicleIdentification.VehicleExteriorColor` | attribute | string | str | "Black", "White", "Silver", "Gray", "Blue", "Red", "Green" | fixed: "Blue" | read-only | `get_vehicle_specs` |
