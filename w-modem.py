import socket
import threading

class WModemHost:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.packet_mods = {
            "Data": 0x80,
            "DtD": 0x81,
            "SOP": 0x8D,
            "HED": 0x8E,
            "EOP": 0xAF
        }
        self.commands = {
            "ACK": 0x86,
            "NAK": 0x87,
            "ABO": 0x88,
            "OCK": 0x89,
            "ERR": 0x8A,
            "IGN": 0x8B,
            "SEA": 0x8C,
        }
        self.state = "IDLE"
        self.buffer = bytearray()  # Use bytearray to accumulate incoming data
        self.packet_size = 128
        self.packet_number = 0
        self.packet_number_ack = 0
        self.packet_number_err = 0
        self.ign_count = 0

        self.receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.receive_thread.start()  # Start the background thread for receiving data

    def packet_template(self,type,length,payload,checksum):
        return bytes([self.packet_mods["HED"],self.packet_mods[type],length,self.packet_mods["SOP"],payload,checksum,self.packet_mods["EOP"]])

    def send_packet(self, data, packet_type="data"):
        self.socket.send(self.packet_template(packet_type,len(data),data,self.calculate_checksum(data)))

    def calculate_checksum(self, data):
        checksum = 0
        for i in range(len(data)):
            checksum += data[i]
        return checksum % 256

    def receive_loop(self):
        while True:
            try:
                data = self.socket.recv(1024)  # Adjust the buffer size as needed
                if not data:
                    break
                self.handle_received_data(data)
            except Exception as e:
                print(f"Error in receive_loop: {e}")
                break

    def handle_received_data(self, data):
        self.buffer.extend(data)  # Append received data to the buffer

    def process_buffer(self):
        for i in range(len(self.buffer),0,-1):
            event = self.buffer[i-1]
            if event in self.commands.values():
                if self.ign_count > 0:
                    self.ign_count -= 1
                else:
                    self.process_packet(self.buffer[:i])
                    self.buffer = self.buffer[i:]

    def receive_packet(self, data):
        # Implement your packet processing logic here
        print("Received packet:", data.hex())