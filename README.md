# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube predict what you'll love next by
combining two strategies. **Collaborative filtering** looks at other users'
behavior — "people who liked the songs you liked also played this" — while
**content-based filtering** looks at the attributes of the songs themselves —
tempo, energy, mood — and finds more of what already matches your taste. Real
systems blend both and learn their weights automatically from millions of likes,
skips, and playlist adds. 
My version is a **simple content-based recommender**:
it prioritizes matching a song's measurable attributes to a user's stated taste
profile, using hand-chosen weights instead of learned ones. It rewards songs
whose genre and mood match the user, and — most importantly — whose energy is
*closest* to the user's target energy, rather than just favoring high or low
values.

### Data flow (my plan)

The whole system is a three-step pipeline:

```
INPUT                    PROCESS (the loop)                      OUTPUT
─────                    ──────────────────                      ──────
User Prefs  ─┐
             ├─►  for each song:  score it against prefs   ─►  sort by score  ─►  top-k
songs.csv  ──┘        └─ returns (score, reasons)             (high → low)      recommendations
 (catalog)                                                                       + explanation
```

1. **Input** — load the song catalog from `data/songs.csv` (casting numeric
   columns like `energy` from text to `float`) and read the user's taste
   profile.
2. **Process** — loop over every song and run the scoring rule below, which
   returns both a numeric `score` and the list of `reasons` it earned points.
3. **Output** — sort all songs high-to-low by score, keep the top `k`, and turn
   each song's reasons into a short human-readable explanation.

### Scoring rule (my finalized "Algorithm Recipe")

Each song starts at score 0 and earns points:

- **Genre match** → +3.0 if `song.genre == user.favorite_genre`
  (strongest signal of taste)
- **Mood match** → +2.0 if `song.mood == user.favorite_mood`
  (a modifier, worth less than genre)
- **Energy closeness** → `(1 - abs(song.energy - user.target_energy)) * 2.0`
  (max points when the energy is an exact match, fewer as it drifts either way)
- **Acoustic preference** → +1.0 if `user.likes_acoustic` **and**
  `song.acousticness > 0.7`

The recommender **scores** every song this way, then **ranks** them
high-to-low and returns the top `k`.

### Potential biases I expect

Because the weights are hand-chosen, the system has built-in blind spots:

- **Over-prioritizes genre.** At +3.0, genre outweighs every other signal, so a
  great song that nails the user's mood and energy but sits in a different genre
  can get buried — the recommender rarely helps a user discover across genres.
- **Punishes sparsely-labeled genres.** Exact-string genre matching means niche
  or inconsistently-tagged genres (e.g. "indie pop" vs "pop") never match and
  are effectively invisible, which can systematically under-serve certain
  artists.
- **Filter bubble by design.** It only ever rewards what the user already says
  they like, so it reinforces existing taste instead of broadening it.
- **Energy is the only "distance" feature.** Tempo, valence, and danceability
  are loaded but unused in scoring, so two very different songs with the same
  genre/mood/energy are treated as interchangeable.

### Features used in my simulation

**`Song`** uses:

- `id`, `title`, `artist` — identifiers / display
- `genre` — categorical (pop, lofi, rock, jazz, …)
- `mood` — categorical (happy, chill, intense, …)
- `energy` — numeric 0–1
- `tempo_bpm` — numeric (BPM)
- `valence` — numeric 0–1 (positivity)
- `danceability` — numeric 0–1
- `acousticness` — numeric 0–1

**`UserProfile`** uses:

- `favorite_genre` — the genre to match against
- `favorite_mood` — the mood to match against
- `target_energy` — the energy level the user wants (0–1)
- `likes_acoustic` — whether to reward acoustic songs

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Below is real output from `python -m src.main` for a **happy pop listener**
(`genre=pop, mood=happy, energy=0.8`):

