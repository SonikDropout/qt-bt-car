from PyQt5.QtCore import pyqtSignal, QObject
from bluepy.btle import Scanner, DefaultDelegate
import threading

BLUETOOTH_UUID = "00001101-0000-1000-8000-00805F9B34FB"
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

class BtConnector(QObject):

  scanner = Scanner()
  btDelegate = DefaultDelegate()
  deviceDiscovered = pyqtSignal(object)
  stateChanged = pyqtSignal(str)
  devices = []
  state = 'idle'

  def __init__(self, parent):
    super().__init__(parent)
    self.btDelegate.handleDiscovery = self.addDevice
    self.scanner.withDelegate(self.btDelegate)

  def scan(self):
    threading.Thread(target=self._startScanning, daemon=True).start()

  def addDevice(self, dev, isNewDev, isNewData):
    if isNewDev:
      self.deviceDiscovered.emit(dev)

  def _startScanning(self):
    self._state = 'scanning...'
    self.stateChanged.emit(self._state)
    self.scanner.scan()
    self._state = 'scanning done'
    self.stateChanged.emit(self._state)
    
