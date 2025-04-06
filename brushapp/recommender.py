import pandas as pd
import os

# Get the directory of the current script (recommender.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to imdb_data.csv
data_path = os.path.join(script_dir, "data", "imdb_data.csv")

# Load preprocessed IMDb data
data = pd.read_csv(data_path)

def recommend_daily_binge(time_limit_minutes, genre=None):
    """Recommend episodes for a single sitting based on time and genre."""
    # Filter by genre if provided
    if genre:
        filtered = data[data["genres"].str.contains(genre, case=False, na=False)].copy()
    else:
        filtered = data.copy()

    # Calculate cumulative runtime within time limit
    filtered["cumulative_runtime"] = filtered.groupby("parentTconst")["runtimeMinutes"].cumsum()
    available = filtered[filtered["cumulative_runtime"] <= time_limit_minutes].copy()

    # Group by show and take episodes that fit
    recommendations = []
    for parent_tconst, group in available.groupby("parentTconst"):
        episodes = group.sort_values(["seasonNumber", "episodeNumber"])
        num_episodes = len(episodes)
        total_time = episodes["runtimeMinutes"].sum()
        if total_time > 0:  # Ensure there’s content
            recommendations.append({
                "title": episodes["primaryTitle"].iloc[0],
                "episodes": num_episodes,
                "total_time": total_time,
                "episode_list": episodes[["seasonNumber", "episodeNumber", "runtimeMinutes", "averageRating", "isCliffhanger"]].to_dict("records"),
                "genres": episodes["genres"].iloc[0]
            })

    # Sort by rating and return top 5
    return sorted(recommendations, key=lambda x: max(ep["averageRating"] for ep in x["episode_list"]), reverse=True)[:5]

def recommend_full_completion(total_days, minutes_per_day, genre=None):
    """Recommend shows/seasons to complete within a time frame."""
    total_time = total_days * minutes_per_day
    if genre:
        filtered = data[data["genres"].str.contains(genre, case=False, na=False)].copy()
    else:
        filtered = data.copy()

    # Group by show and calculate total runtime
    shows = filtered.groupby("parentTconst").agg({
        "primaryTitle": "first",
        "runtimeMinutes": "sum",
        "genres": "first",
        "averageRating": "mean",
        "tconst": "count"  # Number of episodes
    }).reset_index()
    shows = shows.rename(columns={"tconst": "episode_count", "runtimeMinutes": "total_runtime"})

    # Filter shows that fit within total time
    viable_shows = shows[shows["total_runtime"] <= total_time].copy()
    viable_shows["daily_time"] = viable_shows["total_runtime"] / total_days

    # Return top 5 by average rating
    return viable_shows.sort_values("averageRating", ascending=False).head(5).to_dict("records")

# Example usage
if __name__ == "__main__":
    # Daily binge: 2 hours, comedy
    daily_recs = recommend_daily_binge(120, "Comedy")
    print("Daily Binge Recommendations:")
    for rec in daily_recs:
        print(f"{rec['title']} - {rec['episodes']} episodes, {rec['total_time']} mins")

    # Full completion: 1 week, 30 mins/day
    full_recs = recommend_full_completion(7, 30)
    print("\nFull Completion Recommendations:")
    for rec in full_recs:
        print(f"{rec['primaryTitle']} - {rec['total_runtime']} mins total, {rec['daily_time']:.1f} mins/day")