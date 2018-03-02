import subprocess
import os
from collections import OrderedDict

class seLinuxMemory:
    def __init__(self):
        pass

    def readMemory(self, userAddress=None):
         cmd = ['.//Application//SeLinux.out', '-memory', userAddress]
         output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
         output = list(output)
         self.devicesRegList = "".join(map(chr, output))
         self.devicesRegList = self.devicesRegList.split(" ")
         self.devicesRegList.pop()

         return self.devicesRegList


    def writeMemory(self, userAddress, orgRegister, newRegister):
        #cmd = ['.//Application//SeLinux.out', '-memory', memAddress]
        #output = subprocess.Popen( cmd ).communicate()[0]
        # find differente
        for i in range(len(orgRegister)):
            if(orgRegister[i].upper() != newRegister[i].upper()):
                cmd = ['.//Application//SeLinux.out', '-memory', userAddress, str(hex(i))[2:], newRegister[i]]
                output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]

        return self.readMemory(userAddress)
