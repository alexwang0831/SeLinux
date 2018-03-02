/*
 * File    SeLinux.c
 * Author  Alex Wang
 * Date    2018/01/29
 * version 1.0.0
 * brief   Accessing system I/O and memory under Linux,
 *         ioctl can't pass so many parameter, like address, content etc,
 *         SeLinux use write to send access type, address and content,
           use read to get the content from register, and
           use ioctl to sent I/O or Memory command
*/


#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include "../Include/ioc.h"
#include "../Include/selinux.h"

int main(int argc, char *argv[])
{
    int fd;
    int index;
    unsigned int offset = 0;
    unsigned int data = 0;
    unsigned int rwFlag;
    unsigned long ret=0x00BB;
    union unionBuffer buffer;

    char *argv_1[] = {"-pci", "-memory", "-io", "-index"};

    //
    // Prepare all data to sent to drvier
    //

    // Avoid magic number
    for(index = 0; index < sizeof(buffer); index++) {
        buffer.AsciiPackage[index] = '\0';
    }

    // check number of argument
    if((argc != 3) && (argc != 5))
        return -1;

    // check function argument
    for(index = 0; index < 4; index++) {
        if(!strcmp(argv[1],argv_1[index]))
            break;
    }

    if(index >= 4)
        return -1;

    switch(index) {
        case 0: // PCI
            buffer.communication.AccessType = 'P';
            buffer.communication.AccessAddress[0] = '8';
            buffer.communication.AccessAddress[1] = '0';
            buffer.communication.AccessAddress[2] = '0';
            buffer.communication.AccessAddress[3] = '0';
            buffer.communication.AccessAddress[4] = '0';
            buffer.communication.AccessAddress[5] = '0';
            buffer.communication.AccessAddress[6] = '0';
            buffer.communication.AccessAddress[7] = '0';
            break;
        case 1: // Memory
            buffer.communication.AccessType = 'M';
            buffer.communication.AccessAddress[0] = '0';
            buffer.communication.AccessAddress[1] = '0';
            buffer.communication.AccessAddress[2] = '0';
            buffer.communication.AccessAddress[3] = '9';
            buffer.communication.AccessAddress[4] = 'F';
            buffer.communication.AccessAddress[5] = '8';
            buffer.communication.AccessAddress[6] = '0';
            buffer.communication.AccessAddress[7] = '0';

            break;
        case 2: // General I/O
            buffer.communication.AccessType = 'I';
            buffer.communication.AccessAddress[0] = '0';
            buffer.communication.AccessAddress[1] = '0';
            buffer.communication.AccessAddress[2] = '0';
            buffer.communication.AccessAddress[3] = '0';
            buffer.communication.AccessAddress[4] = '0';
            buffer.communication.AccessAddress[5] = '0';
            buffer.communication.AccessAddress[6] = '0';
            buffer.communication.AccessAddress[7] = '0';

            break;
        case 3: // Index I/O
            buffer.communication.AccessType = 'N';
            buffer.communication.AccessAddress[0] = '0';
            buffer.communication.AccessAddress[1] = '0';
            buffer.communication.AccessAddress[2] = '7';
            buffer.communication.AccessAddress[3] = '2';
            buffer.communication.AccessAddress[4] = '0';
            buffer.communication.AccessAddress[5] = '0';
            buffer.communication.AccessAddress[6] = '7';
            buffer.communication.AccessAddress[7] = '3';

            break;
    }

    // copy address char by char
    if(strlen(argv[2]) != 8)
        return -1;
    for(index = 0; index < 8; index++) {
        buffer.communication.AccessAddress[index] = argv[2][index];
    }

    // check offset and data to be write and rw flag
    rwFlag = GETNUM;
    if(argc == 5) {
        offset = strtol(argv[3], NULL, 16);
        data = strtol(argv[4], NULL, 16);
        if((offset > 0xFF) || (data > 0xFF))
            return -1;

        ret = (offset << 8) | data;
        rwFlag = SETNUM;
    }

    //
    // communicate with driver
    //

    // open dev file
    fd=open("/dev/SeLinux", O_RDWR);
    if(fd < 0) {
        printf("open %s failed\n", argv[1]);
        return -1;
    }


    // write to kernel
    write(fd, buffer.AsciiPackage, sizeof(buffer));

    // ioctl(fd, GETNUM, &ret);

    ioctl(fd, rwFlag, &ret);

    // read from kernel
    read(fd, buffer.AsciiPackage, sizeof(buffer));
    for(index = 0; index < 256; index++) {
        //if(index % 0x10 == 0)
        //    printf("\n");
        printf("%02x ", (unsigned int)(buffer.communication.AccessContent[index]));
    }

    //printf("\n");
    return 0;
}
