from django.shortcuts import render
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def home(request):
    recommended_movies = []
    # This grabs the movie name the user types into the search box
    search_query = request.GET.get('movie_name') 

    if search_query:
        try:
            # 1. Load your movie list
            df = pd.read_csv('movies.csv')

            # 2. Math: Convert descriptions into numbers (TF-IDF)
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(df['description'])

            # 3. Math: Calculate which movies are most similar
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

            # 4. Find the movie the user typed in your CSV
            idx = df[df['title'].str.contains(search_query, case=False)].index[0]
            
            # 5. Get the top 3 similar movies
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            movie_indices = [i[0] for i in sim_scores[1:4]] 
            recommended_movies = df['title'].iloc[movie_indices].tolist()
            
        except Exception:
            # If they type a movie name that isn't in your CSV
            recommended_movies = ["Movie not found. Try 'Inception' or 'The Matrix'!"]

    return render(request, 'movie_engine/index.html', {'movies': recommended_movies})