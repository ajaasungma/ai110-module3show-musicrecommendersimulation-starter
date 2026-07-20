import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file into a list of dictionaries.

    Numeric columns are converted from text to numbers so later scoring
    logic can do math on them:
      - id -> int
      - energy, tempo_bpm, valence, danceability, acousticness -> float
    The remaining columns (title, artist, genre, mood) stay as strings.

    Required by src/main.py
    """
    int_fields = {"id"}
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = dict(row)
            for field in int_fields:
                song[field] = int(song[field])
            for field in float_fields:
                song[field] = float(song[field])
            songs.append(song)

    print(f"Loaded songs: {len(songs)}")
    return songs

# --- Scoring weights ---------------------------------------------------------
# EXPERIMENT (sensitivity test): "Weight Shift" -> double the importance of
# energy and halve the importance of genre, to see how much the rankings depend
# on the continuous energy feature vs. the categorical genre match.
#   Genre:  3.0 -> 1.5  (halved)
#   Energy: x2.0 -> x4.0 (doubled)
# Math check: energy distance abs(song.energy - target) stays in [0, 1] for
# valid inputs, so (1 - d) * 4.0 stays in [0, 4.0] (no negatives, no division).
# Max valid score = 1.5 + 2.0 + 4.0 + 1.0 = 8.5.
GENRE_WEIGHT = 1.5     # was 3.0
MOOD_WEIGHT = 2.0      # unchanged
ENERGY_WEIGHT = 4.0    # was 2.0
ACOUSTIC_WEIGHT = 1.0  # unchanged


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences using the Algorithm Recipe.

    Scoring rule (see README "How The System Works"), Weight Shift experiment:
      - Genre match       -> +1.5 if song genre == favorite_genre   (halved)
      - Mood match        -> +2.0 if song mood  == favorite_mood
      - Energy closeness  -> (1 - abs(song.energy - target_energy)) * 4.0 (doubled)
      - Acoustic bonus    -> +1.0 if likes_acoustic and acousticness > 0.7

    Returns (score, reasons) where reasons explains where the points came from.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons: List[str] = []

    # Genre match (halved: no longer the dominant signal)
    if song["genre"] == user_prefs["favorite_genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT:.1f})")

    # Mood match (a modifier)
    if song["mood"] == user_prefs["favorite_mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT:.1f})")

    # Energy closeness (doubled): max points at an exact match, fewer as it drifts.
    energy_points = (1 - abs(song["energy"] - user_prefs["target_energy"])) * ENERGY_WEIGHT
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    # Acoustic preference bonus
    if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.7:
        score += ACOUSTIC_WEIGHT
        reasons.append(f"acoustic match (+{ACOUSTIC_WEIGHT:.1f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # 1. JUDGE: score every song in the catalog, building (song, score, explanation).
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))

    # 2. RANK: sort highest score first. sorted() returns a NEW list and leaves
    #    the caller's `songs` untouched; item[1] is the numeric score.
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    # 3. TOP-K: slice off the best k results.
    return ranked[:k]
