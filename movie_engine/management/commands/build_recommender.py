from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from movie_engine.recommender import build_artifacts


class Command(BaseCommand):
    help = "Build recommender artifacts for offline loading."

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            dest="csv_path",
            default=None,
            help="Path to movies.csv (defaults to settings.MOVIES_CSV_PATH or project root).",
        )
        parser.add_argument(
            "--artifacts-dir",
            dest="artifacts_dir",
            default=None,
            help="Directory to write artifacts (defaults to movie_engine/artifacts).",
        )

    def handle(self, *args, **options):
        csv_path = options.get("csv_path")
        if not csv_path:
            csv_path = getattr(
                settings,
                "MOVIES_CSV_PATH",
                settings.BASE_DIR / "movies.csv",
            )
        artifacts_dir = options.get("artifacts_dir")

        output_dir = build_artifacts(str(csv_path), artifacts_dir=artifacts_dir)
        self.stdout.write(
            self.style.SUCCESS(f"Recommender artifacts built at {Path(output_dir)}")
        )
