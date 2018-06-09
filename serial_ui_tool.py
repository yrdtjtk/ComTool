# -*- coding:utf-8 -*-
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer
from ui_serial_tool import Ui_Form

import time
import datetime

import serial
import serial.tools.list_ports

import threading

import func
from res import images_qr


def getProgVer():
    return 'V1.001'


def getNowStr(isCompact=True, isMill=False):
    now = datetime.datetime.now()
    if isCompact:
        if isMill:
            s_datatime = now.strftime('%Y%m%d%H%M%S%f')
        else:
            s_datatime = now.strftime('%Y%m%d%H%M%S')
    else:
        if isMill:
            s_datatime = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        else:
            s_datatime = now.strftime('%Y-%m-%d %H:%M:%S')
    return s_datatime


def getTxt(txtName):
    table = {'openPort': 'Open(&O)', 'closePort': 'Close(&C)'}
    return table[txtName]


def createSerial(portName, baudrate):
    ser = serial.Serial()
    ser.port = portName
    ser.baudrate = baudrate
    ser.timeout = 2
    ser.parity = 'N'
    ser.stopbits = 1

    return ser


def portRecvProc(ser, sig):
    while ser.isOpen():
        try:
            num = ser.inWaiting()
            if num > 0:
                b = ser.read(num)
                sig.emit(b)
        except Exception as e:
            print(str(e))
            ser.close()
            return
        time.sleep(0.01)


