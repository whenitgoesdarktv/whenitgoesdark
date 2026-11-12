"""Master timeline for the hotel video: narration placement with dramatic pauses, chapters, shots, overlays, SFX cues.

All story beats are keyed to narration line indices (lines.json from align.py). build() returns a dict with
absolute times on the final video timeline.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

# extra silence inserted AFTER line i (seconds)
PAUSE_AFTER = {10: 0.6, 17: 2.6, 38: 2.0, 40: 0.5, 43: 1.6, 47: 1.0, 59: 0.8, 64: 2.0, 90: 2.0, 113: 0.6,
               124: 2.2, 135: 0.6, 154: 2.0, 158: 3.2, 161: 2.0, 163: 1.0, 192: 2.0, 209: 2.0,
               222: 0.8, 224: 0.6}
END_CARD = 7.0
# lines re-voiced after review: line -> (wav file, new text)
VOICE_FIX = {8: ('fix_line08.wav', 'Past room twenty-four.'), 18: ('fix_line18.wav', 'Nine hours earlier.')}
LEAD_IN = 0.35  # tiny breath before the first word

CHAPTERS = [  # (first line, number, title)
    (18, 1, 'THE LAST ROOM'), (39, 2, 'LIGHTS OUT'), (65, 3, 'THE COLD'), (91, 4, 'SOMETHING IN THE WALLS'),
    (125, 5, 'THE HUM'), (155, 6, 'INSIDE OR OUT'), (162, 7, 'FRESH AIR'), (193, 8, 'THE TAILPIPE'), (210, 9, 'MORNING')]

# Status bar state from a line onward: time, power, phone, temp
STATUS = [(0, '2:47 AM', 'OFF', '12%', '49°F'), (18, '6:00 PM', 'ON', '80%', '68°F'), (35, '7:00 PM', 'ON', '77%', '68°F'),
          (39, '8:12 PM', 'ON', '64%', '68°F'), (43, '8:12 PM', 'OFF', '64%', '66°F'), (65, '10:00 PM', 'OFF', '41%', '58°F'),
          (66, '12:00 AM', 'OFF', '33%', '51°F'), (73, '12:40 AM', 'OFF', '31%', '51°F'), (91, '2:47 AM', 'OFF', '12%', '49°F'),
          (136, '2:55 AM', 'OFF', '11%', '49°F'), (162, '3:10 AM', 'OFF', '9%', '49°F'), (164, '3:10 AM', 'OFF', '9%', '9°F'), (193, '3:40 AM', 'OFF', '6%', '9°F'), (210, '5:50 AM', 'OFF', '3%', '12°F')]
NO_STATUS = [(17, 18), (155, 162), (225, 999)]  # line ranges without the status bar (title, choice, ending)

RULES = [  # (first line, last line, label, title, lines)
    (60, 61, 'RULE 1', 'FLASHLIGHTS, NOT CANDLES', ['Candles start fires.', 'Fire trucks may not reach you.']),
    (67, 70, 'RULE 2', 'KEEP THE HEAT IN', ['Loose, warm layers', 'Towels under the door', 'Close off unused rooms']),
    (125, 133, 'RULE 3', 'THE INVISIBLE KILLER', ['No color. No smell.', 'Headache, dizziness, confusion', 'Sleepers may never wake']),
    (151, 154, 'RULE 4', 'GENERATORS GO OUTSIDE', ['Never indoors, even with doors open', '20+ feet from doors, windows, vents']),
    (160, 161, 'RULE 5', 'FRESH AIR FIRST', ['Get outside right away', 'Then call 911']),
    (185, 190, 'RULE 6', 'HYPOTHERMIA SIGNS', ['Shivering, exhaustion, confusion', 'Fumbling hands, slurred speech']),
    (204, 206, 'RULE 7', 'CLEAR THE EXHAUST', ['Dig out the tailpipe first', 'Engine 10 min an hour, window cracked']),
]

# Shots: (first line, bg, camera, characters, fx)
#   camera: (zoom0, zoom1, cx0, cy0, cx1, cy1) in fractions of the bg; zoom 1 = full frame
#   characters: list of (file, x_frac, y_bottom_frac, height_frac, flip)
#   fx: set of effect names
SHOTS = [
    (0,  'OPEN', (1.0, 1.15, .62, .5, .7, .5), [], {'dust'}),
    (4,  'bg07_room22', (2.4, 2.7, .14, .2, .16, .2), [], {'dark', 'blackout_grade', 'shake_soft', 'scratch'}),
    (5,  'bg01_hallway_dark', (1.0, 1.45, .5, .5, .5, .42), [], {'dark', 'beam', 'dust', 'scratch'}),
    (9,  'bg01_hallway_dark', (1.35, 1.6, .5, .55, .5, .55), [('hero_walk_headlamp', .5, .86, .45, False)], {'dark', 'beam_char'}),
    (11, 'bg03_front_desk', (1.3, 1.45, .62, .45, .62, .45), [], {'dark', 'blackout_grade', 'lights_off'}),
    (12, 'bg06_balcony_view', (1.05, 1.3, .45, .45, .4, .4), [], {'dark', 'blackout_grade', 'rumble', 'heat_haze'}),
    (15, 'bg07_room22', (2.5, 2.8, .14, .2, .15, .2), [], {'dark', 'blackout_grade', 'scratch'}),
    (16, 'bg09_stairs_down', (1.05, 1.35, .6, .6, .62, .68), [], {'dark', 'heat_haze', 'rumble'}),
    (17, 'bg02_lodge_exterior_dusk', (1.0, 1.25, .58, .4, .6, .38), [], {'snow', 'blackout_grade', 'night', 'windows_off'}),
    (18, 'bg02_lodge_exterior_dusk', (1.0, 1.15, .55, .45, .58, .42), [], {'snow'}),
    (21, 'bg02_lodge_exterior_dusk', (2.6, 3.0, .6, .5, .6, .49), [], {'snow', 'sign_nopets'}),
    (22, 'bg03_front_desk', (1.15, 1.25, .5, .6, .5, .6), [('lando_bag_asleep', .30, 1.12, .36, False)], {'warm'}),
    (24, 'bg03_front_desk', (1.5, 1.6, .38, .65, .38, .65), [('lando_bag', .38, .93, .3, False)], {'warm'}),
    (26, 'bg04_parking_lot_snow', (1.0, 1.2, .5, .5, .4, .5), [], {'snow_heavy'}),
    (28, 'bg03_front_desk', (1.7, 1.85, .62, .37, .62, .36), [('dale_desk_key@.595', .62, .418, .2, False)], {'warm', 'key_tag'}),
    (31, 'bg03_front_desk', (2.2, 2.4, .42, .74, .42, .74), [('lando_bag>.45', .42, .93, .3, False)], {'warm', 'shake_soft'}),
    (33, 'bg03_front_desk', (2.1, 2.3, .62, .34, .62, .33), [('dale_desk_key@.595', .62, .418, .2, False)], {'warm'}),
    (35, 'bg04_parking_lot_snow', (1.4, 1.7, .33, .55, .33, .55), [], {'snow_heavy'}),
    (38, 'bg02_lodge_exterior_dusk', (1.1, 1.3, .6, .42, .6, .4), [], {'snow', 'night', 'flicker_out'}),
    (44, 'bg07_room22', (1.0, 1.12, .5, .5, .5, .5), [], {'dark', 'blackout_grade', 'phone64'}),
    (48, 'bg06_balcony_view', (1.15, 1.35, .45, .45, .45, .42), [], {'dark', 'rumble'}),
    (50, 'bg05_lobby_fire', (1.8, 1.9, .73, .55, .71, .55), [('dale_generator', .60, .8, .44, True)], {'dark', 'firelight', 'door_snow'}),
    (52, 'bg05_lobby_fire', (1.1, 1.2, .38, .5, .36, .5), [], {'dark', 'firelight'}),
    (53, 'bg05_lobby_fire', (2.0, 2.4, .78, .44, .78, .42), [], {'dark', 'door_snow2', 'firelight'}),
    (56, 'bg05_lobby_fire', (2.0, 2.8, .78, .42, .78, .4), [], {'dark', 'door_snow2', 'ominous'}),
    (57, 'bg03_front_desk', (1.55, 1.7, .65, .45, .65, .45), [('guest_redhat_back', .87, .78, .44, False)], {'dark', 'blackout_grade', 'lights_off', 'candles'}),
    (59, 'bg03_front_desk', (2.4, 2.6, .58, .40, .62, .40), [], {'dark', 'blackout_grade', 'lights_off', 'candles'}),
    (61, 'bg04_parking_lot_snow', (1.2, 1.4, .5, .5, .45, .5), [], {'snow_heavy', 'windows_off'}),
    (62, 'bg03_front_desk', (1.7, 1.8, .78, .45, .78, .45), [('guest_redhat_back', .87, .78, .44, False)], {'dark', 'blackout_grade', 'lights_off', 'candles', 'beam'}),
    (63, 'bg03_front_desk', (1.5, 1.6, .5, .55, .5, .55), [('lando_bag', .4, .9, .26, True)], {'dark', 'blackout_grade', 'lights_off', 'smoke', 'candles_out'}),
    (65, 'bg07_room22', (1.0, 1.15, .45, .5, .45, .5), [], {'dark', 'blackout_grade', 'cold', 'temp_readout'}),
    (67, 'bg07_bedclose', (1.0, 1.1, .5, .5, .5, .55), [], {'dark', 'blackout_grade', 'cold'}),
    (69, 'bg07_room22', (2.2, 2.5, .62, .32, .62, .32), [], {'dark', 'blackout_grade', 'cold'}),
    (70, 'bg01_hallway_dark', (1.0, 1.2, .5, .5, .5, .48), [], {'dark', 'beam'}),
    (71, 'bg07_room22', (1.8, 2.0, .22, .5, .22, .5), [('lando_sleep_curled', .2, .52, .16, False)], {'dark', 'blackout_grade', 'cold'}),
    (72, 'bg07_bedclose', (1.0, 1.08, .5, .5, .5, .52), [('lando_on_face', .5, 1.2, 1.12, False)], {'dark', 'blackout_grade', 'cold', 'char_dim'}),
    (74, 'bg07_room22', (1.0, 1.08, .5, .5, .5, .5), [], {'dark', 'blackout_grade', 'knock'}),
    (75, 'bg01_hallway_dark', (1.3, 1.4, .5, .55, .5, .55), [('rosa_door<.5', .44, .88, .55, False)], {'dark', 'beam_char', 'jamb'}),
    (79, 'bg05_lobby_fire', (1.0, 1.12, .45, .5, .45, .5), [('guests_asleep_couch', .60, .72, .24, False)], {'dark', 'firelight', 'door_snow'}),
    (83, 'bg09_stairs_down', (1.0, 1.2, .62, .55, .7, .55), [], {'dark', 'headache'}),
    (86, 'bg05_lobby_fire', (1.6, 1.8, .3, .55, .3, .55), [('rosa_sleep_couch', .36, .9, .32, False)], {'dark', 'firelight', 'heat_haze'}),
    (87, 'bg05_lobby_fire', (1.4, 1.5, .62, .55, .66, .5), [('lando_yowl', .6, .98, .4, False)], {'dark', 'firelight', 'door_snow'}),
    (89, 'bg09_stairs_down', (1.1, 1.25, .62, .55, .62, .55), [], {'dark'}),
    (91, 'bg07_room22', (1.0, 1.2, .45, .5, .45, .5), [], {'dark', 'blackout_grade', 'dizzy'}),
    (93, 'bg07_room22', (2.6, 3.0, .82, .5, .83, .5), [], {'dark', 'blackout_grade', 'dizzy'}),
    (95, 'bg07_room22', (2.4, 2.8, .14, .2, .15, .2), [], {'dark', 'blackout_grade', 'scratch', 'shake_soft'}),
    (98, 'bg07_room22', (1.5, 1.6, .40, .5, .40, .5), [('hero_ear_wall', .37, .62, .42, True)], {'dark', 'blackout_grade', 'beam_char'}),
    (99, 'bg07_room22', (2.6, 3.0, .14, .22, .2, .22), [], {'dark', 'blackout_grade', 'scratch', 'shake_soft'}),
    (103, 'bg01_hallway_dark', (1.1, 1.6, .5, .5, .5, .42), [], {'dark', 'beam', 'scratch'}),
    (107, 'bg08_vent_grate', (1.0, 1.3, .55, .45, .55, .45), [], {'dark', 'heat_haze'}),
    (111, 'bg08_vent_grate', (1.4, 1.7, .55, .45, .55, .45), [], {'dark', 'heat_haze', 'beam'}),
    (112, 'bg08_vent_grate', (1.4, 1.8, .55, .45, .55, .45), [], {'dark', 'eyes', 'heat_haze'}),
    (116, 'bg01_hallway_dark', (1.3, 1.45, .5, .55, .5, .55), [('hero_dizzy', .5, 1.0, .75, False)], {'dark', 'beam_char', 'dizzy'}),
    (120, 'bg01_hallway_dark', (1.6, 2.0, .5, .38, .5, .36), [], {'dark', 'beam', 'figure', 'dizzy'}),
    (123, 'BLACK', None, [], {'heartbeat'}),
    (124, 'bg05_lobby_fire', (3.0, 3.6, .37, .43, .37, .43), [], {'dark', 'heat_haze', 'red_glow'}),
    (126, 'bg01_hallway_dark', (1.5, 1.6, .5, .55, .5, .55), [('hero_dizzy', .5, 1.0, .75, False)], {'dark', 'beam_char', 'dizzy'}),
    (128, 'bg05_lobby_fire', (1.7, 1.8, .55, .55, .55, .55), [('rosa_blanket', .55, .98, .7, False)], {'dark', 'firelight', 'heat_haze'}),
    (130, 'bg05_lobby_fire', (2.0, 2.2, .60, .62, .60, .62), [('guests_asleep_couch', .60, .72, .24, False)], {'dark', 'heat_haze', 'firelight'}),
    (131, 'bg07_room22', (1.6, 1.8, .45, .5, .45, .5), [], {'dark', 'blackout_grade', 'dizzy'}),
    (133, 'bg05_lobby_fire', (1.6, 1.9, .55, .58, .58, .6), [('guests_asleep_couch', .60, .72, .24, False)], {'dark', 'heat_haze_strong', 'red_glow'}),
    (134, 'bg05_lobby_fire', (1.25, 1.4, .5, .55, .5, .55), [('rosa_sleep_couch', .22, .80, .26, False), ('guests_asleep_couch', .60, .72, .24, False)], {'dark', 'heat_haze', 'firelight'}),
    (135, 'STAT', None, [], set()),
    (136, 'bg09_stairs_down', (1.0, 1.2, .6, .5, .6, .55), [('hero_carry_lando', .56, .92, .62, False)], {'dark', 'dizzy_soft'}),
    (137, 'bg09_stairs_down', (1.2, 1.3, .55, .55, .55, .58), [('hero_carry_lando', .5, 1.0, .72, False)], {'dark', 'dizzy', 'headache'}),
    (138, 'bg05_lobby_fire', (1.15, 1.35, .4, .5, .38, .5), [('guests_asleep_couch', .62, .70, .24, False)], {'dark', 'heat_haze_strong', 'coals'}),
    (142, 'bg05_lobby_fire', (1.7, 1.85, .28, .6, .28, .6), [('rosa_sleep_couch', .30, .92, .32, False)], {'dark', 'heat_haze_strong', 'coals'}),
    (143, 'bg05_lobby_fire', (1.9, 2.0, .28, .6, .28, .6), [('rosa_sleep_couch', .30, .92, .32, False)], {'dark', 'heat_haze_strong', 'coals', 'shake'}),
    (144, 'bg05_lobby_fire', (2.0, 2.1, .5, .5, .5, .5), [('rosa_confused@.45', .5, .64, .5, False)], {'dark', 'heat_haze_strong', 'coals', 'dizzy_soft'}),
    (145, 'bg03_front_desk', (1.8, 1.95, .62, .36, .62, .35), [('dale_slumped@.46', .62, .42, .15, False)], {'dark', 'blackout_grade', 'lights_off', 'heat_haze'}),
    (147, 'bg10_ceiling_alarm', (1.0, 1.4, .58, .32, .58, .3), [], {'dark', 'no_battery'}),
    (151, 'bg11_porch_blizzard', (1.0, 1.15, .5, .5, .5, .5), [], {'snow_heavy', 'door_dim', 'diagram_20ft'}),
    (155, 'SPLIT', None, [], set()),
    (158, 'CHOICE', None, [], set()),
    (159, 'bg11_porch_blizzard', (1.0, 1.2, .5, .5, .55, .5), [], {'snow_heavy', 'door_dim', 'whoosh'}),
    (162, 'bg05_lobby_fire', (2.6, 2.7, .37, .43, .37, .43), [], {'dark', 'coals', 'gen_off'}),
    (164, 'bg11_porch_blizzard', (1.1, 1.25, .45, .55, .45, .55), [('rosa_confused', .43, .95, .6, False), ('hero_walk_headlamp', .50, .96, .62, True)], {'snow_heavy', 'door_dim'}),
    (165, 'bg11_porch_blizzard', (1.05, 1.15, .5, .55, .5, .55), [('guests_porch_group', .5, .86, .45, False)], {'snow_heavy', 'door_dim'}),
    (167, 'bg03_front_desk', (1.8, 1.95, .62, .36, .62, .35), [('dale_slumped@.46', .62, .42, .15, False)], {'dark', 'blackout_grade', 'lights_off'}),
    (168, 'bg05_lobby_fire', (1.15, 1.3, .62, .55, .72, .52), [('hero_drag_dale', .62, .97, .55, True)], {'dark', 'coals', 'door_snow'}),
    (170, 'bg11_porch_blizzard', (1.1, 1.2, .5, .55, .5, .55), [('hero_drag_dale', .48, .95, .55, False)], {'snow_heavy', 'door_dim'}),
    (172, 'bg11_porch_blizzard', (1.2, 1.3, .45, .6, .45, .6), [('lando_parade', .40, .92, .3, True)], {'snow_heavy', 'door_dim'}),
    (173, 'bg11_porch_blizzard', (1.25, 1.35, .45, .55, .45, .55), [], {'snow_heavy', 'door_dim', 'phone_call'}),
    (181, 'bg11_porch_blizzard', (1.0, 1.15, .5, .5, .5, .5), [('guests_porch_group', .42, .90, .42, False), ('rosa_confused', .66, .95, .40, False), ('lando_parade', .25, .97, .14, False)], {'snow_heavy', 'temp_9', 'door_dim'}),
    (191, 'bg11_porch_blizzard', (1.5, 1.6, .45, .6, .45, .6), [('rosa_confused', .58, .97, .5, False)], {'snow_heavy', 'door_dim', 'cold'}),
    (193, 'bg04_parking_lot_snow', (1.3, 1.5, .33, .55, .33, .55), [], {'snow_heavy', 'windows_off'}),
    (194, 'bg04_parking_lot_snow', (1.6, 1.7, .36, .6, .36, .6), [('hero_dig_snow_night@.86', .40, .70, .24, False)], {'snow_heavy', 'windows_off'}),
    (195, 'bg13_car_interior', (1.0, 1.15, .5, .45, .5, .45), [], {'dash_glow'}),
    (199, 'bg12_car_tailpipe', (1.6, 1.7, .34, .42, .34, .42), [('lando_yowl@.55', .30, .45, .10, False)], {'snow', 'windows_off', 'char_dim'}),
    (202, 'bg12_car_tailpipe', (1.0, 1.5, .4, .6, .28, .72), [], {'snow_heavy', 'ominous'}),
    (207, 'bg12_car_tailpipe', (1.3, 1.4, .45, .65, .45, .65), [('hero_dig_snow_night', .36, .95, .34, False), ('lando_parade', .62, .95, .26, True)], {'snow', 'windows_off'}),
    (210, 'bg14_mountain_dawn', (1.0, 1.25, .5, .5, .5, .55), [], {'snow_light', 'dawn', 'siren_lights'}),
    (214, 'bg14_mountain_dawn', (1.3, 1.45, .62, .65, .62, .65), [('dale_oxygen', .58, 1.04, .45, False)], {'snow_light', 'dawn', 'siren_lights'}),
    (219, 'bg14_mountain_dawn', (1.4, 1.5, .62, .7, .62, .7), [('lando_parade', .6, .97, .32, False)], {'snow_light', 'dawn', 'warm'}),
    (223, 'bg15_ambulance_interior', (1.1, 1.22, .55, .55, .57, .55), [('rosa_lando_bench@.70', .72, .66, .40, False)], {'dawn_grade', 'siren_soft'}),
    (225, 'bg02_lodge_exterior_dusk', (1.0, 1.1, .58, .42, .6, .4), [], {'snow', 'night', 'windows_off'}),
    (228, 'bg05_lobby_fire', (2.6, 3.0, .37, .43, .37, .43), [], {'dark', 'heat_haze', 'red_glow'}),
    (229, 'SPLIT', None, [], set()),
    (231, 'bg02_lodge_exterior_dusk', (1.0, 1.12, .58, .45, .6, .42), [], {'snow', 'night', 'windows_off'}),
    (233, 'END', None, [], set()),
]

# SFX cues: (line, offset seconds from line start, file, gain dB)
SFX = [  # (line, offset s, file, gain dB[, max length s])
    (0, 0.0, 'sfx_scratching_wall', -10, 6.0), (4, 0.0, 'sfx_scratching_wall', -6, 3.0), (6, 0.0, 'sfx_scratching_wall', -9, 4.4),
    (9, 0.2, 'sfx_heartbeat', -10, 3.4), (12, 0.0, 'sfx_whoosh_hit', -21),
    (17, 4.2, 'sfx_whoosh_hit', -11), (23, 0.8, 'sfx_cat_purr', -20, 1.4), (28, 1.0, 'sfx_key_slide', -8),
    (32, 0.1, 'sfx_meow_bag', -8), (41, 0.0, 'sfx_lights_flicker', -8, 0.6), (42, 0.0, 'sfx_lights_flicker', -8, 0.6),
    (43, 0.0, 'sfx_whoosh_hit', -15), (48, 1.2, 'sfx_generator_start', -6), (57, 0.4, 'sfx_candle_light', -10),
    (63, 0.3, 'sfx_blow_out', -9), (74, 0.0, 'sfx_knock_door', -6), (88, -0.35, 'sfx_cat_yowl', -15, 1.3),
    (95, 0.0, 'sfx_scratching_wall', -5, 3.0), (99, 0.0, 'sfx_scratching_wall', -6, 3.2), (103, 0.0, 'sfx_footsteps_carpet', -14),
    (106, 0.0, 'sfx_scratching_wall', -8, 5.2), (112, 0.6, 'sfx_meow_bag', -14, 1.2),
    (123, 0.0, 'sfx_heartbeat', -11, 6.5), (124, 1.8, 'sfx_whoosh_hit', -10), (156, 0.0, 'sfx_heartbeat', -12, 6.0),
    (159, 0.0, 'sfx_whoosh_hit', -11), (162, 1.1, 'sfx_generator_off', -6), (165, 0.0, 'sfx_footsteps_snow', -12),
    (176, 0.0, 'sfx_phone_ring', -12, 1.05), (177, 0.0, 'sfx_phone_ring', -12, 1.05), (178, 0.0, 'sfx_knock_door', -24, 0.09),
    (194, 0.0, 'sfx_digging_snow', -10, 2.5), (196, 0.0, 'sfx_car_start', -8), (199, 0.0, 'sfx_cat_yowl', -22),
    (207, 0.0, 'sfx_digging_snow', -10, 2.5), (210, 0.0, 'sfx_plow', -10), (213, 0.0, 'sfx_siren_distant', -14, 6.0),
    (222, 1.0, 'sfx_cat_purr', -16, 3.0),
]

# Ambience beds by line range: (first line, last line, file, gain dB)
BEDS = [
    (0, 17, 'amb_lodge_inside', -26), (17, 22, 'amb_blizzard_outside', -24), (22, 26, 'amb_lodge_inside', -28),
    (26, 28, 'amb_blizzard_outside', -24), (28, 35, 'amb_lodge_inside', -28), (35, 44, 'amb_blizzard_outside', -24),
    (44, 151, 'amb_lodge_inside', -25), (151, 155, 'amb_blizzard_outside', -22), (155, 159, 'amb_lodge_inside', -26),
    (159, 162, 'amb_blizzard_outside', -20), (162, 164, 'amb_lodge_inside', -37), (164, 195, 'amb_blizzard_outside', -21),
    (195, 202, 'amb_lodge_inside', -30), (202, 210, 'amb_blizzard_outside', -21), (210, 233, 'amb_blizzard_outside', -27),
]
# Generator hum: audible from line 46 to 162 (loud in the lobby, faint through the floor elsewhere)
HUM = (48, 162)
HUM_START_OFF = 1.5   # the motor catches a beat after the line starts
GEN_OFF_AT = 1.1      # hum stops this long after line 162 starts (the 'off' in the line)
CAR_IDLE = (196, 210, 1.6, -24)   # engine idle under the car scenes: lines, start offset, gain
HUM_COLD_OPEN = (12, 17)


def build():
    lines = json.load(open(os.path.join(HERE, 'lines.json')))
    words = json.load(open(os.path.join(HERE, 'words.json')))
    pause = dict(PAUSE_AFTER)
    fixw = {}
    for i, (fn, txt) in VOICE_FIX.items():
        import wave as _wave
        with _wave.open(os.path.join(HERE, fn)) as wf:
            dur = wf.getnframes() / wf.getframerate()
        old_end = lines[i]['end']
        lines[i] = dict(lines[i], text=txt, end=lines[i]['start'] + dur, orig_end=old_end)
        pause[i] = pause.get(i, 0.0) + max(0.0, lines[i]['end'] - old_end)   # longer take pushes the rest later
        ws = txt.split(); wt = [max(1, sum(ch in 'aeiouy' for ch in w.lower())) for w in ws]; acc_w = 0.0
        fixw[i] = []
        for w, k in zip(ws, wt):
            a = lines[i]['start'] + dur * acc_w / sum(wt); acc_w += k
            fixw[i].append({'text': w, 'start': a, 'end': lines[i]['start'] + dur * acc_w / sum(wt)})
    shift = [0.0] * len(lines)
    acc = LEAD_IN
    for i in range(len(lines)):
        shift[i] = acc
        acc += pause.get(i, 0.0)
    L = []
    for i, l in enumerate(lines):
        L.append({'i': i, 'text': l['text'], 'start': l['start'] + shift[i], 'end': l['end'] + shift[i],
                  'src_start': l['start'], 'src_end': l['end']})
    # words: assign each word to its line by time
    W = []
    li = 0
    for w in words:
        while li + 1 < len(lines) and w['start'] >= lines[li + 1]['start'] - 0.02:
            li += 1
        if li in fixw:
            continue
        W.append({'text': w['text'], 'start': w['start'] + shift[li], 'end': w['end'] + shift[li], 'line': li})
    for i, ws in fixw.items():
        W += [{'text': x['text'], 'start': x['start'] + shift[i], 'end': x['end'] + shift[i], 'line': i} for x in ws]
    W.sort(key=lambda x: x['start'])
    narr_end = L[-1]['end'] + 0.6
    total = narr_end + END_CARD
    def t_of(line):
        return L[line]['start'] if line < len(L) else narr_end
    return {'lines': L, 'words': W, 'shift': shift, 'total': total, 'narr_end': narr_end, 't_of': t_of, 'raw_lines': lines}


if __name__ == '__main__':
    b = build()
    print('video length', round(b['total'], 1), 's =', int(b['total'] // 60), 'min', round(b['total'] % 60, 1), 's')
    for c in CHAPTERS:
        print(c, round(b['t_of'](c[0]), 1))