```
Loaded songs: 20

====================================================
  TOP RECOMMENDATIONS
  Profile: genre=pop, mood=happy, energy=0.8
====================================================

1. Sunrise City - Neon Echo
   Score:   6.96
   Reasons: genre match (+3.0), mood match (+2.0), energy closeness (+1.96)

2. Gym Hero - Max Pulse
   Score:   4.74
   Reasons: genre match (+3.0), energy closeness (+1.74)

3. Rooftop Lights - Indigo Parade
   Score:   3.92
   Reasons: mood match (+2.0), energy closeness (+1.92)

4. Concrete Kings - Blocktape
   Score:   2.00
   Reasons: energy closeness (+2.00)

5. Golden Groove - The Funk Council
   Score:   1.96
   Reasons: energy closeness (+1.96)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Experiment: Weight Shift — double energy, halve genre

**The change** (in `src/recommender.py`, `score_song`): I doubled the energy
weight and halved the genre weight so the continuous energy feature — not the
categorical genre match — became the dominant signal:

| Signal | Before | After |
|--------|-------:|------:|
| Genre match | +3.0 | **+1.5** |
| Mood match | +2.0 | +2.0 |
| Energy closeness (multiplier) | ×2.0 | **×4.0** |
| Acoustic bonus | +1.0 | +1.0 |

**Math validity:** energy distance `abs(song.energy - target)` stays in `[0, 1]`
for valid inputs, so `(1 - d) × 4.0` stays in `[0, 4.0]` — no negatives, no
division, no domain errors. Max valid score = `1.5 + 2.0 + 4.0 + 1.0 = 8.5`
(was 8.0). Starter tests still pass (`2 passed`).

**What changed in the rankings (before → after):**

- **High-Energy Pop:** *Rooftop Lights* (genre `indie pop`, high energy + mood
  match) leapfrogged *Gym Hero* (true `pop`) into #2. A song that **isn't even
  the user's genre now outranks one that is**, because energy + mood beat the
  halved genre bonus.
- **Chill Lofi:** *Spacewalk Thoughts* (`ambient`) rose over *Focus Flow*
  (`lofi`) — again an **off-genre** track passing an on-genre one.
- **Deep Intense Rock:** top 3 unchanged (*Storm Runner* wins under both
  weightings), showing the shift only reorders results when energy and genre
  actually disagree.
- **Conflicting Vibes** (adversarial, `energy=0.95` + sad folk): the sad
  *Paper Boats* lead collapsed from **5.76 vs 2.00** to **5.02 vs 4.00** — the
  high-energy songs the user literally asked for nearly overtook it.

**More accurate, or just different?** *Mostly different, with one real
improvement.* For most normal users it just reshuffles neighbors, and it
**weakens genre loyalty** (arguably *less* accurate for someone who really only
wants pop). But it makes the system far more responsive to the *energy* a user
requests, which is a genuine improvement for **cross-genre discovery** and for
**conflicting profiles** — the Conflicting Vibes case now respects the stated
0.95 energy instead of burying it under category points. Net: energy sensitivity
is now the main driver, so this is a tunable trade-off between *taste loyalty*
(high genre weight) and *mood/energy discovery* (high energy weight), not a
strict accuracy win.

> The output snapshots below were captured **before** this experiment, with the
> original weights (genre +3.0, energy ×2.0).

---

## System Evaluation — User Profiles

`src/main.py` defines two groups of taste profiles and prints the top-5 for
each: three **normal** listeners, and five **adversarial / edge-case**
listeners designed (in a separate "System Evaluation" session) to try to *trick*
the scoring logic. Run everything with:

```bash
python -m src.main
```

### Normal profiles

**High-Energy Pop** (`genre=pop, mood=happy, energy=0.9, acoustic=False`)

```
============================================================
  PROFILE: High-Energy Pop
  Prefs: genre=pop, mood=happy, energy=0.9, acoustic=False
============================================================

