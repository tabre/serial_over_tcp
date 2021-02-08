"""Functions for Serial Over TCP server."""
import socket
import ast
import os

import serial  # pylint: disable=import-error

default_params = {
    'tcp_address': '0.0.0.0',
    'tcp_port': 5000,
    'serial_port': 'COM3',
    'serial_baud': 9600,
    'serial_parity': None,
    'serial_stopbits': 1,
    'serial_bytesize': 8,
    'serial_timeout': 1,
    'serial_read_bytes': 32,
    'serial_send_on': '\r'
}


def read_config(path):
    """Parse server config file, returning dictionary."""
    file_path = os.path.realpath(__file__).replace(
        "\r", "/r").replace("\f", "/f").replace("\\", "/")

    file_path = file_path.split("/")[:-1]

    if file_path[-1] == 'library.zip':
        file_path = file_path[:-1]

    file_path[0] = file_path[0] + "\\"

    path = os.path.join(*file_path, path)

    print("Loading config file from: {path}".format(path=path))

    try:
        configs = []
        config = {}
        config_file = open(path, "r")

        for line in config_file.readlines():

            if line[0] == '[':

                if len(config) > 0:
                    configs.append(config)
                config = {}

                key = 'name'
                value = line.strip().strip('[').strip(']')

                config[key] = value

            elif len(line.strip()) > 0:

                line = line.split("=")

                key = line[0].strip()
                value = ast.literal_eval(line[1].strip())

                config[key] = value

        configs.append(config)

    except IndexError as e:
        print("Warning - Error reading config file. Using default settings.")
        print(e)
        configs = [default_params]

    return configs


def get_tcp_socket(address='0.0.0.0', port=5000):
    """Create and return TCP/IP socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (address, port)
    print('Starting server on %s port %s' % server_address)
    sock.bind(server_address)

    return sock


def connect_serial(params):
    """Connect to serial port, return connection."""
    parities = {
        None: serial.PARITY_NONE,
        'even': serial.PARITY_EVEN,
        'odd': serial.PARITY_ODD,
        'mark': serial.PARITY_MARK,
        'space': serial.PARITY_SPACE
    }

    stopbitses = {
        1: serial.STOPBITS_ONE,
        1.5: serial.STOPBITS_ONE_POINT_FIVE,
        2: serial.STOPBITS_TWO
    }

    bytesizes = {
        5: serial.FIVEBITS,
        6: serial.SIXBITS,
        7: serial.SEVENBITS,
        8: serial.EIGHTBITS,
    }

    try:
        print("Connecting to serial port: {port}".format(
            port=params.get('port')
        ))
        ser = serial.Serial(
            port=params.get('port'),
            baudrate=params.get('baud'),
            parity=parities[params.get('parity')],
            stopbits=stopbitses[params.get('stopbits')],
            bytesize=bytesizes[params.get('bytesize')],
            timeout=params.get('timeout')
        )

        return ser

    except Exception as e:
        print("Error connecting to serial port: {port}".format(
            port=params['port']
        ))
        raise e


def cleanup(server):
    """Close connections cleanly."""
    print("[{}] Closing TCP listener on {}:{}".format(
        server.get('name'), server.get('address'), server.get('port')
    ))
    server.get('conn').close()
    print("[{}] Closing serial connection on {}".format(
        server.get('name'), server.get('ser').port
    ))
    server.get('ser').close()


def read_send_data(server):
    """Read data from serial device and send to TCP client."""
    if 'data' not in server:
        server['data'] = ''

    for byte in server.get('ser').read(server.get('serial_read_bytes')):
        byte = chr(byte)

        if byte != server.get('sso'):
            server['data'] = server.get('data') + byte
        else:
            print("[{}] Sending data to client ({}:{}): {}".format(
                server.get('name'), server.get('client_addr')[0],
                server.get('port'), server.get('data')
            ))
            server.get('conn').sendall(server.get('data').encode('utf-8'))
            server['data'] = ''


def run_server(servers, service=None):
    """Start TCP socket and connect to serial device. Run server."""
    for server in servers:
        server.get('sock').listen(1)

    while service is None or service.run:

        for server in servers:
            # Output listening message
            print("[{}] listening for TCP connections on {}:{}".format(
                server.get('name'), server.get('address'), server.get('port')
            ))

            # Accept incoming connection
            server['conn'], server['client_addr'] = server.get('sock').accept()

            # Output incoming connection message
            print('Incoming connection', server['client_addr'][0])

        while service is None or service.run:
            try:
                for server in servers:
                    read_send_data(server)

            except KeyboardInterrupt:
                for server in servers:
                    cleanup(server)
                return
    for server in servers:
        cleanup(server)
    return
