import subprocess
import os
from collections import OrderedDict

class seLinuxIndexIo:
    def __init__(self):
        pass

    def readIndexIo(self, userAddress=None):
         cmd = ['.//Application//SeLinux.out', '-index', userAddress]
         output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
         output = list(output)
         self.devicesRegList = "".join(map(chr, output))
         self.devicesRegList = self.devicesRegList.split(" ")
         self.devicesRegList.pop()

         return self.devicesRegList


    def writeIndexIo(self, userAddress, orgRegister, newRegister):
        #cmd = ['.//Application//SeLinux.out', '-memory', memAddress]
        #output = subprocess.Popen( cmd ).communicate()[0]
        # find differente
        for i in range(len(orgRegister)):
            if(orgRegister[i].upper() != newRegister[i].upper()):
                cmd = ['.//Application//SeLinux.out', '-index', userAddress, str(hex(i))[2:], newRegister[i]]
                output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]

        return self.readIndexIo(userAddress)
