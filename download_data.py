import pandas as pd
import requests
import io

# This is a verified, stable link to the 5,000 movies dataset
URL = "https://raw.githubusercontent.com/mrdbourke/tensorflow-deep-learning/main/extras/tmdb_5000_movies.csv"

print("📡 Connecting to the movie cloud...")

try:
    response = requests.get(URL)
    
    # Check if the internet actually gave us the file
    if response.status_code == 200:
        # Load the data into a table
        df = pd.read_csv(io.StringIO(response.text))
        
        print(f"✅ Connection successful! Found {len(df)} movies.")

        # We only want the title and the overview (description)
        # We use 'title' and 'overview' because those are the exact names in this file
        new_df = df[['title', 'overview']].copy()
        
        # Rename 'overview' to 'description' so it matches your Django code
        new_df.columns = ['title', 'description']
        
        # Drop any rows that are missing a description
        new_df = new_df.dropna()

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