import sys
from PyQt5.QtWidgets import *
import os
        
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

        self.lineEdit = QLineEdit()
        
        layout.addWidget(self.combobox)
        layout.addWidget(self.textbox_sourcePath)
        layout.addWidget(self.btn_sourcePath)
        layout.addWidget(self.btn_getstart)
        layout.addWidget(self.lineEdit)
        
        self.error_dialog = QErrorMessage()
         
    def get_start(self):

        command = ['python', 'main.py', '-m', 'formatter', '-t', self.combobox.currentText(), '--source', self.sourcePath]
        command = " ".join(command)

        output = os.popen(command).read()
        self.lineEdit.setText(output)
        
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

        self.lineEdit = QLineEdit()
        
        layout.addWidget(self.textbox_sourcePath)
        layout.addWidget(self.btn_sourcePath)
        
        layout.addWidget(self.textbox_targetPath)
        layout.addWidget(self.btn_targetPath)
        
        layout.addWidget(self.btn_getstart)
        layout.addWidget(self.lineEdit)
        
        self.error_dialog = QErrorMessage()
        
    def get_start(self):
        command = ['python', 'main.py', '-m', 'updater', '--source', self.sourcePath, '--target', self.targetPath]
        command = " ".join(command)

        output = os.popen(command).read()
        self.lineEdit.setText(output)
        
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