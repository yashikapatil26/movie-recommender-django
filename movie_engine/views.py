from django.shortcuts import render
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

API_KEY = '5086ae93'

def get_poster(movie_title):
    # This reaches out to OMDb to grab the image URL
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    try:
        data = requests.get(url).json()
        return data.get('Poster', 'https://via.placeholder.com/300x450?text=No+Poster')
    except:
        return 'https://via.placeholder.com/300x450?text=Error'

def home(request):
    recommended_movies = []
    search_query = request.GET.get('movie_name')

    if search_query:
        try:
            df = pd.read_csv('movies.csv')
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(df['description'])
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

            idx = df[df['title'].str.contains(search_query, case=False)].index[0]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            for i in sim_scores[1:4]:
                title = df['title'].iloc[i[0]]
                poster_url = get_poster(title)
                recommended_movies.append({'title': title, 'poster': poster_url})
        except:
            pass 

    return render(request, 'movie_engine/index.html', {'movies': recommended_movies})