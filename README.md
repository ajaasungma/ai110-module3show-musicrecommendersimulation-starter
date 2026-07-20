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

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



