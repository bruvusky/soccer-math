from django.shortcuts import render
import requests
from django.contrib.auth.decorators import permission_required
from requests.compat import quote_plus
import os
import csv
from bs4 import BeautifulSoup

import sqlite3
import pandas as pd
from pandas import DataFrame
import math
import scipy
from scipy.stats import poisson
import datetime
import pytz
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

x = 0
y = 0


def home(request):
    return render(request, "base.html")


def new_search(request):

    search = request.POST.get("search")
    position = request.POST.get("position")
    position1 = request.POST.get("position1")

    # print(search + " " + position + " " + position1)

    BASE_URL = "https://www.soccerstats.com/homeaway.asp?league={}"
    final_url = BASE_URL.format(quote_plus(search))
    page = requests.get(final_url)
    soup = BeautifulSoup(page.content, "html.parser")
    filename = "home.csv"
    filename1 = "away.csv"
    csv_writer = csv.writer(open(filename, "w"))
    csv_writer1 = csv.writer(open(filename1, "w"))
    home_stat = soup.find(id="h2h-team1")
    away_stat = soup.find(id="h2h-team2")
    home_table = home_stat.find("table", id="btable")
    away_table = away_stat.find("table", id="btable")
    # print (home_table)

    headers = []
    for th in home_table.find("tr", class_="even").find_all("th"):
        headers.append(th.text.strip())
    print(" {}".format(" , ".join(headers)))
    # csv_writer.writerow(headers)

    rows = []
    for tr in home_table.find_all("tr", class_="odd"):
        cells = []
        # grab all td tags in this table row
        tds = tr.find_all("td")

        for td in tds:
            cells.append(td.text.strip())
        rows.append(cells)
        if cells:  # print(cells)
            print("{}".format(" , ".join(cells)))
            csv_writer.writerow(cells)
            continue

    headers1 = []
    for th in away_table.find("tr", class_="even").find_all("th"):
        headers1.append(th.text.strip())
    print(" {}".format(" , ".join(headers)))
    # csv_writer1.writerow(headers1)

    rows1 = []
    for tr in away_table.find_all("tr", class_="odd"):
        cells1 = []
        # grab all td tags in this table row
        tds1 = tr.find_all("td")

        for td in tds1:
            cells1.append(td.text.strip())
        rows1.append(cells1)
        if cells1:  # print(cells)
            print("{}".format(" , ".join(cells1)))
            csv_writer1.writerow(cells1)
            continue

    stuff_for_frontend = {
        "search": search,
        "position": position,
        "position1": position1,
    }

    return render(request, "machinesoccer/new_search.html", stuff_for_frontend)


# conn = sqlite3.connect(':memory:')
# conn = sqlite3.connect("soccer.db")
# creating a cursor
# c = conn.cursor()

# c.execute("PRAGMA table_info(soccerstats2)")
# main = c.fetchall()
# print(main)
# @csrf_exempt
# @permission_required("admin")
def insert_into_db_tables(request):

    conn = sqlite3.connect("soccer.db")
    # c = conn.cursor()
    home_csv = os.path.join("home.csv")
    away_csv = os.path.join("away.csv")
    read_teams = pd.read_csv(
        home_csv,
        names=["Position", "Team", "GP", "W", "D", "L", "GF", "GA", "GD", "PTS"],
        header=None,
    )

    read_teams.to_sql(
        "homestats", conn, if_exists="append", index=False
    )  # Insert the values from the csv file into the table 'soccerstats'

    read_teams = pd.read_csv(
        away_csv,
        names=["Position", "Team", "GP", "W", "D", "L", "GF", "GA", "GD", "PTS"],
        header=None,
    )

    read_teams.to_sql(
        "awaystats", conn, if_exists="append", index=False
    )  # Insert the values from the csv file into the table 'soccerstats'

    print("command executed succesfully")
    conn.commit()
    conn.close()
    # return HttpResponseRedirect("/new_search")
    return render(request, "machinesoccer/insert_into_db_tables.html")


# @permission_required("perm")


# create hometable
# create awaytable


def create_hometable(request):

    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute(
        """ CREATE TABLE homestats(
        position integer,
        team text,
        gp integer,
        w integer,
        d  integer,
        l   integer,
        gf  integer,
        ga  integer,
        gd integer,
        Pts integer
    )"""
    )
    print("command executed succesfully")
    conn.commit()
    conn.close()
    return render(request, "machinesoccer/create_hometable.html")


def create_awaytable(request):

    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute(
        """ CREATE TABLE awaystats(
        position integer,
        team text,
        gp integer,
        w integer,
        d  integer,
        l   integer,
        gf  integer,
        ga  integer,
        gd integer,
        Pts integer
    )"""
    )
    print("command executed succesfully")
    conn.commit()
    conn.close()
    return render(request, "machinesoccer/create_awaytable.html")


def clear_tables_function(request):
    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute("DELETE  FROM  'homestats'")
    c.execute("DELETE  FROM  'awaystats'")
    print("command executed succesfully")
    conn.commit()
    conn.close()
    return render(request, "machinesoccer/clear_tables_function.html")


def drop_prediction_table(request):
    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute("DROP TABLE 'finalprediction' ")
    print("command executed succesfully")
    conn.commit()
    conn.close()

    return render(request, "machinesoccer/drop_prediction_table.html")


def clear_prediction_table(request):
    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute("DELETE FROM 'finalprediction' ")
    print("command executed succesfully")
    conn.commit()
    conn.close()

    return render(request, "machinesoccer/clear_prediction_table.html")


def drop_home_away_stats_table(request):
    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute("DROP TABLE  'homestats' ")
    c.execute("DROP TABLE  'awaystats' ")
    print("command executed succesfully")
    conn.commit()
    conn.close()

    return render(request, "machinesoccer/drop_home_away_stats_table.html")


