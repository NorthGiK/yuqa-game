import json


with open("static/default_pass.json", "r") as file:
    pass_ = json.load(file)

for key in range(10, 51, 10):
    pass_[str(key)] = {
        "type": "gold_pit",
        "count": 1,
    }


with open("static/default_pass.json", "w") as file:
    json.dump(pass_, file)
