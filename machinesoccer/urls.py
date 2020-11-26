from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("new_search", views.new_search, name="new_search"),
    path("new_searchone", views.new_searchone, name="new_searchone"),
    path(
        "insert_into_db_tables",
        views.insert_into_db_tables,
        name="insert_into_db_tables",
    ),
    path(
        "clear_tables_function",
        views.clear_tables_function,
        name="clear_tables_function",
    ),
    path(
        "drop_prediction_table",
        views.drop_prediction_table,
        name="drop_prediction_table",
    ),
    path(
        "clear_prediction_table",
        views.clear_prediction_table,
        name="clear_prediction_table",
    ),
    path(
        "clear_item_in_prediction_table",
        views.clear_item_in_prediction_table,
        name="clear_item_in_prediction_table",
    ),
    path(
        "create_prediction_table",
        views.create_prediction_table,
        name="create_prediction_table",
    ),
    path(
        "query_tables_function",
        views.query_tables_function,
        name="query_tables_function",
    ),
    path(
        "append_finalpredictions_to_table",
        views.append_finalpredictions_to_table,
        name="append_finalpredictions_to_table",
    ),
    path(
        "finalprediction_of_the_day",
        views.finalprediction_of_the_day,
        name="finalprediction_of_the_day",
    ),
    path("create_hometable", views.create_hometable, name="create_hometable",),
    path("create_awaytable", views.create_awaytable, name="create_awaytable",),
    path(
        "drop_home_away_stats_table",
        views.drop_home_away_stats_table,
        name="drop_home_away_stats_table",
    ),
    path(
        "find_finalprediction_of_the_day",
        views.find_finalprediction_of_the_day,
        name="find_finalprediction_of_the_day",
    ),
    path(
        "find_finalprediction_of_the_day_prev",
        views.find_finalprediction_of_the_day_prev,
        name="find_finalprediction_of_the_day_prev",
    ),
    path(
        "find_finalprediction_of_the_day_next",
        views.find_finalprediction_of_the_day_next,
        name="find_finalprediction_of_the_day_next",
    ),
]

