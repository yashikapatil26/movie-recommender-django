from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import Normalizer


@dataclass(frozen=True)
class RecommenderArtifacts:
    titles: list[str]
    vectorizer: TfidfVectorizer
    svd: TruncatedSVD | None
    feature_matrix: Any
    nn_model: NearestNeighbors


ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACT_VECTOR = "tfidf_vectorizer.joblib"
ARTIFACT_SVD = "svd.joblib"
ARTIFACT_MATRIX = "feature_matrix.joblib"
ARTIFACT_NN = "nn_model.joblib"
ARTIFACT_TITLES = "titles.joblib"


def _normalize_query(query: str | None) -> str:
    return (query or "").strip()


def _ensure_columns_for_dataset(df: pd.DataFrame) -> pd.DataFrame:
    if "title" not in df.columns:
        raise ValueError("movies dataset missing required column: title")

    if "description" not in df.columns:
        # best-effort discovery (supports common TMDB naming)
        candidates = [
            col
            for col in df.columns
            if col.lower() in {"overview", "description", "plot", "summary"}
        ]
        if candidates:
            df = df.rename(columns={candidates[0]: "description"})
        else:
            # Keep dataset usable for trending even if descriptions are missing.
            df = df.assign(description="")

    df = df[["title", "description"]].copy()
    df["title"] = df["title"].astype(str)
    df["description"] = df["description"].fillna("").astype(str)
    return df


def _build_feature_matrix(
    descriptions: pd.Series,
) -> tuple[TfidfVectorizer, TruncatedSVD | None, Any]:
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(descriptions)

    if tfidf_matrix.shape[0] < 2 or tfidf_matrix.shape[1] < 2:
        return vectorizer, None, tfidf_matrix

    max_components = min(200, tfidf_matrix.shape[0] - 1, tfidf_matrix.shape[1] - 1)
    if max_components < 2:
        return vectorizer, None, tfidf_matrix

    svd = TruncatedSVD(n_components=max_components, random_state=42)
    reduced_matrix = svd.fit_transform(tfidf_matrix)
    reduced_matrix = Normalizer(copy=False).fit_transform(reduced_matrix)
    return vectorizer, svd, reduced_matrix


def _resolve_artifacts_dir(artifacts_dir: str | Path | None) -> Path:
    return Path(artifacts_dir) if artifacts_dir else ARTIFACTS_DIR


@lru_cache(maxsize=8)
def get_movies_df(csv_path: str) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"movies dataset not found: {path}")

    df = pd.read_csv(path)
    df = _ensure_columns_for_dataset(df)

    return df


