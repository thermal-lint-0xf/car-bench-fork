# Hybrid Assistant Tools

**108 tools** in total: **96 positive** and **12 negative**. The spec files are the `2026-10-11_hybrid_*.json` files in this folder.

Of the 96 positive tools, **52 come from CAR-bench** (38 with the same capability, 14 extended) and **44 are new**.

## Positive tools by domain

| Domain | Action | Retrieve | Total | From CAR-bench | New |
|---|---|---|---|---|---|
| Vehicle (Body, lights, climate, seats, vehicle status) | 32 | 19 | 51 | 26 | 25 |
| Navigation (Routes, stops, places) | 9 | 6 | 15 | 13 | 2 |
| Energy (Hybrid powertrain, charging, fuel) | 5 | 7 | 12 | 4 | 8 |
| Media (Audio and radio) | 7 | 1 | 8 | – | 8 |
| Communication (Calls, texts, email, calendar) | 3 | 3 | 6 | 5 | 1 |
| Utility (Math and time) | – | 2 | 2 | 2 | – |
| Weather (Conditions at a place today) | – | 1 | 1 | 1 | – |
| Preferences (Saved driver preferences) | – | 1 | 1 | 1 | – |
| **Total** | **56** | **40** | **96** | **52** | **44** |

CAR-bench has 57 tools. All of them are covered except `think` and `planning_tool`, which are reasoning scaffolds for the agent rather than features for the driver.

Origin tags used below:

- **CAR-bench**: the same capability as a CAR-bench tool, sometimes renamed or merged from several getters.
- **CAR-bench, extended**: built on a CAR-bench tool, with added parameters, values, or state.
- **New**: not in CAR-bench.

## Positive tools

