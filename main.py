import json
import os
import sqlite3
import requests
from dotenv import load_dotenv

TEAM_LIST_URL = "https://api.nhle.com/stats/rest/en/team"
SCHEDULE_URL = "https://api-web.nhle.com/v1/scoreboard/tor/now"
PLAYERS_URL = "https://api-web.nhle.com/v1/roster/tor/20242025"

conn = sqlite3.connect('scoreclock.db')  # Creates a new database file if it doesn’t exist


def setup_db():
    # cursor = conn.cursor()
    # Create teams table
    conn.execute('''CREATE TABLE IF NOT EXISTS teams(
    id INTEGER,
    franchiseId INTEGER,
    fullName TEXT,
    triCode TEXT,
    logoLink TEXT);''')

    conn.execute(''' CREATE UNIQUE INDEX IF NOT EXISTS TeamId ON teams (id)  ''')

    # Create schedule table
    # https://www.postman.com/telecoms-participant-38756299/nhl-api/request/6bcqoi1/team-schedule?action=share&source=copy-link&creator=17590512&active-environment=5fb916f5-4f2b-4470-a9c2-852c88d2b63d
    conn.execute('''CREATE TABLE IF NOT EXISTS schedule(
    id INTEGER,
    season INTEGER,
    gameType INTEGER,
    gameDate TEXT,
    gameCenterLink TEXT,
    venue TEXT,
    startTimeUTC TEXT,
    awayTeamId INTEGER,
    awayTeamScore INTEGER,
    homeTeamId INTEGER,
    homeTeamScore INTEGER,
    threeMinRecap TEXT);''')

    conn.execute(''' CREATE UNIQUE INDEX IF NOT EXISTS ScheduleId ON schedule (id)  ''')

    # Create boxscore table
    # https://www.postman.com/telecoms-participant-38756299/nhl-api/example/17726769-4c903f06-9dfb-4dbd-b4dc-a8a044948120?action=share&source=copy-link&creator=17590512&active-environment=5fb916f5-4f2b-4470-a9c2-852c88d2b63d
    conn.execute('''CREATE TABLE IF NOT EXISTS boxscore(
    id INTEGER,
    period INTEGER,
    periodType TEXT,
    timeRemaining TEXT,
    secondsRemaining INTEGER,
    running BOOL,
    inIntermission BOOL,
    awayTeamScore INTEGER,
    awayTeamSOG INTEGER,
    awayTeamPIM INTEGER,
    awayTeamHits INTEGER,
    awayTeamFaceoffWin REAL,
    homeTeamScore INTEGER,
    homeTeamSOG INTEGER,
    homeTeamPIM INTEGER,
    homeTeamHits INTEGER,
    homeTeamFaceoffWin REAL);''')

    conn.execute(''' CREATE UNIQUE INDEX IF NOT EXISTS BoxScoreId ON boxscore (id)  ''')

    # Create players table
    # https://www.postman.com/telecoms-participant-38756299/nhl-api/example/17726769-8e43a4e4-0b2c-4d29-8ff0-de26ba54e01e?action=share&source=copy-link&creator=17590512&active-environment=5fb916f5-4f2b-4470-a9c2-852c88d2b63d
    conn.execute('''CREATE TABLE IF NOT EXISTS players(
    playerId INTEGER,
    currentTeamId INTEGER,
    firstName TEXT,
    lastName TEXT,
    position TEXT,
    sweaterNumber INTEGER,
    headshot TEXT,
    heroImage TEXT
    );''')

    conn.execute(''' CREATE UNIQUE INDEX IF NOT EXISTS PlayersPlayerId ON players (playerId)  ''')


# https://www.postman.com/telecoms-participant-38756299/nhl-api/request/s66qexc/team-list?action=share&source=copy-link&creator=17590512&active-environment=5fb916f5-4f2b-4470-a9c2-852c88d2b63d
def load_teams():
    api_response = requests.get(
        TEAM_LIST_URL,
    )
    api_response.raise_for_status()
    payload = api_response.json()
    # print(payload)

    # Insert each row; skip duplicates using INSERT OR IGNORE
    for team in payload['data']:
        # print(team)
        columns = "id, franchiseId, fullName, triCode"
        placeholders = "?, ?, ?, ?"
        values = [team['id'], team['franchiseId'], team['fullName'], team['triCode']]

        query = f"INSERT OR IGNORE INTO teams ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)

        conn.commit()


def load_team_schedule():
    load_dotenv()
    api_response = requests.get(
        SCHEDULE_URL,
    )
    api_response.raise_for_status()
    payload = api_response.json()
    # print(payload)

    # Insert each row; skip duplicates using INSERT OR IGNORE
    for games in payload['gamesByDate']:
        # print(games)
        record = games["games"][0]
        print(record)
        columns = "id, season, gameType, gameDate, gameCenterLink, venue, startTimeUTC, awayTeamId, awayTeamScore, homeTeamId, homeTeamScore, threeMinRecap"
        placeholders = "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?"

        try:
            threeMinRecap = record['threeMinRecap']
        except KeyError:
            record['threeMinRecap'] = ''
        try:
            score = record['awayTeam']['score']
        except KeyError:
            record['awayTeam']['score'] = 0
            record['homeTeam']['score'] = 0

        values = [record['id'], record['season'], record['gameType'], record['gameDate'], record['gameCenterLink'],
                  record['venue']['default'], record['startTimeUTC'], record['awayTeam']['id'],
                  record['awayTeam']['score'], record['homeTeam']['id'], record['homeTeam']['score'],
                  record['threeMinRecap']]

        print(values)
        query = f"INSERT OR IGNORE INTO schedule ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)

        conn.commit()


# https://www.postman.com/telecoms-participant-38756299/nhl-api/request/s66qexc/team-list?action=share&source=copy-link&creator=17590512&active-environment=5fb916f5-4f2b-4470-a9c2-852c88d2b63d
def load_players():
    api_response = requests.get(
        PLAYERS_URL,
    )
    api_response.raise_for_status()
    payload = api_response.json()
    placeholders = "?, ?, ?, ?, ?, ?, ?"

    for player in payload['forwards']:
        columns = "playerId, currentTeamId, firstName, lastName, position, sweaterNumber, headshot"
        values = [player['id'], '', player['firstName']['default'], player['lastName']['default'],
                  player['positionCode'], player['sweaterNumber'], player['headshot']]
        query = f"INSERT OR IGNORE INTO players ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)

    for player in payload['defensemen']:
        columns = "playerId, currentTeamId, firstName, lastName, position, sweaterNumber, headshot"
        values = [player['id'], '', player['firstName']['default'], player['lastName']['default'],
                  player['positionCode'], player['sweaterNumber'], player['headshot']]
        query = f"INSERT OR IGNORE INTO players ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)

    for player in payload['goalies']:
        columns = "playerId, currentTeamId, firstName, lastName, position, sweaterNumber, headshot"
        values = [player['id'], '', player['firstName']['default'], player['lastName']['default'],
                  player['positionCode'], player['sweaterNumber'], player['headshot']]
        query = f"INSERT OR IGNORE INTO players ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)

        conn.commit()


# setup_db()
# load_teams()
# load_team_schedule()
load_players()
conn.close()
