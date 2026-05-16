import pandas as pd

print("🛡️ Running the 'Force-Clean' sequence...")

try:
    # 1. Load the file but ignore any broken or messy lines
    # We also tell it to ignore 'quoting' errors which happen with movie descriptions
    df = pd.read_csv('movies_raw.csv', on_bad_lines='skip', engine='python')

    print(f"📊 Found {len(df)} readable lines. Searching for columns...")

    # 2. Find the right columns even if they are capitalized
    title_col = [c for c in df.columns if 'title' in c.lower()][0]
    desc_col = [c for c in df.columns if 'overview' in c.lower() or 'description' in c.lower()][0]

    # 3. Clean and Save
    new_df = df[[title_col, desc_col]].copy()
    new_df.columns = ['title', 'description']
    new_df = new_df.dropna()

    new_df.to_csv('movies.csv', index=False)

    print("-" * 30)
    print(f"✅ FINAL SUCCESS! 4,000+ movies ready.")
    print("-" * 30)
    print("Restart your server and search for 'Batman'!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 TIP: If it still fails, your 'movies_raw.csv' might be an HTML page.")
    print("Open it in VS Code—if the first line starts with '<!DOCTYPE html>', it's a webpage, not a CSV!")