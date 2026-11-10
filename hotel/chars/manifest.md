# Character cutouts: "Winter Storm: 12 Hours Trapped in a Hotel"

All images were made on the ElevenLabs creative flow `rJlIUOf7hVqeignE5TBe` (Season 1 flow) with `gemini-3.1-flash-image`, one take per node (no retries, no edits).
- Pose cutouts are RGBA PNGs with a transparent background, each exactly 1200 px tall.
- The background was removed by flood-filling the near-white pixels connected to the image border, plus the pure-white gaps fully enclosed by the figure (between arms and body, inside the generator frame, under the stretcher, between legs). Each of those gaps was checked by hand.
- White areas inside the characters were kept. That includes the hero's head, the robe, eyes, teeth, the oxygen-mask highlight and the pillow/sheets.
- Edges are feathered by 1 to 2 px. The edge ring is recolored to the nearby outline color, so there is no white halo.
- Images were upscaled with FSRCNN_x4, then downsampled to 1200 px with INTER_AREA.
- All cutouts were checked on a navy composite.

## Credits

| Generation (node) | Contents | Res | Refs wired | Credits |
|---|---|---|---|---|
| 7NlohXasshpNxWAoLq0x (tXQQGTz6bHY6UrhBv3t4 "HOTEL Dale sheet") | Dale front + 3/4 | 1K 1:1 | Hero sheet, Walt image (D6 v2) | 812 |
| IzEg6WmlHZ0fcvgmiVZl (3YwROgOpYN9KWlwo6AN2 "HOTEL Rosa sheet") | Rosa front + 3/4 | 1K 1:1 | Hero sheet, neighbor (S13 v2) | 812 |
| qvR8zNUqRw3raNQ3Mxst (BVQfhVzr220adVQ47TOF "HOTEL hero poses") | walk, kneel, dizzy, carry Lando | 2K 1:1 | Hero sheet, Lando sheet | 1224 |
| p6a2ED77h4QfN8QGAS7Q (FZ9Fqi2lOQhQEedIqU9q "HOTEL Lando poses") | yowl, bag, parade, sleep | 2K 1:1 | Lando sheet | 918 |
| UC5B6v9DVVtfBZo0uMh2 (LVx7Yb4Zhq3VrdJGnGve "HOTEL Dale poses") | generator, desk key, slumped, oxygen | 2K 1:1 | Dale sheet | 918 |
| 3383YYObZSPZX1etgMM8 (xXVYoyAW4rVOkodAZ3pw "HOTEL Rosa poses") | door, confused, sleep couch, blanket | 2K 1:1 | Rosa sheet | 918 |
| D5UrewsuUf0UgHmLc4Ru (ITYW1V9g8H6N9Ecb4NPO "HOTEL extras") | ear wall, dig snow, Lando on face, red-hat guest | 2K 1:1 | hero poses sheet, Lando sheet | 1224 |
| JwXzXcz13TpVPS6lRBmq (IhsPGDpcYxZG17Di3cK1 "HOTEL Rosa + Lando ambulance bench") | Rosa asleep on bench with Lando (coordinator's late request) | 2K 3:4 | Rosa sheet, Lando sheet | 1224 |
| i12euQ8XMSZwwIjb8UA2 (OnMxVJKuNtZhrs9ZgDZU "HOTEL review extras") | couch guests, porch group, hero drags Dale, Lando bag asleep (independent review) | 2K 1:1 | hero poses sheet, Dale poses sheet, Lando poses sheet | 1530 |
| **Total** | | | | **9,580** |

Node BTKMwBEwTk3ZNrTeBgFx ("HOTEL hero drags Dale (fix, priced only)") was only priced, at 409 credits for a 512 px edit, and never run. It cost nothing. At 512 px the pose would have been too small to use, so I fixed hero_drag_dale locally instead.

## Files

| File | Source generation | Size (w x h) | Flaws / notes |
|---|---|---|---|
| dale_sheet.png | 7NlohXasshpNxWAoLq0x | 2048x2048 (FSRCNN 2x, white bg) | On model: no nose; flannel is blue-gray, not red; blank name tag. The 3/4 view is only slightly turned. |
| rosa_sheet.png | IzEg6WmlHZ0fcvgmiVZl | 2048x2048 (FSRCNN 2x, white bg) | Neither view has a mouth (the poses do). The brown coat under the robe reads partly as side panels. |
| dale_generator.png | UC5B6v9DVVtfBZo0uMh2 | 1037x1200 | Good. Red open-frame generator pulled behind him; the holes in the frame are transparent. |
| dale_slumped.png | UC5B6v9DVVtfBZo0uMh2 | 1129x1200 | Good. Brown armchair is included. |
| dale_desk_key.png | UC5B6v9DVVtfBZo0uMh2 | 1182x1200 | The desk is a plain standalone honey-wood block and won't match bg03's desk exactly. The key is small. |
| dale_oxygen.png | UC5B6v9DVVtfBZo0uMh2 | 1364x1200 | Stretcher is included. The clear mask's contour could faintly read as a nose bridge under the mask. The gaps in the stretcher frame are transparent. |
| rosa_confused.png | 3383YYObZSPZX1etgMM8 | 640x1200 | Eyes are heavy-lidded with whites and pupils, not dot eyes. This was deliberate, to show "unfocused." |
| rosa_sleep_couch.png | 3383YYObZSPZX1etgMM8 | 1958x1200 | Green couch and plaid blanket are included. Her eyes are closed and no mouth is visible. |
| rosa_door.png | 3383YYObZSPZX1etgMM8 | 796x1200 | The brown door slab is part of the cutout (no frame or wall). |
| rosa_blanket.png | 3383YYObZSPZX1etgMM8 | 847x1200 | Bonus pose (not on the priority list). Gray blanket, shiver lines and chattering teeth are kept. |
| hero_walk_headlamp.png | qvR8zNUqRw3raNQ3Mxst | 687x1200 | Good. The headlamp lens glows amber but no beam is drawn (add it in compositing). |
| hero_kneel_vent.png | qvR8zNUqRw3raNQ3Mxst | 1044x1200 | Good. |
| hero_dizzy.png | qvR8zNUqRw3raNQ3Mxst | 735x1200 | Good. Eyes are squeezed shut, mouth is wavy. |
| hero_carry_lando.png | qvR8zNUqRw3raNQ3Mxst | 636x1200 | Good. Lando is orange and white with green eyes. |
| lando_yowl.png | p6a2ED77h4QfN8QGAS7Q | 1810x1200 | No door is drawn; he strains and reaches to the right. Whiskers are thin and partly faint after the cut. |
| lando_bag.png | p6a2ED77h4QfN8QGAS7Q | 1818x1200 | Good. Dark gray duffel, grumpy face; the gap inside the handle is transparent. |
| lando_parade.png | p6a2ED77h4QfN8QGAS7Q | 1094x1200 | Good. Tail up. Whiskers are faint. |
| lando_sleep_curled.png | p6a2ED77h4QfN8QGAS7Q | 1738x1200 | Bonus pose (not on the priority list). Good. |
| hero_ear_wall.png | D5UrewsuUf0UgHmLc4Ru | 657x1200 | Not on the priority list (extras sheet). The hand is cupped by his ear against an implied wall on the right. The model drew a wall line, which I erased. A straight dark contact edge remains on the right of the hand and sleeve, with a tiny stub above the fingertips. His expression is a frown. |
| hero_dig_snow.png | D5UrewsuUf0UgHmLc4Ru | 1409x1200 | Not on the priority list. The bottom of the snow mound and the ground snow have no outline, so those edges are soft and white and partly cut. It looks best over a snowy background (bg04). |
| lando_on_face.png | D5UrewsuUf0UgHmLc4Ru | 1409x1200 | Not on the priority list. Hero lies on a pillow under a white zigzag blanket (no bed frame), with Lando draped over his eyes. The blanket's cut-off ends have no outline (soft white edge). |
| guest_redhat_back.png | D5UrewsuUf0UgHmLc4Ru | 735x1200 | Not on the priority list. 3/4 back view: red pompom beanie, navy parka, lighting a candle with a match. No facial features are visible. |

| rosa_lando_bench.png | JwXzXcz13TpVPS6lRBmq | 1392x2204 (native, no upscale) | Requested late by the coordinator. On model: she sleeps sitting up with her head tilted, no nose, wrapped in a gray blanket, with Lando curled asleep on her lap. The bench was drawn as a padded seat with a short backrest (no ambulance walls). The blanket hides most of the maroon scarf; only a sliver shows next to the mustard one. |

| guests_asleep_couch.png | i12euQ8XMSZwwIjb8UA2 | 2148x1200 | Long three-seat dark-green couch with three sleepers under brown plaid, navy quilt and mustard throw. No faces: blond tuft, gray tuft with a white pillow, a hanging hand, red-and-white striped socks. The couch was drawn from a text description (no reference image), so it is a close match to the rosa_sleep_couch couch, not an exact copy. |
| guests_porch_group.png | i12euQ8XMSZwwIjb8UA2 | 1340x1200 | Four guests from behind: gray bun, brown hair, bald, black ponytail. They wear pajamas and robes with blankets and slippers, with shiver lines. Ears and cheek edges show, but no facial features. The gaps between legs are transparent. |
| hero_drag_dale.png | i12euQ8XMSZwwIjb8UA2, recomposited locally | 1112x1200 | The model swapped the legs: the hero had Dale's khaki trousers stretched out, and Dale had the hero's jeans walking. I fixed this locally with no credits. I cut both pairs of legs out, moved the dark jeans and gray sneakers under the hero (walking backwards), and mirrored the khaki legs and brown shoes under Dale so they trail forward-right with the heels dragging. The leg tops are tucked under the jacket and vest hems. The joins look clean on navy, but a close look shows Dale's torso stays fairly upright, so he reads as "carried and slumping" more than fully dragged. No noses. |
| lando_bag_asleep.png | i12euQ8XMSZwwIjb8UA2 | 1702x1200 | Good. Same dark gray duffel as lando_bag; Lando is asleep with closed eyes and a content smile, one paw out. The gap inside the handle is transparent. |
| hero_dig_snow_night.png | recolor of hero_dig_snow.png (no generation) | 1409x1200 | The snow (mound, ground strip, flung puffs and drops) is multiplied toward #9fb0c8, so white becomes about #9fb0c8 and the shading darkens proportionally. The hero's white head, neck and hands are untouched. The script is snow_tint.py in the scratchpad. |

Every brief pose is covered. The last four rows come from one extra sheet (1,224 credits). I made it because the 14 priority poses came in well under budget. No edits or fix generations were run. All 9 generations are first takes. The total is 9,580 credits, under the 10,000 cap.
The raw sheets I downloaded are in the session scratchpad: /tmp/claude-0/-home-claude/ec2f9e2c-42c6-5caf-b097-14fc003ba9bf/scratchpad/gen/. The cutout script is cutout.py in the same scratchpad folder.
