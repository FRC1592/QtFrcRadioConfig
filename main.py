from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PyQt5.uic import loadUi

import socket
import re

import sys
class FrcRadioConfig(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)

        self.ui = loadUi('main.ui')
        self.ui.show()

        self.radio_modes = ['AP24', 'AP5', 'B24', 'B5']

        self.ui.config_radio.clicked.connect(self.config_radio)

        self.team_num = 0
        self.team_name = ''
        self.wpa_key = 0

    def validate_inputs(self):
        if not 0 <= self.ui.radio_mode.currentIndex() <= 3:
            return 'Invalid radio mode!'
        if not 1 <= self.team_num <= 9999:
            return 'Team number must be from 1-9999!'
        if not 1 <= len(str(self.team_num)) + 1 + len(self.team_name) <= 31:
            return 'SSID Must be 1-31 characters long!'
        if len(self.ui.wpa_key.text()) > 0 and not re.match('[^,]{8,30}', self.ui.wpa_key.text()):
            return 'WPA key must be 8-30 characters long and not contain commas!'
        return None

    def build_cfg_string(self):
        mode = self.radio_modes[self.ui.radio_mode.currentIndex()]
        if mode in ['B24', 'B5']:
            ssid = self.team_name
        else:
            ssid = str(self.team_num) + '_' + self.team_name
        firewall = 'Y' if self.ui.en_firewall.checkState() else 'N'
        bwlimit = '4000,' if self.ui.en_limit.checkState() else ''
        dhcp = 'Y,' if mode in ['B24', 'B5'] else ''
        # The following values are essentially hardcoded, possibly used at comp
        chan24 = '0'
        chan5 = '0'
        comment = 'Home'
        date = ''

        return f'{mode},{str(self.team_num)},{ssid},{self.wpa_key},{firewall},{bwlimit}{dhcp}{chan24},{chan5},{comment},{date}'

    @pyqtSlot()
    def config_radio(self):
        self.team_num = self.ui.team_num.value()
        self.team_name = self.ui.team_name.text()
        self.wpa_key = self.ui.wpa_key.text()

        res = self.validate_inputs()
        if res is not None:
            QMessageBox.critical(self, 'Error', res)
            return

        cfg = self.build_cfg_string()

        addr = '10.'+str(int(self.team_num / 100))+'.'+str(self.team_num % 100)+'.1'

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((addr, 8888))
                lines = s.recv(1000).decode('utf-8').split('\n')
                print(lines)

                s.sendall(cfg.encode('utf-8') + b'\n')
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    frq = FrcRadioConfig()

    sys.exit(app.exec())
