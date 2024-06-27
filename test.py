import json

top20 = json.load(open("data/gokz/json/top20_players.json"))
players = [player['steamid'] for player in top20]
print(players, sep=', ')