### Vehicle (51)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `set_window_position` | `window: str`, `position?: int` | action | CAR-bench | `open_close_window` | Open or close one window, or all four, to a position from 0 (closed) to 100 (fully open). |
| `set_sunshade_position` | `position?: int` | action | CAR-bench | `open_close_sunshade` | Open or close the sunroof sunshade to a position from 0 (closed) to 100 (fully open). |
| `set_sunroof_position` | `position?: int` | action | CAR-bench | `open_close_sunroof` | Open or close the sunroof to a position from 0 (closed) to 100 (fully open). |
| `get_window_positions` | – | retrieve | CAR-bench | `get_vehicle_window_positions` | Return the opening position of all four windows. |
| `get_sunroof_and_sunshade_position` | – | retrieve | CAR-bench | `get_sunroof_and_sunshade_position` | Return the opening position of the sunroof and the sunshade. |
| `set_door_locks` | `locked: bool` | action | New | – | Lock or unlock all doors. |
| `set_child_lock` | `door: str`, `on: bool` | action | New | – | Engage or release the child safety lock on a rear door, so it cannot be opened from inside. |
| `set_trunk` | `open: bool` | action | CAR-bench, extended | `open_close_trunk_door` | Open or close the power trunk lid. Adds the stopped-in-park rule. |
| `set_fuel_door` | `open: bool` | action | New | – | Open or close the fuel filler door for refueling. |
| `set_charge_port` | `open: bool` | action | New | – | Open or close the charging port door for plug-in charging. |
| `get_door_lock_status` | – | retrieve | New | – | Return whether the doors are locked. |
| `get_child_lock_status` | – | retrieve | New | – | Return whether the child safety lock is engaged on each rear door. |
| `get_trunk_status` | – | retrieve | CAR-bench | `get_trunk_door_position` | Return whether the trunk lid is open or closed. |
| `get_fuel_door_status` | – | retrieve | New | – | Return whether the fuel filler door is open or closed. |
| `get_charge_port_status` | – | retrieve | New | – | Return whether the charging port door is open or closed. |
| `set_low_beams` | `on: bool` | action | CAR-bench | `set_head_lights_low_beams` | Turn the low beam headlights on or off. |
| `set_high_beams` | `on: bool` | action | CAR-bench | `set_head_lights_high_beams` | Turn the high beam headlights on or off. |
| `set_fog_lights` | `on: bool` | action | CAR-bench | `set_fog_lights` | Turn the front fog lights on or off. |
| `set_wiper_speed` | `speed: int` | action | New | – | Set the front windshield wiper speed. |
| `set_rear_wiper` | `on: bool` | action | New | – | Turn the rear window wiper on or off. |
| `set_side_mirrors_folded` | `folded: bool` | action | New | – | Fold or unfold both side mirrors. |
| `set_mirror_heating` | `on: bool` | action | New | – | Turn side mirror heating on or off, to clear ice, frost, or fog from the mirrors. |
| `get_exterior_lights_status` | – | retrieve | CAR-bench | `get_exterior_lights_status` | Return whether the low beams, high beams, and fog lights are on. |
| `get_wiper_status` | – | retrieve | New | – | Return the front wiper speed and whether the rear wiper is on. |
| `get_side_mirror_status` | – | retrieve | New | – | Return whether the side mirrors are folded and whether mirror heating is on. |
| `set_reading_light` | `seat: str`, `on: bool` | action | CAR-bench | `set_reading_light` | Turn the reading light at one seat, or at all seats, on or off. |
| `set_ambient_light` | `color: str`, `brightness_pct?: int` | action | CAR-bench, extended | `set_ambient_lights` | Set the ambient interior lighting color and brightness, or turn it off with color "off". Adds brightness. |
| `get_reading_lights_status` | – | retrieve | CAR-bench | `get_reading_lights_status` | Return which seats have their reading light on. |
| `get_ambient_light_status` | – | retrieve | CAR-bench, extended | `get_ambient_light_status_and_color` | Return the ambient light color, or "off", and its brightness. Adds brightness. |
| `set_climate_temperature` | `zone: str`, `temperature_c: float` | action | CAR-bench, extended | `set_climate_temperature` | Set the target temperature of one climate zone or all zones. Adds a rear zone. |
| `set_fan_speed` | `speed: int` | action | CAR-bench | `set_fan_speed` | Set the climate fan speed. |
| `set_airflow_direction` | `direction: str` | action | CAR-bench | `set_fan_airflow_direction` | Set where the climate fan blows air. |
| `set_air_conditioning` | `on: bool` | action | CAR-bench | `set_air_conditioning` | Turn the air conditioning compressor on or off. |
| `set_air_circulation` | `mode: str` | action | CAR-bench | `set_air_circulation` | Set the air intake mode: automatic, fresh outside air, or recirculated cabin air. |
| `set_defrost` | `window: str`, `on: bool` | action | CAR-bench | `set_window_defrost` | Turn the front windshield defrost, the rear window defrost, or both on or off. |
| `set_climate_auto_mode` | `on: bool` | action | New | – | Turn climate auto mode on or off. |
| `get_climate_status` | – | retrieve | CAR-bench, extended | `get_climate_settings`, `get_temperature_inside_car` | Return the climate settings (auto mode, zone temperatures, fan speed, airflow direction, air conditioning, air circulation, defrost) plus the measured cabin and outside temperatures. Merges two CAR-bench getters and adds auto mode, the rear zone, and measured cabin and outside temperatures. |
| `set_seat_heating` | `seat: str`, `level: int` | action | CAR-bench, extended | `set_seat_heating` | Set the seat heating level for one seat or all seats. Adds the rear seats. |
| `set_seat_ventilation` | `seat: str`, `level: int` | action | New | – | Set the seat ventilation (cooling) level for a front seat. |
| `set_seat_massage` | `seat: str`, `mode: str`, `intensity?: int` | action | New | – | Start, change, or stop the massage program of a front seat. |
| `set_seat_fore_aft` | `seat: str`, `position_pct: int` | action | New | – | Move a front seat forward or back. |
| `set_seat_backrest` | `seat: str`, `angle_deg: int` | action | New | – | Change the backrest angle of a front seat. |
| `recall_driver_memory_profile` | `profile: int` | action | New | – | Move the driver seat to a saved memory profile. |
| `set_steering_wheel_heating` | `level: int` | action | CAR-bench | `set_steering_wheel_heating` | Set the steering wheel heating level. |
| `get_seat_status` | – | retrieve | CAR-bench, extended | `get_seat_heating_level`, `get_seats_occupancy`, `get_steering_wheel_heating_level` | Return seat occupancy, seat heating, ventilation, massage, front seat positions, the last recalled driver memory profile, and steering wheel heating. Merges three CAR-bench getters and adds ventilation, massage, and seat position. |
| `get_driving_status` | – | retrieve | New | – | Return the current speed, selected gear, and odometer. |
| `get_tire_pressure` | – | retrieve | New | – | Return the pressure of all four tires in kPa and flag any tire below 200 kPa as low. |
| `get_maintenance_status` | – | retrieve | New | – | Return engine oil life, washer fluid level, and the distance until the next scheduled service. |
| `get_trip_info` | – | retrieve | New | – | Return the trip computer: distance since last reset, average fuel and electric consumption, and the share driven electrically. |
| `reset_trip_computer` | – | action | New | – | Reset the trip computer to zero. |
| `get_vehicle_specs` | – | retrieve | CAR-bench, extended | `get_car_color` | Return fixed facts about the car: exterior color, fuel tank capacity, usable battery capacity, reference consumption figures, and maximum AC and DC charging power. Adds tank, battery, consumption, and charging specs. |

