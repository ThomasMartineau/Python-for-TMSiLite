import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi

class Test(QDialog):
    
    def __init__(self):
        super(Test, self).__init__()
        loadUi('test.ui', self)
        self.setWindowTitle('this is a test')
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        
    @pyqtSlot()
    def on_pushButton_clicked(self):
        self.label_2.setText("Welcome: " + self.lineEdit.text())
        
app = QApplication(sys.argv)
widget = Test()
widget.show()
sys.exit(app.exec_())
    