def clear_item_in_prediction_table(request):

    rowid = request.POST.get("id")

    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute("DELETE  FROM 'finalprediction' WHERE rowid = (?) ", (rowid,))
    print("command executed succesfully")
    conn.commit()
    conn.close()

    return render(request, "machinesoccer/clear_item_in_prediction_table.html")


def create_prediction_table(request):
    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute(
        """ CREATE TABLE finalprediction(
        Date  text, 
        Home_pg integer,
        Away_pg integer,   
        Hometeam text ,
        Awayteam text,
        homewinodds integer,
        Drawodds integer,
        Awaywinodds integer,
        Over15  integer,
        Under15  integer,
        Over25  integer,
        Under25  integer,
        bttsyes integer,
        bttsno  integer,
        CS0_0 integer,
        CS1_1 integer,
        CS2_2 integer,
        CS3_3 integer,
        CS4_4 integer,
        CS5_5 integer,
        CS1_0 integer,
        CS2_0 integer,
        CS3_0 integer,
        CS4_0 integer,
        CS5_0 integer,
        CS2_1 integer,
        CS3_1 integer,
        CS3_2 integer,
        CS4_1 integer,
        CS4_2 integer,
        CS4_3 integer,
        CS5_1 integer,
        CS5_2 integer,
        CS5_3 integer,
        CS5_4 integer,
        CS0_1 integer,
        CS0_2 integer,
        CS0_3 integer,
        CS0_4 integer,
        CS0_5 integer,
        CS1_2 integer,
        CS1_3 integer,
        CS2_3 integer,
        CS1_4 integer,
        CS2_4 integer,
        CS3_4 integer,
        CS1_5 integer,
        CS2_5 integer,
        CS3_5 integer,
        CS4_5 integer
    )"""
    )
    print("command executed succesfully")
    conn.commit()
    conn.close()

    return render(request, "machinesoccer/create_prediction_table.html")


# many_teams = [
#     ("Hamburger SV", "13", "9", "2", "2", "27", "9", "18", "29"),
#     ("Heidenheim", "14", "8", "4", "2", "23", "11", "12", "28"),
#     ("Sankt Pauli", "15", "7", "5", "3", "21", "12", "9", "26"),
#     ("Bielefeld", "13", "6", "6", "1", "23", "11", "12", "24"),
#     ("Darmstadt", "14", "5", "8", "1", "22", "14", "8", "23"),
# ]
# c.executemany("INSERT INTO soccerstats VALUES(?,?,?,?,	?,	?,	?,	?,?)", many_teams)


