# preprocess.py
import pandas as pd

# Define dtypes to avoid mixed-type warnings and handle NaN
dtypes = {
    "tconst": str,
    "titleType": str,
    "primaryTitle": str,
    "originalTitle": str,
    "isAdult": "Int64",
    "startYear": str,
    "endYear": str,
    "runtimeMinutes": "Int64",
    "genres": str
}

# Explicitly name columns to match IMDb structure
column_names = ["tconst", "titleType", "primaryTitle", "originalTitle", "isAdult", 
                "startYear", "endYear", "runtimeMinutes", "genres"]

# Load basics with error handling
try:
    basics = pd.read_csv(
        "title.basics.tsv.gz",
        sep="\t",
        compression="gzip",
        na_values="\\N",
        dtype=dtypes,
        names=column_names,
        header=0,
        usecols=column_names,
        on_bad_lines="skip"  # Skip bad rows to finish preprocessing
    )
except ValueError as e:
    print(f"Error loading basics: {e}")
    # Debug: Load a precise chunk around 48090
    basics_chunk = pd.read_csv(
        "title.basics.tsv.gz",
        sep="\t",
        compression="gzip",
        na_values="\\N",
        names=column_names,
        header=0,
        skiprows=48080,  # Start at 48080 (includes header, so 48081 is first data row)
        nrows=20,        # Load 20 rows (up to ~48100)
        on_bad_lines="warn"
    )
    print("Rows around 48090 (adjusted):")
    print(basics_chunk)
    raise  # Stop to inspect

# Load other datasets
episodes = pd.read_csv("title.episode.tsv.gz", sep="\t", compression="gzip", na_values="\\N")
ratings = pd.read_csv("title.ratings.tsv.gz", sep="\t", compression="gzip")

# Filter TV content
tv_series = basics[basics["titleType"] == "tvSeries"]
tv_episodes = episodes.merge(basics, on="tconst").merge(ratings, on="tconst")

# Add cliffhanger flag
tv_episodes["isCliffhanger"] = tv_episodes.groupby(["parentTconst", "seasonNumber"])["episodeNumber"].transform("max") == tv_episodes["episodeNumber"]

# Save relevant columns
output_columns = ["tconst", "parentTconst", "primaryTitle", "seasonNumber", "episodeNumber", "runtimeMinutes", "genres", "averageRating", "isCliffhanger"]
tv_episodes[output_columns].to_csv("data/imdb_data.csv", index=False)

print("Preprocessing complete! Saved to data/imdb_data.csv")