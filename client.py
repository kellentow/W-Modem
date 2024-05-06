import socket
import os

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

def receive_chunk(client_socket):
    chunk, address = client_socket.recvfrom(1028)
    return chunk

def receive_file(file_path, client_socket):
    with open(file_path, 'wb') as file:
        while True:
            chunk = receive_chunk(client_socket)
            command_code = int.from_bytes(chunk[:4], 'big')
            if command_code == COMMAND_CODES['cnk']:
                file.write(chunk[4:])
            elif command_code == COMMAND_CODES['eot']:
                print("File received successfully.")
                break
            else:
                print("Error: Unexpected command code received.")

def main():
    # Read the config file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'wmodem.config')
    config_data = read_config(config_file_path)
    while True:
        # Get user input for the file path
        file_path = input("Enter the file path to save: ")

        # Connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            # Send request for file
            req_code = COMMAND_CODES['req']
            client_socket.sendto(req_code.to_bytes(4, 'big'), (config_data["ip"], int(config_data["port"])))

            # Receive the file from the server
            receive_file(file_path, client_socket)

if __name__ == "__main__":
    main()
