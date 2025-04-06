import pandas as pd

# Define dtypes (relaxed for initial load)
initial_dtypes = {
    "tconst": str,
    "titleType": str,
    "primaryTitle": str,
    "originalTitle": str,
    "isAdult": str,  # Load as string first
    "startYear": str,
    "endYear": str,
    "runtimeMinutes": str,  # Load as string first
    "genres": str
}

column_names = ["tconst", "titleType", "primaryTitle", "originalTitle", "isAdult", 
                "startYear", "endYear", "runtimeMinutes", "genres"]

# Load basics
print("Loading title.basics.tsv.gz...")
basics = pd.read_csv(
    "title.basics.tsv.gz",
    sep="\t",
    compression="gzip",
    na_values="\\N",
    dtype=initial_dtypes,
    names=column_names,
    header=0,
    on_bad_lines="warn"  # Warn and skip bad rows
)
print(f"Loaded title.basics.tsv.gz: {len(basics)} rows")

# Convert numeric columns after loading
basics["isAdult"] = pd.to_numeric(basics["isAdult"], errors="coerce").astype("Int64")
basics["runtimeMinutes"] = pd.to_numeric(basics["runtimeMinutes"], errors="coerce").astype("Int64")
print("Converted numeric columns. Sample:")
print(basics[["tconst", "isAdult", "runtimeMinutes"]].head())

# Load other datasets
episodes = pd.read_csv("title.episode.tsv.gz", sep="\t", compression="gzip", na_values="\\N")
ratings = pd.read_csv("title.ratings.tsv.gz", sep="\t", compression="gzip")
print(f"Loaded title.episode.tsv.gz: {len(episodes)} rows")
print(f"Loaded title.ratings.tsv.gz: {len(ratings)} rows")

# Filter TV content
tv_series = basics[basics["titleType"] == "tvSeries"]
print(f"Filtered to {len(tv_series)} TV series")

# Merge episodes with basics and ratings
tv_episodes = episodes.merge(basics, on="tconst").merge(ratings, on="tconst")
print(f"After merging with basics: {len(tv_episodes)} episodes")
print(f"After merging with ratings: {len(tv_episodes)} episodes")

# Clean data: Remove rows with missing runtimeMinutes
tv_episodes = tv_episodes.dropna(subset=["runtimeMinutes"])
print("Cleaned runtimeMinutes. Sample:")
print(tv_episodes[["tconst", "runtimeMinutes"]].head())

# Convert seasonNumber and episodeNumber to Int64
tv_episodes["seasonNumber"] = pd.to_numeric(tv_episodes["seasonNumber"], errors="coerce").astype("Int64")
tv_episodes["episodeNumber"] = pd.to_numeric(tv_episodes["episodeNumber"], errors="coerce").astype("Int64")

# Add cliffhanger flag
tv_episodes["isCliffhanger"] = tv_episodes.groupby(["parentTconst", "seasonNumber"])["episodeNumber"].transform("max") == tv_episodes["episodeNumber"]
print("Cliffhanger flag added. Sample:")
print(tv_episodes[["tconst", "parentTconst", "seasonNumber", "episodeNumber", "isCliffhanger"]].head())

# Save relevant columns
output_columns = ["tconst", "parentTconst", "primaryTitle", "seasonNumber", "episodeNumber", "runtimeMinutes", "genres", "averageRating", "isCliffhanger"]
tv_episodes[output_columns].to_csv("data/imdb_data.csv", index=False)

print("Preprocessing complete! Saved to data/imdb_data.csv")

print("Sample after merging with basics:")
print(episodes.merge(basics, on="tconst").head())
print("Sample after merging with ratings:")
print(episodes.merge(basics, on="tconst").merge(ratings, on="tconst").head())