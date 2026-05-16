from django.conf import settings
from django.shortcuts import render

from .omdb import fetch_movie_details
from .recommender import pick_trending_titles, recommend_titles_with_scores, search_titles


def home(request):
    csv_path = str(getattr(settings, "MOVIES_CSV_PATH", settings.BASE_DIR / "movies.csv"))

    trending_titles = pick_trending_titles(csv_path, n=4)
    trending_movies = [fetch_movie_details(t) for t in trending_titles]

    recommendations: list[dict[str, str]] = []
    search_results: list[dict[str, str]] = []
    error_message: str | None = None
    search_query = (request.GET.get("movie_name") or "").strip()

    if search_query:
        scored_recommendations = recommend_titles_with_scores(csv_path, search_query, k=4)
        recommended_titles = [title for title, _ in scored_recommendations]
        search_titles_list = search_titles(
            csv_path,
            search_query,
            max_results=10,
            exclude=recommended_titles,
        )

        if scored_recommendations:
            recommendations = []
            for title, similarity in scored_recommendations:
                details = fetch_movie_details(title)
                # Make score always truthy so template `{% if movie.match_score %}` renders.
                details["match_score"] = f"{round(similarity * 100):d}%"
                recommendations.append(details)
        if search_titles_list:
            search_results = [fetch_movie_details(t) for t in search_titles_list]

        if not recommendations and not search_results:
            error_message = "No matches found. Try another title."

    return render(request, 'movie_engine/index.html', {
        'trending': trending_movies,
        'recommendations': recommendations,
        'search_results': search_results,
        'query': search_query,
        'error_message': error_message,
    })
