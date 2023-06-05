# import os
# import openai
# os.environ["http_proxy"] = "http://127.0.0.1:10809"
# os.environ["https_proxy"] = "http://127.0.0.1:10809"
# openai.api_key = "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"
# messages = [{"role": "system", "content": "你是一个人工智能助手"}]
# while(1):
#     print("用户:",end="")
#     message=input()
#     messages.append({"role":"user","content":message})
#     print("CHATGPT:",end="")
#     completion = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         temperature=0.8,
#         messages=messages
#     )
#     answer = completion.choices[0].message['content']
#     messages.append({"role":"assistant","content":answer})
#
#     print(messages)
#     print(answer)
import os
import pickle

import openai
import yaml

os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
openai.api_key=""
model="gpt-3.5-turbo"
originMessages = [{"role": "system", "content": "你是一个人工智能助手"}]
def saveHistory(filename,message):
    file="history/"+filename+".pickle"
    with open(file, 'wb') as f:
        pickle.dump(message, f)

def readHistory(filename):
    file = "history/"+filename + ".pickle"
    with open(file, 'rb') as f:
        messages = pickle.load(f)
    return messages

def getConfig():
    if os.path.isfile("test-data")==True:
        with open('Config.yml', 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        os.environ["http_proxy"] = config['proxy']
        os.environ["https_proxy"] = config['proxy']
        openai.api_key=config["APIKEY"]



