# 混动车 Assistant Tools 统计

共 **100 个** tools：**88 个正向**，**12 个负向**。规格文件见同目录下的 `2026-10-11_hybrid_*.json`。

## 正向 tools 按领域

| 领域 | action | retrieve | 合计 |
|---|---|---|---|
| Vehicle（车身、灯光、空调、座椅、车况） | 32 | 11 | 43 |
| Navigation（导航） | 9 | 6 | 15 |
| Energy（混动、充电） | 5 | 7 | 12 |
| Media（影音） | 7 | 1 | 8 |
| Communication（电话、短信、邮件、日历） | 3 | 3 | 6 |
| Utility（数学、时间计算） | – | 2 | 2 |
| Weather（天气） | – | 1 | 1 |
| Preferences（用户偏好） | – | 1 | 1 |
| **合计** | **56** | **32** | **88** |

CAR-bench 原有 57 个 tools，这里没有收录 `think` 和 `planning_tool`。

## 负向 tools

12 个负向 tools 是家居类、手机类和其他非车内请求，模型应识别出它们不适用于车内并拒绝或改用正确的 tool：

- `set_home_thermostat`（SmartHome）：Set the target temperature of the home thermostat.
- `set_home_lights`（SmartHome）：Turn lights in a room of the home on or off and set their color.
- `lock_home_door`（SmartHome）：Lock or unlock the smart lock on the home's front door.
- `play_on_home_speaker`（SmartHome）：Play music on a smart speaker at home.
- `start_home_wallbox_charging`（SmartHome）：Start charging on the home wallbox app account.
- `set_phone_alarm`（Phone）：Set an alarm on the user's phone.
- `set_phone_ringer_volume`（Phone）：Change the phone's own ringer volume.
- `book_flight`（Travel）：Search and book a flight ticket.
- `order_food_delivery`（Shopping）：Order food for delivery to a home address.
- `transfer_money`（Finance）：Transfer money from the user's bank account to another account.
- `create_document`（Productivity）：Create a new text document in the user's cloud drive.
- `post_to_social_media`（Social）：Publish a post on the user's social media account.

## 各领域 tool 列表

### Vehicle（43）

- `set_window_position` · action：Open or close one window, or all four, to a position from 0 (closed) to 100 (fully open).
- `set_sunshade_position` · action：Open or close the sunroof sunshade to a position from 0 (closed) to 100 (fully open).
- `set_sunroof_position` · action：Open or close the sunroof to a position from 0 (closed) to 100 (fully open).
- `get_window_and_roof_status` · retrieve：Return the position of all four windows, the sunroof, and the sunshade.
- `set_door_locks` · action：Lock or unlock all doors.
- `set_child_lock` · action：Engage or release the child safety lock on a rear door, so it cannot be opened from inside.
- `set_trunk` · action：Open or close the power trunk lid.
- `set_fuel_door` · action：Open or close the fuel filler door for refueling.
- `set_charge_port` · action：Open or close the charging port door for plug-in charging.
- `get_access_status` · retrieve：Return whether the doors are locked, the rear child locks, and whether the trunk, fuel door, and charge port door are open.
- `set_low_beams` · action：Turn the low beam headlights on or off.
- `set_high_beams` · action：Turn the high beam headlights on or off.
- `set_fog_lights` · action：Turn the front fog lights on or off.
- `set_wiper_speed` · action：Set the front windshield wiper speed.
- `set_rear_wiper` · action：Turn the rear window wiper on or off.
- `set_side_mirrors_folded` · action：Fold or unfold both side mirrors.
- `set_mirror_heating` · action：Turn side mirror heating on or off, to clear ice, frost, or fog from the mirrors.
- `get_visibility_status` · retrieve：Return the state of the low beams, high beams, fog lights, front and rear wipers, side mirror folding, and mirror heating.
- `set_reading_light` · action：Turn the reading light at one seat, or at all seats, on or off.
- `set_ambient_light` · action：Set the ambient interior lighting color and brightness, or turn it off with color "off".
- `get_interior_lights_status` · retrieve：Return which reading lights are on and the ambient light color and brightness.
- `set_climate_temperature` · action：Set the target temperature of one climate zone or all zones.
- `set_fan_speed` · action：Set the climate fan speed.
- `set_airflow_direction` · action：Set where the climate fan blows air.
- `set_air_conditioning` · action：Turn the air conditioning compressor on or off.
- `set_air_circulation` · action：Set the air intake mode: automatic, fresh outside air, or recirculated cabin air.
- `set_defrost` · action：Turn the front windshield defrost, the rear window defrost, or both on or off.
- `set_climate_auto_mode` · action：Turn climate auto mode on or off.
- `get_climate_status` · retrieve：Return the climate settings (auto mode, zone temperatures, fan speed, airflow direction, air conditioning, air circulation, defrost) plus the measured cabin and outside temperatures.
- `set_seat_heating` · action：Set the seat heating level for one seat or all seats.
- `set_seat_ventilation` · action：Set the seat ventilation (cooling) level for a front seat.
- `set_seat_massage` · action：Start, change, or stop the massage program of a front seat.
- `set_seat_fore_aft` · action：Move a front seat forward or back.
- `set_seat_backrest` · action：Change the backrest angle of a front seat.
- `recall_driver_memory_profile` · action：Move the driver seat to a saved memory profile.
- `set_steering_wheel_heating` · action：Set the steering wheel heating level.
- `get_seat_status` · retrieve：Return seat occupancy, seat heating, ventilation, massage, front seat positions, the last recalled driver memory profile, and steering wheel heating.
- `get_driving_status` · retrieve：Return the current speed, selected gear, and odometer.
- `get_tire_pressure` · retrieve：Return the pressure of all four tires in kPa and flag any tire below 200 kPa as low.
- `get_maintenance_status` · retrieve：Return engine oil life, washer fluid level, and the distance until the next scheduled service.
- `get_trip_info` · retrieve：Return the trip computer: distance since last reset, average fuel and electric consumption, and the share driven electrically.
- `reset_trip_computer` · action：Reset the trip computer to zero.
- `get_vehicle_specs` · retrieve：Return fixed facts about the car: exterior color, fuel tank capacity, usable battery capacity, reference consumption figures, and maximum AC and DC charging power.

