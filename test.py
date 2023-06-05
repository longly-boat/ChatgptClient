import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ChatgptClient import *

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
            'border-width: 3px;border-style: solid;border-radius: 8px; color:white;border-color: gray;')
        self.nameLabel.setFont(QFont("Ya hei",15))
        # 用来显示avator(图像)
        # 设置图像源 和 图像大小
        # 设置布局用来对nameLabel和avatorLabel进行布局
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.nameLabel)
        self.hbox.addStretch(1)
        # 设置widget的布局
        self.widget.setLayout(self.hbox)
        # 设置自定义的QListWidgetItem的sizeHint，不然无法显示
        self.setSizeHint(self.widget.sizeHint())


class MyWindow(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super(MyWindow,self).__init__(parent)
        self.setupUi(self)
        self.setFixedSize(self.width(),self.height())

        width=self.HistoryView.widthMM()

        item1 = customQListWidgetItem("    ➕ 开启新对话   ")

        self.HistoryView.addItem(item1)
        self.HistoryView.setItemWidget(item1, item1.widget)
        #self.HistoryView.itemClicked.connect(lambda item: print(item.nameLabel.text()))

    def sendMessage(self,string):
        str=string


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
