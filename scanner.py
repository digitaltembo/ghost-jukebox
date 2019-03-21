"""
Scanner.py

This will run in the background and act upon any QR Codes that it sees
"""

from ghost_jukebox import conf

from io import BytesIO
from picamera import PiCamera
from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol
from requests.auth import HTTPBasicAuth
from time import sleep

import requests

class Scanner:
    NORTH = 1
    EAST  = 2
    SOUTH = 3
    WEST  = 4
    LEFT  = 5
    RIGHT = 6

    side_threshold = 600
    encoding = 'utf-8'
    base_url ='https://{}/s//QR'.format(conf.host)
    data_prefix = base_url.encode(encoding)
    data_prefix_len = len(data_prefix)
    sleep_time = 0

    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (1024, 768)
        self.current_code = None
        self.current_orientation = None
        self.verification_ticks = 0

    def scan(self):
        decoded_qrs = self.check_for_qr_code()
        if decoded_qrs:
            code, orientation, side = self.get_info(decoded_qrs)
            if self.current_code != code or self.current_orientation != orientation or self.current_side != side:
                self.sleep_time = 0
                self.verification_ticks += 1
                if self.verification_ticks > 2:
                    self.go(code, orientation, side)
                    self.verification_ticks = 0
            else:
                self.sleep_time = 3
                self.verification_ticks = 0
        else:
            if self.current_code is not None:
                self.sleep_time = 0
                self.verification_ticks += 1
                if self.verification_ticks > 4:
                    self.current_code = None
                    self.verification_ticks = 0
                    self.stop()
            else:
                self.verification_ticks = 0
                self.sleep_time = 7
    

    def check_for_qr_code(self):
        stream = BytesIO()
        self.camera.capture(stream, format='jpeg')
        stream.seek(0)
        return decode(Image.open(stream), symbols=[ZBarSymbol.QRCODE])

    def get_code_and_orientation(self, decoded_qrs):
        relevant_qrs = [qr for qr in decoded_qrs if qr.data.startswith(data_prefix)]
        if len(relevant_qrs) > 1:
            return None, None
        else:
            qr = relevant_qrs[0]
            code = qr.data[data_prefix_len:].decode(encoding)
            orientation = self.get_orientation(qr.polygon)
            side = self.get_side(qr.rect)
            return code, orientation, side

    def get_orientation(polygon):
        try:
            a,b,c,d = polygon[0].y, polygon[1].y, polygon[2].y, polygon[3].y

            if a > c and a > d and b > c and b > d:
                return self.NORTH
            elif a < c and a < d and b < c and b < d:
                return self.SOUTH 
            elif a < b and a < c and d < b and d < c:
                return self.WEST 
            else:
                return self.EAST
        except:
            return self.NORTH

    def get_side(rect):
        if rect.left < self.SIDE_THRESHOLD:
            return self.LEFT 
        else:
            return self.RIGHT

    def go(self, code, orientation, side):
        self.current_code = code
        self.current_orientation = orientation
        self.side = side

        if side == self.RIGHT:
            self.radio(code)
        else:
            if orientation = self.NORTH:
                self.play(code)
            else:
                self.shuffle(code)

    # sends a request to <host>/s//QR####/play
    def play(self, code):
        self.start('play', code)
    # sends a request to <host>/s//QR####/radio
    def radio(self, code):
        self.start('radio', code)
    # sends a request to <host>/s//QR####/shuffle
    def shuffle(self, code):
        self.start('shuffle', code)

    def start(self, endpoint, code)
        self.request('{}/{}'.format(code, endpoint))
    # sends a request to <host>/s//QRstop
    def stop(self):
        self.request('stop')

    def request(self, end):
        url = self.base_url + end
        requests.post(
            url,
            auth=HTTPBasicAuth(conf.username, conf.password)
        )

if __name__ == "__main__":
    scanner = Scanner()
    while True:
        scanner.scan()
        sleep(scanner.sleep_time)