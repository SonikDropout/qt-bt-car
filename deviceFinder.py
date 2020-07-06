from PyQt5.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo
from PyQt5.QtCore import pyqtSignal, QObject

BLUETOOTH_UUID = "00001101-0000-1000-8000-00805F9B34FB"
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

class DeviceFinder(QObject):

  stateChanged = pyqtSignal(str)
  scanDone = pyqtSignal(list)
  _status = 'Scanning'
  _devices = []
  _deviceDiscoveryAgent = QBluetoothDeviceDiscoveryAgent()

  def __init__(self, parent):
    super().__init__(parent)
    self._deviceDiscoveryAgent.setLowEnergyDiscoveryTimeout(5000)
    self._deviceDiscoveryAgent.deviceDiscovered.connect(self.add_device)
    self._deviceDiscoveryAgent.error.connect(self.handle_error)
    self._deviceDiscoveryAgent.finished.connect(self.scan_finished)
    self._deviceDiscoveryAgent.canceled.connect(self.scan_finished)


  def find(self):
    self._deviceDiscoveryAgent.start()
    self.stateChanged.emit(self._status)

  def add_device(self, device):
      if device.coreConfiguration() & QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
        self._devices.append(device)

  def scan_finished(self):
    if not len(self._devices):
      self._status = 'No low energy devices found...'
    else:
      self._status = 'Scan done'
      self.scanDone.emit(self._devices)
    self.stateChanged.emit(self._status)

  def handle_error(self):
    self._status = 'Scan failed'
    self.stateChanged.emit(self._status)
    
