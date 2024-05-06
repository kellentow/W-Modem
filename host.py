import socket
import os

host = None
config_data = {}
wmodem_folder = None

COMMAND_CODES = {
    'ack': 0x574D58EB,
    'nak': 0x574D58EC,
    'cap': 0x574D58ED,
    'rst': 0x574D58EE,
    'kac': 0x574D58EF,
    'eot': 0x574D58F0,
    'chk': 0x574D58F1,
    'rts': 0x574D58F2,
    'rty': 0x574D58F3,
    'cnk': 0x574D58F4,
    'req': 0x574D58F5
}

def read_config(config_file_path):
    config_data = {}
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            for line in config_file:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('#', 1)
                    key_value = parts[0].strip().split(':', 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        config_data[key.strip()] = value.strip()
        print("Config file content:")
        print(config_data)
    else:
        print("Config file not found.")
    return config_data

def send_chunk(host, chunk):
    chunk_code = COMMAND_CODES['cnk']
    packet = chunk_code.to_bytes(4, 'big') + chunk
    host.sendto(packet, (config_data["ip"], int(config_data["port"])))

def sanitize_file_path(base_path, requested_path):
    full_path = os.path.normpath(os.path.join(base_path, requested_path))
    if not os.path.commonpath([full_path, base_path]) == base_path or config_data["full-host"].lower() == "true":
        raise ValueError("Requested path is outside the base path.")
    return full_path

def handle_request(request, host):
    global wmodem_folder
    parts = request.split('/')
    file_path = os.path.join(wmodem_folder, '/'.join(parts[2:]))
    sanitized_path = sanitize_file_path(wmodem_folder, file_path)
    if os.path.exists(sanitized_path) and os.path.isfile(sanitized_path):
        with open(sanitized_path, 'rb') as file:
            while True:
                chunk = file.read(1024)
                if not chunk:
                    break
                send_chunk(host, chunk)
    else:
        print("File not found")

def receive_message(host):
    def decorator(func):
        def wrapper(*args, **kwargs):
            message_bytes, address = host.recvfrom(1028)
            func(message_bytes, address, *args, **kwargs)
        return wrapper
    return decorator

def main():
    global host, config_data, wmodem_folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'wmodem.config')
    config_data = read_config(config_file_path)
    wmodem_folder = os.path.join(script_dir, config_data["folder"])

    host = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host.bind((config_data["ip"], int(config_data["port"])))

    print("Waiting for messages...")
    while True:
        pass

@receive_message(host)
def handle_message(message_bytes, address):
    command_code = int.from_bytes(message_bytes[:4], 'big')
    if command_code == COMMAND_CODES['req']:
        request = message_bytes[4:].decode()
        handle_request(request, host)
    elif command_code in COMMAND_CODES.values():
        print("Received command code:", message_bytes)
    else:
        print("Received message:", message_bytes)

if __name__ == "__main__":
    main()
