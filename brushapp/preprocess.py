import pandas as pd
import os
import numpy as np

# Get the directory of the current script (recommender.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to imdb_data.csv
data_path = os.path.join(script_dir, "data", "imdb_data.csv")

# Load preprocessed IMDb data
data = pd.read_csv(data_path)

def recommend_daily_binge(time_limit_minutes, genre=None):
    """Recommend episodes for a single sitting based on time and genre."""
    if genre:
        filtered = data[data["genres"].str.contains(genre, case=False, na=False)].copy()
    else:
        filtered = data.copy()

    filtered["cumulative_runtime"] = filtered.groupby("parentTconst")["runtimeMinutes"].cumsum()
    available = filtered[filtered["cumulative_runtime"] <= time_limit_minutes].copy()

    recommendations = []
    for parent_tconst, group in available.groupby("parentTconst"):
        episodes = group.sort_values(["seasonNumber", "episodeNumber"])
        num_episodes = len(episodes)
        total_time = episodes["runtimeMinutes"].sum()
        if total_time > 0:
            recommendations.append({
                "title": episodes["primaryTitle"].iloc[0],
                "episodes": num_episodes,
                "total_time": total_time,
                "episode_list": episodes[["seasonNumber", "episodeNumber", "runtimeMinutes", "averageRating", "isCliffhanger"]].to_dict("records"),
                "genres": episodes["genres"].iloc[0]
            })

    return sorted(recommendations, key=lambda x: max(ep["averageRating"] for ep in x["episode_list"]), reverse=True)[:5]

def recommend_full_completion(total_days, minutes_per_day, genre=None):
    """Recommend shows/seasons to complete within a time frame."""
    total_time = total_days * minutes_per_day
    min_time = total_time * 0.75  # 75% of requested time

    if genre:
        filtered = data[data["genres"].str.contains(genre, case=False, na=False)].copy()
    else:
        filtered = data.copy()

    # Group by show and calculate total runtime, average rating, total votes
    shows = filtered.groupby("parentTconst").agg({
        "primaryTitle": "first",
        "runtimeMinutes": "sum",
        "genres": "first",
        "averageRating": "mean",
        "numVotes": "sum",  # Sum votes across episodes
        "tconst": "count"  # Number of episodes
    }).reset_index()
    shows = shows.rename(columns={"tconst": "episode_count", "runtimeMinutes": "total_runtime"})

    # Filter shows that fit within total time and meet the minimum time requirement
    viable_shows = shows[(shows["total_runtime"] <= total_time) & (shows["total_runtime"] >= min_time)].copy()
    viable_shows["daily_time"] = viable_shows["total_runtime"] / total_days

    # Normalize numVotes for sorting (log scale)
    viable_shows["normalized_votes"] = np.log1p(viable_shows["numVotes"])
    max_votes = viable_shows["normalized_votes"].max()
    if max_votes > 0:
        viable_shows["normalized_votes"] = viable_shows["normalized_votes"] / max_votes

    # Calculate time closeness
    viable_shows["time_closeness"] = 1 - abs(viable_shows["total_runtime"] - total_time) / total_time

    # Sort by a combination of average rating, time closeness, episode count, and popularity
    viable_shows["sort_score"] = (
        viable_shows["averageRating"] * 0.4 +
        viable_shows["time_closeness"] * 0.25 +
        viable_shows["episode_count"] * 0.15 +
        viable_shows["normalized_votes"] * 0.2
    )

    # Convert to dictionary and include numVotes
    recommendations = viable_shows.sort_values("sort_score", ascending=False).head(5).to_dict("records")
    return recommendations

# Example usage
if __name__ == "__main__":
    # Daily binge: 2 hours, drama
    daily_recs = recommend_daily_binge(120, "Drama")
    print("Daily Binge Recommendations:")
    for rec in daily_recs:
        print(f"{rec['title']} - {rec['episodes']} episodes, {rec['total_time']} mins")

    # Full completion: 7 days, 50 mins/day
    full_recs = recommend_full_completion(7, 50, "Drama")
    print("\nFull Completion Recommendations:")
    for rec in full_recs:
        print(f"{rec['primaryTitle']} - {rec['total_runtime']} mins total, {rec['daily_time']:.1f} mins/day, Votes: {rec['numVotes']}")