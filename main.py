from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5 import uic
from utils.category_functions import add_category, delete_category
from utils.file_functions_sam import ImageViewer
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor



Ui_MainWindow, BaseClass = uic.loadUiType("main.ui")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.myGraphicsViewInstance = ImageViewer(self.listWidget3,self.listWidget,self.listWidget2,self.textEdit, self.graphicsView)
        self.listWidget.setCurrentRow(1)  


    def initUI(self):
        # 添加类别和删除类别的按钮
        self.addButton.clicked.connect(lambda: add_category(self.listWidget))
        self.deleteButton.clicked.connect(lambda: delete_category(self.listWidget))

        # 添加图片文件夹的按钮
        self.openFile.triggered.connect(lambda: self.myGraphicsViewInstance.openImageFolder())
        self.saveFile.triggered.connect(lambda: self.myGraphicsViewInstance.saveAnnotationsToFile())


        #点击图片标注按钮
        self.pointButton.clicked.connect(lambda: self.myGraphicsViewInstance.onPointButtonClick())

        #点击删除标注按钮
        self.deleteButton2.clicked.connect(lambda: self.myGraphicsViewInstance.deleteAnnotation())

    #按e键位结束标注
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_E:
            self.myGraphicsViewInstance.isPointButtonClicked = False
            self.myGraphicsViewInstance.graphicsView.setCursor(QCursor(Qt.ArrowCursor))
            self.myGraphicsViewInstance.finishAnnotation()
        if event.key() == Qt.Key_Z:
            self.myGraphicsViewInstance.undoLastPoint()  # 调用 ImageViewer 类中的方法撤销最后一个点
        



if __name__ == '__main__':
    app = QApplication([])
    win = MainWindow()
    
    win.show()
    app.exec_()

