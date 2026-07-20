"""
Command line runner for the Music Recommender Simulation.

This file runs the recommender against a set of *user taste profiles* and
prints the top-k recommendations for each one.

Two groups of profiles are defined:

  1. NORMAL profiles      - well-formed, "realistic" listeners.
  2. ADVERSARIAL profiles - deliberately tricky / edge-case listeners used for
                            System Evaluation. These are designed to see whether
                            the scoring logic can be "tricked" or produces
                            unexpected results (conflicting preferences,
                            out-of-catalog values, out-of-range numbers, and
                            case-sensitivity traps).

The scoring functions live in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

# Support both `python -m src.main` (run from project root) and
# `python src/main.py` (run with src/ on the path).
try:
    from src.recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    from recommender import load_songs, recommend_songs


# --- NORMAL profiles: three distinct, well-formed listeners ------------------
NORMAL_PROFILES = [
    {
        "name": "High-Energy Pop",
        "why": "A mainstream listener who wants upbeat, high-energy pop.",
        "prefs": {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.90,
            "likes_acoustic": False,
        },
    },
    {
        "name": "Chill Lofi",
        "why": "A study/relax listener who wants calm, acoustic lofi.",
        "prefs": {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.35,
            "likes_acoustic": True,
        },
    },
    {
        "name": "Deep Intense Rock",
        "why": "A listener who wants driving, high-intensity rock.",
        "prefs": {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.90,
            "likes_acoustic": False,
        },
    },
]


# --- ADVERSARIAL / edge-case profiles: "System Evaluation" -------------------
# Each profile targets a specific weakness in the scoring rule.
ADVERSARIAL_PROFILES = [
    {
        "name": "Conflicting Vibes (high energy + sad mood)",
        "why": (
            "Asks for very high energy (0.95) but a melancholy folk mood. "
            "Melancholy folk songs are inherently low-energy, so the mood match "
            "and the energy target actively fight each other."
        ),
        "prefs": {
            "favorite_genre": "folk",
            "favorite_mood": "melancholy",
            "target_energy": 0.95,
            "likes_acoustic": False,
        },
    },
    {
        "name": "Impossible Acoustic Raver (acoustic + EDM)",
        "why": (
            "Wants the acoustic bonus AND high-energy EDM. EDM tracks have "
            "acousticness near 0, so the +1.0 acoustic bonus can NEVER fire "
            "for the user's favorite genre - a self-contradicting preference."
        ),
        "prefs": {
            "favorite_genre": "edm",
            "favorite_mood": "euphoric",
            "target_energy": 0.98,
            "likes_acoustic": True,
        },
    },
    {
        "name": "Ghost Genre (values not in the catalog)",
        "why": (
            "favorite_genre='k-pop' and favorite_mood='dreamy' do not exist in "
            "the dataset, so genre/mood points can never be earned. Only energy "
            "closeness decides the ranking - tests graceful degradation."
        ),
        "prefs": {
            "favorite_genre": "k-pop",
            "favorite_mood": "dreamy",
            "target_energy": 0.50,
            "likes_acoustic": False,
        },
    },
    {
        "name": "Out-of-Range Energy (target_energy = 2.0)",
        "why": (
            "target_energy=2.0 is outside the valid 0-1 range. The energy "
            "formula (1 - abs(energy - target)) * 2 is NOT clamped, so it "
            "produces large NEGATIVE scores - an unvalidated-input edge case."
        ),
        "prefs": {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 2.00,
            "likes_acoustic": False,
        },
    },
    {
        "name": "Case Mismatch Trick ('Pop' vs 'pop')",
        "why": (
            "favorite_genre='Pop' and favorite_mood='Happy' are capitalized. "
            "Scoring uses exact string equality, so these silently NEVER match "
            "the lowercase catalog values - a brittle-matching trap."
        ),
        "prefs": {
            "favorite_genre": "Pop",
            "favorite_mood": "Happy",
            "target_energy": 0.80,
            "likes_acoustic": False,
        },
    },
]


def print_recommendations(profile: dict, songs: list, k: int = 5) -> None:
    """Print the top-k recommendations for a single named profile."""
    prefs = profile["prefs"]

    print("\n" + "=" * 60)
    print(f"  PROFILE: {profile['name']}")
    print(
        f"  Prefs: genre={prefs['favorite_genre']}, "
        f"mood={prefs['favorite_mood']}, "
        f"energy={prefs['target_energy']}, "
        f"acoustic={prefs['likes_acoustic']}"
    )
    print("=" * 60 + "\n")

    recommendations = recommend_songs(prefs, songs, k=k)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - {song['artist']}")
        print(f"   Score:   {score:.2f}")
        print(f"   Reasons: {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    print("\n" + "#" * 60)
    print("#  NORMAL PROFILES")
    print("#" * 60)
    for profile in NORMAL_PROFILES:
        print_recommendations(profile, songs, k=5)

    print("\n" + "#" * 60)
    print("#  ADVERSARIAL / EDGE-CASE PROFILES  (System Evaluation)")
    print("#" * 60)
    for profile in ADVERSARIAL_PROFILES:
        print_recommendations(profile, songs, k=5)


if __name__ == "__main__":
    main()
