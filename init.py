import load

if __name__ == "__main__":
    print("Initializing scoreboard database and filling with API data")
    load.setup_db()
    load.load_teams()
    load.load_team_scoreboard()
    load.load_players()