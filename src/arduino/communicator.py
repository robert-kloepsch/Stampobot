import configparser
import serial
import time

from settings import CONFIG_FILE_PATH, BAUD_RATE


class ArduinoCom:

    def __init__(self):
        params = configparser.ConfigParser()
        params.read(CONFIG_FILE_PATH)
        self.ard = serial.Serial(params.get('DEFAULT', 'arduino_port'), BAUD_RATE, timeout=5)
        self.ard_res = "detect"
        self.receive_ret = True
        time.sleep(2)

    def send_command_arduino(self, command):

        command += "\n"
        print(f"[INFO] To Arduino: {command}")
        self.ard.write(command.encode("utf-8"))

        return

    def receive_command_arduino(self):

        while True:
            if not self.receive_ret:
                break
            response = self.ard.read(self.ard.inWaiting())
            decode_res = response.decode().replace("\r\n", "")
            if decode_res != "":
                self.ard_res = decode_res
                print(f"[INFO] From Arduino: {self.ard_res}")
            time.sleep(0.1)

        return

    def close_port(self):

        if self.ard.isOpen():
            self.ard.close()


if __name__ == '__main__':

    ard_com = ArduinoCom()

    for i in range(3):
        ard_com.send_command_arduino(command="2,3")
