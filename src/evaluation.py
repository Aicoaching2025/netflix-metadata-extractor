import json
import pandas as pd
from datetime import datetime
from .schemas import ContentMetadata
from .extractor import NetflixExtractor


def schema_compliance_rate(results: list[dict]) -> float:
    """Calculate the % of extractions that passed Pydantic validation without retry."""
    if not results:
        return 0.0
    first_try_success = sum(1 for r in results if r["success"] and r["retries"] == 0)
    return first_try_success / len(results) * 100


def overall_success_rate(results: list[dict]) -> float:
    """Calculate the % of extractions that ultimately succeeded (with or without retry)."""
    if not results:
        return 0.0
    successes = sum(1 for r in results if r["success"])
    return successes / len(results) * 100


def retry_rate(results: list[dict]) -> float:
    """Calculate the % of extractions that needed at least one retry."""
    if not results:
        return 0.0
    retried = sum(1 for r in results if r["success"] and r["retries"] > 0)
    return retried / len(results) * 100


def genre_accuracy(results: list[dict], df: pd.DataFrame) -> dict:
    """
    Compare extracted genres against the dataset's 'Type' column.
    Returns accuracy metrics.
    """
    matches = 0
    total = 0
    details = []

    for result in results:
        if not result["success"]:
            continue

        title = result["title"]
        extracted_genres = [g.lower() for g in result["metadata"].genres]

        # Find the matching row in the dataframe
        row = df[df["Title"] == title]
        if row.empty:
            continue

        actual_type = row.iloc[0]["Type"].lower().strip()
        # Split on commas if multiple types are listed
        actual_genres = [g.strip().lower() for g in actual_type.split(",")]

        # Check if any extracted genre matches any actual genre
        overlap = set(extracted_genres) & set(actual_genres)
        has_match = len(overlap) > 0

        if has_match:
            matches += 1
        total += 1

        details.append({
            "title": title,
            "extracted": extracted_genres,
            "actual": actual_genres,
            "match": has_match
        })

    return {
        "accuracy": matches / total * 100 if total > 0 else 0.0,
        "matches": matches,
        "total": total,
        "details": details
    }


def manual_accuracy(results: list[dict], annotations: list[dict]) -> dict:
    """
    Compare extraction results against manually annotated ground truth.
    Returns per-field accuracy scores.
    """
    field_scores = {
        "genres": [],
        "themes": [],
        "mood": [],
        "target_audience": [],
        "content_warnings": []
    }

    comparison_details = []

    for annotation in annotations:
        title = annotation["title"]
        expected = annotation["expected"]

        # Find matching result
        result = next((r for r in results if r["title"] == title), None)
        if not result or not result["success"]:
            continue

        extracted = result["metadata"]

        # Genre overlap (Jaccard similarity)
        ext_genres = set(g.lower() for g in extracted.genres)
        exp_genres = set(g.lower() for g in expected.genres)
        if ext_genres or exp_genres:
            genre_score = len(ext_genres & exp_genres) / len(ext_genres | exp_genres)
        else:
            genre_score = 1.0
        field_scores["genres"].append(genre_score)

        # Theme overlap (Jaccard similarity)
        ext_themes = set(t.lower() for t in extracted.themes)
        exp_themes = set(t.lower() for t in expected.themes)
        if ext_themes or exp_themes:
            theme_score = len(ext_themes & exp_themes) / len(ext_themes | exp_themes)
        else:
            theme_score = 1.0
        field_scores["themes"].append(theme_score)

        # Mood (exact or partial match)
        mood_score = 1.0 if extracted.mood.lower() == expected.mood.lower() else 0.0
        field_scores["mood"].append(mood_score)

        # Target audience (exact match)
        audience_score = 1.0 if extracted.target_audience.lower() == expected.target_audience.lower() else 0.0
        field_scores["target_audience"].append(audience_score)

        # Content warnings overlap
        ext_warnings = set(w.lower() for w in extracted.content_warnings)
        exp_warnings = set(w.lower() for w in expected.content_warnings)
        if ext_warnings or exp_warnings:
            warning_score = len(ext_warnings & exp_warnings) / len(ext_warnings | exp_warnings)
        else:
            warning_score = 1.0
        field_scores["content_warnings"].append(warning_score)

        comparison_details.append({
            "title": title,
            "extracted": extracted.model_dump(),
            "expected": expected.model_dump(),
            "scores": {
                "genres": genre_score,
                "themes": theme_score,
                "mood": mood_score,
                "target_audience": audience_score,
                "content_warnings": warning_score
            }
        })

    # Calculate averages
    avg_scores = {}
    for field, scores in field_scores.items():
        avg_scores[field] = sum(scores) / len(scores) * 100 if scores else 0.0

    avg_scores["overall"] = sum(avg_scores.values()) / len(avg_scores)

    return {
        "average_scores": avg_scores,
        "details": comparison_details
    }


