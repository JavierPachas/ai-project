from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# test the health check endpoint
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API health check successful"}


# test /v0/players/
def test_read_players():
    response = client.get("/v0/players/?skip=0&limit=10000")
    assert response.status_code == 200
    assert len(response.json()) == 1018


def test_read_players_by_name():
    response = client.get("/v0/players/?first_name=Bryce&last_name=Young")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0].get("player_id") == 2009
    assert len(response.json()[0].get("performances")) == 17


# test /v0/players/{player_id}/
def test_read_players_with_id():
    response = client.get("/v0/players/1001/")
    assert response.status_code == 200
    assert response.json().get("player_id") == 1001



# test /v0/performances/
def test_read_performances():
    response = client.get("/v0/performances/?skip=0&limit=20000")
    assert response.status_code == 200
    assert len(response.json()) == 17306


# test /v0/performances/ with changed date
def test_read_performances_by_date():
    response = client.get(
        "/v0/performances/?skip=0&limit=20000&minimum_last_changed_date=2024-04-01"
    )
    assert response.status_code == 200
    assert len(response.json()) == 2711


# test /v0/leagues/{league_id}/
def test_read_leagues_with_id():
    response = client.get("/v0/leagues/5002/")
    assert response.status_code == 200
    assert len(response.json()["teams"]) == 8


# test /v0/leagues/
def test_read_leagues():
    response = client.get("/v0/leagues/?skip=0&limit=500")
    assert response.status_code == 200
    assert len(response.json()) == 5 


# test /v0/teams/
def test_read_teams():
    response = client.get("/v0/teams/?skip=0&limit=500")
    assert response.status_code == 200
    assert len(response.json()) == 52 #v0.2


# test /v0/teams/
def test_read_teams_for_one_league():
    response = client.get("/v0/teams/?skip=0&limit=500&league_id=5001")
    assert response.status_code == 200
    assert len(response.json()) == 12

#v0.2 test added weeks object
def test_read_one_team():
    response = client.get("/v0/teams/?skip=0&limit=500&team_name=?skip=0&limit=100&team_name=Wallaby%20Stew")
    assert response.status_code == 200
    teams = response.json()
    assert len(teams) == 1
    my_team = teams[0]
    assert my_team.get("team_name") == "Wallaby Stew"
    assert len(my_team.get("weekly_scores")) == 17
    assert len(my_team.get("players")) == 7


# test the count functions
def test_counts():
    response = client.get("/v0/counts/")
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["league_count"] == 5
    assert response_data["team_count"] == 52 #v0.2
    assert response_data["player_count"] == 1018
    assert response_data["week_count"] == 18 #v0.2

#v0.2
def test_read_weeks():
    response = client.get("/v0/weeks/?skip=0&limit=1000")
    assert response.status_code == 200
    assert len(response.json()) == 18 #v0.2