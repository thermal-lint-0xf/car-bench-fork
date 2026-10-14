# Hybrid Assistant Tools

**100 tools** in total: **88 positive** and **12 negative**. The spec files are the `2026-10-11_hybrid_*.json` files in this folder.

Of the 88 positive tools, **50 come from CAR-bench** (34 with the same capability, 16 extended) and **38 are new**.

## Positive tools by domain

| Domain | Action | Retrieve | Total | From CAR-bench | New |
|---|---|---|---|---|---|
| Vehicle (Body, lights, climate, seats, vehicle status) | 32 | 11 | 43 | 24 | 19 |
| Navigation (Routes, stops, places) | 9 | 6 | 15 | 13 | 2 |
| Energy (Hybrid powertrain, charging, fuel) | 5 | 7 | 12 | 4 | 8 |
| Media (Audio and radio) | 7 | 1 | 8 | – | 8 |
| Communication (Calls, texts, email, calendar) | 3 | 3 | 6 | 5 | 1 |
| Utility (Math and time) | – | 2 | 2 | 2 | – |
| Weather (Conditions at a place today) | – | 1 | 1 | 1 | – |
| Preferences (Saved driver preferences) | – | 1 | 1 | 1 | – |
| **Total** | **56** | **32** | **88** | **50** | **38** |

CAR-bench has 57 tools. All of them are covered except `think` and `planning_tool`, which are reasoning scaffolds for the agent rather than features for the driver.

Origin tags used below:

- **CAR-bench**: the same capability as a CAR-bench tool, sometimes renamed or merged from several getters.
- **CAR-bench, extended**: built on a CAR-bench tool, with added parameters, values, or state.
- **New**: not in CAR-bench.

## Positive tools

### Vehicle (43)

| Tool | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|
| `set_window_position` | action | CAR-bench | `open_close_window` | Open or close one window, or all four, to a position from 0 (closed) to 100 (fully open). |
| `set_sunshade_position` | action | CAR-bench | `open_close_sunshade` | Open or close the sunroof sunshade to a position from 0 (closed) to 100 (fully open). |
| `set_sunroof_position` | action | CAR-bench | `open_close_sunroof` | Open or close the sunroof to a position from 0 (closed) to 100 (fully open). |
| `get_window_and_roof_status` | retrieve | CAR-bench | `get_vehicle_window_positions`, `get_sunroof_and_sunshade_position` | Return the position of all four windows, the sunroof, and the sunshade. Merges two CAR-bench getters. |
| `set_door_locks` | action | New | – | Lock or unlock all doors. |
| `set_child_lock` | action | New | – | Engage or release the child safety lock on a rear door, so it cannot be opened from inside. |
| `set_trunk` | action | CAR-bench, extended | `open_close_trunk_door` | Open or close the power trunk lid. Adds the stopped-in-park rule. |
| `set_fuel_door` | action | New | – | Open or close the fuel filler door for refueling. |
| `set_charge_port` | action | New | – | Open or close the charging port door for plug-in charging. |
| `get_access_status` | retrieve | CAR-bench, extended | `get_trunk_door_position` | Return whether the doors are locked, the rear child locks, and whether the trunk, fuel door, and charge port door are open. Adds door locks, child locks, fuel door, and charge port. |
| `set_low_beams` | action | CAR-bench | `set_head_lights_low_beams` | Turn the low beam headlights on or off. |
| `set_high_beams` | action | CAR-bench | `set_head_lights_high_beams` | Turn the high beam headlights on or off. |
| `set_fog_lights` | action | CAR-bench | `set_fog_lights` | Turn the front fog lights on or off. |
| `set_wiper_speed` | action | New | – | Set the front windshield wiper speed. |
| `set_rear_wiper` | action | New | – | Turn the rear window wiper on or off. |
| `set_side_mirrors_folded` | action | New | – | Fold or unfold both side mirrors. |
| `set_mirror_heating` | action | New | – | Turn side mirror heating on or off, to clear ice, frost, or fog from the mirrors. |
| `get_visibility_status` | retrieve | CAR-bench, extended | `get_exterior_lights_status` | Return the state of the low beams, high beams, fog lights, front and rear wipers, side mirror folding, and mirror heating. Adds wipers and side mirrors. |
| `set_reading_light` | action | CAR-bench | `set_reading_light` | Turn the reading light at one seat, or at all seats, on or off. |
| `set_ambient_light` | action | CAR-bench, extended | `set_ambient_lights` | Set the ambient interior lighting color and brightness, or turn it off with color "off". Adds brightness. |
| `get_interior_lights_status` | retrieve | CAR-bench, extended | `get_ambient_light_status_and_color`, `get_reading_lights_status` | Return which reading lights are on and the ambient light color and brightness. Merges two CAR-bench getters and adds brightness. |
| `set_climate_temperature` | action | CAR-bench, extended | `set_climate_temperature` | Set the target temperature of one climate zone or all zones. Adds a rear zone. |
| `set_fan_speed` | action | CAR-bench | `set_fan_speed` | Set the climate fan speed. |
| `set_airflow_direction` | action | CAR-bench | `set_fan_airflow_direction` | Set where the climate fan blows air. |
| `set_air_conditioning` | action | CAR-bench | `set_air_conditioning` | Turn the air conditioning compressor on or off. |
| `set_air_circulation` | action | CAR-bench | `set_air_circulation` | Set the air intake mode: automatic, fresh outside air, or recirculated cabin air. |
| `set_defrost` | action | CAR-bench | `set_window_defrost` | Turn the front windshield defrost, the rear window defrost, or both on or off. |
| `set_climate_auto_mode` | action | New | – | Turn climate auto mode on or off. |
| `get_climate_status` | retrieve | CAR-bench, extended | `get_climate_settings`, `get_temperature_inside_car` | Return the climate settings (auto mode, zone temperatures, fan speed, airflow direction, air conditioning, air circulation, defrost) plus the measured cabin and outside temperatures. Merges two CAR-bench getters and adds auto mode, the rear zone, and measured cabin and outside temperatures. |
| `set_seat_heating` | action | CAR-bench, extended | `set_seat_heating` | Set the seat heating level for one seat or all seats. Adds the rear seats. |
| `set_seat_ventilation` | action | New | – | Set the seat ventilation (cooling) level for a front seat. |
| `set_seat_massage` | action | New | – | Start, change, or stop the massage program of a front seat. |
| `set_seat_fore_aft` | action | New | – | Move a front seat forward or back. |
| `set_seat_backrest` | action | New | – | Change the backrest angle of a front seat. |
| `recall_driver_memory_profile` | action | New | – | Move the driver seat to a saved memory profile. |
| `set_steering_wheel_heating` | action | CAR-bench | `set_steering_wheel_heating` | Set the steering wheel heating level. |
| `get_seat_status` | retrieve | CAR-bench, extended | `get_seat_heating_level`, `get_seats_occupancy`, `get_steering_wheel_heating_level` | Return seat occupancy, seat heating, ventilation, massage, front seat positions, the last recalled driver memory profile, and steering wheel heating. Merges three CAR-bench getters and adds ventilation, massage, and seat position. |
| `get_driving_status` | retrieve | New | – | Return the current speed, selected gear, and odometer. |
| `get_tire_pressure` | retrieve | New | – | Return the pressure of all four tires in kPa and flag any tire below 200 kPa as low. |
| `get_maintenance_status` | retrieve | New | – | Return engine oil life, washer fluid level, and the distance until the next scheduled service. |
| `get_trip_info` | retrieve | New | – | Return the trip computer: distance since last reset, average fuel and electric consumption, and the share driven electrically. |
| `reset_trip_computer` | action | New | – | Reset the trip computer to zero. |
| `get_vehicle_specs` | retrieve | CAR-bench, extended | `get_car_color` | Return fixed facts about the car: exterior color, fuel tank capacity, usable battery capacity, reference consumption figures, and maximum AC and DC charging power. Adds tank, battery, consumption, and charging specs. |