### Navigation (15)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_location_id_by_name` | `name: str` | retrieve | CAR-bench | `get_location_id_by_location_name` | Look up the location ID of a city, address, or named place. |
| `search_poi_at_location` | `location_id: str`, `category: str`, `open_now_only?: bool` | retrieve | CAR-bench, extended | `search_poi_at_location` | Find points of interest of one category near a location. Adds gas stations and other categories, and an open-now filter. |
| `search_poi_along_route` | `route_id: str`, `category: str`, `max_detour_minutes?: int` | retrieve | CAR-bench, extended | `search_poi_along_the_route` | Find points of interest of one category along a route, with the km along the route and the detour time. Adds gas stations and other categories, and a detour limit. |
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
| `set_voice_guidance` | `on: bool` | action | New | – | Turn spoken turn-by-turn navigation guidance on or off. |
| `get_navigation_status` | – | retrieve | CAR-bench, extended | `get_current_navigation_state` | Return whether guidance is active, the destination, intermediate stops, current route ID, route options, and voice guidance state. Adds route options and voice guidance. |

### Energy (12)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `get_energy_status` | – | retrieve | CAR-bench, extended | `get_charging_specs_and_status`, `get_fuel_information` | Return the battery level, fuel level, estimated electric range, fuel range, and combined range in km, plus the current hybrid mode, drive mode, regen level, charge target, and whether the engine is running. Combines battery and fuel for the hybrid and adds hybrid mode, drive mode, and regen. |
| `set_hybrid_mode` | `mode: str`, `charge_target_pct?: int` | action | New | – | Choose how the hybrid system uses the battery and the engine. |
| `set_drive_mode` | `mode: str` | action | New | – | Set the driving dynamics mode, which changes throttle response and efficiency. |
| `set_regen_level` | `level: int` | action | New | – | Set the regenerative braking strength. |
| `get_charging_settings` | – | retrieve | New | – | Return the plug-in charging settings: whether a cable is connected, the charge limit, and the delayed charging schedule. |
| `set_charge_limit` | `limit_pct: int` | action | New | – | Set the battery level at which plug-in charging stops. |
| `set_scheduled_charging` | `enabled: bool`, `start_hour?: int` | action | New | – | Turn delayed plug-in charging on or off and set the hour it starts, for example to use cheaper night-time electricity. |
| `estimate_charging_time` | `charger_power_kw: float`, `charger_type: str`, `target_soc_pct: int`, `start_soc_pct: int` | retrieve | CAR-bench | `calculate_charging_time_by_soc` | Estimate how many minutes plug-in charging takes from a start battery level to a target level at a given charger. |
| `estimate_soc_after_charging` | `charger_power_kw: float`, `charger_type: str`, `minutes: int`, `start_soc_pct: int` | retrieve | CAR-bench | `calculate_charging_soc_by_time` | Estimate the battery level after charging for a given number of minutes at a given charger. |
| `estimate_electric_distance` | `from_soc_pct: int`, `to_soc_pct?: int` | retrieve | CAR-bench | `get_distance_by_soc` | Estimate how many km the car can drive on electric power alone between two battery levels. |
| `estimate_refuel` | `target_fuel_pct?: int` | retrieve | New | – | Estimate how many liters are needed to fill the tank to a target level, and the added fuel range in km. |
| `estimate_route_energy` | `route_id: str` | retrieve | New | – | Estimate how much of a route can be driven electrically, how much fuel the rest needs, and whether the car reaches the end without charging or refueling. |

### Media (8)

| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|---|
| `set_media_volume` | `volume: int` | action | New | – | Set the audio volume. |
| `set_media_mute` | `muted: bool` | action | New | – | Mute or unmute the audio without changing the volume. |
| `set_media_source` | `source: str` | action | New | – | Switch the audio source. |
| `set_media_playback` | `playing: bool` | action | New | – | Play or pause the current audio source. |
| `skip_media_track` | `direction: str` | action | New | – | Skip to the next or previous track on the current source and keep playing. |
| `tune_fm_radio` | `frequency_mhz: float` | action | New | – | Tune the FM radio to a frequency and switch the audio source to FM radio. |
| `play_media_by_query` | `query: str`, `media_type?: str` | action | New | – | Search the streaming service for a song, artist, album, playlist, or podcast and start playing the best match. |
| `get_media_status` | – | retrieve | New | – | Return the audio source, whether it is playing, the volume, mute state, and the tuned FM frequency. |

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
| `calculate_datetime` | `time: str`, `add_minutes: int` | retrieve | CAR-bench | `calculate_datetime` | Add or subtract hours and minutes to a time, for example to work out an arrival time. |

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

The 103 state values the tools change and read, grouped by component. Each conversation starts from a random but valid state, and every successful action updates it.

### Comfort

Windows, sunroof, seats, steering wheel, interior lights.

| State | Type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|
| `vehicle.comfort.window_positions.front_left` | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `vehicle.comfort.window_positions.front_right` | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `vehicle.comfort.window_positions.rear_left` | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `vehicle.comfort.window_positions.rear_right` | int | 0 to 100, step 5 | random | `set_window_position` | `get_window_positions` |
| `vehicle.comfort.sunroof_position_pct` | int | 0 to 100, step 5 | from weather | `set_sunroof_position` | `get_sunroof_and_sunshade_position` |
| `vehicle.comfort.sunshade_position_pct` | int | 0 to 100, step 5 | random | `set_sunshade_position` | `get_sunroof_and_sunshade_position` |
| `vehicle.comfort.seat_occupied.front_left` | bool | true, false | fixed: true | read-only | `get_seat_status` |
| `vehicle.comfort.seat_occupied.front_right` | bool | true, false | random | read-only | `get_seat_status` |
| `vehicle.comfort.seat_occupied.rear_left` | bool | true, false | random | read-only | `get_seat_status` |
| `vehicle.comfort.seat_occupied.rear_right` | bool | true, false | random | read-only | `get_seat_status` |
| `vehicle.comfort.seat_heating.front_left` | int | 0, 1, 2, 3 | from weather | `set_seat_heating` | `get_seat_status` |
| `vehicle.comfort.seat_heating.front_right` | int | 0, 1, 2, 3 | from weather | `set_seat_heating` | `get_seat_status` |
| `vehicle.comfort.seat_heating.rear_left` | int | 0, 1, 2, 3 | from weather | `set_seat_heating` | `get_seat_status` |
| `vehicle.comfort.seat_heating.rear_right` | int | 0, 1, 2, 3 | from weather | `set_seat_heating` | `get_seat_status` |
| `vehicle.comfort.seat_ventilation.front_left` | int | 0, 1, 2, 3 | from weather | `set_seat_ventilation` | `get_seat_status` |
| `vehicle.comfort.seat_massage_mode.front_left` | str | "off", "wave", "pulse", "stretch", "lumbar" | random | `set_seat_massage` | `get_seat_status` |
| `vehicle.comfort.seat_massage_intensity.front_left` | int | 1, 2, 3 | random | `set_seat_massage` | `get_seat_status` |
| `vehicle.comfort.seat_fore_aft_pct.front_left` | int | 0 to 100, step 5 | random | `set_seat_fore_aft`, `recall_driver_memory_profile` | `get_seat_status` |
| `vehicle.comfort.seat_backrest_angle_deg.front_left` | int | 5 to 40, step 1 | random | `set_seat_backrest`, `recall_driver_memory_profile` | `get_seat_status` |
| `vehicle.comfort.seat_ventilation.front_right` | int | 0, 1, 2, 3 | from weather | `set_seat_ventilation` | `get_seat_status` |
| `vehicle.comfort.seat_massage_mode.front_right` | str | "off", "wave", "pulse", "stretch", "lumbar" | random | `set_seat_massage` | `get_seat_status` |
| `vehicle.comfort.seat_massage_intensity.front_right` | int | 1, 2, 3 | random | `set_seat_massage` | `get_seat_status` |
| `vehicle.comfort.seat_fore_aft_pct.front_right` | int | 0 to 100, step 5 | random | `set_seat_fore_aft` | `get_seat_status` |
| `vehicle.comfort.seat_backrest_angle_deg.front_right` | int | 5 to 40, step 1 | random | `set_seat_backrest` | `get_seat_status` |
| `vehicle.comfort.driver_memory_profile` | int | 0, 1, 2, 3 | random | `recall_driver_memory_profile` | `get_seat_status` |
| `vehicle.comfort.steering_wheel_heating` | int | 0, 1, 2, 3 | from weather | `set_steering_wheel_heating` | `get_seat_status` |
| `vehicle.comfort.reading_light.front_left` | bool | true, false | random | `set_reading_light` | `get_reading_lights_status` |
| `vehicle.comfort.reading_light.front_right` | bool | true, false | random | `set_reading_light` | `get_reading_lights_status` |
| `vehicle.comfort.reading_light.rear_left` | bool | true, false | random | `set_reading_light` | `get_reading_lights_status` |
| `vehicle.comfort.reading_light.rear_right` | bool | true, false | random | `set_reading_light` | `get_reading_lights_status` |
| `vehicle.comfort.ambient_light_color` | str | "off", "red", "green", "blue", "yellow", "white", "pink", "orange", "purple", "cyan" | random | `set_ambient_light` | `get_ambient_light_status` |
| `vehicle.comfort.ambient_light_brightness_pct` | int | 10 to 100, step 10 | random | `set_ambient_light` | `get_ambient_light_status` |

