import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ChatgptClient import *
from settingpage import *
from chatgpt import *
import markdown

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
    setName=pyqtSignal(str)
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
            self.setName.emit(self.sessionName)
        else:
            chatHistorys[self.sessionName].append({"role": "user", "content": self.str})
            answer=chat(chatHistorys[self.sessionName])
            self.end.emit(answer)
        saveHistory(self.sessionName, chatHistorys)



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
        self.chatThread.setName.connect(self.setSessionName)

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
        self.updateChatlist(str)
        self.chatbox.update()
        self.chatThread.setChat(self.sessionName,str)
        self.chatThread.start()

    def setSessionName(self,sessionName):
        self.sessionName=sessionName


    def updateChatlist(self, str):
        # 解析的文本
        markdown_text = str
        text_edit1 = QTextEdit()
        # 只读
        text_edit1.setReadOnly(True)

        # 解析markdown
        html1 = markdown.markdown(markdown_text, extensions=['fenced_code'])
        text_edit1.setHtml(html1)
        item1 = QListWidgetItem()

        item1.setSizeHint(text_edit1.sizeHint())  # 设置 QListWidgetItem 的大小
        self.chatlist.addItem(item1)
        self.chatlist.setItemWidget(item1, text_edit1)
        #添加自动滚动到下方
        self.chatlist.setCurrentRow(self.chatlist.count()-1)


    def changeSession(self, sessionName):
        self.sessionName = sessionName
        messages = readHistory(sessionName)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    setting = settingDialog()
    w.actionSetting.triggered.connect(setting.reshow)
    sys.exit(app.exec_())