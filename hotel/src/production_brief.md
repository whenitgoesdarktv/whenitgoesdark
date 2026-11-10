# Production brief: "Winter Storm: 12 Hours Trapped in a Hotel With No Power"

Channel: When It Goes Dark (faceless animated survival stories, narrator speaks to "you"). Long video, 16:9, 1920x1080, ~11 min, posts Thu Nov 12, 4 PM ET. Due to Darien (owner) Thu 1 PM; assembled by the showrunner Wed night.
Script: /home/claude/wigd_build/hotel/narration.md (narration only). Full plan + script with on-screen notes: Claude Doc https://claude.ai/artifact/LWTuJzdzATQQHAEbMYeh41

## Look (match Season 1 exactly)
Style references (Season 1 frames, ignore the UI overlays and captions): /home/claude/wigd_build/hotel/style_refs/*.png
- Clean modern cartoon / animated-explainer illustration: bold dark outlines, flat colors with soft cel shading, slightly painterly backgrounds, no photorealism, no anime, no 3D.
- Night palette: deep navy, slate blue, teal; warm amber (#ffb547) only for practical light (headlamp, fire, candles, lit windows). Snow scenes: blue-gray with white snow.
- Wide 16:9 compositions with clear empty space in the lower-middle third where characters get pasted, and nothing important in the bottom 15% (captions go there).
- NO text, letters, signs with words, logos or watermarks in any image (we add all text in code). NO people in background images.

## Characters (must always look the same)
- YOU (hero): white round head, simple face (dot eyes, small mouth/eyebrows), headlamp with amber light, dark teal hooded jacket, dark pants, gray sneakers. Never speaks.
- LANDO: orange-and-white tabby cat (white muzzle/chest/paws, orange back and tail, green eyes). Expressive but never in real danger.
- DALE (new): hotel night manager, about 60, tall and thin, receding gray hair, bushy gray mustache, skin-colored round face, dot eyes, small mouth, NO nose, dark green fleece vest over a plaid flannel shirt (blue/gray, NOT red: Walt from Season 1 wears red plaid), khaki pants, name-tag rectangle with no letters.
- ROSA (new): guest from room 12, about 40, skin-colored round face (a bit warmer tone than the neighbor), dot eyes, small mouth, NO nose, curly dark-brown shoulder-length hair, two knitted scarves (mustard and maroon), a white hotel bathrobe worn over a long brown winter coat.
- Other guests: dark sleeping shapes under blankets (no faces needed). One guest in a red knit hat (seen from behind lighting candles).
Faces front-on or 3/4 at most (side views make the image model add a nose).

## Backgrounds (Canva, 16:9, export at least 1920x1080, PNG). File names exactly:
- bg01_hallway_dark.png  Long hotel corridor at night, pitch dark, patterned wallpaper, numbered doors (no readable numbers), an ice-machine alcove halfway, a metal floor vent grate at the far end; lit as if only by a weak headlamp from the camera.
- bg02_lodge_exterior_dusk.png  Rustic two-story mountain lodge in heavy snowfall at dusk, warm lit windows, steep snowy roof, pine trees, front door with a small blank sign.
- bg03_front_desk.png  Cozy wooden reception desk with a key-rack of brass keys behind it, warm table lamps on, a bell on the desk, before the blackout.
- bg04_parking_lot_snow.png  Snowy lodge parking lot at night, one car completely buried as a white hump, snow falling, lodge windows dimly glowing behind.
- bg05_lobby_fire.png  Lodge lobby at night with the power out: big stone fireplace with a fire, couches with blankets, a red portable generator on the floor right next to the fireplace, the front door standing open to blowing snow. Warm firelight vs cold blue doorway.
- bg06_balcony_view.png  View from an upstairs balcony railing looking down into the same lobby (fireplace, couches, open front door), dark, firelight glow.
- bg07_room22.png  Small hotel room at night, power out, cold blue: bed with heavy blanket, patterned wallpaper, window with snow outside, heavy curtains, a cat carrier on the floor with its door open.
- bg08_vent_grate.png  Close-up top-down view of a metal floor vent grate in a dark hallway carpet, faint warm haze rising, deep black space behind the slats.
- bg09_stairs_down.png  Lodge wooden staircase going down into darkness, handrail, faint orange glow from below.
- bg10_ceiling_alarm.png  Close-up of a lodge ceiling with a round wall-powered alarm unit, its indicator light off, dark.
- bg11_porch_blizzard.png  Lodge porch under its roof at 3 AM, blizzard blowing sideways, porch light off, snow piling on steps, the lobby door open with orange glow inside.
- bg12_car_tailpipe.png  Rear of a car in a parking lot at night with a deep snow drift covering the tailpipe, exhaust vapor trapped, snow falling.
- bg13_car_interior.png  Inside a car at night, view from the back seat toward the windshield covered in snow, dashboard lights glowing amber.
- bg14_mountain_dawn.png  Snowy mountain road at dawn, gray-blue light, a snowplow coming with headlights, an ambulance behind it with red lights, the lodge in the foreground edge.

## Character poses (cutouts, PNG with transparent background, at least 1200 px tall). File names:
- hero_walk_headlamp.png (walking, 3/4 view, headlamp on)
- hero_kneel_vent.png (kneeling, looking down)
- hero_ear_wall.png (pressing ear to a wall, side-ish 3/4)
- hero_dizzy.png (hand on head, wobbly)
- hero_carry_lando.png (holding Lando in one arm)
- hero_dig_snow.png (digging snow with bare hands)
- lando_bag.png (Lando's head poking out of a duffel bag, grumpy)
- lando_on_face.png (Lando lying across the hero's face in bed, comic)
- lando_yowl.png (Lando yowling, pulling toward a door)
- lando_parade.png (Lando walking proudly, tail up)
- lando_sleep_curled.png (sleeping, curled)
- dale_desk_key.png (Dale behind a desk sliding a key, deadpan)
- dale_generator.png (Dale dragging a red generator)
- dale_slumped.png (Dale slumped asleep in a chair)
- dale_oxygen.png (Dale lying on a stretcher wearing a clear oxygen mask, eyes open)
- rosa_door.png (Rosa standing at a door in scarves + robe over coat)
- rosa_sleep_couch.png (Rosa asleep under a blanket on a couch)
- rosa_confused.png (Rosa half-awake, unfocused eyes)
- rosa_blanket.png (Rosa wrapped in a blanket, shivering)
- guest_redhat_back.png (guest in red knit hat seen from behind lighting a candle)

## Sound (WAV 48 kHz). File names:
- amb_blizzard_outside.wav (60 s loop, howling wind + blowing snow)
- amb_lodge_inside.wav (60 s loop, muffled wind, creaks)
- sfx_generator_hum.wav (30 s loop, small portable generator idling, low steady hum)
- sfx_generator_start.wav (pull-start, motor coughs to life)
- sfx_generator_off.wav (engine stops, silence)
- sfx_scratching_wall.wav (claws scratching inside a wall, moving)
- sfx_knock_door.wav (three knocks on a hotel room door)
- sfx_meow_bag.wav, sfx_cat_yowl.wav, sfx_cat_purr.wav
- sfx_lights_flicker.wav (electrical buzz + click off)
- sfx_footsteps_carpet.wav, sfx_footsteps_snow.wav
- sfx_key_slide.wav (key slid across wood), sfx_candle_light.wav (match strike), sfx_blow_out.wav
- sfx_phone_ring.wav (call ringing tone), sfx_car_start.wav, sfx_digging_snow.wav
- sfx_plow.wav (snowplow engine and scraping), sfx_siren_distant.wav, sfx_heartbeat.wav, sfx_whoosh_hit.wav (trailer-style impact)
