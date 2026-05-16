from django.shortcuts import render
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import random

# --- CONFIGURATION ---
API_KEY = '5086ae93' # <--- Put your OMDb key here!

def get_movie_details(movie_title):
    """Fetches posters and metadata from OMDb API"""
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    try:
        data = requests.get(url).json()
        poster = data.get('Poster')
        
        # Use a high-quality placeholder if the API has no image
        if not poster or poster == "N/A":
            poster = "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=300&h=450&auto=format&fit=crop"
            
        return {
            'title': movie_title,
            'poster': poster,
            'rating': data.get('imdbRating', 'N/A'),
            'year': data.get('Year', 'Unknown'),
            'genre': data.get('Genre', 'Movie').split(',')[0]
        }
    except:
        return {'title': movie_title, 'poster': '', 'rating': 'N/A', 'year': '', 'genre': ''}

def home(request):
    df = pd.read_csv('movies.csv')
    
    # 1. Improved Trending: Pick 4 varied movies for the dashboard
    trending_movies = [get_movie_details(t) for t in df['title'].sample(4).tolist()]
    
    recommendations = []
    search_query = request.GET.get('movie_name')

    if search_query:
        # We search the description for the movie title entered
        match = df[df['title'].str.contains(search_query, case=False)]
        
        if not match.empty:
            idx = match.index[0]
            
            # The AI Logic
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(df['description'])
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Get top 4 results (skipping the first one as it's the movie itself)
            for i in sim_scores[1:5]:
                movie_title = df['title'].iloc[i[0]]
                recommendations.append(get_movie_details(movie_title))
        else:
            # If movie not found, we can show a message or random picks
            print("Movie not found in the 5k dataset")

    return render(request, 'movie_engine/index.html', {
        'trending': trending_movies,
        'recommendations': recommendations,
        'query': search_query
    })