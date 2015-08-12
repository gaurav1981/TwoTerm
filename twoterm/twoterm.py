__author__ = 'Markus Becker'

try:
    from PyQt5.QtCore import pyqtSlot, QTimer
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.uic import loadUi
except ImportError:
    print("Problems with PyQt5. Falling back to PyQt4.")
    from PyQt4.QtCore import pyqtSlot, QTimer
    from PyQt4.QtGui import QMainWindow
    from PyQt4.uic import loadUi

import serial
import io
from serial.tools.list_ports import comports

CONNECT_LABEL = "Connect"
DISCONNECT_LABEL = "Disconnect"
TIMEOUT_READLINE = 0.01
TIMEOUT_TIMER = 1


class TwoTermWidget(QMainWindow):
    def __init__(self, *args):
        super(TwoTermWidget, self).__init__(*args)
        self.serL = None
        self.serR = None
        self.sioL = None
        self.sioR = None

        loadUi('TwoTermSingleScrollArea.ui', self)

        self.connect_status = False

        iterator = sorted(comports())
        for port, desc, hwid in iterator:
            self.comboBoxL.addItem(str(port))
            self.comboBoxR.addItem(str(port))
            print("Port: " + str(port))

        self.comboBoxLBaudrate.addItems(map(str, serial.Serial.BAUDRATES))
        self.comboBoxRBaudrate.addItems(map(str, serial.Serial.BAUDRATES))

        self.textR.verticalScrollBar().valueChanged.connect(self.textL.verticalScrollBar().setValue)
        self.textR.horizontalScrollBar().valueChanged.connect(self.textL.horizontalScrollBar().setValue)
        self.textL.horizontalScrollBar().valueChanged.connect(self.textR.horizontalScrollBar().setValue)

    def timeout(self):
        l = self.sioL.readline()
        r = self.sioR.readline()
        if l != "":
            self.textL.append(l)
        if r != "":
            self.textR.append(r)

        if l != "" and r == "":
            self.textR.append("")
        if l == "" and r != "":
            self.textL.append("")

    @pyqtSlot()
    def on_connectButton_clicked(self):

        if not self.connect_status:

            portL = self.comboBoxL.currentText()
            portR = self.comboBoxR.currentText()

            if portL == "":
                portL = 'loop://'

            if portR == "":
                portR = 'loop://'

            self.serL = serial.serial_for_url(portL, baudrate=int(self.comboBoxLBaudrate.currentText()),
                                              timeout=TIMEOUT_READLINE)
            self.serR = serial.serial_for_url(portR, baudrate=int(self.comboBoxRBaudrate.currentText()),
                                              timeout=TIMEOUT_READLINE)

            self.sioL = io.TextIOWrapper(io.BufferedRWPair(self.serL, self.serL))
            self.sioR = io.TextIOWrapper(io.BufferedRWPair(self.serR, self.serR))

            # test
            self.sioL.write(u"hello l")
            self.sioL.flush()
            self.sioR.write(u"hello r")
            self.sioR.flush()

            self.connectButton.setText(DISCONNECT_LABEL)
            self.connect_status = True
            self.textL.append(CONNECT_LABEL + " " + str(self.serL))
            self.textR.append(CONNECT_LABEL + " " + str(self.serR))

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.timeout)
            self.timer.start(TIMEOUT_TIMER)
        else:

            self.timer.stop()

            self.serL.close()
            self.serR.close()

            self.serL = None
            self.serR = None

            self.sioL = None
            self.sioR = None

            self.connectButton.setText(CONNECT_LABEL)
            self.connect_status = False
            self.textL.append(DISCONNECT_LABEL)
            self.textR.append(DISCONNECT_LABEL)
