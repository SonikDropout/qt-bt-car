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
    pass

class BtConnector(QObject):

  deviceDiscovered = pyqtSignal(object)
  stateChanged = pyqtSignal(str)
  dataRecieved = pyqtSignal(dict)
  _btDelegate = DefaultDelegate()
  _scanner = Scanner()
  _devices = []
  _state = 'idle'
  _foundCar = None
  _carCharacteristic = None

  def __init__(self, parent):
    super().__init__(parent)
    self.btDelegate.handleDiscovery = self._addDevice
    self.btDelegate.handleNotification = self._emitBtData
    self._scanner.withDelegate(self._btDelegate)

  def scan(self):
    threading.Thread(target=self._startScanning, daemon=True).start()

  def _startScanning(self):
    self._state = 'scanning...'
    self.stateChanged.emit(self._state)
    self._scanner.scan()
    self._state = 'scanning done'
    self.stateChanged.emit(self._state)
    self._handleFoundDevices()

  def _handleFoundDevices(self):
    for dev in self._devices:
      peripheral = Peripheral()
      try:
        peripheral.connect(dev.addr)
        peripheral.getServiceByUUID(SERVICE_UUID)
        self._establishConnectionWithCar(peripheral)
      except BTLEException:
        peripheral.disconnect()
      else:
        break

  def _establishConnectionWithCar(self, peripheral):
    print(f'Fround bluetooth car with address: {peripheral.addr}')
    self._foundCar = peripheral
    self._foundCar.withDelegate(self._btDelegate)
    self._carCharacteristic = self._foundCar.getCharacteristics(uuid=CHARACTERISTIC_UUID)
    self._readCarCharacteristic()
  
  def _readCarCharacteristic(self):
    data = self._carCharacteristic.read()
    try:
      self.dataRecieved.emit(self._parseBtData(data))
    except BTDataExeption:
      print(f'Invalid data revieved: {data}')
    finally:
      threading.Timer(1.0, self._readCarCharacteristic).start()

  def _addDevice(self, dev, isNewDev, isNewData):
    if isNewDev and dev.connectable:
      self._devices.append(dev)
      self.deviceDiscovered.emit(dev)
  
  def _emitBtData(self, cHandle, data):
    try:
      self.dataRecieved.emit(self._parseBtData(data))
    except BTDataExeption:
      print(f'Invalid data recieved: {data}')

  def _parseBtData(self,data):
    if data[0:6] is not BT_DIVIDERS:
      raise BTDataExeption()
    return dict(zip(BT_DATA, list(unpack(BT_DATA_FORMAT, data[6:]))))