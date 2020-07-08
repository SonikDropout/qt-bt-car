from PyQt5.QtCore import pyqtSignal, QObject
from bluepy.btle import *
from struct import unpack
import threading

SERVICE_UUID = "0000ffe0"
CHARACTERISTIC_UUID = "0000ffe1"
BT_DATA = ['batV', 'batC', 'canCharge', 'canDischarge', 'fcV', 'fcC', 'fcT', 'fan', 'fcOn', 'HConsumption', 'HPressure', 'batCDirection', 'recuperation']
BT_DIVIDERS = bytes((161, 178, 195, 195, 212,247))
BT_DATA_FORMAT = 'HHBBHHBBBHHBB'

class BTDataExeption(BaseException): 
  # pass

class BtConnector(QObject):

  scanner = Scanner()
  btDelegate = DefaultDelegate()
  deviceDiscovered = pyqtSignal(object)
  stateChanged = pyqtSignal(str)
  dataRecieved = pyqtSignal(dict)
  devices = []
  state = 'idle'
  foundCar = None

  def __init__(self, parent):
    super().__init__(parent)
    self.btDelegate.handleDiscovery = self.addDevice
    self.btDelegate.handleNotification = self.emitBtData
    self.scanner.withDelegate(self.btDelegate)

  def scan(self):
    threading.Thread(target=self._startScanning, daemon=True).start()

  def addDevice(self, dev, isNewDev, isNewData):
    try:
      if isNewDev and dev.connectable:
        self.devices.append(dev)
        self.deviceDiscovered.emit(dev)
    except:
      return
  
  def emitBtData(self, cHandle, data):
    try:
      self.dataRecieved.emit(self.parseBtData(data))
    except BTDataExeption:
      print(f'Invalid data recieved: {data}')

  def parseBtData(self,data):
    if data[0:6] is not BT_DIVIDERS:
      raise BTDataExeption()
    return dict(zip(BT_DATA, list(unpack(BT_DATA_FORMAT, data[6:]))))


  def _startScanning(self):
    self._state = 'scanning...'
    self.stateChanged.emit(self._state)
    self.scanner.scan()
    self._state = 'scanning done'
    self.stateChanged.emit(self._state)
    for dev in self.devices:
      peripheral = Peripheral
      try:
        peripheral.connect(dev.addr)
        peripheral.getServiceByUUID(SERVICE_UUID)
        self.foundCar = peripheral
        self.foundCar.withDelegate(self.btDelegate)
        break
      except BTLEEException:
        peripheral.disconnect()
    
