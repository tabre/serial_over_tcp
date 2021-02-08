"""Serial Over TCP Server Windows Service to run hidden in background."""
import socket

import win32serviceutil
import win32service
import win32event
import servicemanager

from funcs import (
    read_config, get_tcp_socket, connect_serial, run_server
)

CONFIG_PATH = 'server.cfg'


class SerialOverTCPSvc (win32serviceutil.ServiceFramework):
    """Serial Over TCP Server Windows Service."""

    _svc_name_ = "serial_over_tcp"
    _svc_display_name_ = "Serial Over TCP Server"
    _svc_description_ = 'Simple server to send serial input over TCP.'

    @classmethod
    def parse_command_line(cls):
        """Parse the command line."""
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        """Construct the winservice."""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(  # pylint: disable=C0103
            None, 0, 0, None
        )
        socket.setdefaulttimeout(60)
        self.run = True

    def SvcStop(self):  # pylint: disable=C0103
        """Stop service."""
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):  # pylint: disable=C0103
        """Start service."""
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        """Set running flag on start."""
        self.run = True

    def stop(self):
        """Set running flag on stop."""
        self.run = False

    def main(self):
        """Run server."""
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        configs = read_config(CONFIG_PATH)

        run_server([{
            'name': config.get('name'),
            'address': config.get('tcp_address'),
            'port': config.get('tcp_port'),
            'sock': get_tcp_socket(
                config.get('tcp_address'),
                config.get('tcp_port')
            ),
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
        } for config in configs], service=self)


if __name__ == '__main__':
    SerialOverTCPSvc.parse_command_line()