### Climate

Temperature zones, fan, air conditioning, defrost.

| State | Type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|
| `vehicle.climate.auto_mode` | bool | true, false | fixed: true | `set_fan_speed`, `set_airflow_direction`, `set_climate_auto_mode` | `get_climate_status` |
| `vehicle.climate.temperature_c.front_left` | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `vehicle.climate.temperature_c.front_right` | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `vehicle.climate.temperature_c.rear` | float | 16.0 to 28.0, step 0.5 | random | `set_climate_temperature` | `get_climate_status` |
| `vehicle.climate.fan_speed` | int | 0, 1, 2, 3, 4, 5 | random | `set_fan_speed` | `get_climate_status` |
| `vehicle.climate.airflow_direction` | str | "feet", "head", "head_feet", "windshield", "windshield_feet", "windshield_head", "windshield_head_feet" | random | `set_airflow_direction` | `get_climate_status` |
| `vehicle.climate.ac_on` | bool | true, false | from weather | `set_air_conditioning` | `get_climate_status` |
| `vehicle.climate.air_circulation` | str | "auto", "fresh_air", "recirculation" | random | `set_air_circulation` | `get_climate_status` |
| `vehicle.climate.front_defrost` | bool | true, false | from weather | `set_defrost` | `get_climate_status` |
| `vehicle.climate.rear_defrost` | bool | true, false | from weather | `set_defrost` | `get_climate_status` |

### Visibility

Exterior lights, wipers, side mirrors.

| State | Type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|
| `vehicle.visibility.low_beams` | bool | true, false | from weather | `set_low_beams` | `get_exterior_lights_status` |
| `vehicle.visibility.high_beams` | bool | true, false | random | `set_high_beams` | `get_exterior_lights_status` |
| `vehicle.visibility.fog_lights` | bool | true, false | from weather | `set_fog_lights` | `get_exterior_lights_status` |
| `vehicle.visibility.wiper_speed` | int | 0, 1, 2, 3 | from weather | `set_wiper_speed` | `get_wiper_status` |
| `vehicle.visibility.rear_wiper` | bool | true, false | from weather | `set_rear_wiper` | `get_wiper_status` |
| `vehicle.visibility.mirrors_folded` | bool | true, false | fixed: false | `set_side_mirrors_folded` | `get_side_mirror_status` |
| `vehicle.visibility.mirror_heating` | bool | true, false | from weather | `set_mirror_heating` | `get_side_mirror_status` |

### Access

Door locks, child locks, trunk, fuel door, charge port.

| State | Type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|
| `vehicle.access.doors_locked` | bool | true, false | random | `set_door_locks` | `get_door_lock_status` |
| `vehicle.access.child_lock.rear_left` | bool | true, false | random | `set_child_lock` | `get_child_lock_status` |
| `vehicle.access.child_lock.rear_right` | bool | true, false | random | `set_child_lock` | `get_child_lock_status` |
| `vehicle.access.trunk_open` | bool | true, false | fixed: false | `set_trunk` | `get_trunk_status` |
| `vehicle.access.fuel_door_open` | bool | true, false | fixed: false | `set_fuel_door` | `get_fuel_door_status` |
| `vehicle.access.charge_port_open` | bool | true, false | fixed: false | `set_charge_port` | `get_charge_port_status` |