### Navigation (15)

| Tool | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|
| `get_location_id_by_name` | retrieve | CAR-bench | `get_location_id_by_location_name` | Look up the location ID of a city, address, or named place. |
| `search_poi_at_location` | retrieve | CAR-bench, extended | `search_poi_at_location` | Find points of interest of one category near a location. Adds gas stations and other categories, and an open-now filter. |
| `search_poi_along_route` | retrieve | CAR-bench, extended | `search_poi_along_the_route` | Find points of interest of one category along a route, with the km along the route and the detour time. Adds gas stations and other categories, and a detour limit. |
| `get_routes` | retrieve | CAR-bench, extended | `get_routes_from_start_to_destination` | Return up to three route options between two locations with route IDs, distance, duration, toll roads, and road types. Respects the avoid-tolls and avoid-highways options. |
| `convert_route_distance_and_time` | retrieve | CAR-bench | `convert_route_distance_and_time` | On a given route, convert a distance in km into driving time, or a driving time in minutes into distance. |
| `set_navigation` | action | CAR-bench | `set_new_navigation` | Start guidance from the current location to a destination, with up to three intermediate stops in order. |
| `add_navigation_waypoint` | action | CAR-bench | `navigation_add_one_waypoint` | Insert an intermediate stop into the active route. |
| `replace_navigation_waypoint` | action | CAR-bench | `navigation_replace_one_waypoint` | Replace one intermediate stop of the active route with another location. |
| `delete_navigation_waypoint` | action | CAR-bench | `navigation_delete_waypoint` | Remove one intermediate stop from the active route. |
| `replace_navigation_destination` | action | CAR-bench | `navigation_replace_final_destination` | Replace the final destination of the active route and keep the intermediate stops. |
| `delete_navigation_destination` | action | CAR-bench | `navigation_delete_destination` | Remove the final destination so the last intermediate stop becomes the destination. |
| `cancel_navigation` | action | CAR-bench | `delete_current_navigation` | Stop guidance and clear the destination and all stops. |
| `set_route_options` | action | New | – | Set whether route planning avoids toll roads and highways. |
| `set_voice_guidance` | action | New | – | Turn spoken turn-by-turn navigation guidance on or off. |
| `get_navigation_status` | retrieve | CAR-bench, extended | `get_current_navigation_state` | Return whether guidance is active, the destination, intermediate stops, current route ID, route options, and voice guidance state. Adds route options and voice guidance. |

