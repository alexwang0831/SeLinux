"""
SeLinux
Read/Write memory and I/O under Linux
"""

from tkinter import *
from tkinter import filedialog
import subprocess
import os
import SeLinuxPci
import SeLinuxMem
import SeLinuxIo
import SeLinuxIndex

PROGRAM_NAME = "SeLinux"
TOTAL_WIDTH = 550
TOTAL_HEIGHT = 340

# SeLinux UI Class
class seLinuxApplication:
    def __init__(self, root):
        ## private variable
        self.registerListTextWidget = []
        self.registerList = []
        self.StrToHex = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        self.userAddress = str()

        self.pciDevice = SeLinuxPci.seLinuxPciDevice()
        self.memRegister = SeLinuxMem.seLinuxMemory()
        self.ioRegister = SeLinuxIo.seLinuxIo()
        self.indexRegister = SeLinuxIndex.seLinuxIndexIo()

        self.seletcFunction = StringVar()
        ## draw ui
        self.root = root
        self.root.title(PROGRAM_NAME)
        #self.root.geometry('550x340')
        self.root.resizable(width = False, height = False)

        # Default Function
        self.registerList = self.pciDevice.readPciDevRegister()

        self.rowNumberFrame = Frame(self.root)
        self.rowNumberLabel = Label(self.rowNumberFrame, text = "00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F", padx=20, font=("Courier", 9))
        self.rowNumberLabel.pack(side="left")

        self.cancel_btn = Button(self.rowNumberFrame)
        self.cancel_btn.config(text="Cancel", font="Arial 6 bold", width=10, command = self.cancelUpdate)
        self.cancel_btn.pack(side='right')

        self.update_btn = Button(self.rowNumberFrame)
        self.update_btn.config(text="Update", font="Arial 6 bold", width=10, command = self.updateRegister)
        self.update_btn.pack(side='right')

        #Label(self.rowNumberFrame, text="", padx=8).pack(side="left")
        #for r in range(0x10):
        #    Label(self.rowNumberFrame, text="0{0}".format(self.StrToHex[r]), borderwidth=1).pack(side="left")
        self.rowNumberFrame.grid(row=0, column=0, columnspan=3, stick="wn")

        self.columnNumberFrame = Frame(self.root, width=20)
        #for r in range(0x10):
        #    Label(self.columnNumberFrame, text="{0}0".format(self.StrToHex[r]), font=("Courier", 8)).pack(side="top")
        self.columnNumberLabel = Label(self.columnNumberFrame, text = "00\n10\n20\n30\n40\n50\n60\n70\n80\n90\nA0\nB0\nC0\nD0\nE0\nF0", font=("Courier", 9))
        self.columnNumberLabel.pack(side="top")

        self.columnNumberFrame.grid(row=1, column=0, stick="wn")

        self.registerFrame = Frame(self.root)
        self.registerText = Text(self.registerFrame, wrap='word', border = 1,
                                 width = 48, height = 16)
        registerStr = ' '.join(self.registerList)
        self.registerText.insert("1.0", registerStr.upper())
        self.registerText.pack(side = 'top')
        #for r in range(16):
        #    for c in range(16):
        #        self.registerListTextWidget.append(Text(self.registerFrame, wrap='char', border=0, width=2, height=1))

        #for r in range(16):
        #    for c in range(16):
        #        self.registerListTextWidget[r*0x10 + c].insert("1.0", self.registerList[r*0x10 + c].upper())
        #        self.registerListTextWidget[r*0x10 + c].grid(row=r, column=c)
        self.registerFrame.grid(row=1, column=1, stick="nesw")

        self.asciiFrame = Frame(self.root, width=200, height=230)
        self.asciiFrame.grid(row=1, column=2)

        #self.root.grid_rowconfigure(1, weight=1)
        #self.root.grid_columnconfigure(1, weight=1)
        self.buildMenu()
        self.registerText.bind('<Key>', self.keyStatus)
        self.keyEvent = self.root.after(1000, self.repeat)

    def buildMenu(self):
        self.menuBar = Menu(self.root)
        self.fileMenu = Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label='Open', compound='left', command=self.openFunction )
        self.fileMenu.add_command(label='Save', compound='left', command=self.saveFunction)
        self.fileMenu.add_command(label='Exit', accelerator='Alt+F4', command=self.exitFunction)

        self.funcionMenu = Menu(self.menuBar, tearoff=0)
        self.funcionMenu.add_radiobutton(label='Memory', compound='left', variable=self.seletcFunction, command=self.processFunction)
        self.funcionMenu.add_radiobutton(label='General I/O', compound='left', variable=self.seletcFunction, command=self.processFunction)
        self.funcionMenu.add_radiobutton(label='Index I/O', compound='left', variable=self.seletcFunction, command=self.processFunction)
        self.funcionMenu.add_separator()

        self.pciMenu = Menu(self.menuBar, tearoff=0)
        for k, v in self.pciDevice.all_Pci_Device_Dict.items():
            self.pciMenu.add_radiobutton(label = "{0} {1}".format(k,v), compound='left', variable=self.seletcFunction, command=self.processFunction)
        self.funcionMenu.add_cascade(label='PCI Device', menu=self.pciMenu)

        self.aboutMenu = Menu(self.menuBar, tearoff=0)
        self.aboutMenu.add_radiobutton(label='About',command=self.aboutFunction)

        self.menuBar.add_cascade(label='File', menu=self.fileMenu)
        self.menuBar.add_cascade(label='Function', menu=self.funcionMenu)
        self.menuBar.add_cascade(label='About', menu=self.aboutMenu)
        self.root.config(menu=self.menuBar)

    def aboutFunction(self):
        self.about_toplevel = Toplevel(self.root, bg='White')
        aboutStr = "\nThis Tool is used to read/Write PCI, I/O, ISA I/O and memory value.\nIt may destory your system, please take care before you modify."
        writerStr = "\n\n\n\n\n                               Write by Alex Wang"
        #label = Label(self.about_toplevel)
        #label.grid(row=0, column=0)
        textAbout = Text(self.about_toplevel, height=10)
        textAbout.insert('1.0', "{0} {1} {2}".format("version: 1.0.0", aboutStr, writerStr))
        textAbout.config(state='disabled')
        textAbout.grid(row=0, column = 0)
        Button(self.about_toplevel, text="Done", underline=0, command=lambda: self.about_toplevel.destroy()) \
              .grid(row=1, column=0)

    def openFunction(self):
        options = {}
        options['initialdir'] = os.getcwd()
        options['title'] = "Open File"
        filename = filedialog.askopenfilename(**options)

        if not filename: # askopenfilename return an empty string if dialog closed with "cancel".
            return

        f = open(filename, "r")
        text2read = f.read()
        f.close() # `()` was missing.

       
        # Find first "\n" in text2save
        firstN = 0
        while True:
            if text2read[firstN] == "\n":
                break
            firstN += 1

        # Find second "\n" in text2save
        secondN = firstN +1
        while True:
            if text2read[secondN] == "\n":
                break
            secondN += 1

        # Compare function type
        functionType = text2read[:firstN]
        addressInFile = text2read[firstN+1:secondN]

        # Chectk file content
        # Error check do not finish, don't modify the format and content  in register file
        if functionType not in ['Memory', 'General I/O', 'Index I/O', 'PCI Device']:
            print("file corruption")
            return
        
        # Compare function and address
        if functionType in ['Memory', 'General I/O', 'Index I/O']:
            if functionType != self.seletcFunction.get():
                print("function is not match!")
                return
            if addressInFile != self.userAddress:
                print("Address is not match!")
                return
        else:
            if addressInFile != self.seletcFunction.get()[:7]:
                print("PCI Device is not match")
                return

        registerStr = text2read[secondN+1: -1]
        registerStr = registerStr.replace("\n", "")
        self.registerText.delete("1.0", "end")
        self.registerText.insert("1.0", registerStr.upper())
        
        # Stop update Text widget, because it will be destoried by auto-update event
        self.root.after_cancel(self.keyEvent)

    def saveFunction(self):       
        
        if self.seletcFunction.get() == "":
            # Default Function
            text2save = "PCI Device" + "\n" + "00:00.0" + "\n"
        elif self.seletcFunction.get() not in ['Memory', 'General I/O', 'Index I/O']:
            # Select Pci Device
            text2save = "PCI Device" + "\n" + self.seletcFunction.get()[:7] + "\n"
        else:
            # Other function
            text2save = self.seletcFunction.get() + "\n" + self.userAddress + "\n"

        # Transfer register content to 16 * 16 array
        RegisteContent = ' '.join(self.registerList)
        
        for i in range(16):
            for x in range(16):
                text2save += self.registerList[i * 16 + x] + " "
            text2save += "\n"

        # Find first "\n" in text2save
        firstN = 0
        while True:
            if text2save[firstN] == "\n":
                break
            firstN += 1

        # Find second "\n" in text2save
        secondN = firstN +1
        while True:
            if text2save[secondN] == "\n":
                break
            secondN += 1

        options = {}
        options['defaultextension'] = ".txt"
        options['filetypes'] = [("all files", ".*"), ("text files", ".txt")]
        options['initialdir'] = os.getcwd()
        options['initialfile'] = text2save[:3] + text2save[firstN+1:secondN]
        options['title'] = "Save As"

        f2 = filedialog.asksaveasfilename(**options)
        if not f2: # asksaveasfilename return an empty string if dialog closed with "cancel".
            return

        f = open(f2, "w")
        f.write(text2save)
        f.close() # `()` was missing.        

    def exitFunction(self):
        self.root.destroy()

    def cancelUpdate(self):
        self.keyEvent = self.root.after(1000, self.repeat)

    def updateRegister(self):
        newRegister = self.registerText.get('1.0', 'end').split(" ")
        newRegister[-1] = newRegister[-1][0:2]

        if(self.seletcFunction.get() == 'Memory'):
            self.registerList = self.memRegister.writeMemory(self.userAddress, self.registerList, newRegister)
        elif(self.seletcFunction.get() == 'Index I/O'):
            self.registerList = self.indexRegister.writeIndexIo(self.userAddress, self.registerList, newRegister)
        elif(self.seletcFunction.get() == 'General I/O'):
            self.registerList = self.ioRegister.writeIo(self.userAddress, self.registerList, newRegister)
        else:
            # Calculate PFA
            pfaHex = 0x80000000
            shortAddr = self.seletcFunction.get()[:7]
            pfaHex = 0x80000000 + (int(shortAddr[0:2], 16) << 16) + (int(shortAddr[3:5],16) << 11) + (int(shortAddr[-1],16) << 8)
            pfaHex = str(hex(pfaHex))
            self.registerList = self.pciDevice.writePciDevRegister(pfaHex[2:], self.registerList, newRegister)

        self.keyEvent = self.root.after(1000, self.repeat)

    def processFunction(self):
        # PCI Device
        if self.seletcFunction.get() not in ['Memory', 'General I/O', 'Index I/O']:
            # Calculate PFA
            pfaHex = 0x80000000
            shortAddr = self.seletcFunction.get()[:7]
            pfaHex = 0x80000000 + (int(shortAddr[0:2], 16) << 16) + (int(shortAddr[3:5],16) << 11) + (int(shortAddr[-1],16) << 8)
            pfaHex = str(hex(pfaHex))
            self.registerList = self.pciDevice.readPciDevRegister(pfaHex[2:])
        else:
            self.userEntryAddress()

    def readFromRegister(self, userAddress, topLevel):
        topLevel.destroy()
        self.userAddress = userAddress

        if self.seletcFunction.get() == 'Memory':
            self.registerList = self.memRegister.readMemory(userAddress)
        elif(self.seletcFunction.get() == 'Index I/O'):
            self.registerList = self.indexRegister.readIndexIo(userAddress)
        else:
            self.registerList = self.ioRegister.readIo(userAddress)


    def userEntryAddress(self):

        self.userAddr_toplevel = Toplevel(self.root)
        if(self.seletcFunction.get() == 'Memory'):
            self.userAddr_toplevel.title('Memory Address')
        elif(self.seletcFunction.get() == 'Index I/O'):
            self.userAddr_toplevel.title('Index I/O')
        else:
            self.userAddr_toplevel.title('General I/O')

        self.userAddr_toplevel.transient(self.root)

        Label(self.userAddr_toplevel, text="Address:").grid(row=0, column=0, sticky='e')

        self.userAddr_widget = Entry(self.userAddr_toplevel, width=15)
        self.userAddr_widget.grid(row=0, column=1, padx=2, pady=2, sticky='we')
        self.userAddr_widget.focus_set()

        Button(self.userAddr_toplevel, text="Done", command=lambda: self.readFromRegister(self.userAddr_widget.get(), self.userAddr_toplevel), underline=0) \
               .grid(row=0, column=2, sticky='e' + 'w', padx=2, pady=2)

    def keyStatus(self, event):
        if (event.char):
            self.root.after_cancel(self.keyEvent)

    def repeat(self):

        #for r in range(0, 234):
        #    self.registerListTextWidget[r].delete("1.0", "end")
        #    self.registerListTextWidget[r].insert("1.0", self.registerList[r].upper())
        if self.seletcFunction.get() == 'Memory':
            self.registerList = self.memRegister.readMemory(self.userAddress)
        elif(self.seletcFunction.get() == 'Index I/O'):
            self.registerList = self.indexRegister.readIndexIo(self.userAddress)
        elif(self.seletcFunction.get() == 'General I/O'):
            self.registerList = self.ioRegister.readIo(self.userAddress)
        elif(self.seletcFunction.get() != ''):
            # Calculate PFA
            pfaHex = 0x80000000
            shortAddr = self.seletcFunction.get()[:7]
            pfaHex = 0x80000000 + (int(shortAddr[0:2], 16) << 16) + (int(shortAddr[3:5],16) << 11) + (int(shortAddr[-1],16) << 8)
            pfaHex = str(hex(pfaHex))
            self.registerList = self.pciDevice.readPciDevRegister(pfaHex[2:])
        else:
            self.registerList = self.pciDevice.readPciDevRegister()

        registerStr = ' '.join(self.registerList)
        self.registerText.delete("1.0", "end")
        self.registerText.insert("1.0", registerStr.upper())

        self.keyEvent = self.root.after(1000, self.repeat)

if __name__ == "__main__":
    root = Tk()
    seLinuxApplication(root)

    root.mainloop()
