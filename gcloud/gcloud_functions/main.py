import functions_framework
import sys
import os
import requests
from google.cloud import pubsub_v1
import json


class MovieFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"


    def _get(self, endpoint, params=None):
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()


    def get_popular_movies(self, pages=1):
        movies = []
        for page in range(1, pages + 1):
            data = self._get("/movie/popular", {"page": page})
            movies.extend(data.get("results", []))
        return movies


    def get_movie_details(self, movie_id):
        return self._get(f"/movie/{movie_id}")


    def get_movie_reviews(self, movie_id):
        data = self._get(f"/movie/{movie_id}/reviews")
        return data.get("results", [])


    def get_movie_cast(self, movie_id):
        data = self._get(f"/movie/{movie_id}/credits")
        return data.get("cast", [])


    def collect_movies_dataframe(self, pages=1):
        all_movies = self.get_popular_movies(pages)
        movie_data = []

        for movie in all_movies:
            try:
                details = self.get_movie_details(movie["id"])
                genres = ", ".join([genre["name"] for genre in details.get("genres", [])])
                movie_data.append({
                    "id": movie["id"],
                    "title": movie["title"],
                    "release_date": movie["release_date"],
                    "genres": genres,
                    "overview": movie["overview"],
                    "vote_average": movie["vote_average"]
                })
            except Exception as e:
                print(f"Error processing movie {movie['id']}: {e}")

        return pd.DataFrame(movie_data)


    def collect_reviews_dataframe(self, movie_ids):
        review_data = []
        for movie_id in movie_ids:
            try:
                reviews = self.get_movie_reviews(movie_id)
                for review in reviews:
                    review_data.append({
                        "movie_id": movie_id,
                        "author": review.get("author"),
                        "content": review.get("content"),
                        "rating": review.get("author_details", {}).get("rating")
                    })
            except Exception as e:
                print(f"Error fetching reviews for movie {movie_id}: {e}")
        return pd.DataFrame(review_data)


    def collect_cast_dataframe(self, movie_ids, top_n=5):
        cast_data = []
        for movie_id in movie_ids:
            try:
                cast_list = self.get_movie_cast(movie_id)[:top_n] 
                for cast in cast_list:
                    cast_data.append({
                        "movie_id": movie_id,
                        "actor_name": cast.get("name"),
                        "character": cast.get("character"),
                        "order": cast.get("order")
                    })
            except Exception as e:
                print(f"Error fetching cast for movie {movie_id}: {e}")
        return pd.DataFrame(cast_data)


@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    project_id = "numeric-datum-450017-k4"
    topic_id = "projects/numeric-datum-450017-k4/topics/test"

    # key_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    # key_dict = json.loads(key_json)
    # key_path = "/tmp/key.json"

    # with open(key_path, "w") as f:
    #     json.dump(key_dict, f)


    fetcher = MovieFetcher(api_key="9369a5ad92b5bf33193a720693c63ed7")
    movies_df = fetcher.collect_movies_dataframe(pages=2)
    reviews_df = fetcher.collect_reviews_dataframe(movies_df["id"])
    cast_df = fetcher.collect_cast_dataframe(movies_df["id"])

    data = {
        "movies": movies_df.to_dict(orient="records"),
        "reviews": reviews_df.to_dict(orient="records"),
        "cast": cast_df.to_dict(orient="records")
    }
    data_str = json.dumps(data)
    data_bytes = data_str.encode("utf-8")

    #credentials = (service_account.Credentials.from_service_account_file(key_path))
    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(project_id, topic_id)
    future = publisher.publish(topic_path, data_bytes)

    return f"Published message ID: {future.result()}"