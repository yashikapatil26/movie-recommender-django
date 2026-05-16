import io
import zipfile

import pandas as pd
import requests

# Stable archive containing the TMDB 5k dataset.
URL = "https://raw.githubusercontent.com/evan-william/tmdb-5000-movie-recommender/main/data.zip"
MOVIES_CSV_NAME = "tmdb_5000_movies.csv"

print("📡 Connecting to the movie cloud...")

try:
    response = requests.get(URL, timeout=20)
    
    # Check if the internet actually gave us the file
    if response.status_code == 200:
        archive = zipfile.ZipFile(io.BytesIO(response.content))
        with archive.open(MOVIES_CSV_NAME) as handle:
            df = pd.read_csv(handle)
        
        print(f"✅ Connection successful! Found {len(df)} movies.")

        # We only want the title and the overview (description)
        # We use 'title' and 'overview' because those are the exact names in this file
        new_df = df["title"].to_frame()
        new_df["description"] = df["overview"]
        
        # Rename 'overview' to 'description' so it matches your Django code
        # Drop any rows that are missing required fields
        new_df = new_df.dropna(subset=["title", "description"])

        # Overwrite your old 6-movie file with the 4,800-movie file
        new_df.to_csv('movies.csv', index=False)

        print("-" * 30)
        print(f"🚀 SUCCESS! 'movies.csv' now has {len(new_df)} movies.")
        print("-" * 30)
        print("Now go to your browser and search for 'Fight Club'!")
    else:
        print(f"❌ Failed to download. Status code: {response.status_code}")

except Exception as e:
    print(f"❌ ERROR: {e}")