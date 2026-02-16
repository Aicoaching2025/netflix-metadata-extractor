"""
Netflix Metadata Extractor - Main Application

Usage:
    python app.py test        # Test on 5 descriptions
    python app.py evaluate    # Run full evaluation
    python app.py extract     # Extract single description (interactive)
"""
import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from src.extractor import NetflixExtractor
from src.evaluation import run_evaluation


# --- Configuration ---
DATA_PATH = "/Users/candace/.cache/kagglehub/datasets/rohitgrewal/netflix-data/versions/1"
CSV_FILE = "Netflix Dataset.csv"
API_KEY = os.getenv("ANTHROPIC_API_KEY")


def load_data() -> pd.DataFrame:
    """Load the Netflix dataset."""
    filepath = os.path.join(DATA_PATH, CSV_FILE)
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows from dataset.")
    return df


def test_extraction():
    """Test the extractor on 5 sample descriptions."""
    if not API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY in your .env file")
        return

    df = load_data()
    extractor = NetflixExtractor(api_key=API_KEY)

    # Pick 5 diverse samples
    samples = df[["Title", "Description"]].dropna().head(5)
    items = [
        {"title": row["Title"], "description": row["Description"]}
        for _, row in samples.iterrows()
    ]

    print("\n--- Testing on 5 descriptions ---\n")
    results = extractor.extract_batch(items)

    # Print results
    for r in results:
        print(f"\n{'='*50}")
        print(f"Title: {r['title']}")
        print(f"Description: {r['description'][:100]}...")
        if r["success"]:
            m = r["metadata"]
            print(f"Genres: {m.genres}")
            print(f"Themes: {m.themes}")
            print(f"Mood: {m.mood}")
            print(f"Audience: {m.target_audience}")
            print(f"Warnings: {m.content_warnings}")
            print(f"Retries: {r['retries']}")
        else:
            print(f"FAILED: {r['error']}")

    # Summary
    successes = sum(1 for r in results if r["success"])
    print(f"\n--- Results: {successes}/{len(results)} successful ---")


def run_full_evaluation():
    """Run the full evaluation pipeline."""
    if not API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY in your .env file")
        return

    # Import ground truth annotations
    sys.path.insert(0, ".")
    from data.ground_truth import annotations

    df = load_data()
    extractor = NetflixExtractor(api_key=API_KEY)

    report = run_evaluation(
        extractor=extractor,
        df=df,
        annotations=annotations,
        n_samples=50,
        save_report=True
    )

    return report


def extract_single():
    """Interactive mode: extract metadata for a single description."""
    if not API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY in your .env file")
        return

    extractor = NetflixExtractor(api_key=API_KEY)

    print("Enter a movie/show description (or 'quit' to exit):")
    while True:
        description = input("\n> ")
        if description.lower() in ("quit", "exit", "q"):
            break

        result = extractor.extract(description)
        if result["success"]:
            m = result["metadata"]
            print(f"\nGenres: {m.genres}")
            print(f"Themes: {m.themes}")
            print(f"Mood: {m.mood}")
            print(f"Audience: {m.target_audience}")
            print(f"Warnings: {m.content_warnings}")
        else:
            print(f"Error: {result['error']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "test":
        test_extraction()
    elif command == "evaluate":
        run_full_evaluation()
    elif command == "extract":
        extract_single()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)