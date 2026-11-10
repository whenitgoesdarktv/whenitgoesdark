You are the independent reviewer for a YouTube Shorts / TikTok / Instagram Reels / Facebook Reels trailer for the faceless animated channel "When It Goes Dark" (blackout survival stories, narrator speaks to "you", the cat is called Lando). You have NOT seen it being built. Watch it as a stranger scrolling the Shorts feed who has never seen the channel.

Files (all in /home/claude/wigd_build/):
- trailer_yt.mp4: 1080x1920, ~36.4 s, the YouTube version (end card says "FULL VIDEO ON THE CHANNEL")
- trailer_social.mp4: same video, end card says "FULL 10-MIN VIDEO ON YOUTUBE" (for TikTok, Instagram, Facebook)
- trailer_cover.jpg: the custom cover
- words_full.json: word-level transcript of the 10-minute source the trailer was cut from (source times; the trailer uses source 0.00-20.45, 32.95-36.30, 209.50-214.30, 304.80-308.60, then a 4 s end card)
- post_copy.md: titles, captions, hashtags

Tools: ffmpeg/ffprobe, Python with OpenCV/numpy/PIL. Extract frames (e.g. every 0.5 s, plus every frame around each cut at 4.50, 7.20, 9.47, 11.97, 14.43, 18.03, 20.45, 23.26, 23.80, 28.60, 32.40) and LOOK at them with the Read tool. Check the audio with ffmpeg (ebur128 loudness, true peak; silencedetect) and listen-by-proxy: confirm narration is present where captions are shown.

Check and report PASS/FAIL with specifics (timestamp + what is wrong) for each:
1. First second: does the first frame plus the top text make sense to a stranger? Is it dramatic?
2. Captions: every caption word matches the narration (compare with words_full.json for the source windows), no word cut off at the frame edge, nothing overlapping a face, captions inside the safe zone (not in the bottom 20% of the frame, not under the right-side button column x>960 at y 1000-1700, not in the top 8%).
3. Leftovers: any trace of the OLD burned-in captions from the 16:9 source (white/amber uppercase text near the bottom of the source frame) anywhere in any frame. This is the most important visual check: scan every 0.25 s.
4. Crops: any half-cut faces or characters at the edge that look like mistakes, black bars, frozen frames, glitches, flashes that last too long, text from the source (status bars, chapter labels) cut in half.
5. Characters look consistent: neighbor = skin-colored round face, dot eyes, no nose, dark ponytail, yellow raincoat; Lando = orange-and-white cat.
6. End card: readable, nothing cut off, real-cat photo present with "Don't worry, he's OK.", text not in the bottom 20%.
7. Audio: integrated loudness about -14 LUFS, true peak below -1 dBTP, no clicks at cuts, voice clearly above the low booms at the cuts (check 0.0-1.5 s after 20.45, 23.80, 28.60, 32.40), no dead air longer than 1.5 s except the end card.
8. Copy (post_copy.md + on-screen text): no em dashes; none of these words: prepper, prepping, doomsday, SHTF, end of the world, "you will die", guaranteed, 100% safe, delve, tapestry, testament; no view or vote counts; emoji only 🔦; 3-5 hashtags including #WhenItGoesDark.
9. Overall: would a stranger keep watching past 3 seconds and understand what the full video is? Anything confusing?

Do not edit or re-render anything. Report a short list: blocking problems first (must fix before posting), then minor notes. Be concrete and brief.
