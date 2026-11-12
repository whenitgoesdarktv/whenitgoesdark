You are the independent reviewer for "Winter Storm: 12 Hours Trapped in a Hotel With No Power" (faceless animated channel "When It Goes Dark"; second-person story, the hero's cat is Lando). You passed an earlier version of this video. Since then a coded animation layer was added. You have NOT seen it being built. Watch it as a stranger who clicked the thumbnail, then check the new animation closely.

Files (all in /home/claude/wigd_build/hotel/):
- out/hotel_final.mp4: the new finished video (1920x1080, 30 fps, about 8:41)
- beats.txt: time of every narration line, the shot on screen (background, characters, effects), cards, SFX cues
- narration.md, publish_kit.md, thumb/thumb_A_walls.jpg, thumb/thumb_B_asleep.jpg, thumb/thumb_C_poison.jpg
- chars/*.png: character references

Tools: ffmpeg/ffprobe, Python with OpenCV/numpy/PIL. Extract frames and LOOK at them with the Read tool (contact sheets; crops at full resolution for faces). Do not edit or re-render anything.

What was added (check each one, PASS/FAIL with timestamps):
1. Blinks: every awake character with visible eyes blinks every 3 to 5 s (4 frames). Check at full resolution on at least 8 different shots (e.g. 0:17-0:21 hero walking, 1:00 Lando in the bag, 1:12 and 1:20 Dale at the desk, 2:00 Dale with the generator, 2:56 Rosa at your door, 3:49 hero at the wall, 4:46 Rosa in the blanket, 5:07 hero carrying Lando, 5:24 Rosa close-up, 6:24 porch, 6:41 drag, 6:45 Lando walking, 7:24 dig). A closed eye must be fully covered by face colour with a clean lid line: no leftover pupil, no square patch, no wrong colour.
2. Head motion: heads tilt and nod slightly on the neck (about 1-2 degrees), body stays still. Look for any seam at the neck, a double outline, hair or ears cut off, a hand or prop sliding against the head, or a hole where the head was. Step frame by frame through at least 2 s on 6 different characters.
3. Lando watching the smoke (2:29-2:36): his head turns slowly while the smoke rises. Does it read as him watching it? Any artifact?
4. Breath clouds outdoors (6:24-7:30 porch and parking lot, 7:49 tailpipe): soft white puffs leave the mouth every few seconds. Do they come from the mouth, look like breath (not a glitch or smoke), and never cover a face?
5. "The dizziness is not. Carbon monoxide has no color and no smell." (4:35-4:44): a colourless shimmer rises off the generator, with "NO COLOR" and "NO SMELL" tags popping on those words. Does the shimmer read as an invisible gas (not as a video glitch)? Do the tags fit the words, and avoid the rule card and chapter card?
6. Stat card (4:59-5:06): number counts up while 100 person icons fill in red. Readable? Matches "more than a hundred people" (CPSC)?
7. CO alarm (5:31-5:39): headlamp beam sweeps in and finds the alarm; a red ring draws around the dead light with "LIGHT: OFF" on "Its light is off"; "HOTEL POWER: OFF" on "It runs on the hotel's power"; an empty battery with a red X next to "NO BATTERY BACKUP" on "No battery backup". Timing, readability, nothing covering captions.
8. Two-choices card (5:54-6:04) and the choice card after it: the side being described is lit and the other dimmed; a CO gauge climbs red during "Stay inside..."; a thermometer drops from 49°F to 9°F during "...where it's nine degrees", frost creeps in at the edges. Readable? Any number or claim that is not in the narration or sources?
9. Regression: everything that passed before still passes (hook, picture matches story, captions, status bar, chapter cards vs description chapters, characters consistent with references, no black/frozen/flash frames, segment joins at 60, 120 ... 480 s clean, audio -14 LUFS / true peak at or below -1 dBTP, end card with the real Lando photo and "Don't worry, he's OK.").
10. Performance: no frame-to-frame jitter in characters (track one character for 1 s and report the motion).
11. Viewer simulation: estimate retention at 0:30, 1:00, 2:00, 4:00, 6:00 and the end for (a) a teen on a phone, (b) a 35-year-old survival fan, plus overall; estimated average view duration. Compare with your last estimate (overall 68/57/48/39/33/26%, AVD 42-44%) and say which changes moved it and which did not.

Report blocking problems first (must fix before posting tomorrow at 4 PM), then minor notes. Be concrete and brief, with timestamps.
