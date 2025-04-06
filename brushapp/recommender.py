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
            # Calculate average rating and total votes for the show
            avg_rating = episodes["averageRating"].mean()
            total_votes = episodes["numVotes"].sum()

            # Skip shows with less than 100 votes (to ensure they’re "Google-able")
            if total_votes < 100:
                continue
            
            # Normalize numVotes for sorting (log scale)
            normalized_votes = np.log1p(total_votes)
            max_votes = np.log1p(data["numVotes"].sum())  # Approximate max for normalization
            if max_votes > 0:
                normalized_votes = normalized_votes / max_votes

            # Calculate time closeness
            time_closeness = 1 - abs(total_time - time_limit_minutes) / time_limit_minutes

            # Sort score: 60% popularity, 30% rating, 10% time closeness
            sort_score = (
                normalized_votes * 0.6 +  # Increased weight for popularity
                avg_rating * 0.3 +
                time_closeness * 0.1
            )

            recommendations.append({
                "title": episodes["seriesTitle"].iloc[0],
                "episodes": num_episodes,
                "total_time": total_time,
                "episode_list": episodes[["seasonNumber", "episodeNumber", "runtimeMinutes", "averageRating", "isCliffhanger"]].to_dict("records"),
                "genres": episodes["genres"].iloc[0],
                "avg_rating": avg_rating,
                "numVotes": total_votes,
                "sort_score": sort_score
            })

    # Sort by sort_score
    return sorted(recommendations, key=lambda x: x["sort_score"], reverse=True)[:5]

def recommend_full_completion(total_days, minutes_per_day, genre=None):
    """Recommend shows/seasons to complete within a time frame."""
    total_time = total_days * minutes_per_day
    min_time = total_time * 0.8  # 80% of requested time (280 mins for 350 mins total)

    if genre:
        filtered = data[data["genres"].str.contains(genre, case=False, na=False)].copy()
    else:
        filtered = data.copy()

    # Group by show and calculate total runtime, average rating, total votes
    shows = filtered.groupby("parentTconst").agg({
        "seriesTitle": "first",
        "runtimeMinutes": "sum",
        "genres": "first",
        "averageRating": "mean",
        "numVotes": "sum",
        "tconst": "count"
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
        viable_shows["averageRating"] * 0.2 +
        viable_shows["time_closeness"] * 0.4 +
        viable_shows["episode_count"] * 0.1 +
        viable_shows["normalized_votes"] * 0.3
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
        print(f"{rec['title']} - {rec['episodes']} episodes, {rec['total_time']} mins, Votes: {rec['numVotes']}, Avg Rating: {rec['avg_rating']:.1f}")

    # Full completion: 7 days, 50 mins/day
    full_recs = recommend_full_completion(7, 50, "Drama")
    print("\nFull Completion Recommendations:")
    for rec in full_recs:
        print(f"{rec['seriesTitle']} - {rec['total_runtime']} mins total, {rec['daily_time']:.1f} mins/day, Votes: {rec['numVotes']}")