class MainWindow(QtWidgets.QWidget):

    sig_portRecv = QtCore.pyqtSignal(bytes, name='refresh_UI_Recv_Signal')

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.t = None


        self.setWindowTitle('COM Tool - ' + getProgVer())

        self.sig_portRecv.connect(self.refresh_UI_Recv)

        for port in serial.tools.list_ports.comports():
            self.ui.cob_Com.addItem(port[0])
        self.ui.cob_Baudrate.setCurrentText('57600')
        self.ui.cob_DataBits.setCurrentText('8')
        self.ui.cob_StopBits.setCurrentText('1')
        self.ui.cob_Parity.setCurrentText('None')
        self.ui.cob_FlowCtrl.setCurrentText('None')
        self.ser = createSerial(self.ui.cob_Com.currentText(),
                                self.ui.cob_Baudrate.currentText())
        # self.ui.pb_OpenOrClose.setAttribute(Qt.WA_NativeWindow)
        self.ui.pb_OpenOrClose.setText(getTxt('openPort'))
        # self.ui.lbl_Com.setPixmap(QtGui.QPixmap("ico/off.png"))
        self.ui.lbl_Com.setPixmap(QtGui.QPixmap(":/ico/off.png"))
        self.ui.te_Recv.setReadOnly(True)
        self.ui.lbl_Status.setText('')
        self.ui.lbl_Tip.setText('')

        self.timerTip = QTimer(self)
        self.timerTip.timeout.connect(self.timerTipProc)

        self.ui.pb_OpenOrClose.clicked.connect(self.on_pb_OpenOrClose_Clicked)
        self.ui.cob_Com.currentIndexChanged.connect(
            self.on_cob_Com_CurrentIndexChanged)
        self.ui.cob_Baudrate.currentIndexChanged.connect(
            self.on_cob_Baudrate_CurrentIndexChanged)
        self.ui.cob_DataBits.currentIndexChanged.connect(
            self.on_cob_DataBits_CurrentIndexChanged)
        self.ui.cob_StopBits.currentIndexChanged.connect(
            self.on_cob_StopBits_CurrentIndexChanged)
        self.ui.cob_Parity.currentIndexChanged.connect(
            self.on_cob_Parity_CurrentIndexChanged)
        self.ui.pb_Send.clicked.connect(self.on_pb_Send_Clicked)
        self.ui.pb_ClearRecv.clicked.connect(self.on_pb_ClearRecv_Clicked)

        QtWidgets.QWidget.setTabOrder(self.ui.cob_Com, self.ui.pb_OpenOrClose)
        QtWidgets.QWidget.setTabOrder(
            self.ui.pb_OpenOrClose, self.ui.chk_HexRecv)
        QtWidgets.QWidget.setTabOrder(
            self.ui.chk_HexRecv, self.ui.pb_ClearRecv)
        QtWidgets.QWidget.setTabOrder(
            self.ui.pb_ClearRecv, self.ui.chk_HexSend)
        QtWidgets.QWidget.setTabOrder(self.ui.chk_HexSend, self.ui.pb_Send)
        QtWidgets.QWidget.setTabOrder(self.ui.pb_Send, self.ui.cob_Com)

        self.show()

    def on_pb_OpenOrClose_Clicked(self):
        if not self.ser.isOpen():
            self.ser = createSerial(
                self.ui.cob_Com.currentText(), self.ui.cob_Baudrate.currentText())
            try:
                self.ser.open()
            except Exception as e:
                print(e)
                self.ui.lbl_Tip.setText(str(e))
                self.timerTip.start(3000)
            if self.ser.isOpen():
                self.showComStatus()
                if not self.t or not self.t.isAlive():
                    self.t = threading.Thread(target=portRecvProc,
                                         args=(self.ser, self.sig_portRecv))
                    self.t.start()
                    print(threading.enumerate())
        else:
            self.ser.close()
            i = 0
            while self.t.isAlive():
                i += 1
                time.sleep(0.01)
                print(str(self.t.isAlive()) + ' i=%d ' % i)
                if i > 2:
                    break
            self.showComStatus()

    def on_cob_Com_CurrentIndexChanged(self, index):
        if self.ser.isOpen():
            self.on_pb_OpenOrClose_Clicked()
            if not self.ser.isOpen():
                self.on_pb_OpenOrClose_Clicked()

    def on_cob_Baudrate_CurrentIndexChanged(self, index):
        if self.ser.isOpen():
            self.ser.baudrate = self.ui.cob_Baudrate.currentText()
            self.showComStatus()

    def on_cob_DataBits_CurrentIndexChanged(self, index):
        if self.ser.isOpen():
            self.ser.bytesize = int(self.ui.cob_DataBits.currentText(), 10)
            self.showComStatus()
    def on_cob_StopBits_CurrentIndexChanged(self, index):
        if self.ser.isOpen():
            try:
                self.ser.stopbits = {'1':1, '1.5':1.5, '2':2}[self.ui.cob_StopBits.currentText()]
            except Exception as e:
                print(e)
                self.ui.lbl_Tip.setText(str(e))
                self.timerTip.start(3000)
            self.showComStatus()

    def on_cob_Parity_CurrentIndexChanged(self, index):
        if self.ser.isOpen():
            self.ser.parity = self.ui.cob_Parity.currentText()[0]
            self.showComStatus()

    def showComStatus(self):
        if self.ser.isOpen():
            # print(dir(self.ser))
            self.ui.pb_OpenOrClose.setText(getTxt('closePort'))
            self.ui.lbl_Com.setPixmap(QtGui.QPixmap(":/ico/on.png"))
            self.ui.lbl_Status.setText(
                self.ser.name + ' is ' + {True: 'ON', False: 'OFF'}[self.ser.isOpen()] + ' %d,%s,%d,%d' % (
                    self.ser.baudrate, self.ser.parity, self.ser.bytesize, self.ser.stopbits))
        else:
            self.ui.pb_OpenOrClose.setText(getTxt('openPort'))
            self.ui.lbl_Com.setPixmap(QtGui.QPixmap(":/ico/off.png"))
            self.ui.lbl_Status.setText(
                self.ser.portstr + ' is ' + {True: 'ON', False: 'OFF'}[self.ser.isOpen()])

    def refresh_UI_Recv(self, b):
        if self.ui.chk_HexRecv.isChecked():
            s1 = func.buf2hexstr(b)
            s2 = '[<font color="red">' + \
                getNowStr(False, True) + '</font>] %04u: ' % len(b)
            s = s2 + s1
            self.ui.te_Recv.append(s)  # 换行追加
        else:
            s = bytes.decode(b, 'utf-8', errors='ignore')
            self.ui.te_Recv.moveCursor(QtGui.QTextCursor.End)
            self.ui.te_Recv.insertPlainText(s)

    def on_pb_Send_Clicked(self):
        if self.ser.isOpen():
            txt = self.ui.te_Send.toPlainText()
            print('txt = ' + txt)
            for c in txt:
                if not c.upper() in ('%X' % x for x in range(0,16)):
                    self.ui.lbl_Tip.setText('Hex Data Format Err!')
                    self.timerTip.start(3000)
                    return
            if self.ui.chk_HexSend.isChecked():
                try:
                    b = func.hexstr2buf(txt)
                except Exception as e:
                    print(e)
                    self.ui.lbl_Tip.setText(str(e))
                    self.timerTip.start(3000)
                    return
            else:
                b = bytes(txt, 'utf-8')
            self.ser.write(b)

    def on_pb_ClearRecv_Clicked(self):
        self.ui.te_Recv.setText('')

    def timerTipProc(self):
        self.ui.lbl_Tip.setText('')

    # def eventFilter(self, obj, ev):
    #     print('eventFilter')

    def keyPressEvent(self, ev):
        # print('keyPressEvent, ev = ' + str(ev.modifiers()) + ', ' + hex(ev.key()))
        if ev.key() == Qt.Key_Return:
            # print('Enter Key')
            if ev.modifiers() == Qt.ControlModifier:
                # print('Ctrl Key')
                if QtWidgets.QWidget.focusWidget(self) == self.ui.te_Send:
                    self.on_pb_Send_Clicked()
            # else:
            #     curWidg = QtWidgets.QWidget.focusWidget(self)

    def closeEvent(self, ev):
        if self.ser.isOpen():
            self.ser.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    sys.exit(app.exec_())
