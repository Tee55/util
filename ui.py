from ast import For
import sys
from PyQt5.QtWidgets import *
import os
from module.formatter import Formatter
from module.updater import Updater
        
class FormatterPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.combobox = QComboBox()
        self.combobox.addItems(["content", "author", "category", "collection"])
        
        self.textbox_sourcePath = QLineEdit(self)
        self.textbox_sourcePath.setReadOnly(True)
        
        self.btn_sourcePath = QPushButton("Select Source Folder")
        self.btn_sourcePath.clicked.connect(self.openSourcePath)
        
        self.btn_getstart = QPushButton("Get Start")
        self.btn_getstart.clicked.connect(self.get_start)

        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        
        layout.addWidget(self.combobox)
        layout.addWidget(self.textbox_sourcePath)
        layout.addWidget(self.btn_sourcePath)
        layout.addWidget(self.btn_getstart)
        layout.addWidget(self.progressBar)
        
        self.error_dialog = QErrorMessage()
         
    def get_start(self):
        formatter = Formatter()
        if self.combobox.currentText() == "content":

            print("here")
            if os.path.basename(self.sourcePath) in ["r18", "norm"]:
                formatter.clean(self.sourcePath)
            else:
                print("{}: This is not content folder.".format(self.sourcePath))
        elif self.combobox.currentText() == "author":
            if os.path.basename(self.sourcePath) not in ["r18", "norm"]:
                author = os.path.basename(self.sourcePath)
                formatter.cleanRecur(author, self.sourcePath, isChapter=False)
        elif self.combobox.currentText() == "category":
            for content_folder in os.listdir(self.sourcePath):
                if content_folder in ["r18", "norm"]:
                    formatter.clean(os.path.join(self.sourcePath, content_folder))
        elif self.combobox.currentText() == "collection":
            for category_folder in os.listdir(self.sourcePath):
                if os.path.isdir(os.path.join(self.sourcePath, category_folder)):
                    for content_folder in os.listdir(os.path.join(self.sourcePath, category_folder)):
                        if content_folder in ["r18", "norm"]:
                            formatter.clean(os.path.join(self.sourcePath, category_folder, content_folder))
        
    def openSourcePath(self):
        self.sourcePath = QFileDialog.getExistingDirectory(self, "Select Directory")
        
        if self.sourcePath:
            self.textbox_sourcePath.setText(self.sourcePath)
        else:    
            self.error_dialog.showMessage('No directory select.')
            
        
class UpdaterPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.textbox_sourcePath = QLineEdit(self)
        self.textbox_sourcePath.setReadOnly(True)
        
        self.btn_sourcePath = QPushButton("Select Source Folder")
        self.btn_sourcePath.clicked.connect(self.openSourcePath)
        
        self.textbox_targetPath = QLineEdit(self)
        self.textbox_sourcePath.setReadOnly(True)
        
        self.btn_targetPath = QPushButton("Select Target Folder")
        self.btn_targetPath.clicked.connect(self.openTargetPath)
        
        self.btn_getstart = QPushButton("Get Start")
        self.btn_getstart.clicked.connect(self.get_start)
        
        layout.addWidget(self.textbox_sourcePath)
        layout.addWidget(self.btn_sourcePath)
        
        layout.addWidget(self.textbox_targetPath)
        layout.addWidget(self.btn_targetPath)
        
        layout.addWidget(self.btn_getstart)
        
        self.error_dialog = QErrorMessage()
        
    def get_start(self):
        updater = Updater()
        if os.path.basename(self.sourcePath) in ["r18", "norm"]:
            if os.path.basename(self.targetPath) in ["r18", "norm"]:
                updater = Updater()
                updater.run(self.sourcePath, self.targetPath)
            else:
                print("{}: TARGET_FOLDER is not CONTENT_FOLDER".format(self.sourcePath))
        else:
            print("{}: SOURCE_FOLDER is not CONTENT_FOLDER".format(self.sourcePath))
        
    def openSourcePath(self):
        self.sourcePath = QFileDialog.getExistingDirectory(self, "Select Directory")
        
        if self.sourcePath:
            self.textbox_sourcePath.setText(self.sourcePath)
        else:    
            self.error_dialog.showMessage('No directory select.')
            
    def openTargetPath(self):
        self.targetPath = QFileDialog.getExistingDirectory(self, "Select Directory")
        
        if self.targetPath:
            self.textbox_targetPath.setText(self.targetPath)
        else:    
            self.error_dialog.showMessage('No directory select.')
        
class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Utility")
        self.initUI()
    
    def initUI(self):
        self.leftlist = QListWidget()
        self.leftlist.insertItem (0, 'Formatter' )
        self.leftlist.insertItem (1, 'Updater' )
        self.leftlist.currentRowChanged.connect(self.display)
        
        
        self.stack = QStackedWidget(self)
        formatterPage = FormatterPage()
        updaterPage = UpdaterPage()
        self.stack.addWidget(formatterPage)
        self.stack.addWidget(updaterPage)
        
        mainPageLayout = QHBoxLayout(self)
        mainPageLayout.addWidget(self.leftlist)
        mainPageLayout.addWidget(self.stack)
        
        self.setLayout(mainPageLayout)
        self.show()
        
    def display(self, i):
        self.stack.setCurrentIndex(i)
            
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())