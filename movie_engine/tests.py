import csv
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings

from .recommender import (
	build_artifacts,
	clear_recommender_cache,
	load_artifacts,
	recommend_titles,
)


class RecommenderTests(TestCase):
	def setUp(self):
		clear_recommender_cache()

	def test_recommend_titles_returns_results_and_excludes_self(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			csv_path = Path(tmpdir) / "movies.csv"
			artifacts_dir = Path(tmpdir) / "artifacts"
			with csv_path.open("w", newline="", encoding="utf-8") as f:
				writer = csv.DictWriter(f, fieldnames=["title", "description"])
				writer.writeheader()
				writer.writerow(
					{
						"title": "Toy Story",
						"description": "toys come to life when humans leave",
					}
				)
				writer.writerow(
					{
						"title": "Toy Soldiers",
						"description": "soldiers in a toy box come to life",
					}
				)
				writer.writerow(
					{
						"title": "The Matrix",
						"description": "a hacker learns the true nature of reality",
					}
				)

				build_artifacts(str(csv_path), artifacts_dir)
				artifacts = load_artifacts(str(artifacts_dir))
				self.assertGreaterEqual(len(artifacts.titles), 3)

				results = recommend_titles(
					str(csv_path), "Toy Story", k=2, artifacts_dir=str(artifacts_dir)
				)
			self.assertLessEqual(len(results), 2)
			self.assertNotIn("Toy Story", results)

	def test_recommend_titles_empty_when_not_found(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			csv_path = Path(tmpdir) / "movies.csv"
			artifacts_dir = Path(tmpdir) / "artifacts"
			with csv_path.open("w", newline="", encoding="utf-8") as f:
				writer = csv.DictWriter(f, fieldnames=["title", "description"])
				writer.writeheader()
				writer.writerow({"title": "Inception", "description": "dream heist"})

			build_artifacts(str(csv_path), artifacts_dir)
			results = recommend_titles(
				str(csv_path), "No Such Movie", k=4, artifacts_dir=str(artifacts_dir)
			)
			self.assertEqual(results, [])


class HomeViewTests(TestCase):
	def _fake_details(self, title: str):
		return {
			"title": title,
			"poster": "https://example.com/poster.jpg",
			"rating": "N/A",
			"year": "Unknown",
			"genre": "Movie",
		}

	@override_settings(MOVIES_CSV_PATH="/tmp/movies.csv")
	@patch("movie_engine.views.search_titles")
	@patch("movie_engine.views.fetch_movie_details")
	@patch("movie_engine.views.recommend_titles_with_scores")
	@patch("movie_engine.views.pick_trending_titles")
	def test_home_with_results(
		self, mock_pick_trending, mock_recommend_scored, mock_fetch_details, mock_search_titles
	):
		mock_pick_trending.return_value = ["A", "B", "C", "D"]
		mock_recommend_scored.return_value = [("X", 0.9), ("Y", 0.8)]
		mock_search_titles.return_value = ["R1", "R2"]
		mock_fetch_details.side_effect = self._fake_details

		response = self.client.get("/", {"movie_name": "Inception"})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["query"], "Inception")
		self.assertIsNone(response.context["error_message"])
		self.assertEqual(len(response.context["trending"]), 4)
		self.assertEqual(len(response.context["recommendations"]), 2)
		self.assertEqual(len(response.context["search_results"]), 2)

	@override_settings(MOVIES_CSV_PATH="/tmp/movies.csv")
	@patch("movie_engine.views.search_titles")
	@patch("movie_engine.views.fetch_movie_details")
	@patch("movie_engine.views.recommend_titles_with_scores")
	@patch("movie_engine.views.pick_trending_titles")
	def test_home_no_results_sets_error_message(
		self, mock_pick_trending, mock_recommend_scored, mock_fetch_details, mock_search_titles
	):
		mock_pick_trending.return_value = ["A", "B", "C", "D"]
		mock_recommend_scored.return_value = []
		mock_search_titles.return_value = []
		mock_fetch_details.side_effect = self._fake_details

		response = self.client.get("/", {"movie_name": "Unknown Movie"})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["query"], "Unknown Movie")
		self.assertIsNotNone(response.context["error_message"])
		self.assertEqual(response.context["recommendations"], [])
		self.assertEqual(response.context["search_results"], [])
