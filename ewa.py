import datetime
import logging

import requests
from pymodbus.datastore import ModbusSparseDataBlock

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ServerData(ModbusSparseDataBlock):
    def __init__(self):
        ModbusSparseDataBlock.__init__(self, values=None, mutable=True)

        self.blindleistung = 0                  # VAr
        self.scheinleistung = 0                 # VA
        self.leistungsfaktor = 1                # Cosphi/1000
        self.phases_ampere = (0*10, 0*10, 0*10)          # in A (*10
        self._phases_voltage = (230,230,230)     # in V

        self.phases_measured_url = 'http://192.168.179.65:1880/sensor?datensammler_sdm630.status'
        self.phases_maxampere = (0, 0, 0)       # in A
        self.phases = 1                         # Anzahl verwendeter Phasen (1 oder 3)
        self._energietotal = 0                  # in kWh
        self._energietotal_dt = 0.0
        self._energieaktuell = 0                # in kWh
        self._energieaktuell_dt = 0.0
        self.maxleistung = 0                    # maximale Leistung in W
        self.netzfrequenz = 50.0                # in hz
        self.mac = 'E8D8D1663B5B'               # MAC-Addr
        self.seriennummer = '00000000001'       # Seriennummer
        self.ladestrom = 16*10                  # Ladestrom in A
        self._laedt = False                     # Ladevorgang gestartet
        self._ladestart : float = 0.0           # Ladestart gestartet

        self.entriegelt = False                 # Verriegelung
        self.autoangesteckt = True              # Auto angesteckt?
        self.freigegeben = False                # Ladevorgang freigegeben?
        self.fahrzeugabweisen = False           # Fahrzeug abweisen
        self.verfuegbarkeit_ladestation = True  # Verfügbarkeit der Ladestation

        self.fehlercodes1 = 0b0000000000000000  # Register 107 - Fehlercodes
        self.dipschalter = 0b0000001001         # DIP-Schalter 0b0000001001 = mit Ladekabel (7+10), 0b1111011001 = mit Steckdose
        self.fehlercodes2 = 0b0000000           # Register 155 - Fehlercodes
        self.ip = '192.168.179.30'              # IP-Adresse
        self.subnet = '255.255.255.0'           # Mac-Adresse
        self.ladekabel = 320                    # Stromtragfähigkeit Ladekabel
        self.maximaler_ladestrom = 320          # Maximaler Ladestrom
        self.firmware = '1.21'                  # Firmware-Version

        self.ocppPricePerKWh = 0                # cent
        self.ocppHeartbeatInterval = 0          # s
        self.ocppConnectionTimeOut = 0          # s
        self.ocppMeterValueSampleInterval = 0   # s
        self.ocppResetRetries = 0               # count
        self.ocppTransactionMessageAttempts = 0     # count
        self.ocppMessageRetryInterval = 0           # s
        self._ladestatus = None

        self.setValues(101, self.get_100(), onlyset=True)
        self.setValues(301, self.get_300(), onlyset=True)
        self.setValues(328, self.get_327(), onlyset=True)
        self.setValues(520, self.get_519(), onlyset=True)
        self.setValues(3385, self.get_3384(), onlyset=True)
        self.setValues(201, self.get_200(), onlyset=True)
        self.setValues(401, self.get_400(), onlyset=True)
        self.setValues(462, self.get_461(), onlyset=True)
        self.setValues(436, self.get_435(), onlyset=True)
        self.setValues(413, self.get_412(), onlyset=True)

    def setValues(self, address, values, use_as_default=False, onlyset=False):
        if onlyset == False:
            logger.info('Set Values for address ' + str(address) + '/' + str(type(address)) + ' value ' + str(values))

            adr = address
            for value in values:
                if adr == 401:
                    logger.info('Ladevorgang gestartet / beendet: ' + str(value))
                    self.freigegeben = value
                    self.laedt = value
                elif adr == 529:
                    logger.info('Neuer Ladestrom: ' + str(int(round(value*0.1,0))) + 'A')
                    self.ladestrom = value
                    self.phases_ampere = (value,value,value)
                elif adr == 413:
                    self.fahrzeugabweisen = value
                elif adr == 414:
                    if value:
                        self.reset()
                elif adr == 441:
                    self.entriegelt = value
                elif adr == 403:
                    self.verfuegbarkeit_ladestation = value

                adr+=1

        ModbusSparseDataBlock.setValues(self, address=address, values=values, use_as_default=use_as_default)

    def getValues(self, address, count=1):
        #logger.debug('Get Values for address: ' + str(address) + ' count ' + str(count))
        if address == 101:
            self.setValues(101, self.get_100(), onlyset=True)
        if address == 301:
            self.setValues(301, self.get_300(), onlyset=True)
        if address == 328:
            self.setValues(328, self.get_327(), onlyset=True)
        if address == 520:
            self.setValues(520, self.get_519(), onlyset=True)
        if address == 3385:
            self.setValues(3385, self.get_3384(), onlyset=True)
        if address == 201:
            self.setValues(201, self.get_200(), onlyset=True)
        if address == 401:
            self.setValues(401, self.get_400(), onlyset=True)
        if address == 462:
            self.setValues(462, self.get_461(), onlyset=True)
        if address == 436:
            self.setValues(436, self.get_435(), onlyset=True)
        if address == 413:
            self.setValues(413, self.get_412(), onlyset=True)
        return ModbusSparseDataBlock.getValues(self, address, count)

    # Ladestatus A-F
    def get_ladestatus(self) -> str:
        if self._ladestatus is not None:
            return self._ladestatus
        if self.laedt:
            return 'C'
        if self.autoangesteckt and not self.laedt:
            return 'B'

        return 'A'

    def set_ladestatus(self, value: str):
        if value.upper() not in ('A','B','C','D','E','F'):
            self._ladestatus = None
        else:
            self._ladestatus = value.upper()

    ladestatus = property(get_ladestatus, set_ladestatus)

    def get_ladezeit(self) -> int:
        if self.laedt == True and self._ladestart is not None:
            return int(round(datetime.datetime.now().timestamp() - self._ladestart,0))
        else:
            return 0

    ladezeit = property(get_ladezeit)

    def get_laedt(self) -> bool:
        return self._laedt and self.autoangesteckt and self.entriegelt and self.freigegeben

    def set_laedt(self, value: bool):
        if self.freigegeben and self.autoangesteckt:
            if value == False:
                self._ladestart = None
                self.maxleistung = 0
                self._energieaktuell = 0
                self._energieaktuell_dt = 0.0

            if self._laedt == False and value == True:
                self._ladestart = datetime.datetime.now().timestamp()

            self._laedt = value

    laedt = property(get_laedt, set_laedt)

    def reset(self):
        self.laedt = False
        self.freigegeben = False
        self.entriegelt = True

    def get_phases_voltage(self) -> tuple:
        if self.phases_measured_url != '':
            try:
                req = requests.get(self.phases_measured_url)
                data = req.json()['data']
                self._phases_voltage = (int(data['30001']), int(data['30003']), int(data['30005']))
            except:
                pass

        return self._phases_voltage

    phases_voltage = property(get_phases_voltage)

    def get_phases_ampere(self) -> tuple:
        if self.laedt:
            if self.phases == 1:
                return (self._phases_ampere[0],0,0)
            else:
                return self._phases_ampere
        else:
            return (0,0,0)

    def set_phases_ampere(self, value: tuple):
        self._phases_ampere = value

    phases_ampere = property(get_phases_ampere, set_phases_ampere)

    def get_ladeleistung(self) -> int:
        if self.laedt:
            ladeleistung =  int(round(((self.phases_voltage[0] * self.phases_ampere[0]) + \
                            (self.phases_voltage[1] * self.phases_ampere[1]) + \
                            (self.phases_voltage[2] * self.phases_ampere[2]))* 0.1,0))

            if ladeleistung > self.maxleistung:
                self.maxleistung = ladeleistung

            ct = datetime.datetime.now().timestamp()
            if self._energieaktuell_dt > 0.0:
                if int(round(ct, 0)) != int(round(self._energieaktuell_dt, 0)):
                    diff = ct - self._energieaktuell_dt

                    ws = diff * ladeleistung

                    self._energieaktuell += ws
                    self._energieaktuell_dt = ct
            else:
                self._energieaktuell_dt = ct

            if self._energietotal_dt > 0.0:
                if int(round(ct, 0)) != int(round(self._energietotal_dt, 0)):
                    diff = ct - self._energietotal_dt

                    ws = diff * ladeleistung

                    self._energietotal += ws
                    self._energietotal_dt = ct
            else:
                self._energietotal_dt = ct

            return ladeleistung
        else:
            return 0

    ladeleistung = property(get_ladeleistung)

    def get_energieaktuell(self) -> int:
        return int(round(((self._energieaktuell / 3600) / 1000),0))

    energieaktuell = property(get_energieaktuell)

    def get_energietotal(self) -> int:
        return int(round(((self._energietotal / 3600) / 1000), 0))

    energietotal = property(get_energietotal)

    def get_100(self):
        return [ord(self.ladestatus), #StatusByte bei C  +32
                self.ladekabel,
                self.ladezeit,
                0,
                self.dipschalter] + \
                self.c_ascii216b(self.firmware) + \
                [self.fehlercodes1,
                self.phases_voltage[0], 0,  #100-109
                self.phases_voltage[1], 0,
                self.phases_voltage[2], 0,
                self.phases_ampere[0], 0,
                self.phases_ampere[1], 0,
                self.phases_ampere[2], 0,  #110-119
                self.ladeleistung, 0,
                self.blindleistung, 0,
                self.scheinleistung, 0,
                self.leistungsfaktor, 0,
                self.energietotal, 0,  #120-129
                self.maxleistung, 0,
                self.energieaktuell, 0,
                int(round(self.netzfrequenz*10,0)), 0,
                self.phases_maxampere[0], 0,
                self.phases_maxampere[1], 0,  #130-139
                self.phases_maxampere[2], 0,
                self.ocppPricePerKWh,
                self.ocppHeartbeatInterval,
                self.ocppConnectionTimeOut,
                self.ocppMeterValueSampleInterval,
                self.ocppResetRetries,
                self.ocppTransactionMessageAttempts,
                self.ocppMessageRetryInterval, 0,  #140-149
                0, 0, 0, 0, 0, 0]

    def get_300(self):
        ret= [self.ladestrom] + \
                self.c_ascii2hex(self.mac) + \
                self.c_ascii216b(self.seriennummer) + \
                [0, 0, 0, 0, 0] + \
                self.c_ip2int(self.ip) + \
                self.c_ip2int(self.subnet)
        return ret

    def get_327(self):
        return [15, 17, 16,  # 327-329
         40, 34, 50, 66, 36, 52, 68, 16, 18, 20,  # 330-339
         0, 0, 0, 0, 22, 0, 0, 0, 0, 0,  # 340-349
         0, 0, 1, 0, 1, 0, 1, 0, 1, 0,  # 350-359
         1, 0, 1, 0, 1, 0, 1, 0, 1, 0,  # 360-369
         1000, 0, 1000, 0, 0, 0, 0, 0, 10, 0,  # 370-379
         1, 0, 1, 0, 1, 0, 19200, 0, 1, 1000,  # 380-389
         1, 0, 0, 0, 0, 0, 0, 0]

    def get_519(self):
        return [500, 22, 1, 11, 2, 11, 500, 500, 2000, self.ladestrom]

    def get_3384(self):
        return [self.maximaler_ladestrom]

    def get_200(self):
        return [self.values.get(201,True),    #statusByte+16 (True)
                self.laedt,
                self.values.get(203,True),
                self.values.get(204,False),
                self.values.get(205,False),
                self.values.get(206,False),   #statusByte+8 (True)
                self.values.get(207,False),
                self.values.get(208,True),
                self.values.get(209,False)]

    def get_400(self):
        return [self.freigegeben,
                self.values.get(402,False),
                self.verfuegbarkeit_ladestation,
                self.values.get(404,False),
                self.values.get(405,True),   # Auf False versucht E3DC einen reset(414=True)
                self.values.get(406,False),
                self.values.get(407,False),
                self.values.get(408,False),
                self.values.get(409,False),
                self.values.get(410,False),
                self.values.get(411,False)]

    def get_461(self):
        return [self.values.get(462,True),
                self.values.get(463,True),
                self.values.get(464,False),
                self.values.get(465,False)]

    def get_435(self):
        return [self.values.get(436,False),
                self.values.get(437,False),  # passiert nichts
                self.values.get(438,False),
                self.values.get(439,False),
                self.values.get(440,False),
                self.entriegelt]

    def get_412(self):
        return [self.fahrzeugabweisen,
                self.values.get(414,False)]

    def c_ip2int(self, s: [str, list]):
        if isinstance(s, str):
            segments = s.split('.')
        elif isinstance(s, list):
            segments = s
        else:
            raise Exception('IP-Adresse in falschem Format (str, list)')

        if len(segments) < 4:
            raise Exception('IP-Adresse in falschem Format ' + s)

        return [int(i) for i in segments]

    def c_ascii2hex(self, s):
        res = []
        for i in range(0,len(s)):
            if i % 4 == 3:
                a = s[i-1] + s[i] + s[i-3] + s[i-2]
                res.append((int(a,16)))

        if len(s) % 2 == 1:
            res.append((int(s[-1:],16)))

        return res


    def c_16b2ascii(self, i):
        def _(c):
            return [c] if c <= 255 else list(divmod(c, 256))

        return ''.join([chr(c) for h in i for c in _(h)])

    def c_ascii216b(self, s):
        res = []
        for i in range(0,len(s)):
            if i % 2 == 1:
                a1 = ord(s[i-1]) << 8
                a2 = ord(s[i])
                res.append(a1 | a2)

        if len(s) % 2 == 1:
            res.append(ord(s[-1:]))

        return res