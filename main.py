from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5 import uic
from utils.category_functions import add_category, delete_category
from utils.file_functions import ImageViewer
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
        self.addButton.clicked.connect(lambda: add_category(self.listWidget))
        self.deleteButton.clicked.connect(lambda: delete_category(self.listWidget))

        self.openFile.triggered.connect(lambda: self.myGraphicsViewInstance.openImageFolder())
        self.saveFile.triggered.connect(lambda: self.myGraphicsViewInstance.saveAnnotationsToFile())


        self.pointButton.clicked.connect(lambda: self.myGraphicsViewInstance.onPointButtonClick())

        self.deleteButton2.clicked.connect(lambda: self.myGraphicsViewInstance.deleteAnnotation())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_E:
            self.myGraphicsViewInstance.isPointButtonClicked = False
            self.myGraphicsViewInstance.graphicsView.setCursor(QCursor(Qt.ArrowCursor))
            self.myGraphicsViewInstance.finishAnnotation()
        if event.key() == Qt.Key_Z:
            self.myGraphicsViewInstance.undoLastPoint()  
        



if __name__ == '__main__':
    app = QApplication([])
    win = MainWindow()
    
    win.show()
    app.exec_()