def query_tables_function(request, *args, **kwargs):
    global x, y

    x = request.POST.get("position")
    # print(position)
    y = request.POST.get("position1")
    # print(position1)
    # Position = position
    # Position1 = position1
    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    today = datetime.date.today()
    query_tables_function.leo = str(today)
    # print(query_tables_function.leo)
    c.execute("SELECT * FROM 'homestats' WHERE position = (?) ", (x,))
    hometeam = c.fetchone()
    # print(hometeam)
    query_tables_function.home_team_playing = hometeam[1]
    c.execute("SELECT  SUM(gp) FROM  'homestats' ")
    gamesplayed = c.fetchone()
    # print(gamesplayed)
    c.execute("SELECT  SUM(gf) FROM  'homestats' ")
    goalsfor = c.fetchone()
    # print(goalsfor)
    c.execute("SELECT  SUM(ga) FROM 'homestats' ")
    goalsagainist = c.fetchone()
    # print(goalsagainist)
    c.execute("SELECT * FROM 'awaystats' WHERE position = (?) ", (y,))
    awayteam = c.fetchone()
    # print(awayteam)
    query_tables_function.away_team_playing = awayteam[1]
    H_gf_pergame = hometeam[6] / hometeam[2]
    # print(H_gf_pergame)

    H_ga_pergame = hometeam[7] / hometeam[2]
    # print(H_ga_pergame)

    A_gf_pergame = awayteam[6] / awayteam[2]
    # print(A_gf_pergame)

    A_ga_pergame = awayteam[7] / awayteam[2]
    # print(A_ga_pergame)

    goals_for_per_homematch = goalsfor[0] / gamesplayed[0]
    # print(goals_for_per_homematch)

    goals_againist_per_homematch = goalsagainist[0] / gamesplayed[0]
    # print(goals_againist_per_homematch)

    homeatt = H_gf_pergame / goals_for_per_homematch
    # print(homeatt)

    homedefence = H_ga_pergame / goals_againist_per_homematch
    # print(homedefence)

    awayatt = A_gf_pergame / goals_againist_per_homematch
    # print(awayatt)

    awaydiffence = A_ga_pergame / goals_for_per_homematch
    # print(awaydiffence)

    home_probable_goal = homeatt * awaydiffence * goals_for_per_homematch
    away_probable_goal = awayatt * homedefence * goals_againist_per_homematch

    query_tables_function.hpg = str((round(home_probable_goal, 4)))
    # print("predicted home score " + query_tables_function.hpg)

    query_tables_function.apg = str((round(away_probable_goal, 4)))
    # print("predicted away score " + query_tables_function.apg)
    goals = [0, 1, 2, 3, 4, 5]

    home_score_0 = poisson.pmf(goals[0], home_probable_goal)
    home_score_1 = poisson.pmf(goals[1], home_probable_goal)
    home_score_2 = poisson.pmf(goals[2], home_probable_goal)
    home_score_3 = poisson.pmf(goals[3], home_probable_goal)
    home_score_4 = poisson.pmf(goals[4], home_probable_goal)
    home_score_5 = poisson.pmf(goals[5], home_probable_goal)

    away_score_0 = poisson.pmf(goals[0], away_probable_goal)
    away_score_1 = poisson.pmf(goals[1], away_probable_goal)
    away_score_2 = poisson.pmf(goals[2], away_probable_goal)
    away_score_3 = poisson.pmf(goals[3], away_probable_goal)
    away_score_4 = poisson.pmf(goals[4], away_probable_goal)
    away_score_5 = poisson.pmf(goals[5], away_probable_goal)

    under15 = 1 / (
        (home_score_0 * away_score_0)
        + (away_score_1 * home_score_0)
        + (home_score_1 * away_score_0)
    )

    over15 = 1 / (1 - (1 / under15))

    under25 = 1 / (
        (home_score_0 * away_score_0)
        + (away_score_1 * home_score_0)
        + (home_score_1 * away_score_0)
        + (away_score_1 * home_score_1)
        + (away_score_2 * home_score_0)
        + (away_score_0 * home_score_2)
    )

    over25 = 1 / (1 - (1 / under25))

    Both_TO_Score_No = 1 / (
        (home_score_0 * away_score_0)
        + (home_score_0 * away_score_1)
        + (home_score_0 * away_score_2)
        + (home_score_0 * away_score_3)
        + (home_score_0 * away_score_4)
        + (home_score_0 * away_score_5)
        + (home_score_1 * away_score_0)
        + (home_score_2 * away_score_0)
        + (home_score_3 * away_score_0)
        + (home_score_4 * away_score_0)
        + (home_score_5 * away_score_0)
    )

    Both_TO_Score = 1 / (1 - (1 / Both_TO_Score_No))

    homewin = 1 / (
        (home_score_1 * away_score_0)
        + (home_score_2 * away_score_0)
        + (home_score_3 * away_score_0)
        + (home_score_4 * away_score_0)
        + (home_score_5 * away_score_0)
        + (home_score_2 * away_score_1)
        + (home_score_3 * away_score_1)
        + (home_score_3 * away_score_2)
        + (home_score_4 * away_score_1)
        + (home_score_4 * away_score_2)
        + (home_score_4 * away_score_3)
        + (home_score_5 * away_score_1)
        + (home_score_5 * away_score_2)
        + (home_score_5 * away_score_3)
        + (home_score_5 * away_score_4)
    )

    draw = 1 / (
        (home_score_1 * away_score_1)
        + (away_score_0 * home_score_0)
        + (home_score_2 * away_score_2)
        + (home_score_3 * away_score_3)
        + (home_score_4 * away_score_4)
        + (home_score_5 * away_score_5)
    )

    Awaywin = 1 / (
        (home_score_0 * away_score_1)
        + (home_score_0 * away_score_2)
        + (home_score_0 * away_score_3)
        + (home_score_0 * away_score_4)
        + (home_score_0 * away_score_5)
        + (home_score_1 * away_score_2)
        + (home_score_1 * away_score_3)
        + (home_score_2 * away_score_3)
        + (home_score_1 * away_score_4)
        + (home_score_2 * away_score_4)
        + (home_score_3 * away_score_4)
        + (home_score_1 * away_score_5)
        + (home_score_2 * away_score_5)
        + (home_score_3 * away_score_5)
        + (home_score_4 * away_score_5)
    )
    #  draw
    cs0_0 = 1 / (home_score_0 * away_score_0)
    cs1_1 = 1 / (home_score_1 * away_score_1)
    cs2_2 = 1 / (home_score_2 * away_score_2)
    cs3_3 = 1 / (home_score_3 * away_score_3)
    cs4_4 = 1 / (home_score_4 * away_score_4)
    cs5_5 = 1 / (home_score_5 * away_score_5)
    #  home win
    cs1_0 = 1 / (home_score_1 * away_score_0)
    cs2_0 = 1 / (home_score_2 * away_score_0)
    cs3_0 = 1 / (home_score_3 * away_score_0)
    cs4_0 = 1 / (home_score_4 * away_score_0)
    cs5_0 = 1 / (home_score_5 * away_score_0)
    cs2_1 = 1 / (home_score_2 * away_score_1)
    cs3_1 = 1 / (home_score_3 * away_score_1)
    cs3_2 = 1 / (home_score_3 * away_score_2)
    cs4_1 = 1 / (home_score_4 * away_score_1)
    cs4_2 = 1 / (home_score_4 * away_score_2)
    cs4_3 = 1 / (home_score_4 * away_score_3)
    cs5_1 = 1 / (home_score_5 * away_score_1)
    cs5_2 = 1 / (home_score_5 * away_score_2)
    cs5_3 = 1 / (home_score_5 * away_score_3)
    cs5_4 = 1 / (home_score_5 * away_score_4)
    #  away win
    cs0_1 = 1 / (home_score_0 * away_score_1)
    cs0_2 = 1 / (home_score_0 * away_score_2)
    cs0_3 = 1 / (home_score_0 * away_score_3)
    cs0_4 = 1 / (home_score_0 * away_score_4)
    cs0_5 = 1 / (home_score_0 * away_score_5)
    cs1_2 = 1 / (home_score_1 * away_score_2)
    cs1_3 = 1 / (home_score_1 * away_score_3)
    cs2_3 = 1 / (home_score_2 * away_score_3)
    cs1_4 = 1 / (home_score_1 * away_score_4)
    cs2_4 = 1 / (home_score_2 * away_score_4)
    cs3_4 = 1 / (home_score_3 * away_score_4)
    cs1_5 = 1 / (home_score_1 * away_score_5)
    cs2_5 = 1 / (home_score_2 * away_score_5)
    cs3_5 = 1 / (home_score_3 * away_score_5)
    cs4_5 = 1 / (home_score_4 * away_score_5)

    query_tables_function.hm = str((round(homewin, 2)))
    # print("Home win Odd  " + query_tables_function.hm)

    query_tables_function.d = str((round(draw, 2)))
    # print("Draw Odd  " + query_tables_function.d)

    query_tables_function.Aw = str((round(Awaywin, 2)))
    # print("Away win Odd  " + query_tables_function.Aw)

    query_tables_function.btts = str((round(Both_TO_Score, 2)))
    # print("Btts Yes " + query_tables_function.btts)

    query_tables_function.btts_no = str((round(Both_TO_Score_No, 2)))
    # print("Btts No " + query_tables_function.btts_no)

    query_tables_function.ov15 = str((round(over15, 2)))
    # print("ov15 " + query_tables_function.ov15)

    query_tables_function.un15 = str((round(under15, 2)))
    # print("un15 " + query_tables_function.un15)

    query_tables_function.ov25 = str((round(over25, 2)))
    # print("Ov2.5 " + query_tables_function.ov25)

    query_tables_function.un25 = str((round(under25, 2)))
    # print("Un2.5 " + query_tables_function.un25)

    query_tables_function.cs0_0 = str((round(cs0_0, 2)))
    # print("CS 0-0 " + query_tables_function.cs0_0)

    query_tables_function.cs1_1 = str((round(cs1_1, 2)))
    # print("CS 1-1 " + query_tables_function.cs1_1)

    query_tables_function.cs2_2 = str((round(cs2_2, 2)))
    # print("CS 2-2 " + query_tables_function.cs2_2)

    query_tables_function.cs3_3 = str((round(cs3_3, 2)))
    # print("CS 3-3 " + query_tables_function.cs3_3)

    query_tables_function.cs4_4 = str((round(cs4_4, 2)))
    # print("CS 4-4 " + query_tables_function.cs4_4)

    query_tables_function.cs5_5 = str((round(cs5_5, 2)))
    # print("CS 5-5 " + query_tables_function.cs5_5)

    query_tables_function.cs1_0 = str((round(cs1_0, 2)))
    # print("CS 1-0 " + query_tables_function.cs1_0)

    query_tables_function.cs2_0 = str((round(cs2_0, 2)))
    # print("CS 2-0 " + query_tables_function.cs2_0)

    query_tables_function.cs3_0 = str((round(cs3_0, 2)))
    # print("CS 3-0 " + query_tables_function.cs3_0)

    query_tables_function.cs4_0 = str((round(cs4_0, 2)))
    # print("CS 3-0 " + query_tables_function.cs3_0)

    query_tables_function.cs5_0 = str((round(cs5_0, 2)))
    # print("CS 3-0 " + query_tables_function.cs3_0)

    query_tables_function.cs2_1 = str((round(cs2_1, 2)))
    # print("CS 2-1 " + query_tables_function.cs2_1)

    query_tables_function.cs3_1 = str((round(cs3_1, 2)))
    # print("CS 3-1 " + query_tables_function.cs3_1)

    query_tables_function.cs3_2 = str((round(cs3_2, 2)))
    # print("CS 3-2 " + query_tables_function.cs3_2)

    query_tables_function.cs4_1 = str((round(cs4_1, 2)))
    # print("CS 4-1 " + query_tables_function.cs4_1)

    query_tables_function.cs4_2 = str((round(cs4_2, 2)))
    # print("CS 4-2 " + query_tables_function.cs4_2)

    query_tables_function.cs4_3 = str((round(cs4_3, 2)))
    # print("CS 4-3 " + query_tables_function.cs4_3)

    query_tables_function.cs5_1 = str((round(cs5_1, 2)))
    # print("CS 5-1 " + query_tables_function.cs5_1)

    query_tables_function.cs5_2 = str((round(cs5_2, 2)))
    # print("CS 5-2 " + query_tables_function.cs5_2)

    query_tables_function.cs5_3 = str((round(cs5_3, 2)))
    # print("CS 5-3 " + query_tables_function.cs5_3)

    query_tables_function.cs5_4 = str((round(cs5_4, 2)))
    # print("CS 5-4 " + query_tables_function.cs5_4)

    query_tables_function.cs0_1 = str((round(cs0_1, 2)))
    # print("CS 0-1 " + query_tables_function.cs0_1)

    query_tables_function.cs0_2 = str((round(cs0_2, 2)))
    # print("CS 0-2 " + query_tables_function.cs0_2)

    query_tables_function.cs0_3 = str((round(cs0_3, 2)))
    # print("CS 0-3 " + query_tables_function.cs0_3)

    query_tables_function.cs0_4 = str((round(cs0_4, 2)))
    # print("CS 0-4 " + query_tables_function.cs0_4)

    query_tables_function.cs0_5 = str((round(cs0_5, 2)))
    # print("CS 0-5 " + query_tables_function.cs0_5)

    query_tables_function.cs1_2 = str((round(cs1_2, 2)))
    # print("CS 1-2 " + query_tables_function.cs1_2)

    query_tables_function.cs1_3 = str((round(cs1_3, 2)))
    # print("CS 1-3 " + query_tables_function.cs1_3)

    query_tables_function.cs2_3 = str((round(cs2_3, 2)))
    # print("CS 2-3 " + query_tables_function.cs2_3)

    query_tables_function.cs1_4 = str((round(cs1_4, 2)))
    # print("CS 1-4 " + query_tables_function.cs1_4)

    query_tables_function.cs2_4 = str((round(cs2_4, 2)))
    # print("CS 2-4 " + query_tables_function.cs2_4)

    query_tables_function.cs3_4 = str((round(cs3_4, 2)))
    # print("CS 3-4 " + query_tables_function.cs3_4)

    query_tables_function.cs1_5 = str((round(cs1_5, 2)))
    # print("CS 1-5 " + query_tables_function.cs1_5)

    query_tables_function.cs2_5 = str((round(cs2_5, 2)))
    # print("CS 2-5 " + query_tables_function.cs2_5)

    query_tables_function.cs3_5 = str((round(cs3_5, 2)))
    # print("CS 3-5 " + query_tables_function.cs3_5)

    query_tables_function.cs4_5 = str((round(cs4_5, 2)))
    # print("CS 4-5 " + query_tables_function.cs4_5)

    conn.commit()
    conn.close()
    # return (Position, Position1)
    return render(request, "machinesoccer/query_tables_function.html")


