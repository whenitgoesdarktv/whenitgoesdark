"""Hand-placed puppet rigs, in fractions of each trimmed base drawing (x of width, y of height).
eyes: (x0, y0, x1, y1) boxes   head: (cx, cy, rx, ry) ellipse   pivot: neck point   mouth: breath point
excl: boxes kept out of the head layer (a hand or a cat touching the head)   amp: head sway in degrees"""
RIGS = {
    'hero_walk_headlamp': dict(eyes=[(.561, .165, .603, .212), (.735, .165, .774, .212)], head=(.57, .16, .30, .155), pivot=(.573, .304), mouth=(.66, .255), amp=1.4),
    'hero_carry_lando':   dict(eyes=[(.291, .164, .331, .209), (.492, .164, .538, .209)], head=(.475, .16, .315, .155), pivot=(.453, .315), excl=[(.60, .24, 1.0, 1.0)], amp=1.8),
    'hero_ear_wall':      dict(eyes=[(.584, .164, .626, .212), (.767, .164, .807, .212)], head=(.585, .16, .30, .155), pivot=(.566, .317), excl=[(.86, 0, 1.0, 1.0)], amp=0.8),
    'hero_drag_dale':     dict(eyes=[(.187, .171, .215, .216), (.285, .150, .312, .192)], head=(.185, .17, .165, .148), pivot=(.22, .31), mouth=(.262, .248), amp=1.5),
    'hero_dig_snow_night': dict(eyes=[(.329, .300, .361, .351), (.419, .274, .450, .327)], head=(.42, .21, .174, .195), pivot=(.511, .413), mouth=(.425, .377), amp=1.6),
    'rosa_confused':      dict(eyes=[(.18, .182, .27, .22), (.347, .169, .45, .206)], head=(.44, .15, .40, .15), pivot=(.40, .29), mouth=(.35, .253), amp=1.6),
    'rosa_door':          dict(eyes=[(.267, .231, .298, .263), (.383, .222, .413, .254)], head=(.25, .22, .25, .14), pivot=(.333, .338), excl=[(.465, 0, 1.0, 1.0)], amp=1.4),
    'rosa_blanket':       dict(eyes=[(.347, .173, .371, .204), (.478, .172, .502, .203)], head=(.48, .14, .30, .15), pivot=(.447, .29), mouth=(.44, .255), amp=1.3),
    'dale_desk_key':      dict(eyes=[(.468, .150, .503, .175), (.562, .148, .606, .175)], head=(.543, .15, .14, .148), pivot=(.542, .29), amp=1.6),
    'dale_generator':     dict(eyes=[(.848, .140, .867, .164), (.943, .151, .961, .175)], head=(.86, .145, .14, .14), pivot=(.867, .282), amp=1.2),
    'lando_bag':          dict(eyes=[(.117, .243, .181, .300), (.243, .257, .322, .311)], head=(.25, .235, .29, .215), pivot=(.20, .41), excl=[(.53, 0, 1.0, 1.0)], amp=2.0),
    'lando_parade':       dict(eyes=[(.659, .268, .752, .310), (.820, .257, .874, .296)], head=(.72, .215, .25, .195), pivot=(.735, .39), mouth=(.80, .352), amp=2.2),
    'guest_redhat_back_hair': dict(eyes=[], head=(.50, .155, .19, .15), pivot=(.51, .296), amp=1.4),
}
