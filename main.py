import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from deviceFinder import DeviceFinder


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.searchButton = QPushButton("Search")
        self.finder = DeviceFinder(self)

        self.vbox = QVBoxLayout()
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.searchButton)

        self.searchButton.clicked.connect(self.finder.find)
        self.finder.stateChanged.connect(self.change_btn_text)
        self.finder.scanDone.connect(self.display_found_devices)

        self.setLayout(self.vbox)

        self.setGeometry(300, 60, 300, 480)
        self.setWindowTitle('Bt-Scanner')
        self.show()

    def change_btn_text(self, text):
      self.searchButton.setText(text)

    
    def display_found_devices(self, devices):
      for device in devices:
        deviceView = QLabel()
        deviceView.setText(device.name())
        deviceView.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(deviceView)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())