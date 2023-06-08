import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
# from ChatgptClient import *
from settingpage import *
from chatgpt import *
import markdown


class customQListWidgetItem(QListWidgetItem):
    def __init__(self, name):
        super().__init__()
        # 自定义item中的widget 用来显示自定义的内容
        self.widget = QWidget()
        # 用来显示name
        self.nameLabel = QLabel()
        self.nameLabel.setText(name)
        # self.nameLabel.setStyleSheet("border:white 1px solid; color:white")
        self.nameLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.nameLabel.setStyleSheet(
            'QLabel{border-width: 3px;border-style: solid;border-radius: 8px; color:white;border-color: gray;}'
            'QLabel:hover{border-width: 3px;border-style: solid;border-radius: 8px; color:white;border-color: gray;background-color:rgb(191,191,191);}'
        )
        self.nameLabel.setFont(QFont("Ya hei", 15))

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.nameLabel)
        self.hbox.addStretch(1)
        # 设置widget的布局
        self.widget.setLayout(self.hbox)
        # 设置自定义的QListWidgetItem的sizeHint，不然无法显示
        self.setSizeHint(self.widget.sizeHint())


class ChatThread(QThread):
    end=pyqtSignal(str, bool)
    setName=pyqtSignal(str)
    sessionName=""
    str=""
    def __init__(self,parent=None):
        super(ChatThread, self).__init__(parent)
        self.count = 0

    def setChat(self,sessionName,str,chatHistorys):
        self.sessionName=sessionName
        self.str=str
        self.chatHistorys = chatHistorys

    def resetCount(self):
        self.count = 0

    def setChatHistorys(self, chatHistorys):
        self.chatHistorys = chatHistorys

    def run(self):

        if self.sessionName == "":
            newchat, self.sessionName ,answer= getNewChat(self.str)
            self.chatHistorys[self.sessionName]=newchat
            self.end.emit(answer, False)
            self.setName.emit(self.sessionName)
            saveHistory(self.sessionName, answer)
        else:
            self.chatHistorys[self.sessionName].append({"role": "user", "content": self.str})
            answer=chat(self.chatHistorys[self.sessionName])
            self.end.emit(answer, False)
            saveHistory(self.sessionName, answer)



class settingDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(settingDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("设置")
        if os.path.isfile("Config.yml") == True:
            with open('Config.yml', 'r') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
            self.proxy.setText(config['proxy'])
            self.APIKEY.setText(config["APIKEY"])


    def saveSetting(self):
        key = self.APIKEY.text()
        proxy = self.proxy.text()
        index = self.model.currentIndex()
        model = self.model.itemText(index)
        config = {
            "APIKEY": key,
            "proxy": proxy,
            "model": model,
        }
        with open('./Config.yml', 'w', encoding='utf-8') as f:
            yaml.dump(data=config, stream=f, allow_unicode=True)
        self.close()
        getConfig()
    def reshow(self):
        if os.path.isfile("Config.yml") == True:
            with open('Config.yml', 'r') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
            self.proxy.setText(config['proxy'])
            self.APIKEY.setText(config["APIKEY"])
        self.show()

# 定义新聊天消息格式
class ChatItem(QWidget):
    def __init__(self, avatar, text, parent=None):
        super(ChatItem, self).__init__(parent)
        self.layout = QHBoxLayout(self)

        self.avatarLabel = QLabel(self)
        self.avatarLabel.setPixmap(QPixmap(avatar))

        self.textLabel = QTextEdit()
        # 只读
        self.textLabel.setReadOnly(True)
        # 解析markdown
        html = markdown.markdown(text, extensions=['fenced_code'])
        self.textLabel.setHtml(html)

        self.layout.addWidget(self.avatarLabel)
        self.layout.addWidget(self.textLabel)


class MyWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        # 直接加载UI文件，不需要ChatgptClient.py文件了
        self.ui = uic.loadUi("./ChatgptClient.ui", self)  # 加载UI文件
        self.setWindowTitle("ChatGPT客户端")
        # self.setFixedSize(self.width(),self.height())
        width = self.HistoryView.widthMM()
        item1 = customQListWidgetItem("➕开启新对话")
        self.HistoryView.addItem(item1)
        self.HistoryView.setItemWidget(item1, item1.widget)
        self.HistoryView.itemClicked.connect(self.NewSession)
        self.sessionName = ""
        getConfig()
        self.chatThread=ChatThread()
        self.chatThread.end.connect(self.updateChatlist)
        self.chatThread.setName.connect(self.setSessionName)
        self.newChatWindow.triggered.connect(self.newWindow)
        # 在每个窗口中创建一个新的settingDialog实例
        self.setting = settingDialog()
        self.actionSetting.triggered.connect(self.setting.reshow)

        self.chatHistorys = {}  # 创建一个新的chatHistorys字典

        #回车发送文本
        self.chatbox.textChanged.connect(self.text_changed)

    #回车发送文本
    def text_changed(self):
        # 每当文本框内容发生改变一次，该方法即执行一次
        msg = self.chatbox.toPlainText()  # 首先在这里拿到文本框内容
        if '\n' in msg:
            # 做一个判断，textedit默认按回车换行，本质是在后面加了一个\n，那我们判断换行的根据就是判断\n是否在我那本框中，如果在，OK，那下一步
            msg = msg.replace('\n', '')  # 将文本框的\n清除掉
            self.chatbox.setText(msg)  # 将处理后的内容重新放入文本框
            self.sendMessage()

    def NewSession(self):
        self.chatlist.clear()
        self.chatbox.clear()
        self.sessionName = ""

    def sendMessage(self):
        str = self.chatbox.toPlainText()
        self.chatbox.clear()
        self.updateChatlist(str, True)
        self.chatThread.setChat(self.sessionName,str, self.chatHistorys)
        self.chatThread.start()

    def setSessionName(self,sessionName):
        self.sessionName=sessionName

    def newWindow(self):
        new_window = MyWindow()
        new_window.chatThread.setChatHistorys(new_window.chatHistorys)
        new_window.show()

    def updateChatlist(self, str, is_user):
        # 根据消息是来自用户还是GPT来设置不同的头像
        avatar = "user.png" if is_user else "gpt.png"

        # 创建一个新的聊天项
        chatItem = ChatItem(avatar, str)
        item = QListWidgetItem()
        item.setSizeHint(chatItem.sizeHint())

        self.chatlist.addItem(item)
        self.chatlist.setItemWidget(item, chatItem)

        # 添加自动滚动到下方
        self.chatlist.setCurrentRow(self.chatlist.count() - 1)


    def changeSession(self, sessionName):
        self.sessionName = sessionName
        messages = readHistory(sessionName)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWindow()
    # 展示窗口
    w.ui.show()
    sys.exit(app.exec_())
