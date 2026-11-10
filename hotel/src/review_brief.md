You are the independent reviewer for a long-form YouTube video for the faceless animated channel "When It Goes Dark" (blackout survival stories told in second person, "you"; the hero's cat is Lando). You have NOT seen it being built. Watch it as a stranger who clicked the thumbnail.

Video: "Winter Storm: 12 Hours Trapped in a Hotel With No Power", 1920x1080, 30 fps, about 8:39.

Files (all in /home/claude/wigd_build/hotel/):
- out/hotel_final.mp4: the finished video
- beats.txt: the time of every narration line in the final video, the shot on screen (background, characters, effects), chapter/rule card times, status-bar changes and sound-effect cues
- narration.md: the narration script
- publish_kit.md: title, description with chapters and sources, settings, pinned comment
- thumb/thumb_A_walls.jpg, thumb/thumb_B_asleep.jpg: the two thumbnails (A/B test)
- chars/*.png and chars/dale_sheet.png, chars/rosa_sheet.png: the character references

Tools: ffmpeg/ffprobe, Python with OpenCV/numpy/PIL, WebFetch for the source pages. Extract frames (at least one every 2 s, plus every 0.1 s for 1 s around each shot change listed in beats.txt and around 60, 120, 180, 240, 300, 360, 420, 480 s, where render segments were joined) and LOOK at them with the Read tool. Make contact sheets to keep this fast. Check audio with ffmpeg (ebur128 with true peak; silencedetect at -45 dB, 2 s; volumedetect) and listen by proxy: narration present where captions show, SFX at their cues.

Check and report PASS/FAIL with specifics (timestamp + what is wrong) for each:
1. Hook: is the first 30 s dramatic and clear to a stranger? Are the two open questions ("what's inside the walls?", "what is that hum?") set up by about 0:30? Does the thumbnail promise (eyes in a vent / people asleep by a generator) get paid off in the video?
2. Picture matches story: for each beat in beats.txt, does the picture fit the line being spoken (who is on screen, where, what's happening)? Flag any shot that contradicts the narration (wrong character, wrong place, wrong time of day, lights on when the power is out, etc.).
3. Captions: words match the narration, never cut off at the frame edge, never covering a face, readable.
4. Overlays: status bar (time, power, phone %, temperature) changes at the right story moments and never contradicts the narration; chapter cards and the chapter label match the description's chapter list; rule cards are readable and accurate; the choice card, stat card and end card are readable with nothing cut off.
5. Characters stay consistent with the reference sheets: hero (white round head, headlamp, dark teal jacket), Lando (orange-and-white tabby, green eyes), Dale (60s, gray mustache, dark green fleece vest over blue/gray plaid, no nose), Rosa (curly dark-brown hair, mustard + maroon scarves, white robe over brown coat, no nose). Note any pasted character that floats, has a halo, is badly cut out, or is the wrong size for the scene.
6. Glitches: black or blank frames, frozen frames longer than intended, flashes, jumps or repeated frames at the segment joins, text from one card overlapping another, effects that look broken.
7. Audio: integrated loudness about -14 LUFS, true peak at or below -1 dBTP, no clipping or clicks, narration always clearly on top of the ambience and SFX, no dead air longer than 2 s except the intended dramatic pauses (after the title, before chapter cards, after the choice question, end card), audio and picture in sync (knock at "A knock.", generator start at "a motor coughs to life", generator stops at "You shut the generator off").
8. Safety facts: every rule card and every safety claim in the narration matches its official source in publish_kit.md (open the pages). Flag anything overstated or not supported.
9. End: the real Lando photo with "Don't worry, he's OK." is present and readable; the closing question is clear.
10. Copy (publish_kit.md + all on-screen text): no em dashes; none of these words: prepper, prepping, doomsday, SHTF, end of the world, "you will die", guaranteed, 100% safe, delve, tapestry, testament; no view or vote counts; chapter timestamps in the description match the chapter cards in the video (within 2 s) and start at 0:00.
11. Overall retention: where would a viewer most likely drop off and why? Anything confusing?

Do not edit or re-render anything. Report: blocking problems first (must fix before posting), then minor notes. Be concrete and brief, with timestamps.
