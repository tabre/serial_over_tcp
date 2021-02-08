"""Serial Over TCP Server to run from command line."""

from funcs import (
    read_config, get_tcp_socket, connect_serial, run_server
)

CONFIG_PATH = 'server.cfg'

configs = read_config(CONFIG_PATH)

run_server([{
    'name': config.get('name'),
    'address': config.get('tcp_address'),
    'port': config.get('tcp_port'),
    'sock': get_tcp_socket(config.get('tcp_address'), config.get('tcp_port')),
    'ser':  connect_serial({
        'port': config.get('serial_port'),
        'baud': config.get('serial_baud'),
        'parity': config.get('serial_parity'),
        'stopbits': config.get('serial_stopbits'),
        'bytesize': config.get('serial_bytesize'),
        'timeout': config.get('serial_timeout')
    }),
    'serial_read_bytes': config.get('serial_read_bytes'),
    'sso': config.get('serial_send_on')
} for config in configs], service=None)
