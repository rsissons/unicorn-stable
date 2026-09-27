# Unicorn Stable

A unicorn game for little kids (about 3 to 6). It's all pictures, so you don't need to read to play.

**Play it:** https://rsissons.github.io/unicorn-stable/

- **Make:** build your own unicorn. Pick the body color, mane and tail, horn, wings, a magic picture and a name. The unicorn says every choice out loud, with a word to learn ("Pink, like a flamingo!", "A star has five points!"). Extras (a bow, a flower crown, a star necklace, a cozy blanket) unlock with chore stickers.
- **Stable:** a chore chart with pictures: feed, water, scoop the sparkle poops, brush, then bedtime. The unicorn asks for each chore in a kid voice, and a pointing hand shows what to tap.
  - Counting: "Can I have three apples?", then counting the sparkle poops as you scoop them.
  - Empty and full: filling the water bucket.
  - Finishing every chore earns a sticker and a cupcake treat. After bedtime it's a new day with new chores, and the chores also reset every real day.
- **Fly:** drag your finger to fly through the sky. Catch five stars of each color to paint that stripe of the rainbow ("Catch five red stars!"). Catching a different color names it, and clouds just go boing, so there's no way to lose.

It's one self-contained HTML file with the voice clips built in. It makes no network requests and collects no data, and it saves your unicorn only in the browser on your device.

On an iPad, open the link in Safari, then tap Share → Add to Home Screen so it opens like an app.

MIT licensed.

## Building

`source/unicorn-stable.src.html` is the code. `python source/build.py` records every voice line with Microsoft's child voice `en-US-AnaNeural` (via [edge-tts](https://github.com/rany2/edge-tts)), caches the clips in `source/voice/`, and writes `unicorn-stable.html` and `index.html`. Kokoro is kept as an offline fallback engine; its model files go in `source/model/` (not committed).