### Media

Audio source, playback, volume, radio.

| State | Type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|
| `vehicle.media.source` | str | "fm_radio", "dab_radio", "bluetooth", "usb", "streaming" | random | `set_media_source`, `tune_fm_radio`, `play_media_by_query` | `get_media_status` |
| `vehicle.media.playing` | bool | true, false | random | `set_media_source`, `set_media_playback`, `skip_media_track`, `tune_fm_radio`, `play_media_by_query` | `get_media_status` |
| `vehicle.media.volume` | int | 0 to 30, step 1 | random | `set_media_volume` | `get_media_status` |
| `vehicle.media.muted` | bool | true, false | random | `set_media_volume`, `set_media_mute` | `get_media_status` |
| `vehicle.media.fm_frequency_mhz` | float | 87.5 to 108.0, step 0.1 | random | `tune_fm_radio` | `get_media_status` |

### Powertrain

Battery, fuel, hybrid and drive modes, charging settings.

| State | Type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|
| `vehicle.powertrain.fuel_level_pct` | int | 0 to 100, step 1 | random | read-only | `get_energy_status`, `estimate_refuel`, `estimate_route_energy` |
| `vehicle.powertrain.battery_soc_pct` | int | 0 to 100, step 1 | random | read-only | `get_energy_status`, `estimate_charging_time`, `estimate_soc_after_charging`, `estimate_electric_distance`, `estimate_route_energy` |
| `vehicle.powertrain.fuel_tank_capacity_l` | float | 30.0 to 80.0, step 0.5 | fixed: 45.0 | read-only | `get_vehicle_specs`, `get_energy_status`, `estimate_refuel`, `estimate_route_energy` |
| `vehicle.powertrain.battery_usable_capacity_kwh` | float | 8.0 to 40.0, step 0.5 | fixed: 18.0 | read-only | `get_vehicle_specs`, `get_energy_status`, `estimate_charging_time`, `estimate_soc_after_charging`, `estimate_electric_distance`, `estimate_route_energy` |
| `vehicle.powertrain.electric_consumption_kwh_per_100km` | float | 12.0 to 25.0, step 0.5 | fixed: 18.0 | read-only | `get_vehicle_specs`, `get_energy_status`, `estimate_electric_distance`, `estimate_route_energy` |
| `vehicle.powertrain.fuel_consumption_l_per_100km` | float | 3.0 to 12.0, step 0.1 | fixed: 6.0 | read-only | `get_vehicle_specs`, `get_energy_status`, `estimate_refuel`, `estimate_route_energy` |
| `vehicle.powertrain.max_ac_charging_kw` | float | 3.7, 7.4, 11.0 | fixed: 7.4 | read-only | `get_vehicle_specs`, `get_charging_settings`, `estimate_charging_time`, `estimate_soc_after_charging` |
| `vehicle.powertrain.max_dc_charging_kw` | float | 0.0, 50.0, 80.0 | fixed: 50.0 | read-only | `get_vehicle_specs`, `get_charging_settings`, `estimate_charging_time`, `estimate_soc_after_charging` |
| `vehicle.powertrain.drive_mode` | str | "eco", "comfort", "sport" | random | `set_drive_mode` | `get_energy_status` |
| `vehicle.powertrain.hybrid_mode` | str | "auto", "electric", "hold", "charge" | random | `set_hybrid_mode` | `get_energy_status`, `estimate_route_energy` |
| `vehicle.powertrain.battery_charge_target_pct` | int | 20 to 80, step 10 | random | `set_hybrid_mode` | `get_energy_status` |
| `vehicle.powertrain.regen_level` | int | 0, 1, 2, 3 | random | `set_regen_level` | `get_energy_status` |
| `vehicle.powertrain.engine_running` | bool | true, false | random | `set_hybrid_mode` | `get_energy_status` |
| `vehicle.powertrain.plugged_in` | bool | true, false | fixed: false | read-only | `get_charging_settings` |
| `vehicle.powertrain.charge_limit_pct` | int | 50 to 100, step 5 | random | `set_charge_limit` | `get_charging_settings`, `estimate_charging_time`, `estimate_soc_after_charging` |
| `vehicle.powertrain.scheduled_charging_enabled` | bool | true, false | random | `set_scheduled_charging` | `get_charging_settings` |
| `vehicle.powertrain.scheduled_charging_start_hour` | int | 0 to 23, step 1 | random | `set_scheduled_charging` | `get_charging_settings` |