def append_finalpredictions_to_table(request):
    global x, y
    # Position = Position
    # Position1 = Position1
    # position = request.POST.get("position")
    # p = str(position)
    # position1 = request.POST.get("position1")
    # p1 = str(position1)
    query_tables_function(request, x, y)
    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    my_prediction = [
        (query_tables_function.leo),
        (query_tables_function.hpg),
        (query_tables_function.apg),
        (query_tables_function.home_team_playing),
        (query_tables_function.away_team_playing),
        (query_tables_function.hm),
        (query_tables_function.d),
        (query_tables_function.Aw),
        (query_tables_function.ov15),
        (query_tables_function.un15),
        (query_tables_function.ov25),
        (query_tables_function.un25),
        (query_tables_function.btts),
        (query_tables_function.btts_no),
        (query_tables_function.cs0_0),
        (query_tables_function.cs1_1),
        (query_tables_function.cs2_2),
        (query_tables_function.cs3_3),
        (query_tables_function.cs4_4),
        (query_tables_function.cs5_5),
        (query_tables_function.cs1_0),
        (query_tables_function.cs2_0),
        (query_tables_function.cs3_0),
        (query_tables_function.cs4_0),
        (query_tables_function.cs5_0),
        (query_tables_function.cs2_1),
        (query_tables_function.cs3_1),
        (query_tables_function.cs3_2),
        (query_tables_function.cs4_1),
        (query_tables_function.cs4_2),
        (query_tables_function.cs4_3),
        (query_tables_function.cs5_1),
        (query_tables_function.cs5_2),
        (query_tables_function.cs5_3),
        (query_tables_function.cs5_4),
        (query_tables_function.cs0_1),
        (query_tables_function.cs0_2),
        (query_tables_function.cs0_3),
        (query_tables_function.cs0_4),
        (query_tables_function.cs0_5),
        (query_tables_function.cs1_2),
        (query_tables_function.cs1_3),
        (query_tables_function.cs2_3),
        (query_tables_function.cs1_4),
        (query_tables_function.cs2_4),
        (query_tables_function.cs3_4),
        (query_tables_function.cs1_5),
        (query_tables_function.cs2_5),
        (query_tables_function.cs3_5),
        (query_tables_function.cs4_5),
    ]
    c.executemany(
        "INSERT INTO finalprediction  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (my_prediction,),
    )
    print("command executed succesfully")
    conn.commit()
    conn.close()
    # print(my_prediction)
    return render(request, "machinesoccer/append_finalpredictions_to_table.html")


