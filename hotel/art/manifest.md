# WIGD Hotel: background manifest

All 14 backgrounds were generated with Canva generate-image, placed full-bleed on new 1920x1080 pages added to the working design **DAHZ9qxEHJU** ("WIGD S1 full story backgrounds (working file)", https://www.canva.com/d/jmW1vAT3yqRO-Ml), and exported from there as lossless PNG at 1920x1080. The pages are titled "WIGD Hotel - <bg name>". Pages 1 to 5 (Season 1) were not touched. No separate Canva designs were created. Nothing was published or shared.

Every export came out at exactly 1920x1080, 16:9, so no Python normalization was needed and there are no `*_orig.png` files. Every final was viewed at full size.

| File | Canva page / media id | Description | Issues / notes |
|---|---|---|---|
| bg01_hallway_dark.png | p6 / MAHai38XqL0 | Pitch-dark lodge corridor with pine-tree wallpaper, doors with blank oval plaques, an ice machine in an alcove on the left, a vent grate at the far end, and an amber headlamp pool on the carpet | Regenerated: v1 (MAHai3Q9anE) had lit wall sconces. The vent sits at the base of the end wall, not mid-floor. |
| bg02_lodge_exterior_dusk.png | p7 / MAHaix1r2xQ | Two-story log lodge in snowfall at dusk with warm windows, a steep snowy roof, pines, and a blank sign over the door | Thinner, more painterly outlines than the S1 character frames (closer to the S1 storm-skyline frame). |
| bg03_front_desk.png | p8 / MAHai2vNL24 | Wooden reception desk with a brass bell, a brass key rack, lamps on, red patterned wallpaper and stone pillars | Mostly amber on purpose, since this is before the blackout. A framed mountain painting has no text. |
| bg04_parking_lot_snow.png | p9 / MAHai8geCbo | Night lot with a car buried as a white hump, snow falling, and the lodge behind with glowing windows | The windows are fairly bright for "dimly glowing". Darken them in the edit if needed. |
| bg05_lobby_fire.png | p10 / MAHai8pJHtU | Blackout lobby with a stone fireplace fire, a red generator by the hearth, log couches with blankets, and the front door open to blowing snow | A table-lamp shade at the far right edge looks pale and could read as lit. Minor. |
| bg06_balcony_view.png | p11 / MAHaiyxrVHU | POV from the upstairs railing down into the lobby: fireplace, couches, open front door, firelight | Point-of-view shot, so the railing fills the lower third. No generator is visible (the brief doesn't require it here). A small lantern on the table is lit. |
| bg07_room22.png | p12 / MAHai_Qq0-4 | Cold-blue room with a quilted bed, pine wallpaper, a snowy window with heavy curtains, and a cat carrier with its door open | None. Open floor in the center. |
| bg08_vent_grate.png | p13 / MAHaiwHiKEQ | Top-down metal vent grate in patterned carpet, faint amber haze, black void behind the slats | Close-up insert with no character space. |
| bg09_stairs_down.png | p14 / MAHai5NybNQ | Upstairs landing with a wooden newel post and handrail, stairs going down into the dark, orange glow from a lantern below | The glow comes from a wall lantern at the bottom of the stairs. |
| bg10_ceiling_alarm.png | p15 / MAHai1wstA8 | Low-angle view of a beamed ceiling with a round alarm unit, its indicator dark | Close-up insert. No text on the unit. |
| bg11_porch_blizzard.png | p16 / MAHai-qD3UU | Lodge porch at 3 AM, snow blowing sideways, porch lantern off, snow on the steps, lobby door open with firelight inside | None. |
| bg12_car_tailpipe.png | p17 / MAHai-Ow1Wg | Rear of a sedan with a drift burying the tailpipe, exhaust trapped and curling, dark lamp posts, one candle-lit lodge window far behind | Regenerated: v1 (MAHai4E1kVc) was near-photoreal and had lit street lamps and windows. The license plate is blank. |
| bg13_car_interior.png | p18 / MAHai2sJ2-U | Back-seat view toward a snow-packed windshield, amber dashboard and gauges | The front seats fill the lower left and right. The gauges show tick marks only, plus a small hazard-triangle icon. |
| bg14_mountain_dawn.png | p19 / MAHai2plSi0 | Gray-blue dawn road with a plow truck coming, headlights on, an ambulance with red lights behind it, and the lodge corner at the left edge | The ambulance and plow have no lettering. The sun is visible on the horizon. More detailed and painterly than the interiors. |

## General notes
- Canva doesn't report the native resolution of the generated images. The exports are rendered at 1920x1080 and may be upscaled, so expect slight softness at 100% zoom.
- Line weight varies: interiors (bg01, bg05, bg06, bg09, bg12) have the boldest outlines, while the exteriors (bg02, bg04, bg14) are more painterly. The whole set shares the same lodge (log and timber, stone fireplace, pine-pattern wallpaper, Navajo-style rugs) and the navy/teal plus amber palette.
- The first generate-image call returned HTTP 409. A single retry worked, and there were no other Canva errors.
