
#############################################
# DATA PREPARATION
#############################################
import pandas as pd

pd.set_option ('display.max_columns', 20)
pd.set_option ('display.width', None)


movie = pd.read_csv(r'E:\CAGLAR\datasets\movie.csv')
rating = pd.read_csv(r'E:\CAGLAR\datasets\rating.csv')
df = movie.merge(rating, how="left", on="movieId")
df.head()
comment_counts = pd.DataFrame(df["title"].value_counts())
comment_counts.head()
rare_movies = comment_counts[comment_counts["title"] <= 1000].index  # to filter the data
rare_movies[0:10]
common_movies = df[~df["title"].isin(rare_movies)]
user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")
user_movie_df.head()

#############################################
# Determining the Movies Watched by the User to Make a Suggestion
#############################################

random_user = 108170
random_user_df = user_movie_df[user_movie_df.index == random_user]
random_user_df.head()
movies_watched = random_user_df.columns[random_user_df.notna().any()].tolist()
movies_watched[0:10]

#############################################
# Data and ID information of Other Users Watching the Same Movies
#############################################

len(movies_watched)
movies_watched_df = user_movie_df[movies_watched]
movies_watched_df.head()
movies_watched_df.T.head()

user_movie_count = movies_watched_df.T.notnull().sum()
user_movie_count = user_movie_count.reset_index()
user_movie_count.head()
user_movie_count.columns = ["userId", "movie_count"]
user_movie_count.sort_values(by="movie_count", ascending=False)

perc = len(movies_watched) * 60 / 100
users_same_movies = user_movie_count[user_movie_count["movie_count"] > perc]["userId"]
users_same_movies.head()

#############################################
# Determining The Users to be Suggested and Most Similar Users
#############################################

movies_watched_df.head()
final_df = movies_watched_df[movies_watched_df.index.isin(users_same_movies.values)]
final_df.head()
final_df.shape

final_df[final_df.index == random_user]

final_df.T.head()
final_df.T.corr().head()
final_df.T.corr().unstack().head()
corr_df = final_df.T.corr().unstack().sort_values().drop_duplicates()
corr_df = pd.DataFrame(corr_df, columns=["corr"])
corr_df.head()
corr_df.index.names = ['user_id_1', 'user_id_2']
corr_df = corr_df.reset_index()
corr_df.head()

top_users = corr_df[(corr_df["user_id_1"] == random_user) & (corr_df["corr"] >= 0.50)][
    ["user_id_2", "corr"]].reset_index(drop=True)

top_users = top_users.sort_values (by='corr', ascending=False)
top_users.head()

top_users.rename(columns={"user_id_2": "userId"}, inplace=True)

rating = pd.read_csv(r'E:\CAGLAR\datasets\rating.csv')
top_users_ratings = top_users.merge(rating[["userId", "movieId", "rating"]], how='inner')
top_users_ratings.head()

#############################################
# Calculating Weighted Average Recommendation Score and Keeping Top 5 Movies
#############################################

top_users_ratings['weighted_rating'] = top_users_ratings['corr'] * top_users_ratings['rating']
top_users_ratings.head()

top_users_ratings.groupby('movieId').agg({"weighted_rating": "mean"})

recommendation_df = top_users_ratings.groupby('movieId').agg({"weighted_rating": "mean"})
recommendation_df = recommendation_df.reset_index()
recommendation_df.head()


import matplotlib.pyplot as plt
recommendation_df["weighted_rating"].hist()
plt.show()

# weighted_rating greater than 2.7
recommendation_df[recommendation_df["weighted_rating"] > 2.7]
movies_to_be_recommend = recommendation_df[recommendation_df["weighted_rating"] > 2.7].\
    sort_values("weighted_rating", ascending = False)
movies_to_be_recommend.head()

#check movie name

def check_movie_id(dataframe, movieId):
    movie_name = dataframe[dataframe["movieId"]==movieId][["title"]].values[0].tolist()
    print(movie_name)
check_movie_id(df,114066) # ['20,000 Days on Earth (2014)']

#############################################
# User-Based Recommendation
#############################################

movie = pd.read_csv ('datasets/movie.csv')
recommended_user_based_df = movies_to_be_recommend.merge (movie[["movieId", "title"]])
recommended_user_based_df.head()
recommended_user_based_df.shape

# Suggesting movies that the user hasn't watched before
recommended_user_based_df = recommended_user_based_df.loc[~recommended_user_based_df["title"].isin(movies_watched)][:5]
recommended_user_based_df.head()

#     movieId      weighted_rating                            title
# 0   114066         3.174975                        20,000 Days on Earth (2014)
# 1   106111         3.174975                     Marc Maron: Thinky Pain (2013)
# 2     7126         3.174975            Killing of a Chinese Bookie, The (1976)
# 3     5216         3.067234  Pepi, Luci, Bom (Pepi, Luci, Bom y Otras Chica...
# 4    49394         3.067234    Simon of the Desert (Simón del desierto) (1965)

#############################################
# Item-Based Recommendation
#############################################

user = 108170

movie = pd.read_csv (r'E:\CAGLAR\datasets\movie.csv')
rating = pd.read_csv (r'E:\CAGLAR\datasets\rating.csv')


# Getting the id of the movie with the most recent score from the movies that
# the user to be suggested gives 5 points:
movie_id = rating[(rating["userId"] == user) & (rating["rating"] == 5.0)]. \
               sort_values (by="timestamp", ascending=False)["movieId"][0:1].values[0]

movie.loc[movie["movieId"] == movie_id, "title"]

user_movie_df[movie[movie["movieId"] == movie_id]["title"].values[0]]
user_movie_df.corrwith(movie).sort_values(ascending=False).head(5)

def item_based_recommender(movie_name, user_movie_df, head=10):
    movie = user_movie_df[movie_name]
    return user_movie_df.corrwith (movie).sort_values(ascending=False).head(head)


movies_from_item_based = item_based_recommender(movie[movie["movieId"] == movie_id]["title"].values[0], user_movie_df, 20).reset_index()
movies_from_item_based.head()
movies_from_item_based.rename(columns={0:"corr"}, inplace=True)
movies_from_item_based.head()

# Suggesting movies that the user has not watched before
recommended_item_based_df = movies_from_item_based.loc[~movies_from_item_based["title"].isin(movies_watched)][:5]
recommended_item_based_df

#            title      corr
#1       Jeffrey (1995)  0.532232
#2   Blue Velvet (1986)  0.494317
#3  Lost Highway (1997)  0.489621
#4    Life of Pi (2012)  0.487213
#5      Repo Man (1984)  0.480227

hybrid_rec_df = pd.concat([recommended_user_based_df["title"], recommended_item_based_df["title"]]).reset_index(drop=True)
hybrid_rec_df

#0                          20,000 Days on Earth (2014)
#1                       Marc Maron: Thinky Pain (2013)
#2              Killing of a Chinese Bookie, The (1976)
#3    Pepi, Luci, Bom (Pepi, Luci, Bom y Otras Chica...
#4      Simon of the Desert (Simón del desierto) (1965)
#5                                       Jeffrey (1995)
#6                                   Blue Velvet (1986)
#7                                  Lost Highway (1997)
#8                                    Life of Pi (2012)
#9                                      Repo Man (1984)