### Telemetry

Read-only sensors: speed, gear, temperatures, tires, maintenance, trip computer.

| State | Type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|
| `vehicle.telemetry.speed_kph` | int | 0 to 160, step 1 | random | read-only | `get_driving_status` |
| `vehicle.telemetry.gear` | str | "P", "R", "N", "D" | random | read-only | `get_driving_status` |
| `vehicle.telemetry.outside_temp_c` | float | -30.0 to 50.0, step 0.5 | from weather | read-only | `get_climate_status` |
| `vehicle.telemetry.cabin_temp_c` | float | -20.0 to 55.0, step 0.5 | from weather | read-only | `get_climate_status` |
| `vehicle.telemetry.tire_pressure_kpa.front_left` | int | 150 to 280, step 5 | random | read-only | `get_tire_pressure` |
| `vehicle.telemetry.tire_pressure_kpa.front_right` | int | 150 to 280, step 5 | random | read-only | `get_tire_pressure` |
| `vehicle.telemetry.tire_pressure_kpa.rear_left` | int | 150 to 280, step 5 | random | read-only | `get_tire_pressure` |
| `vehicle.telemetry.tire_pressure_kpa.rear_right` | int | 150 to 280, step 5 | random | read-only | `get_tire_pressure` |
| `vehicle.telemetry.odometer_km` | int | 0 to 300000, step 1 | random | read-only | `get_driving_status`, `get_maintenance_status` |
| `vehicle.telemetry.oil_life_pct` | int | 0 to 100, step 1 | random | read-only | `get_maintenance_status` |
| `vehicle.telemetry.washer_fluid_pct` | int | 0 to 100, step 5 | random | read-only | `get_maintenance_status` |
| `vehicle.telemetry.next_service_km` | int | 0 to 30000, step 100 | random | read-only | `get_maintenance_status` |
| `vehicle.telemetry.trip_distance_km` | float | 0.0 to 2000.0, step 0.1 | random | `reset_trip_computer` | `get_trip_info` |
| `vehicle.telemetry.trip_avg_fuel_l_per_100km` | float | 0.0 to 15.0, step 0.1 | random | `reset_trip_computer` | `get_trip_info` |
| `vehicle.telemetry.trip_avg_energy_kwh_per_100km` | float | 0.0 to 30.0, step 0.1 | random | `reset_trip_computer` | `get_trip_info` |
| `vehicle.telemetry.trip_electric_share_pct` | int | 0 to 100, step 1 | random | `reset_trip_computer` | `get_trip_info` |

### Vehicle info

Fixed facts about the car.

| State | Type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|
| `vehicle.info.exterior_color` | str | "black", "white", "silver", "gray", "blue", "red", "green" | fixed: "blue" | read-only | `get_vehicle_specs` |

### Navigation

Active route, stops, route options.

| State | Type | Values | Start | Changed by | Read by |
|---|---|---|---|---|---|
| `navigation.active` | bool | true, false | fixed: false | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `navigation.destination_id` | str | location or route ID, empty when unset | fixed: "" | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `navigation.waypoint_1_id` | str | location or route ID, empty when unset | fixed: "" | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `navigation.waypoint_2_id` | str | location or route ID, empty when unset | fixed: "" | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `navigation.waypoint_3_id` | str | location or route ID, empty when unset | fixed: "" | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `navigation.route_id` | str | location or route ID, empty when unset | fixed: "" | `set_navigation`, `add_navigation_waypoint`, `replace_navigation_waypoint`, `delete_navigation_waypoint`, `replace_navigation_destination`, `delete_navigation_destination`, `cancel_navigation` | `get_navigation_status` |
| `navigation.avoid_tolls` | bool | true, false | random | `set_route_options` | `get_routes`, `get_navigation_status` |
| `navigation.avoid_highways` | bool | true, false | random | `set_route_options` | `get_routes`, `get_navigation_status` |
| `navigation.voice_guidance_on` | bool | true, false | random | `set_voice_guidance` | `get_navigation_status` |
