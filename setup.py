from distutils.core import setup
import py2exe

setup(
    service=[{
        'modules': 'service',
        'cmdline_style': 'pywin32',
        'description': 'Serial over TCP server service.'
    }],
    console=['server.py'],
)