def finalprediction_of_the_day(request):
    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute(
        "SELECT rowid, Date, Hometeam, Awayteam, Home_pg, Away_pg,homewinodds,Drawodds,Awaywinodds FROM 'finalprediction' "
    )
    matches_predicted = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,homewinodds,Drawodds,Awaywinodds FROM 'finalprediction' "
    )
    matches_predicted1 = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,Over15,Under15 FROM 'finalprediction' "
    )
    matches_predicted2 = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,Over25,Under25 FROM 'finalprediction' "
    )
    matches_predicted3 = c.fetchall()

    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,bttsyes,bttsno FROM 'finalprediction' "
    )
    matches_predicted4 = c.fetchall()
    c.execute(
        "SELECT rowid, cs1_0,cs2_0,cs3_0,cs4_0,cs5_0,cs2_1,cs3_1,cs3_2,cs4_1,cs4_2,cs4_3,cs5_1,cs5_2,cs5_3,cs5_4,cs0_0,cs1_1,cs2_2,cs3_3,cs4_4,cs5_5,cs0_1,cs0_2,cs0_3,cs0_4,cs0_5,cs1_2,cs1_3,cs2_3,cs1_4,cs2_4,cs3_4,cs1_5,cs2_5,cs3_5,cs4_5 FROM 'finalprediction' "
    )
    matches_predicted5 = c.fetchall()
    finalforecast = []
    for match in matches_predicted:
        p = (match)[0]
        p1 = (match)[1]
        p2 = (match)[2]
        p3 = (match)[3]
        p4 = (match)[4]
        p5 = (match)[5]
        p6 = (match)[6]
        p7 = (match)[7]
        p8 = (match)[8]

    for match in matches_predicted1:
        q = (match)[0]
        q1 = (match)[1]
        q2 = (match)[2]

    for match in matches_predicted2:
        r = (match)[0]
        r1 = (match)[1]
        r2 = (match)[2]
        r3 = (match)[3]
        r4 = (match)[4]
        r5 = (match)[5]

    for match in matches_predicted3:
        s = (match)[0]
        s1 = (match)[1]
        s2 = (match)[2]
        s3 = (match)[3]
        s4 = (match)[4]
        s5 = (match)[5]
    for match in matches_predicted4:
        t = (match)[0]
        t1 = (match)[1]
        t2 = (match)[2]
        t3 = (match)[3]
        t4 = (match)[4]
        t5 = (match)[5]

    for match4 in matches_predicted5:
        u = (match4)[0]

        u1 = (match4)[1]
        u2 = (match4)[2]
        u3 = (match4)[3]
        u4 = (match4)[4]
        u5 = (match4)[5]
        u6 = (match4)[6]
        u7 = (match4)[7]
        u8 = (match4)[8]
        u9 = (match4)[9]
        u10 = (match4)[10]
        u11 = (match4)[11]
        u12 = (match4)[12]
        u13 = (match4)[13]
        u14 = (match4)[14]
        u15 = (match4)[15]
        u16 = (match4)[16]
        u17 = (match4)[17]
        u18 = (match4)[18]
        u19 = (match4)[19]
        u20 = (match4)[20]
        u21 = (match4)[21]
        u22 = (match4)[22]
        u23 = (match4)[23]
        u24 = (match4)[24]
        u25 = (match4)[25]
        u26 = (match4)[26]
        u27 = (match4)[27]
        u28 = (match4)[28]
        u29 = (match4)[29]
        u30 = (match4)[30]
        u31 = (match4)[31]
        u32 = (match4)[32]
        u33 = (match4)[33]
        u34 = (match4)[34]
        u35 = (match4)[35]
        u36 = (match4)[36]
    finalforecast.append(
        (
            p,
            p1,
            p2,
            p3,
            p4,
            p5,
            p6,
            p7,
            p8,
            q,
            q1,
            q2,
            r,
            r1,
            r2,
            r3,
            r4,
            r5,
            s,
            s1,
            s2,
            s3,
            s4,
            s5,
            t,
            t1,
            t2,
            t3,
            t4,
            t5,
            u,
            u1,
            u2,
            u3,
            u4,
            u5,
            u6,
            u7,
            u8,
            u9,
            u10,
            u11,
            u12,
            u13,
            u14,
            u15,
            u16,
            u17,
            u18,
            u19,
            u20,
            u21,
            u22,
            u23,
            u24,
            u25,
            u26,
            u27,
            u28,
            u29,
            u30,
            u31,
            u32,
            u33,
            u34,
            u35,
            u36,
        )
    )
    print("command executed succesfully")

    stuff_for_frontend = {
        "finalforecast": finalforecast,
    }

    conn.commit()
    conn.close()

    return render(
        request, "machinesoccer/finalprediction_of_the_day.html", stuff_for_frontend
    )


