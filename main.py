import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from deviceFinder import BtConnector


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.searchButton = QPushButton("Search")
        self.connector = BtConnector(self)

        self.vbox = QVBoxLayout()
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.searchButton)

        self.searchButton.clicked.connect(self.connector.scan)
        self.connector.stateChanged.connect(self.change_btn_text)
        self.connector.deviceDiscovered.connect(self.display_found_device)

        self.setLayout(self.vbox)

        self.setGeometry(300, 60, 300, 480)
        self.setWindowTitle('Bt-Scanner')
        self.show()

    def change_btn_text(self, text):
      self.searchButton.setText(text)

    
    def display_found_device(self, device):
        deviceView = QLabel()
        deviceView.setText(device.addr)
        deviceView.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(deviceView)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())