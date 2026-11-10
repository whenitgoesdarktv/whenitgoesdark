"""Master timeline for the hotel video: narration placement with dramatic pauses, chapters, shots, overlays, SFX cues.

All story beats are keyed to narration line indices (lines.json from align.py). build() returns a dict with
absolute times on the final video timeline.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

# extra silence inserted AFTER line i (seconds)
PAUSE_AFTER = {10: 0.6, 17: 5.0, 38: 0.5, 40: 0.5, 43: 1.6, 47: 1.0, 59: 0.8, 64: 1.6, 90: 1.6, 113: 0.6,
               124: 2.2, 135: 0.6, 154: 1.2, 158: 3.2, 161: 1.4, 163: 1.0, 192: 1.4, 209: 1.6,
               222: 0.8, 224: 0.6}
END_CARD = 7.0
LEAD_IN = 0.35  # tiny breath before the first word

CHAPTERS = [  # (first line, number, title)
    (18, 1, 'THE LAST ROOM'), (39, 2, 'LIGHTS OUT'), (65, 3, 'THE COLD'), (91, 4, 'SOMETHING IN THE WALLS'),
    (125, 5, 'THE HUM'), (155, 6, 'INSIDE OR OUT'), (162, 7, 'FRESH AIR'), (193, 8, 'THE TAILPIPE'), (210, 9, 'MORNING')]

# Status bar state from a line onward: time, power, phone, temp
STATUS = [(0, '2:47 AM', 'OFF', '12%', '49°F'), (18, '6:00 PM', 'ON', '80%', '68°F'), (35, '7:00 PM', 'ON', '77%', '68°F'),
          (39, '8:12 PM', 'ON', '64%', '68°F'), (43, '8:12 PM', 'OFF', '64%', '66°F'), (65, '10:00 PM', 'OFF', '41%', '58°F'),
          (66, '12:00 AM', 'OFF', '33%', '51°F'), (73, '12:40 AM', 'OFF', '31%', '51°F'), (91, '2:47 AM', 'OFF', '12%', '49°F'),
          (162, '3:10 AM', 'OFF', '9%', '9°F'), (193, '3:40 AM', 'OFF', '6%', '9°F'), (210, '5:50 AM', 'OFF', '3%', '12°F')]
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
    (16, 'bg05_lobby_fire', (3.0, 3.6, .37, .43, .37, .43), [], {'dark', 'heat_haze', 'rumble', 'red_glow'}),
    (17, 'bg02_lodge_exterior_dusk', (1.0, 1.25, .58, .4, .6, .38), [], {'snow', 'blackout_grade', 'night'}),
    (18, 'bg02_lodge_exterior_dusk', (1.0, 1.15, .55, .45, .58, .42), [], {'snow'}),
    (21, 'bg02_lodge_exterior_dusk', (2.6, 3.0, .6, .5, .6, .49), [], {'snow', 'sign_nopets'}),
    (22, 'bg03_front_desk', (1.15, 1.25, .5, .6, .5, .6), [('lando_bag', .36, .97, .3, False)], {'warm'}),
    (26, 'bg04_parking_lot_snow', (1.0, 1.2, .5, .5, .4, .5), [], {'snow_heavy'}),
    (28, 'bg03_front_desk', (1.7, 1.85, .62, .37, .62, .36), [('dale_desk_key@.595', .62, .418, .2, False)], {'warm', 'key_tag'}),
    (31, 'bg03_front_desk', (1.5, 1.7, .35, .65, .35, .65), [('lando_bag', .35, .93, .3, False)], {'warm'}),
    (33, 'bg03_front_desk', (2.1, 2.3, .62, .34, .62, .33), [('dale_desk_key@.595', .62, .418, .2, False)], {'warm'}),
    (35, 'bg04_parking_lot_snow', (1.4, 1.7, .33, .55, .33, .55), [], {'snow_heavy'}),
    (38, 'bg02_lodge_exterior_dusk', (1.1, 1.3, .6, .42, .6, .4), [], {'snow', 'night', 'flicker_out'}),
    (44, 'bg07_room22', (1.0, 1.12, .5, .5, .5, .5), [], {'dark', 'blackout_grade', 'phone64'}),
    (48, 'bg06_balcony_view', (1.15, 1.35, .45, .45, .45, .42), [], {'dark', 'rumble'}),
    (50, 'bg05_lobby_fire', (1.05, 1.18, .45, .55, .45, .55), [('dale_generator', .52, .98, .62, False)], {'dark', 'firelight', 'door_snow'}),
    (53, 'bg05_lobby_fire', (2.2, 2.5, .78, .42, .78, .42), [], {'dark', 'door_snow2', 'firelight'}),
    (54, 'bg05_lobby_fire', (1.25, 1.35, .48, .55, .48, .55), [('dale_generator', .52, .98, .62, False)], {'dark', 'firelight'}),
    (56, 'bg05_lobby_fire', (2.0, 2.8, .78, .42, .78, .4), [], {'dark', 'door_snow2', 'ominous'}),
    (57, 'bg03_front_desk', (1.55, 1.7, .65, .45, .65, .45), [('guest_redhat_back', .87, .78, .44, False)], {'dark', 'blackout_grade', 'lights_off', 'candles'}),
    (63, 'bg03_front_desk', (1.5, 1.6, .5, .55, .5, .55), [('lando_bag', .4, .9, .26, False)], {'dark', 'blackout_grade', 'lights_off', 'smoke'}),
    (65, 'bg07_room22', (1.0, 1.15, .45, .5, .45, .5), [], {'dark', 'blackout_grade', 'cold', 'temp_readout'}),
    (71, 'bg07_room22', (1.8, 2.0, .22, .5, .22, .5), [('lando_sleep_curled', .2, .52, .16, False)], {'dark', 'blackout_grade', 'cold'}),
    (72, 'bg07_room22', (1.5, 1.6, .25, .5, .25, .5), [('lando_on_face', .24, .64, .3, False)], {'dark', 'blackout_grade', 'cold'}),
    (74, 'bg07_room22', (1.0, 1.08, .5, .5, .5, .5), [], {'dark', 'blackout_grade', 'knock'}),
    (75, 'bg01_hallway_dark', (1.3, 1.4, .5, .55, .5, .55), [('rosa_door', .5, .86, .5, False)], {'dark', 'beam_char'}),
    (79, 'bg05_lobby_fire', (1.0, 1.12, .45, .5, .45, .5), [], {'dark', 'firelight', 'door_snow'}),
    (83, 'bg09_stairs_down', (1.0, 1.2, .62, .55, .7, .55), [], {'dark', 'headache'}),
    (86, 'bg05_lobby_fire', (1.6, 1.8, .28, .55, .28, .55), [('rosa_sleep_couch', .3, .9, .32, False)], {'dark', 'firelight', 'heat_haze'}),
    (87, 'bg05_lobby_fire', (1.4, 1.5, .62, .55, .66, .5), [('lando_yowl', .6, .98, .4, False)], {'dark', 'firelight', 'door_snow'}),
    (89, 'bg09_stairs_down', (1.1, 1.25, .62, .55, .62, .55), [], {'dark'}),
    (91, 'bg07_room22', (1.0, 1.2, .45, .5, .45, .5), [], {'dark', 'blackout_grade', 'dizzy'}),
    (93, 'bg07_room22', (2.6, 3.0, .82, .5, .83, .5), [], {'dark', 'blackout_grade', 'dizzy'}),
    (95, 'bg07_room22', (2.4, 2.8, .14, .2, .15, .2), [], {'dark', 'blackout_grade', 'scratch', 'shake_soft'}),
    (98, 'bg07_room22', (1.35, 1.45, .3, .55, .3, .55), [('hero_ear_wall', .3, .9, .5, False)], {'dark', 'blackout_grade', 'beam_char'}),
    (99, 'bg07_room22', (2.6, 3.0, .14, .22, .2, .22), [], {'dark', 'blackout_grade', 'scratch', 'shake_soft'}),
    (103, 'bg01_hallway_dark', (1.1, 1.45, .5, .5, .5, .42), [('hero_walk_headlamp', .42, 1.0, .7, False)], {'dark', 'beam', 'dust', 'scratch'}),
    (107, 'bg08_vent_grate', (1.0, 1.3, .55, .45, .55, .45), [], {'dark', 'heat_haze'}),
    (111, 'bg01_hallway_dark', (1.4, 1.5, .5, .6, .5, .6), [('hero_kneel_vent', .5, 1.0, .55, False)], {'dark', 'beam_char'}),
    (112, 'bg08_vent_grate', (1.4, 1.8, .55, .45, .55, .45), [], {'dark', 'eyes', 'heat_haze'}),
    (116, 'bg01_hallway_dark', (1.3, 1.45, .5, .55, .5, .55), [('hero_dizzy', .5, 1.0, .75, False)], {'dark', 'beam_char', 'dizzy'}),
    (120, 'bg01_hallway_dark', (1.6, 2.0, .5, .38, .5, .36), [], {'dark', 'beam', 'figure', 'dizzy'}),
    (123, 'BLACK', None, [], {'heartbeat'}),
    (124, 'bg05_lobby_fire', (3.0, 3.6, .37, .43, .37, .43), [], {'dark', 'heat_haze', 'red_glow'}),
    (134, 'bg06_balcony_view', (1.1, 1.3, .45, .45, .45, .42), [], {'dark', 'heat_haze'}),
    (135, 'STAT', None, [], set()),
    (136, 'bg09_stairs_down', (1.0, 1.2, .6, .5, .6, .55), [('hero_carry_lando', .45, 1.0, .75, False)], {'dark', 'dizzy_soft'}),
    (138, 'bg05_lobby_fire', (1.15, 1.35, .4, .5, .38, .5), [], {'dark', 'heat_haze_strong', 'coals'}),
    (142, 'bg05_lobby_fire', (1.7, 1.85, .25, .55, .25, .55), [('rosa_confused', .3, 1.0, .6, False)], {'dark', 'heat_haze_strong', 'coals'}),
    (145, 'bg03_front_desk', (1.3, 1.45, .62, .5, .62, .5), [('dale_slumped', .62, .98, .62, False)], {'dark', 'blackout_grade', 'lights_off', 'heat_haze'}),
    (147, 'bg10_ceiling_alarm', (1.0, 1.4, .58, .32, .58, .3), [], {'dark', 'no_battery'}),
    (151, 'bg11_porch_blizzard', (1.0, 1.15, .5, .5, .5, .5), [], {'snow_heavy', 'diagram_20ft'}),
    (155, 'SPLIT', None, [], set()),
    (158, 'CHOICE', None, [], set()),
    (159, 'bg11_porch_blizzard', (1.0, 1.2, .5, .5, .55, .5), [], {'snow_heavy', 'whoosh'}),
    (162, 'bg05_lobby_fire', (2.6, 2.7, .37, .43, .37, .43), [], {'dark', 'coals', 'gen_off'}),
    (164, 'bg11_porch_blizzard', (1.1, 1.25, .45, .55, .45, .55), [('rosa_confused', .36, .95, .6, False), ('hero_walk_headlamp', .52, .96, .62, True)], {'snow_heavy'}),
    (167, 'bg05_lobby_fire', (1.2, 1.35, .62, .55, .7, .55), [('dale_slumped', .58, .98, .55, False)], {'dark', 'coals', 'door_snow'}),
    (172, 'bg11_porch_blizzard', (1.2, 1.3, .45, .6, .45, .6), [('lando_parade', .45, .92, .3, False)], {'snow_heavy'}),
    (173, 'bg11_porch_blizzard', (1.25, 1.35, .45, .55, .45, .55), [], {'snow_heavy', 'phone_call'}),
    (181, 'bg11_porch_blizzard', (1.0, 1.15, .5, .5, .5, .5), [], {'snow_heavy', 'temp_9'}),
    (191, 'bg11_porch_blizzard', (1.6, 1.75, .4, .6, .4, .6), [('rosa_confused', .4, .95, .65, False)], {'snow_heavy', 'cold'}),
    (193, 'bg04_parking_lot_snow', (1.3, 1.5, .33, .55, .33, .55), [], {'snow_heavy'}),
    (194, 'bg04_parking_lot_snow', (1.6, 1.7, .36, .6, .36, .6), [('hero_dig_snow', .31, .74, .26, False)], {'snow_heavy'}),
    (195, 'bg13_car_interior', (1.0, 1.15, .5, .45, .5, .45), [], {'dash_glow'}),
    (199, 'bg13_car_interior', (1.2, 1.35, .5, .55, .5, .55), [('lando_yowl', .5, .98, .45, False)], {'dash_glow'}),
    (202, 'bg12_car_tailpipe', (1.0, 1.5, .4, .6, .28, .72), [], {'snow_heavy', 'ominous'}),
    (207, 'bg12_car_tailpipe', (1.3, 1.4, .45, .65, .45, .65), [('hero_dig_snow', .36, .95, .34, False), ('lando_parade', .62, .95, .26, True)], {'snow'}),
    (210, 'bg14_mountain_dawn', (1.0, 1.25, .5, .5, .5, .55), [], {'snow_light', 'dawn', 'siren_lights'}),
    (214, 'bg14_mountain_dawn', (1.3, 1.45, .62, .65, .62, .65), [('dale_oxygen', .66, .98, .45, False)], {'snow_light', 'dawn', 'siren_lights'}),
    (219, 'bg14_mountain_dawn', (1.4, 1.5, .62, .7, .62, .7), [('lando_parade', .6, .97, .32, False)], {'snow_light', 'dawn', 'warm'}),
    (223, 'bg15_ambulance_interior', (1.1, 1.22, .55, .55, .57, .55), [('rosa_lando_bench', .56, .97, .62, False)], {'dawn_grade', 'siren_soft'}),
    (225, 'SPLIT', None, [], set()),
    (231, 'bg02_lodge_exterior_dusk', (1.0, 1.12, .58, .45, .6, .42), [], {'snow', 'night'}),
    (233, 'END', None, [], set()),
]

# SFX cues: (line, offset seconds from line start, file, gain dB)
SFX = [
    (0, 0.0, 'sfx_scratching_wall', -10), (4, 0.0, 'sfx_scratching_wall', -6), (6, 0.0, 'sfx_scratching_wall', -9),
    (9, 0.2, 'sfx_heartbeat', -10), (12, 0.0, 'sfx_whoosh_hit', -14),
    (17, 4.2, 'sfx_whoosh_hit', -11), (23, 0.8, 'sfx_cat_purr', -20), (28, 1.0, 'sfx_key_slide', -8),
    (32, 0.1, 'sfx_meow_bag', -8), (41, 0.0, 'sfx_lights_flicker', -8), (42, 0.0, 'sfx_lights_flicker', -8),
    (43, 0.0, 'sfx_lights_flicker', -6), (48, 1.2, 'sfx_generator_start', -6), (57, 0.4, 'sfx_candle_light', -10),
    (63, 0.3, 'sfx_blow_out', -9), (74, 0.0, 'sfx_knock_door', -6), (87, 0.5, 'sfx_cat_yowl', -12),
    (95, 0.0, 'sfx_scratching_wall', -5), (99, 0.0, 'sfx_scratching_wall', -6), (103, 0.0, 'sfx_footsteps_carpet', -14),
    (106, 0.0, 'sfx_scratching_wall', -8), (112, 0.6, 'sfx_cat_purr', -16), (121, 0.0, 'sfx_lights_flicker', -12),
    (123, 0.0, 'sfx_heartbeat', -6), (124, 1.8, 'sfx_whoosh_hit', -10), (156, 0.0, 'sfx_heartbeat', -12),
    (159, 0.0, 'sfx_whoosh_hit', -11), (162, 0.4, 'sfx_generator_off', -6), (165, 0.0, 'sfx_footsteps_snow', -12),
    (176, 0.0, 'sfx_phone_ring', -12), (177, 0.0, 'sfx_phone_ring', -12), (194, 0.0, 'sfx_digging_snow', -10),
    (196, 0.0, 'sfx_car_start', -8), (199, 0.0, 'sfx_cat_yowl', -11), (207, 0.0, 'sfx_digging_snow', -10),
    (210, 0.0, 'sfx_plow', -10), (213, 0.0, 'sfx_siren_distant', -14), (222, 1.0, 'sfx_cat_purr', -16),
]

# Ambience beds by line range: (first line, last line, file, gain dB)
BEDS = [
    (0, 17, 'amb_lodge_inside', -26), (17, 22, 'amb_blizzard_outside', -24), (22, 26, 'amb_lodge_inside', -28),
    (26, 27, 'amb_blizzard_outside', -24), (27, 35, 'amb_lodge_inside', -28), (35, 44, 'amb_blizzard_outside', -24),
    (44, 151, 'amb_lodge_inside', -25), (151, 155, 'amb_blizzard_outside', -22), (155, 159, 'amb_lodge_inside', -26),
    (159, 162, 'amb_blizzard_outside', -20), (162, 164, 'amb_lodge_inside', -30), (164, 195, 'amb_blizzard_outside', -21),
    (195, 202, 'amb_lodge_inside', -30), (202, 210, 'amb_blizzard_outside', -21), (210, 233, 'amb_blizzard_outside', -27),
]
# Generator hum: audible from line 46 to 162 (loud in the lobby, faint through the floor elsewhere)
HUM = (48, 162)
HUM_COLD_OPEN = (12, 17)


def build():
    lines = json.load(open(os.path.join(HERE, 'lines.json')))
    words = json.load(open(os.path.join(HERE, 'words.json')))
    shift = [0.0] * len(lines)
    acc = LEAD_IN
    for i in range(len(lines)):
        shift[i] = acc
        acc += PAUSE_AFTER.get(i, 0.0)
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
        W.append({'text': w['text'], 'start': w['start'] + shift[li], 'end': w['end'] + shift[li], 'line': li})
    narr_end = L[-1]['end'] + 0.6
    total = narr_end + END_CARD
    def t_of(line):
        return L[line]['start'] if line < len(L) else narr_end
    return {'lines': L, 'words': W, 'shift': shift, 'total': total, 'narr_end': narr_end, 't_of': t_of}


if __name__ == '__main__':
    b = build()
    print('video length', round(b['total'], 1), 's =', int(b['total'] // 60), 'min', round(b['total'] % 60, 1), 's')
    for c in CHAPTERS:
        print(c, round(b['t_of'](c[0]), 1))
