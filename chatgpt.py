import copy
import os
import pickle

import eventlet as eventlet
import openai
import yaml

os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
openai.api_key=""
model="gpt-3.5-turbo"
originMessages = [{"role": "system", "content": "你是一个人工智能助手"}]
def saveHistory(filename,message):
    file="history/"+filename+".pickle"
    folder = os.path.exists("history")
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs("history")  # makedirs 创建文件时如果路径不存在会创建这个路径

    with open(file, 'wb') as f:
        pickle.dump(message, f)

def readHistory(filename):
    file = "history/"+filename + ".pickle"
    folder = os.path.exists("history")
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs("history")  # makedirs 创建文件时如果路径不存在会创建这个路径
    with open(file, 'rb') as f:
        messages = pickle.load(f)
    return messages

def getConfig():
    if os.path.isfile("Config.yml")==True:
        with open('Config.yml', 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        os.environ["http_proxy"] = config['proxy']
        os.environ["https_proxy"] = config['proxy']
        openai.api_key=config["APIKEY"]

def chat(message):

    try:
        with eventlet.Timeout(60):
            completion = openai.ChatCompletion.create(
                model=model,
                temperature=0.8,
                messages=message
            )
            answer = completion.choices[0].message['content']
            message.append({"role": "assistant", "content": answer})
            return answer
    except :
        answer="api调用失败，请检测网络代理或apikey配置是否正确"
        return answer





def getTitle(message):
    newchat = copy.deepcopy(message)
    newchat.append({"role": "user", "content": "给以上对话取一个短标题"})
    title=chat(newchat)
    return title

def getNewChat(newchat):
    messages = [{"role": "system", "content": "你是一个人工智能助手"}]
    messages.append({"role": "user", "content": newchat})


    try:
        with eventlet.Timeout(90):
            title = getTitle(messages)
            completion = openai.ChatCompletion.create(
                model=model,
                temperature=0.8,
                messages=messages
            )
            answer = completion.choices[0].message['content']

            messages.append({"role": "assistant", "content": answer})
            return messages, title, answer
    except :
        answer="api调用失败，请检测网络代理或apikey配置是否正确"
        title="失败会话"
        return messages, title, answer
