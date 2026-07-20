# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder suggests songs a listener will like. You give it your taste (favorite
genre, mood, energy level, and whether you like acoustic music). It scores every
song in the catalog and returns the top 5 matches with a short reason for each.

---

## 3. Data Used

- **Size:** 20 songs in `data/songs.csv`.
- **Features per song:** genre, mood, energy, tempo, valence (positivity),
  danceability, and acousticness.
- **Limits:** The catalog is tiny. Most genres have only one song (only pop and
  lofi have more). It leans high-energy. It has no lyrics, no artist history, and
  no info about other listeners.

---

## 4. Algorithm Summary (plain language)

Each song starts at zero points and earns points for matching your taste:

- **Same genre** → points.
- **Same mood** → points.
- **Close energy** → the closer a song's energy is to what you want, the more
  points it gets.
- **Acoustic bonus** → extra points if you like acoustic music and the song is
  very acoustic.

The system adds up the points, sorts songs from highest to lowest, and shows the
top 5. It does not "listen" to music — it just checks if labels match.

---

## 5. Observed Behavior / Biases

- **It favors high-energy listeners.** Half the catalog is high-energy, so calm
  or mid-energy users rarely get a strong match.
- **The same loud songs keep appearing.** When genre and mood don't match, the
  ranking falls back to energy alone, and a few loud tracks (like *Neon
  Overdrive* and *Gym Hero*) show up for almost everyone.
- **It matches on paper, not on feel.** *Gym Hero* is tagged "pop" and is high
  energy, so it ranks high for a "Happy Pop" fan even though it's an aggressive
  gym track, not cheerful pop.
- **Tiny genres get ignored.** With most genres having one song, niche tastes get
  one relevant result and then random-feeling filler.

---

## 6. Evaluation Process

I tested 3 normal profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock) and 5
tricky edge-case profiles (like high energy + a sad mood, or a genre not in the
catalog). I ran each profile and read its top 5. I also compared profiles side by
side: opposite tastes (Pop vs. Lofi) shared no songs, while similar tastes (Pop
vs. Rock, both high energy) shared several. I also ran an experiment doubling
energy's weight and halving genre's, which let more off-genre songs into the top
results.

---

## 7. Intended Use and Non-Intended Use

**Intended for:** learning and classroom exploration — showing how a simple
scoring rule turns data into recommendations, and where bias sneaks in.

**Not intended for:** real music apps or real users. The catalog is too small,
it ignores lyrics and listening history, and it can quietly give wrong results
(for example, a capital letter in "Pop" breaks the genre match).

---

## 8. Ideas for Improvement

1. **Clean up input** — lowercase genre/mood and check energy is between 0 and 1,
   so typos and bad values don't break things.
2. **Use more features** — score tempo, valence, and danceability too, not just
   energy.
3. **Add variety** — avoid showing the same loud songs to everyone and help
   people discover across genres.

---

## 9. Personal Reflection

**Biggest learning moment:** seeing that a recommender doesn't understand music —
it just matches labels and adds points. Once I understood that, the weird results
made sense.

**How AI helped (and when I checked it):** AI helped me quickly design test
profiles, apply the weight-change experiment, and write up my findings. I
double-checked its claims against the real terminal output — for example
confirming the actual scores and that "Pop" really did fail to match "pop."

**What surprised me:** how much a few simple rules can *feel* like a real
recommender, and how quickly small biases (like a high-energy catalog) shape the
results.

**What I'd try next:** add more songs and more features, clean up the inputs, and
build in variety so it doesn't keep recommending the same handful of tracks.