### Navigation（15）

- `get_location_id_by_name` · retrieve：Look up the location ID of a city, address, or named place.
- `search_poi_at_location` · retrieve：Find points of interest of one category near a location.
- `search_poi_along_route` · retrieve：Find points of interest of one category along a route, with the km along the route and the detour time.
- `get_routes` · retrieve：Return up to three route options between two locations with route IDs, distance, duration, toll roads, and road types.
- `convert_route_distance_and_time` · retrieve：On a given route, convert a distance in km into driving time, or a driving time in minutes into distance.
- `set_navigation` · action：Start guidance from the current location to a destination, with up to three intermediate stops in order.
- `add_navigation_waypoint` · action：Insert an intermediate stop into the active route.
- `replace_navigation_waypoint` · action：Replace one intermediate stop of the active route with another location.
- `delete_navigation_waypoint` · action：Remove one intermediate stop from the active route.
- `replace_navigation_destination` · action：Replace the final destination of the active route and keep the intermediate stops.
- `delete_navigation_destination` · action：Remove the final destination so the last intermediate stop becomes the destination.
- `cancel_navigation` · action：Stop guidance and clear the destination and all stops.
- `set_route_options` · action：Set whether route planning avoids toll roads and highways.
- `set_voice_guidance` · action：Turn spoken turn-by-turn navigation guidance on or off.
- `get_navigation_status` · retrieve：Return whether guidance is active, the destination, intermediate stops, current route ID, route options, and voice guidance state.

### Energy（12）

- `get_energy_status` · retrieve：Return the battery level, fuel level, estimated electric range, fuel range, and combined range in km, plus the current hybrid mode, drive mode, regen level, charge target, and whether the engine is running.
- `set_hybrid_mode` · action：Choose how the hybrid system uses the battery and the engine.
- `set_drive_mode` · action：Set the driving dynamics mode, which changes throttle response and efficiency.
- `set_regen_level` · action：Set the regenerative braking strength.
- `get_charging_settings` · retrieve：Return the plug-in charging settings: whether a cable is connected, the charge limit, and the delayed charging schedule.
- `set_charge_limit` · action：Set the battery level at which plug-in charging stops.
- `set_scheduled_charging` · action：Turn delayed plug-in charging on or off and set the hour it starts, for example to use cheaper night-time electricity.
- `estimate_charging_time` · retrieve：Estimate how many minutes plug-in charging takes from a start battery level to a target level at a given charger.
- `estimate_soc_after_charging` · retrieve：Estimate the battery level after charging for a given number of minutes at a given charger.
- `estimate_electric_distance` · retrieve：Estimate how many km the car can drive on electric power alone between two battery levels.
- `estimate_refuel` · retrieve：Estimate how many liters are needed to fill the tank to a target level, and the added fuel range in km.
- `estimate_route_energy` · retrieve：Estimate how much of a route can be driven electrically, how much fuel the rest needs, and whether the car reaches the end without charging or refueling.

### Media（8）

- `set_media_volume` · action：Set the audio volume.
- `set_media_mute` · action：Mute or unmute the audio without changing the volume.
- `set_media_source` · action：Switch the audio source.
- `set_media_playback` · action：Play or pause the current audio source.
- `skip_media_track` · action：Skip to the next or previous track on the current source and keep playing.
- `tune_fm_radio` · action：Tune the FM radio to a frequency and switch the audio source to FM radio.
- `play_media_by_query` · action：Search the streaming service for a song, artist, album, playlist, or podcast and start playing the best match.
- `get_media_status` · retrieve：Return the audio source, whether it is playing, the volume, mute state, and the tuned FM frequency.

### Communication（6）

- `get_contact_id_by_name` · retrieve：Find contacts in the connected phone's address book by name and return their contact IDs.
- `get_contact_details` · retrieve：Return the phone numbers and email addresses of contacts.
- `call_phone_number` · action：Place a hands-free call through the connected phone.
- `send_text_message` · action：Send a short SMS through the connected phone.
- `send_email` · action：Send a short email from the driver's connected account.
- `get_calendar_events` · retrieve：Return today's calendar events with start time, duration, topic, location, and attendees.

### Utility（2）

- `calculate_math` · retrieve：Evaluate an arithmetic expression, for example to add up distances or costs.
- `calculate_datetime` · retrieve：Add or subtract hours and minutes to a time, for example to work out an arrival time.

### Weather（1）

- `get_weather` · retrieve：Return the weather condition, temperature, humidity, and wind for a location at a time today.

### Preferences（1）

- `get_user_preferences` · retrieve：Return the driver's saved preferences for one category, such as preferred charging or fuel brands, route choices, or climate habits.
