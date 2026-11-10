# S1 trailer Short build (Nov 10, 2026)

Source: `assets` branch `s1/v3/part_00..03` joined with cat (Season 1 full story, 1920x1080, 10:02).

1. Fonts into `fonts/` from github.com/google/fonts (Anton, Oswald[wght], Bebas Neue, Barlow Bold/SemiBold); `FSRCNN_x4.pb` from github.com/Saafke/FSRCNN_Tensorflow/models.
2. `words_full.json` = ElevenLabs scribe word timings of the full story audio (source times).
3. `python3 -I render_trailer.py s1_full.mp4 trailer_yt_v.mp4 yt` (video only, 1080x1920, 36.4 s).
   Social end card only: `python3 -I render_trailer.py s1_full.mp4 endcard_social.mp4 social --endcard-only`.
4. `python3 -I build_audio.py s1_full.mp4 trailer_audio.wav` (cuts + low hits + storm bed, -14 LUFS).
5. `python3 -I make_cover.py s1_full.mp4 trailer_cover.jpg`.
6. `python3 -I check_leftovers.py s1_full.mp4` confirms no crop window touches the old burned-in captions.

Crops stay above source row 893 (old captions sit at rows ~905-985) or fill below it with a dark fade.
