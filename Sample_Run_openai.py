from Utilities import *
import json

with open("Keys/basic_data.json", "r") as file:
    data = json.load(file)

x = openAIResponse(data["openAi_Key"], 'How do i import image or video through openapi python')
print(x)