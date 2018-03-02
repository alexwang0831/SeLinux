import subprocess
import os
from collections import OrderedDict

class seLinuxPciDevice:
    def __init__(self):
        self.all_Pci_Device_Dict = OrderedDict()
        self.all_Pci_Device_str = str()
        self.pfaToC = str()
        self.devicesRegList = list()

        self.parsingPciDeviceStr(self.getAllPciDeviceStr())

    def getAllPciDeviceStr(self):
        """
        Using Linux build-in function(lspci) to get all pci devices
        return:
            all Pci device in one string
        """

        cmd = ['lspci']
        output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]

        output = list(output)
        devices = "".join(map(chr, output))

        return devices

    def parsingPciDeviceStr(self, pciString):
        """
        Parsing PCI devices in string format
        Input:
            pciString: string to save all pci devices
        return:
            dictionary in {"pfa":"device description"} format
        """

        pfa = str()
        description = str()
        tempList = list()
        i = 0

        # turn str to list
        start = 0
        end = 0
        while(i < pciString.__len__()):
            end = i
            if (pciString[i] == '\n'):
                tempList.append(pciString[start:end])
                start = i + 1
            i += 1

        # Now we have a list which each element save on pci device, turn it to dict
        for i in tempList:
            pfa = i[0:7]
            for index ,c in enumerate(i[8:i.__len__()]):
                if ":"==c:
                    description = i[index + 10:]
                    break # make sure we get whole description

            self.all_Pci_Device_Dict.update({pfa:description})


    def readPciDevRegister(self, pfaAddr="80000000"):
        """
        read specific PCI devices Register
        Input:
            Pci configuration addres, default = 80000000
        return:
            a list that save the device register at pfa address
        """
        VenderDict = {
                      0x8086:"Intel",
                      0x10EC:"Realtek",
                      0x168C:"Qualcomm",
                      0x1022:"AMD",
                      0x1002:"AMD/ATI"
                     }

        ClassDict = {
                     0x00:"Devices built before class codes",
                     0x01:"Mass Storage Controller",
                     0x02:"Network Controller",
                     0x03:"Display Controller",
                     0x04:"Multimedia Controller",
                     0x05:"Memory Controller",
                     0x06:"Bridge Device",
                     0x07:"Simple Communication Controllers",
                     0x08:"Base System Peripherals",
                     0x09:"Input Devices",
                     0x0A:"Docking Stations",
                     0x0B:"Processors",
                     0x0C:"Serial Bus Controllers",
                     0x0D:"Wireless Controllers",
                     0x0E:"Intelligent I/O Controllers",
                     0x0F:"Satellite Communication Controllers",
                     0x10:"Encryption/Decryption Controllers",
                     0x11:"Data Acquisition and Signal Processing Controllers"
                    }
        cmd = ['.//Application//SeLinux.out', '-pci', pfaAddr]
        output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
        output = list(output)
        self.devicesRegList = "".join(map(chr, output))
        self.devicesRegList = self.devicesRegList.split(" ")
        self.devicesRegList.pop()

        return self.devicesRegList

    def writePciDevRegister(self, pfaAddr, orgRegister, newRegister):
        for i in range(len(orgRegister)):
            if(orgRegister[i].upper() != newRegister[i].upper()):
                cmd = ['.//Application//SeLinux.out', '-pci', pfaAddr, str(hex(i))[2:], newRegister[i]]
                output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]

        return self.readPciDevRegister(pfaAddr)
