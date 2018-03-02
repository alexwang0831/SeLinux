# SeLinux
Read/Write Memory, I/O, PCI and ISA I/O under Linux.

# Requisites
1. root permission
2. Python 3.6
3. tkinter

# Installaion
1. Compile Linux Kernel Module
```
cd SeLinux\Driver
make
```

2. Load module
```
sudo insmod SeLinux.ko
```

3. Compile application
```
cd SeLinux\Application
make
```

# Run SeLinux
```
cd SeLinux
sudo python3 SeLinux.py
```
# How to use
For Memory, I/O and ISA I/O, you have to enter 8 digits address after chose them, for example,
Memory address 0xF000, you need to enter 000F0000; I/O adress 0x00, you need to enter 00000000;
ISA I/O is the special one, it need two parts to read/write, "Index" and "data", the high 4 digits are Index,
the others are Data. If you want to read 70/71, please enter 00700071.

SeLinux use "lspci" to get all PCI device, so just select which device you want to read.

SeLinux update(rescen) register window per second, if you want to modify register(s),
please clcik on register window and press any key to disable time interval.

after modification, click Updtate button to write data, BTW, cancel button to cancel update 

# Verify Platform
ubuntu 16.04, AMD chipset

# Please Note
SeLinux don't support any error check, please check everything is fine before click Update button
