import usb.core
import usb.util
import struct
import sys

class Arcticfox(object):
    products = {
        "E052": 'Joyetech eVic VTC Mini',
        "E043": 'Joyetech eVic VTwo',
        "E115": 'Joyetech eVic VTwo Mini',
        "E079": 'Joyetech eVic VTC Dual',
        "E150": 'Joyetech eVic Basic',
        "E092": 'Joyetech eVic AIO',
        "E182": 'Joyetech eVic Primo',
        "E203": 'Joyetech eVic Primo 2.0',
        "E196": 'Joyetech eVic Primo Mini',

        "E060": 'Joyetech Cuboid',
        "E056": 'Joyetech Cuboid Mini',
        "E166": 'Joyetech Cuboid 200',

        "E083": 'Joyetech eGrip II',

        "M973": 'Eleaf iStick QC 200W',
        "M972": 'Eleaf iStick TC200W',
        "M011": 'Eleaf iStick TC100W',
        "M041": 'Eleaf iStick Pico',
        "M038": 'Eleaf iStick Pico RDTA',
        "M045": 'Eleaf iStick Pico Mega',
        "M065": 'Eleaf iStick Pico Dual',
        "M046": 'Eleaf iStick Power',
        "M037": 'Eleaf ASTER',

        "W007": 'Wismec Presa TC75W',
        "W017": 'Wismec Presa TC100W',

        "W018": 'Wismec Reuleaux RX2/3',
        "W014": 'Wismec Reuleaux RX200',
        "W033": 'Wismec Reuleaux RX200S',
        "W026": 'Wismec Reuleaux RX75',
        "W069": 'Wismec Reuleaux RX300',
        "W073": 'Wismec Reuleaux RXmini',
        "W078": 'Wismec Predator',

        "W010": 'Vaporflask Classic',
        "W011": 'Vaporflask Lite',
        "W013": 'Vaporflask Stout',

        "W016": 'Beyondvape Centurion',
        "W043": 'Vaponaute La Petit Box',

        "W057": 'Vapor Shark SwitchBox RX'
    }

    cmds = {
        "readDataflash": 0x35,
        "writeDataflash": 0x53,
        "resetDataflash": 0x7C,

        "writeData": 0xC3,
        "restart": 0xB4,

        "screenshot": 0xC1,

        "readMonitoringData": 0x66,
        "puff": 0x44,

        "readConfiguration": 0x60,
        "writeConfiguration": 0x61,
        "setDateTime": 0x64,

        "setLogo": 0xA5
    }

    hid_signature = bytearray(b'HIDC')

    def __init__(self):
        self.device = None
        self.manufacturer = None
        self.product = None
        self.serial = None
        self.ldrom = False
        self.endpoint_in = None
        self.endpoint_out = None

    def connect(self):
        self.device = usb.core.find(idVendor=0x0416, idProduct=0x5020)

        if self.device is None:
            raise RuntimeError("No devices found")

        reattach = False
        if self.device.is_kernel_driver_active(0):
            reattach = True
            self.device.detach_kernel_driver(0)

        self.endpoint_in = self.device[0][(0,0)][0]
        self.endpoint_out = self.device[0][(0,0)][1]

    def hidcmd(self, cmdcode, arg1, arg2):
        """Generates a Nuvoton HID command.
        Args:
            cmdcode: A byte long HID command.
            arg1: First HID command argument.
            arg2: Second HID command argument.
        Returns:
            A bytearray containing the full HID command.
        """

        # Do not count the last 4 bytes (checksum)
        length = bytearray([14])

        # Construct the command
        cmdcode = bytearray(struct.pack('=B', cmdcode))
        arg1 = bytearray(struct.pack('=I', arg1))
        arg2 = bytearray(struct.pack('=I', arg2))
        cmd = cmdcode + length + arg1 + arg2 + self.hid_signature

        # Return the command with checksum tacked at the end
        return cmd + bytearray(struct.pack('=I', sum(cmd)))

    def send_command(self, cmd, arg1, arg2):
        """Sends a HID command to the device.
        Args:
            cmd: Byte long HID command
            arg1: First argument to the command (integer)
            arg2: Second argument to the command (integer)
        """

        command = self.hidcmd(cmd, arg1, arg2)
        return self.endpoint_out.write(command)


    def readMonitoringData(self):
        self.send_command(self.cmds["readMonitoringData"],0,64)
        data = self.device.read(self.endpoint_in.bEndpointAddress, 64, 1000)
       
        Timestamp = struct.unpack("I", data[0:4])[0]
        IsFiring = struct.unpack("?", data[4:5])[0]
        IsCharging = struct.unpack("?", data[5:6])[0]
        IsCelcius = struct.unpack("?", data[6:7])[0]
        Battery1Voltage = struct.unpack("b", data[7:8])[0]
        Battery2Voltage = struct.unpack("b", data[8:9])[0]
        Battery3Voltage = struct.unpack("b", data[9:10])[0]
        Battery4Voltage = struct.unpack("b", data[10:11])[0]
        PowerSet = struct.unpack("h", data[11:13])[0]
        TemperatureSet = struct.unpack("h", data[13:15])[0]
        Temperature = struct.unpack("h", data[15:17])[0]
        OutputVoltage =struct.unpack("h", data[17:19])[0]
        OutputCurrent = struct.unpack("h", data[19:21])[0]
        Resistance = struct.unpack("h", data[21:23])[0]
        RealResistance = struct.unpack("h", data[23:25])[0]
        BoardTemperature = struct.unpack("b", data[11:12])[0]

        if Battery1Voltage != 0:
            Battery1Voltage = (Battery1Voltage + 275) / 100
        if Battery2Voltage != 0:
            Battery2Voltage = (Battery2Voltage + 275) / 100
        if Battery3Voltage != 0:
            Battery2Voltage= (Battery3Voltage + 275) / 100
        if Battery4Voltage != 0:
            Battery4Voltage = (Battery4Voltage + 275) / 100

        PowerSet = PowerSet / 10
        OutputVoltage = OutputVoltage / 100
        OutputCurrent = OutputCurrent / 100
        OutputPower = "{00:.2f}".format(OutputVoltage * OutputCurrent)

        MonitoringData = {
                "Timestamp": Timestamp,
                "IsFiring":IsFiring,
                "IsCharging": IsCharging,
                "IsCelcius": IsCelcius,
                "Battery1Voltage": Battery1Voltage,
                "Battery2Voltage": Battery2Voltage,
                "Battery3Voltage": Battery3Voltage,
                "Battery4Voltage": Battery4Voltage, 
                "PowerSet": PowerSet,
                "TemperatureSet": TemperatureSet,
                "Temperature": Temperature,
                "OutputVoltage": OutputVoltage,
                "OutputCurrent": OutputCurrent,
                "Resistance": Resistance,
                "RealResistance": RealResistance,
                "BoardTemperature": BoardTemperature,
                "OutputPower": OutputPower
        }
        return MonitoringData

    def restart(self):
        return self.send_command(self.cmds['restart'], 0, 0)

    def screenshot(self):
        #self.send_command(self.cmds["screenshot"], 0, 1024)
        raise NotImplementedError("Feature not yet implemented")

    def setDateTime(self, date):
        #https://github.com/hobbyquaker/arcticfox/blob/master/index.js#L1117
        #self.send_command(self.cmds['setDateTime'], 0, 0)
        raise NotImplementedError("Feature not yet implemented")

    def puff(self, seconds):
        return self.send_command(self.cmds['puff'], seconds, 0)