def build_artifacts(
    csv_path: str,
    artifacts_dir: str | Path | None = None,
) -> Path:
    df = get_movies_df(csv_path)
    vectorizer, svd, feature_matrix = _build_feature_matrix(df["description"])
    nn_model = NearestNeighbors(metric="cosine", algorithm="brute")
    nn_model.fit(feature_matrix)

    titles = df["title"].fillna("").astype(str).tolist()

    output_dir = _resolve_artifacts_dir(artifacts_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(vectorizer, output_dir / ARTIFACT_VECTOR)
    joblib.dump(svd, output_dir / ARTIFACT_SVD)
    joblib.dump(feature_matrix, output_dir / ARTIFACT_MATRIX)
    joblib.dump(nn_model, output_dir / ARTIFACT_NN)
    joblib.dump(titles, output_dir / ARTIFACT_TITLES)

    return output_dir


@lru_cache(maxsize=8)
def load_artifacts(artifacts_dir: str | Path | None = None) -> RecommenderArtifacts:
    artifacts_path = _resolve_artifacts_dir(artifacts_dir)
    vectorizer_path = artifacts_path / ARTIFACT_VECTOR
    matrix_path = artifacts_path / ARTIFACT_MATRIX
    nn_path = artifacts_path / ARTIFACT_NN
    titles_path = artifacts_path / ARTIFACT_TITLES

    missing = [
        path
        for path in (vectorizer_path, matrix_path, nn_path, titles_path)
        if not path.exists()
    ]
    if missing:
        missing_list = ", ".join(path.name for path in missing)
        raise FileNotFoundError(
            "Recommender artifacts missing: "
            f"{missing_list}. Run 'python manage.py build_recommender'."
        )

    vectorizer = joblib.load(vectorizer_path)
    svd_path = artifacts_path / ARTIFACT_SVD
    svd = joblib.load(svd_path) if svd_path.exists() else None
    feature_matrix = joblib.load(matrix_path)
    nn_model = joblib.load(nn_path)
    titles = joblib.load(titles_path)

    return RecommenderArtifacts(
        titles=titles,
        vectorizer=vectorizer,
        svd=svd,
        feature_matrix=feature_matrix,
        nn_model=nn_model,
    )


def _find_best_match_index(titles: list[str], query: str) -> int | None:
    if not query:
        return None

    query_lower = query.lower()

    # Prefer exact match first (case-insensitive)
    for idx, title in enumerate(titles):
        if title.lower() == query_lower:
            return idx

    # Fallback: contains match
    for idx, title in enumerate(titles):
        if query_lower in title.lower():
            return idx

    return None


def recommend_titles(
    csv_path: str,
    query: str | None,
    k: int = 4,
    artifacts_dir: str | Path | None = None,
) -> list[str]:
    scored = recommend_titles_with_scores(
        csv_path, query, k=k, artifacts_dir=artifacts_dir
    )
    return [title for title, _ in scored]


def recommend_titles_with_scores(
    csv_path: str,
    query: str | None,
    k: int = 4,
    artifacts_dir: str | Path | None = None,
) -> list[tuple[str, float]]:
    """Return up to k recommended titles with cosine similarity scores.

    Similarity is in the range [0, 1], where 1 means most similar.
    """

    q = _normalize_query(query)
    if not q:
        return []

    state = load_artifacts(artifacts_dir)
    titles = state.titles

    if len(titles) < 2:
        return []

    idx = _find_best_match_index(titles, q)
    if idx is None:
        return []

    # Use the nearest-neighbors model to fetch closest titles.
    neighbor_count = min(k + 1, len(titles))
    distances, ranked = state.nn_model.kneighbors(
        state.feature_matrix[idx : idx + 1], n_neighbors=neighbor_count
    )
    ranked = ranked.ravel().tolist()
    distances = distances.ravel().tolist()

    results: list[tuple[str, float]] = []
    for row_index, distance in zip(ranked, distances, strict=False):
        if int(row_index) == int(idx):
            continue
        title = str(titles[int(row_index)]).strip()
        if not title:
            continue

        # cosine distance in [0, 2] but with normalized vectors typically [0, 1]
        similarity = 1.0 - float(distance)
        # Clamp to avoid negative values from numerical noise.
        similarity = max(0.0, min(1.0, similarity))
        results.append((title, similarity))
        if len(results) >= k:
            break

    return results


def _dedupe_titles(
    titles: list[str],
    exclude: set[str] | list[str] | None = None,
) -> list[str]:
    exclude_keys = {t.lower() for t in (exclude or []) if t}
    seen: set[str] = set()
    results: list[str] = []
    for title in titles:
        normalized = (title or "").strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in exclude_keys or key in seen:
            continue
        seen.add(key)
        results.append(normalized)
    return results


def search_titles(
    csv_path: str,
    query: str | None,
    max_results: int = 10,
    fuzzy_results: int = 8,
    exclude: list[str] | set[str] | None = None,
) -> list[str]:
    q = _normalize_query(query)
    if not q:
        return []

    df = get_movies_df(csv_path)
    titles = df["title"].fillna("").astype(str)

    substring_hits = titles[titles.str.contains(q, case=False, na=False)].tolist()
    results = _dedupe_titles(substring_hits, exclude)
    if results:
        return results[:max_results]

    candidates = titles.tolist()
    fuzzy_hits = get_close_matches(q, candidates, n=fuzzy_results, cutoff=0.6)
    return _dedupe_titles(fuzzy_hits, exclude)[:max_results]


def pick_trending_titles(csv_path: str, n: int = 4) -> list[str]:
    df = get_movies_df(csv_path)
    titles = df["title"].dropna().astype(str)
    titles = titles[titles.str.strip() != ""]

    if titles.empty:
        return []

    count = min(int(n), int(len(titles)))
    if count <= 0:
        return []

    return titles.sample(count).tolist()


def clear_recommender_cache() -> None:
    get_movies_df.cache_clear()
    load_artifacts.cache_clear()
