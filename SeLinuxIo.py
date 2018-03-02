import subprocess
import os
from collections import OrderedDict

class seLinuxIo:
    def __init__(self):
        pass

    def readIo(self, userAddress=None):
         cmd = ['.//Application//SeLinux.out', '-io', userAddress]
         output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
         output = list(output)
         self.devicesRegList = "".join(map(chr, output))
         self.devicesRegList = self.devicesRegList.split(" ")
         self.devicesRegList.pop()

         return self.devicesRegList


    def writeIo(self, userAddress, orgRegister, newRegister):
        #cmd = ['.//Application//SeLinux.out', '-memory', memAddress]
        #output = subprocess.Popen( cmd ).communicate()[0]
        # find differente
        for i in range(len(orgRegister)):
            if(orgRegister[i].upper() != newRegister[i].upper()):
                cmd = ['.//Application//SeLinux.out', '-io', userAddress, str(hex(i))[2:], newRegister[i]]
                output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]

        return self.readIo(userAddress)