1. Sunrise City - Neon Echo
   Score:   6.84
   Reasons: genre match (+3.0), mood match (+2.0), energy closeness (+1.84)

2. Gym Hero - Max Pulse
   Score:   4.94
   Reasons: genre match (+3.0), energy closeness (+1.94)

3. Rooftop Lights - Indigo Parade
   Score:   3.72
   Reasons: mood match (+2.0), energy closeness (+1.72)

4. Deep Signal - Subframe
   Score:   2.00
   Reasons: energy closeness (+2.00)

5. Storm Runner - Voltline
   Score:   1.98
   Reasons: energy closeness (+1.98)
```

**Chill Lofi** (`genre=lofi, mood=chill, energy=0.35, acoustic=True`)

```
============================================================
  PROFILE: Chill Lofi
  Prefs: genre=lofi, mood=chill, energy=0.35, acoustic=True
============================================================

1. Library Rain - Paper Lanterns
   Score:   8.00
   Reasons: genre match (+3.0), mood match (+2.0), energy closeness (+2.00), acoustic match (+1.0)

2. Midnight Coding - LoRoom
   Score:   7.86
   Reasons: genre match (+3.0), mood match (+2.0), energy closeness (+1.86), acoustic match (+1.0)

3. Focus Flow - LoRoom
   Score:   5.90
   Reasons: genre match (+3.0), energy closeness (+1.90), acoustic match (+1.0)

4. Spacewalk Thoughts - Orbit Bloom
   Score:   4.86
   Reasons: mood match (+2.0), energy closeness (+1.86), acoustic match (+1.0)

5. Coffee Shop Stories - Slow Stereo
   Score:   2.96
   Reasons: energy closeness (+1.96), acoustic match (+1.0)
```

**Deep Intense Rock** (`genre=rock, mood=intense, energy=0.9, acoustic=False`)

```
============================================================
  PROFILE: Deep Intense Rock
  Prefs: genre=rock, mood=intense, energy=0.9, acoustic=False
============================================================

1. Storm Runner - Voltline
   Score:   6.98
   Reasons: genre match (+3.0), mood match (+2.0), energy closeness (+1.98)

2. Gym Hero - Max Pulse
   Score:   3.94
   Reasons: mood match (+2.0), energy closeness (+1.94)

3. Deep Signal - Subframe
   Score:   2.00
   Reasons: energy closeness (+2.00)

4. Neon Overdrive - Pulsewave
   Score:   1.90
   Reasons: energy closeness (+1.90)

5. Iron Verdict - Ashfall
   Score:   1.84
   Reasons: energy closeness (+1.84)
```

### Adversarial / edge-case profiles

These profiles were generated in a dedicated "System Evaluation" session by
asking the AI assistant to design listeners that could break or confuse the
scoring rule. See [Section 7 of the model card](model_card.md) for the analysis
of *why* each one behaves the way it does.

**1. Conflicting Vibes** — high energy (0.95) but a sad, low-energy folk mood.

```
============================================================
  PROFILE: Conflicting Vibes (high energy + sad mood)
  Prefs: genre=folk, mood=melancholy, energy=0.95, acoustic=False
============================================================

1. Paper Boats - Wren Halloway
   Score:   5.76
   Reasons: genre match (+3.0), mood match (+2.0), energy closeness (+0.76)

2. Neon Overdrive - Pulsewave
   Score:   2.00
   Reasons: energy closeness (+2.00)

3. Gym Hero - Max Pulse
   Score:   1.96
   Reasons: energy closeness (+1.96)

4. Iron Verdict - Ashfall
   Score:   1.94
   Reasons: energy closeness (+1.94)

5. Storm Runner - Voltline
   Score:   1.92
   Reasons: energy closeness (+1.92)
```

**2. Impossible Acoustic Raver** — wants the acoustic bonus AND high-energy EDM.

```
============================================================
  PROFILE: Impossible Acoustic Raver (acoustic + EDM)
  Prefs: genre=edm, mood=euphoric, energy=0.98, acoustic=True
