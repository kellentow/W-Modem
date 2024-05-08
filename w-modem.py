import socket
import threading
import math
from EventManager import EventManager
import time

class WModem():
    """
    A class to connect and interact with a server with the WModem protocall

    Args:
        host (str): IP to connect to
        port (int): port to connect to
        key = b''(int): The encryption key to use
        startxt = True (bool): Whether to print the WModem version
    """
    def __init__(self, host, port, key = b'', startxt = True):
        self.version = [0x0,0x01,0x01]
        if type(key) != int:
            raise ValueError(f"Key must be an int and not a {type(key)}")
        self.key = bytes(key)
        self.version_txt = "WModem Version: "
        if self.version[0] == 0x0:
            self.version_txt += "dev"
        elif self.version[0] == 0x1:
            self.version_txt += "alpha"
        elif self.version[0] == 0x2:
            self.version_txt += "beta"
        elif self.version[0] == 0x3:
            self.version_txt += "pre-release"
        elif self.version[0] == 0x4:
            self.version_txt += "release"
        self.version_txt += " "+str(int(self.version[1]))
        for num in self.version[2:]:
            self.version_txt += "."+str(int(num))
        if startxt:
            print(self.version_txt)
        self.events = EventManager()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.packet_mods = {
            "Data": 0x80,
            "DtD": 0x81,
            "SEA": 0x8C,
            "SOP": 0x8D,
            "HED": 0x8E,
            "EOP": 0x8F
        }
        self.commands = {
            "ACK": 0x86,
            "NAK": 0x87,
            "ABO": 0x88,
            "OCK": 0x89,
            "ERR": 0x8A,
            "IGN": 0x8B,
            "KAC": 0x90,
        }
        self.busy = False
        self.buffer = bytearray()  # Use bytearray to accumulate incoming data
        self.packet_size = 1024
        self.packet_number = 0
        self.packet_number_ack = 0
        self.packet_number_err = 0
        self.ign_count = 0
        self.connected = False

        self.receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.receive_thread = threading.Thread(target=self.keep_alive_loop, daemon=True)
        self.receive_thread.start()  # Start the background thread for receiving data

    def keep_alive_loop(self):
        while True:
            try:
                self.send_packet("KAC","DtD")
                time.sleep(1)
                for packet in self.buffer:
                    payload = packet[packet.index(self.packet_mods["SOP"])+1:packet.index(self.packet_mods["EOP"])-2]
                    t = packet[packet.index(self.packet_mods["HED"])+1]
                    if t == self.packet_mods["DtD"] and payoad == self.commands["KAC"]:
                        break
                    else:
                        raise ValueError("KAC not responded to")

            except Exception as e:
                print(f"KAC error: {e}")


    def connect(self):
        i = 0
        self.busy = True
        while not self.connected and i <=10:
            self.socket.send(self.packet_mods["SEA"])
            time.sleep(0.1)
            if len(self.buffer) == 0:
                i += 1
            else:
                self.connected = True
        if not self.connected:
            raise ValueError("Could not connect to other computer")
        self.busy = False

    def packet_template(self,type,payload):
        checksum = self.calculate_checksum(payload)
        length = len(payload)
        if type == "Data":
            return bytes([self.packet_mods["HED"],self.packet_mods[type],length,self.packet_mods["SOP"],payload,checksum,self.packet_mods["EOP"]])
        elif type == "DtD":
            if payload in self.packet_mods:
                return bytes([self.packet_mods["HED"],self.packet_mods[type],length,self.packet_mods["SOP"],self.packet_mods[payload],checksum,self.packet_mods["EOP"]])
            else:
                return bytes([self.packet_mods["HED"],self.packet_mods[type],length,self.packet_mods["SOP"],payload,checksum,self.packet_mods["EOP"]])

    def send_packet(self, data, packet_type="data"):
        self.socket.send(self.packet_template(packet_type,data))

    def calculate_checksum(self, data):
        checksum = 0
        for i in range(len(data)):
            checksum += data[i]
        return math.mod(checksum, 256)

    def receive_loop(self):
        while True:
            try:
                data = self.socket.recv(self.packet_size)
                if not data:
                    break
                self.handle_received_data(data)
            except Exception as e:
                print(f"Error in receive_loop: {e}")
                break

    def handle_received_data(self, data):
        payload = data[data.index(self.packet_mods["SOP"])+1:data.index(self.packet_mods["EOP"])-2]
        rec_check = data[data.index(self.packet_mods["EOP"])-1].decode()
        calc_check = self.calculate_checksum(payload)
        if rec_check != calc_check:
            self.send_packet("ERR","DtD")
        elif rec_check == calc_check:
            self.buffer.extend(data)  # Append received data to the buffer

    def process_buffer(self):
        if self.busy:
            self.send_packet("OCK", packet_type="data")
            return
        decoded = []
        for i in range(len(self.buffer),0,-1):
            payload = i[i.index(self.packet_mods["SOP"])+1:i.index(self.packet_mods["EOP"])-2]
            rec_check = i[i.index(self.packet_mods["EOP"])-1].decode()
            type = i[i.index(self.packet_mods["HED"])+1]
            event = self.buffer[i-1]
            if event in self.commands.values():
                if self.ign_count > 0:
                    self.ign_count -= 1
                elif event == self.commands["ACK"]:
                    self.packet_number_ack += 1
                    self.events.trigger("ACK")
                elif event == self.commands["NAK"]:
                    self.packet_number_err += 1
                    self.events.trigger("NAK")
                elif event == self.commands["ABO"]:
                    self.packet_number_err += 1
                    self.events.trigger("ABO")
                elif event == self.commands["OCK"]:
                    self.events.trigger("OCK")
                elif event == self.commands["ERR"]:
                    self.packet_number_err += 1
                    self.events.trigger("ERR")
                elif event == self.commands["IGN"]:
                    self.ign_count += 1
                    self.events.trigger("IGN")
            decoded.append({"type":type,"payload":payload,"checksum":rec_check})
        return decoded
            

m = WModem("127.0.0.1","1701")
m.events.listen("ACK",lambda: print("ACK"))
m.connect()
while True:
    time.sleep(1)
    print("waiting...")