def find_finalprediction_of_the_day(request):
    x = request.POST.get("matchid")
    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute(
        "SELECT rowid, Date, Hometeam, Awayteam, Home_pg, Away_pg,homewinodds,Drawodds,Awaywinodds FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,homewinodds,Drawodds,Awaywinodds FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted1 = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,Over15,Under15 FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted2 = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,Over25,Under25 FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted3 = c.fetchall()

    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,bttsyes,bttsno FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted4 = c.fetchall()
    c.execute(
        "SELECT rowid, cs1_0,cs2_0,cs3_0,cs4_0,cs5_0,cs2_1,cs3_1,cs3_2,cs4_1,cs4_2,cs4_3,cs5_1,cs5_2,cs5_3,cs5_4,cs0_0,cs1_1,cs2_2,cs3_3,cs4_4,cs5_5,cs0_1,cs0_2,cs0_3,cs0_4,cs0_5,cs1_2,cs1_3,cs2_3,cs1_4,cs2_4,cs3_4,cs1_5,cs2_5,cs3_5,cs4_5 FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted5 = c.fetchall()
    finalforecast = []
    for match in matches_predicted:
        p = (match)[0]
        p1 = (match)[1]
        p2 = (match)[2]
        p3 = (match)[3]
        p4 = (match)[4]
        p5 = (match)[5]
        p6 = (match)[6]
        p7 = (match)[7]
        p8 = (match)[8]

    for match in matches_predicted1:
        q = (match)[0]
        q1 = (match)[1]
        q2 = (match)[2]

    for match in matches_predicted2:
        r = (match)[0]
        r1 = (match)[1]
        r2 = (match)[2]
        r3 = (match)[3]
        r4 = (match)[4]
        r5 = (match)[5]

    for match in matches_predicted3:
        s = (match)[0]
        s1 = (match)[1]
        s2 = (match)[2]
        s3 = (match)[3]
        s4 = (match)[4]
        s5 = (match)[5]
    for match in matches_predicted4:
        t = (match)[0]
        t1 = (match)[1]
        t2 = (match)[2]
        t3 = (match)[3]
        t4 = (match)[4]
        t5 = (match)[5]

    for match4 in matches_predicted5:
        u = (match4)[0]

        u1 = (match4)[1]
        u2 = (match4)[2]
        u3 = (match4)[3]
        u4 = (match4)[4]
        u5 = (match4)[5]
        u6 = (match4)[6]
        u7 = (match4)[7]
        u8 = (match4)[8]
        u9 = (match4)[9]
        u10 = (match4)[10]
        u11 = (match4)[11]
        u12 = (match4)[12]
        u13 = (match4)[13]
        u14 = (match4)[14]
        u15 = (match4)[15]
        u16 = (match4)[16]
        u17 = (match4)[17]
        u18 = (match4)[18]
        u19 = (match4)[19]
        u20 = (match4)[20]
        u21 = (match4)[21]
        u22 = (match4)[22]
        u23 = (match4)[23]
        u24 = (match4)[24]
        u25 = (match4)[25]
        u26 = (match4)[26]
        u27 = (match4)[27]
        u28 = (match4)[28]
        u29 = (match4)[29]
        u30 = (match4)[30]
        u31 = (match4)[31]
        u32 = (match4)[32]
        u33 = (match4)[33]
        u34 = (match4)[34]
        u35 = (match4)[35]
        u36 = (match4)[36]
    finalforecast.append(
        (
            p,
            p1,
            p2,
            p3,
            p4,
            p5,
            p6,
            p7,
            p8,
            q,
            q1,
            q2,
            r,
            r1,
            r2,
            r3,
            r4,
            r5,
            s,
            s1,
            s2,
            s3,
            s4,
            s5,
            t,
            t1,
            t2,
            t3,
            t4,
            t5,
            u,
            u1,
            u2,
            u3,
            u4,
            u5,
            u6,
            u7,
            u8,
            u9,
            u10,
            u11,
            u12,
            u13,
            u14,
            u15,
            u16,
            u17,
            u18,
            u19,
            u20,
            u21,
            u22,
            u23,
            u24,
            u25,
            u26,
            u27,
            u28,
            u29,
            u30,
            u31,
            u32,
            u33,
            u34,
            u35,
            u36,
        )
    )
    print("command executed succesfully")

    stuff_for_frontend = {
        "finalforecast": finalforecast,
    }

    conn.commit()
    conn.close()

    return render(
        request, "machinesoccer/finalprediction_of_the_day.html", stuff_for_frontend
    )


def find_finalprediction_of_the_day_prev(request):
    y = request.POST.get("matchid")
    p = int(y)
    x = p - 1

    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute(
        "SELECT rowid, Date, Hometeam, Awayteam, Home_pg, Away_pg,homewinodds,Drawodds,Awaywinodds FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,homewinodds,Drawodds,Awaywinodds FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted1 = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,Over15,Under15 FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted2 = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,Over25,Under25 FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted3 = c.fetchall()

    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,bttsyes,bttsno FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted4 = c.fetchall()
    c.execute(
        "SELECT rowid, cs1_0,cs2_0,cs3_0,cs4_0,cs5_0,cs2_1,cs3_1,cs3_2,cs4_1,cs4_2,cs4_3,cs5_1,cs5_2,cs5_3,cs5_4,cs0_0,cs1_1,cs2_2,cs3_3,cs4_4,cs5_5,cs0_1,cs0_2,cs0_3,cs0_4,cs0_5,cs1_2,cs1_3,cs2_3,cs1_4,cs2_4,cs3_4,cs1_5,cs2_5,cs3_5,cs4_5 FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted5 = c.fetchall()
    finalforecast = []
    for match in matches_predicted:
        p = (match)[0]
        p1 = (match)[1]
        p2 = (match)[2]
        p3 = (match)[3]
        p4 = (match)[4]
        p5 = (match)[5]
        p6 = (match)[6]
        p7 = (match)[7]
        p8 = (match)[8]

    for match in matches_predicted1:
        q = (match)[0]
        q1 = (match)[1]
        q2 = (match)[2]

    for match in matches_predicted2:
        r = (match)[0]
        r1 = (match)[1]
        r2 = (match)[2]
        r3 = (match)[3]
        r4 = (match)[4]
        r5 = (match)[5]

    for match in matches_predicted3:
        s = (match)[0]
        s1 = (match)[1]
        s2 = (match)[2]
        s3 = (match)[3]
        s4 = (match)[4]
        s5 = (match)[5]
    for match in matches_predicted4:
        t = (match)[0]
        t1 = (match)[1]
        t2 = (match)[2]
        t3 = (match)[3]
        t4 = (match)[4]
        t5 = (match)[5]

    for match4 in matches_predicted5:
        u = (match4)[0]

        u1 = (match4)[1]
        u2 = (match4)[2]
        u3 = (match4)[3]
        u4 = (match4)[4]
        u5 = (match4)[5]
        u6 = (match4)[6]
        u7 = (match4)[7]
        u8 = (match4)[8]
        u9 = (match4)[9]
        u10 = (match4)[10]
        u11 = (match4)[11]
        u12 = (match4)[12]
        u13 = (match4)[13]
        u14 = (match4)[14]
        u15 = (match4)[15]
        u16 = (match4)[16]
        u17 = (match4)[17]
        u18 = (match4)[18]
        u19 = (match4)[19]
        u20 = (match4)[20]
        u21 = (match4)[21]
        u22 = (match4)[22]
        u23 = (match4)[23]
        u24 = (match4)[24]
        u25 = (match4)[25]
        u26 = (match4)[26]
        u27 = (match4)[27]
        u28 = (match4)[28]
        u29 = (match4)[29]
        u30 = (match4)[30]
        u31 = (match4)[31]
        u32 = (match4)[32]
        u33 = (match4)[33]
        u34 = (match4)[34]
        u35 = (match4)[35]
        u36 = (match4)[36]
    finalforecast.append(
        (
            p,
            p1,
            p2,
            p3,
            p4,
            p5,
            p6,
            p7,
            p8,
            q,
            q1,
            q2,
            r,
            r1,
            r2,
            r3,
            r4,
            r5,
            s,
            s1,
            s2,
            s3,
            s4,
            s5,
            t,
            t1,
            t2,
            t3,
            t4,
            t5,
            u,
            u1,
            u2,
            u3,
            u4,
            u5,
            u6,
            u7,
            u8,
            u9,
            u10,
            u11,
            u12,
            u13,
            u14,
            u15,
            u16,
            u17,
            u18,
            u19,
            u20,
            u21,
            u22,
            u23,
            u24,
            u25,
            u26,
            u27,
            u28,
            u29,
            u30,
            u31,
            u32,
            u33,
            u34,
            u35,
            u36,
        )
    )
    print("command executed succesfully")

    stuff_for_frontend = {
        "finalforecast": finalforecast,
    }

    conn.commit()
    conn.close()

    return render(
        request, "machinesoccer/finalprediction_of_the_day.html", stuff_for_frontend
    )


def find_finalprediction_of_the_day_next(request):
    y = request.POST.get("matchid")
    p = int(y)
    x = p + 1

    conn = sqlite3.connect("soccer.db")
    c = conn.cursor()
    c.execute(
        "SELECT rowid, Date, Hometeam, Awayteam, Home_pg, Away_pg,homewinodds,Drawodds,Awaywinodds FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,homewinodds,Drawodds,Awaywinodds FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted1 = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,Over15,Under15 FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted2 = c.fetchall()
    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,Over25,Under25 FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted3 = c.fetchall()

    c.execute(
        "SELECT rowid,Date, Hometeam,Awayteam,bttsyes,bttsno FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted4 = c.fetchall()
    c.execute(
        "SELECT rowid, cs1_0,cs2_0,cs3_0,cs4_0,cs5_0,cs2_1,cs3_1,cs3_2,cs4_1,cs4_2,cs4_3,cs5_1,cs5_2,cs5_3,cs5_4,cs0_0,cs1_1,cs2_2,cs3_3,cs4_4,cs5_5,cs0_1,cs0_2,cs0_3,cs0_4,cs0_5,cs1_2,cs1_3,cs2_3,cs1_4,cs2_4,cs3_4,cs1_5,cs2_5,cs3_5,cs4_5 FROM 'finalprediction' WHERE rowid = ?",
        (x,),
    )
    matches_predicted5 = c.fetchall()
    finalforecast = []
    for match in matches_predicted:
        p = (match)[0]
        p1 = (match)[1]
        p2 = (match)[2]
        p3 = (match)[3]
        p4 = (match)[4]
        p5 = (match)[5]
        p6 = (match)[6]
        p7 = (match)[7]
        p8 = (match)[8]

    for match in matches_predicted1:
        q = (match)[0]
        q1 = (match)[1]
        q2 = (match)[2]

    for match in matches_predicted2:
        r = (match)[0]
        r1 = (match)[1]
        r2 = (match)[2]
        r3 = (match)[3]
        r4 = (match)[4]
        r5 = (match)[5]

    for match in matches_predicted3:
        s = (match)[0]
        s1 = (match)[1]
        s2 = (match)[2]
        s3 = (match)[3]
        s4 = (match)[4]
        s5 = (match)[5]
    for match in matches_predicted4:
        t = (match)[0]
        t1 = (match)[1]
        t2 = (match)[2]
        t3 = (match)[3]
        t4 = (match)[4]
        t5 = (match)[5]

    for match4 in matches_predicted5:
        u = (match4)[0]

        u1 = (match4)[1]
        u2 = (match4)[2]
        u3 = (match4)[3]
        u4 = (match4)[4]
        u5 = (match4)[5]
        u6 = (match4)[6]
        u7 = (match4)[7]
        u8 = (match4)[8]
        u9 = (match4)[9]
        u10 = (match4)[10]
        u11 = (match4)[11]
        u12 = (match4)[12]
        u13 = (match4)[13]
        u14 = (match4)[14]
        u15 = (match4)[15]
        u16 = (match4)[16]
        u17 = (match4)[17]
        u18 = (match4)[18]
        u19 = (match4)[19]
        u20 = (match4)[20]
        u21 = (match4)[21]
        u22 = (match4)[22]
        u23 = (match4)[23]
        u24 = (match4)[24]
        u25 = (match4)[25]
        u26 = (match4)[26]
        u27 = (match4)[27]
        u28 = (match4)[28]
        u29 = (match4)[29]
        u30 = (match4)[30]
        u31 = (match4)[31]
        u32 = (match4)[32]
        u33 = (match4)[33]
        u34 = (match4)[34]
        u35 = (match4)[35]
        u36 = (match4)[36]
    finalforecast.append(
        (
            p,
            p1,
            p2,
            p3,
            p4,
            p5,
            p6,
            p7,
            p8,
            q,
            q1,
            q2,
            r,
            r1,
            r2,
            r3,
            r4,
            r5,
            s,
            s1,
            s2,
            s3,
            s4,
            s5,
            t,
            t1,
            t2,
            t3,
            t4,
            t5,
            u,
            u1,
            u2,
            u3,
            u4,
            u5,
            u6,
            u7,
            u8,
            u9,
            u10,
            u11,
            u12,
            u13,
            u14,
            u15,
            u16,
            u17,
            u18,
            u19,
            u20,
            u21,
            u22,
            u23,
            u24,
            u25,
            u26,
            u27,
            u28,
            u29,
            u30,
            u31,
            u32,
            u33,
            u34,
            u35,
            u36,
        )
    )
    print("command executed succesfully")

    stuff_for_frontend = {
        "finalforecast": finalforecast,
    }

    conn.commit()
    conn.close()

    return render(
        request, "machinesoccer/finalprediction_of_the_day.html", stuff_for_frontend
    )


# def perform_magic(request):
#     position = request.POST.get("position")
#     n = int(position)
#     position1 = request.POST.get("position1")
#     w = int(position1)
#     query_tables_function("n", "w")
#     # append_finalpredictions_to_table()
#     # finalprediction_of_the_day()
#     return render(request, "machinesoccer/new_search.html")


# def clear_insert(request):
#     clear_tables_function()
#     insert_into_db_tables()
#     return render(request, "machinesoccer/new_search.html")


# clear_item_in_prediction_table("4")

# clear_prediction_table()

# clear_tables_function()
# insert_into_db_tables()

# clear_insert()
# perform_magic()
# finalprediction_of_the_day()


# create_prediction_table()


# drop_prediction_table()


# print(away_score_1)
# print(away_score_2)
# print(home_score_1)
# c.execute("DROP table 'finalprediction' ")
# team = c.fetchone()
# teams = team[6]
# teams1 = team[7]
# result = teams[0] / (2)
# exact = poisson.pmf(1, 1.62345)
# print(exact)
# print(team)
# print(teams)

# print(teams1)
# print(result)

# for team in teams:
#     print(
#         team[0], team[1], team[2], team[3], team[4], team[5], team[6], team[7], team[8]
#     )
# print(c.fetchone())
# print(c.fetchmany(3))
# print("command executed succesfully")
# Datatypes:
# NULL
# INTEGER
# BLOB
# REAL
# TEXT

# commit the command
# conn.commit()
# close the connection
# conn.close()

# Create your views here.
