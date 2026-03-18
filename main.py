import logging
import os
import sys
import threading
import traceback

from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.sync import StartTcpServer
from pymodbus.version import version

from ewa import ServerData

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value in (None, ''):
        return default
    return int(value)


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value in (None, ''):
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def interactive_console(dta: ServerData):
    while True:
        try:
            i = input('=>')
        except EOFError:
            return

        if i.lower() == 'exit':
            sys.exit()

        try:
            vals = i.split('=')
            if len(vals) == 1:
                param = vals[0]
                val = None
                if param[0:4] == 'coil':
                    adr = int(param[4:])
                    val = dta.getValues(adr)[0]
                elif param == 'help':
                    print('Values: ' + str(dta.__dict__.keys()))
                    print('Additional values: coilNNN , laedt')
                else:
                    val = dta.__getattribute__(param)

                if val is not None:
                    print('Value of ' + param + ' - ' + str(val) + ' Type: ' + str(type(val)))
            else:
                param,inputvalue = vals
                param = param.strip().lower()
                inputvalue = inputvalue.strip()

                if param == 'laedt':
                    dta.laedt = inputvalue.lower() in ('true', '1', 'ja', 'ok')
                elif param in dta.__dict__.keys():
                    val = dta.__getattribute__(param)
                    if isinstance(val, bool):
                        value = inputvalue.lower() in ('true', '1', 'ja', 'ok')
                    elif isinstance(val, int):
                        value = int(inputvalue)
                    elif isinstance(val, float):
                        value = float(inputvalue)
                    else:
                        value = inputvalue

                    print('Param changed from: ' + str(val) + ' to ' + str(value))

                    dta.__setattr__(param, value)
                elif param[0:4] == 'coil':
                    adr = int(param[4:])
                    value = inputvalue.lower() in ('true', '1', 'ja', 'ok')
                    val = dta.getValues(adr)[0]
                    print('Coil ' + str(adr) + ' set from ' + str(val) + ' to ' + str(value))
                    dta.setValues(adr, [value], onlyset=True)
                else:
                    val = dta.__getattribute__(param)
                    dta.__setattr__(param, inputvalue)

                    print('Param changed from: ' + str(val) + ' to ' + str(inputvalue))
        except Exception:
            traceback.print_exc()


def run_payload_server():
    dta = ServerData()
    store = ModbusSlaveContext(di=dta, co=dta, hr=dta, ir=dta)
    context = ModbusServerContext(slaves=store, single=True)
    bind_host = os.getenv('EWA_BIND_HOST', '0.0.0.0')
    bind_port = env_int('EWA_BIND_PORT', 502)
    interactive = env_bool('EWA_INTERACTIVE', sys.stdin.isatty())

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Easy Wallbox Adapter'
    identity.ProductCode = 'EWA'
    identity.VendorUrl = 'http://github.com/rxhan/ewa/'
    identity.ProductName = 'Easy Wallbox Adapter'
    identity.ModelName = 'Easy Wallbox Adapter'
    identity.MajorMinorRevision = version.short()

    def background():
        StartTcpServer(context, identity=identity, address=(bind_host, bind_port))

    if interactive:
        threading1 = threading.Thread(target=background, name='modbus-server')
        threading1.daemon = True
        threading1.start()
        interactive_console(dta)
        return

    background()


if __name__ == "__main__":
    run_payload_server()
