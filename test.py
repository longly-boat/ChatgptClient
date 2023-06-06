import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ChatgptClient import *
from settingpage import *
from chatgpt import *

chatHistorys = {}


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

    end=pyqtSignal(str)
    sessionName=""
    str=""
    def __init__(self,parent=None):
        super(ChatThread, self).__init__(parent)
        self.count = 0

    def setChat(self,sessionName,str):
        self.sessionName=sessionName
        self.str=str

    def resetCount(self):
        self.count = 0

    def run(self):

        if self.sessionName == "":
            newchat, self.sessionName ,answer= getNewChat(self.str)
            chatHistorys[self.sessionName]=newchat
            self.end.emit(answer)
        else:
            chatHistorys[self.sessionName].append({"role": "user", "content": self.str})
            answer=chat(chatHistorys[self.sessionName])
            self.end.emit(answer)



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


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("ChatGPT客户端")
        # self.setFixedSize(self.width(),self.height())
        width = self.HistoryView.widthMM()
        item1 = customQListWidgetItem("    ➕ 开启新对话   ")
        self.HistoryView.addItem(item1)
        self.HistoryView.setItemWidget(item1, item1.widget)
        self.HistoryView.itemClicked.connect(self.NewSession)
        self.sessionName = ""
        getConfig()
        self.chatThread=ChatThread()
        self.chatThread.end.connect(self.updateChatlist)

    def NewSession(self):
        self.chatlist.clear()
        self.chatbox.clear()
        self.sessionName = ""

    def sendMessage(self):
        str = self.chatbox.toPlainText()
        self.chatbox.clear()
        self.updateChatlist(str)
        self.chatbox.update()
        self.chatThread.setChat(self.sessionName,str)
        self.chatThread.start()



    def updateChatlist(self, str):
        message = QListWidgetItem()
        message.setText(str)

        self.chatlist.addItem(message)


    def changeSession(self, sessionName):
        self.sessionName = sessionName
        messages = readHistory(sessionName)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    setting = settingDialog()
    w.actionSetting.triggered.connect(setting.show)
    sys.exit(app.exec_())