============================================================

1. Neon Overdrive - Pulsewave
   Score:   6.94
   Reasons: genre match (+3.0), mood match (+2.0), energy closeness (+1.94)

2. Iron Verdict - Ashfall
   Score:   2.00
   Reasons: energy closeness (+2.00)

3. Gym Hero - Max Pulse
   Score:   1.90
   Reasons: energy closeness (+1.90)

4. Midnight Coding - LoRoom
   Score:   1.88
   Reasons: energy closeness (+0.88), acoustic match (+1.0)

5. Storm Runner - Voltline
   Score:   1.86
   Reasons: energy closeness (+1.86)
```

**3. Ghost Genre** — `genre=k-pop` / `mood=dreamy`, neither in the catalog.

```
============================================================
  PROFILE: Ghost Genre (values not in the catalog)
  Prefs: genre=k-pop, mood=dreamy, energy=0.5, acoustic=False
============================================================

1. Velvet Hours - Mara Soul
   Score:   2.00
   Reasons: energy closeness (+2.00)

2. Dusty Backroads - The Copperlines
   Score:   1.90
   Reasons: energy closeness (+1.90)

3. Midnight Coding - LoRoom
   Score:   1.84
   Reasons: energy closeness (+1.84)

4. Focus Flow - LoRoom
   Score:   1.80
   Reasons: energy closeness (+1.80)

5. Island Time - Sunroots
   Score:   1.76
   Reasons: energy closeness (+1.76)
```

**4. Out-of-Range Energy** — `target_energy=2.0` (outside the valid 0–1 range).

```
============================================================
  PROFILE: Out-of-Range Energy (target_energy = 2.0)
  Prefs: genre=pop, mood=happy, energy=2.0, acoustic=False
============================================================

1. Sunrise City - Neon Echo
   Score:   4.64
   Reasons: genre match (+3.0), mood match (+2.0), energy closeness (+-0.36)

2. Gym Hero - Max Pulse
   Score:   2.86
   Reasons: genre match (+3.0), energy closeness (+-0.14)

3. Rooftop Lights - Indigo Parade
   Score:   1.52
   Reasons: mood match (+2.0), energy closeness (+-0.48)

4. Iron Verdict - Ashfall
   Score:   -0.04
   Reasons: energy closeness (+-0.04)

5. Neon Overdrive - Pulsewave
   Score:   -0.10
   Reasons: energy closeness (+-0.10)
```

**5. Case Mismatch Trick** — `genre='Pop'` / `mood='Happy'` (capitalized).

```
============================================================
  PROFILE: Case Mismatch Trick ('Pop' vs 'pop')
  Prefs: genre=Pop, mood=Happy, energy=0.8, acoustic=False
============================================================

1. Concrete Kings - Blocktape
   Score:   2.00
   Reasons: energy closeness (+2.00)

2. Sunrise City - Neon Echo
   Score:   1.96
   Reasons: energy closeness (+1.96)

3. Golden Groove - The Funk Council
   Score:   1.96
   Reasons: energy closeness (+1.96)

4. Rooftop Lights - Indigo Parade
   Score:   1.92
   Reasons: energy closeness (+1.92)

5. Night Drive Loop - Neon Echo
   Score:   1.90
   Reasons: energy closeness (+1.90)
```

---

## Limitations and Risks

- **Tiny catalog.** Only 20 songs, and most genres have just one song.
- **No real understanding.** It matches labels only — no lyrics, language, or how
  a song actually sounds.
- **Favors high energy.** The catalog leans loud, so the same high-energy songs
  keep showing up for many users.
- **Brittle inputs.** A capital letter ("Pop" vs "pop") or an out-of-range energy
  value silently breaks the results.

I go deeper on these in the [model card](model_card.md).

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)