### Energy (12)

| Tool | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|
| `get_energy_status` | retrieve | CAR-bench, extended | `get_charging_specs_and_status`, `get_fuel_information` | Return the battery level, fuel level, estimated electric range, fuel range, and combined range in km, plus the current hybrid mode, drive mode, regen level, charge target, and whether the engine is running. Combines battery and fuel for the hybrid and adds hybrid mode, drive mode, and regen. |
| `set_hybrid_mode` | action | New | – | Choose how the hybrid system uses the battery and the engine. |
| `set_drive_mode` | action | New | – | Set the driving dynamics mode, which changes throttle response and efficiency. |
| `set_regen_level` | action | New | – | Set the regenerative braking strength. |
| `get_charging_settings` | retrieve | New | – | Return the plug-in charging settings: whether a cable is connected, the charge limit, and the delayed charging schedule. |
| `set_charge_limit` | action | New | – | Set the battery level at which plug-in charging stops. |
| `set_scheduled_charging` | action | New | – | Turn delayed plug-in charging on or off and set the hour it starts, for example to use cheaper night-time electricity. |
| `estimate_charging_time` | retrieve | CAR-bench | `calculate_charging_time_by_soc` | Estimate how many minutes plug-in charging takes from a start battery level to a target level at a given charger. |
| `estimate_soc_after_charging` | retrieve | CAR-bench | `calculate_charging_soc_by_time` | Estimate the battery level after charging for a given number of minutes at a given charger. |
| `estimate_electric_distance` | retrieve | CAR-bench | `get_distance_by_soc` | Estimate how many km the car can drive on electric power alone between two battery levels. |
| `estimate_refuel` | retrieve | New | – | Estimate how many liters are needed to fill the tank to a target level, and the added fuel range in km. |
| `estimate_route_energy` | retrieve | New | – | Estimate how much of a route can be driven electrically, how much fuel the rest needs, and whether the car reaches the end without charging or refueling. |

### Media (8)

| Tool | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|
| `set_media_volume` | action | New | – | Set the audio volume. |
| `set_media_mute` | action | New | – | Mute or unmute the audio without changing the volume. |
| `set_media_source` | action | New | – | Switch the audio source. |
| `set_media_playback` | action | New | – | Play or pause the current audio source. |
| `skip_media_track` | action | New | – | Skip to the next or previous track on the current source and keep playing. |
| `tune_fm_radio` | action | New | – | Tune the FM radio to a frequency and switch the audio source to FM radio. |
| `play_media_by_query` | action | New | – | Search the streaming service for a song, artist, album, playlist, or podcast and start playing the best match. |
| `get_media_status` | retrieve | New | – | Return the audio source, whether it is playing, the volume, mute state, and the tuned FM frequency. |

### Communication (6)

| Tool | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|
| `get_contact_id_by_name` | retrieve | CAR-bench | `get_contact_id_by_contact_name` | Find contacts in the connected phone's address book by name and return their contact IDs. |
| `get_contact_details` | retrieve | CAR-bench | `get_contact_information` | Return the phone numbers and email addresses of contacts. |
| `call_phone_number` | action | CAR-bench | `call_phone_by_number` | Place a hands-free call through the connected phone. |
| `send_text_message` | action | New | – | Send a short SMS through the connected phone. |
| `send_email` | action | CAR-bench | `send_email` | Send a short email from the driver's connected account. |
| `get_calendar_events` | retrieve | CAR-bench | `get_entries_from_calendar` | Return today's calendar events with start time, duration, topic, location, and attendees. |

### Utility (2)

| Tool | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|
| `calculate_math` | retrieve | CAR-bench | `calculate_math` | Evaluate an arithmetic expression, for example to add up distances or costs. |
| `calculate_datetime` | retrieve | CAR-bench | `calculate_datetime` | Add or subtract hours and minutes to a time, for example to work out an arrival time. |

### Weather (1)

| Tool | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|
| `get_weather` | retrieve | CAR-bench | `get_weather` | Return the weather condition, temperature, humidity, and wind for a location at a time today. |

### Preferences (1)

| Tool | Kind | Origin | CAR-bench source | What it does |
|---|---|---|---|---|
| `get_user_preferences` | retrieve | CAR-bench, extended | `get_user_preferences` | Return the driver's saved preferences for one category, such as preferred charging or fuel brands, route choices, or climate habits. Adds seats, media, and energy categories. |

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