def run_evaluation(
    extractor: NetflixExtractor,
    df: pd.DataFrame,
    annotations: list[dict],
    n_samples: int = 50,
    save_report: bool = True
) -> dict:
    """
    Run a full evaluation pipeline.

    Args:
        extractor: NetflixExtractor instance
        df: Netflix DataFrame
        annotations: List of manual annotations
        n_samples: Number of random descriptions to evaluate
        save_report: Whether to save the report to a file
    """
    print("=" * 60)
    print("NETFLIX METADATA EXTRACTION - EVALUATION REPORT")
    print("=" * 60)

    # --- Part 1: Run on annotated examples ---
    print("\n--- Evaluating on annotated examples ---")
    annotated_items = [
        {"title": a["title"], "description": a["description"]}
        for a in annotations
    ]
    annotated_results = extractor.extract_batch(annotated_items)

    # --- Part 2: Run on random sample ---
    print(f"\n--- Evaluating on {n_samples} random descriptions ---")
    sample_df = df[["Title", "Description", "Type"]].dropna().sample(n=n_samples, random_state=42)
    sample_items = [
        {"title": row["Title"], "description": row["Description"]}
        for _, row in sample_df.iterrows()
    ]
    sample_results = extractor.extract_batch(sample_items)

    # --- Calculate Metrics ---
    all_results = annotated_results + sample_results

    print("\n" + "=" * 60)
    print("METRICS SUMMARY")
    print("=" * 60)

    # Schema compliance
    compliance = schema_compliance_rate(all_results)
    print(f"\nSchema Compliance (1st try): {compliance:.1f}%")

    # Overall success
    success = overall_success_rate(all_results)
    print(f"Overall Success Rate:        {success:.1f}%")

    # Retry rate
    retries = retry_rate(all_results)
    print(f"Retry Rate:                  {retries:.1f}%")

    # Genre accuracy against dataset
    genre_acc = genre_accuracy(sample_results, df)
    print(f"Genre Match (vs dataset):    {genre_acc['accuracy']:.1f}%")

    # Manual accuracy on annotated examples
    manual_acc = manual_accuracy(annotated_results, annotations)
    print(f"\nManual Annotation Accuracy (per field):")
    for field, score in manual_acc["average_scores"].items():
        print(f"  {field:20s}: {score:.1f}%")

    # --- Failure Analysis ---
    failures = [r for r in all_results if not r["success"]]
    if failures:
        print(f"\n--- Failure Analysis ({len(failures)} failures) ---")
        for f in failures:
            print(f"  Title: {f.get('title', 'N/A')}")
            print(f"  Error: {f['error']}")
            print()

    # --- Build Report ---
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_samples": len(all_results),
        "metrics": {
            "schema_compliance_first_try": compliance,
            "overall_success_rate": success,
            "retry_rate": retries,
            "genre_accuracy": genre_acc["accuracy"],
            "manual_accuracy": manual_acc["average_scores"]
        },
        "failure_count": len(failures),
        "failures": [
            {"title": f.get("title"), "error": f["error"]} for f in failures
        ]
    }

    if save_report:
        report_path = "data/evaluation_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to {report_path}")

    return report