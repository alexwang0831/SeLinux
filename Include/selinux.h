#ifndef SELINUX_H
#define SELINUX_H

typedef struct _buffer {
    unsigned char AccessType;
    unsigned char AccessAddress[8];
    unsigned char AccessContent[256];
}Buffer;

union unionBuffer {
    Buffer communication;
    unsigned char AsciiPackage[266];
};

#define SE_PCI_TOKEN   'P'
#define SE_MEM_TOKEN   'M'
#define SE_IO_TOKEN    'I'
#define SE_INDEX_TOKEN 'N'

#define SE_PCI_CODE   0
#define SE_MEM_CODE   1
#define SE_IO_CODE    2
#define SE_INDEX_CODE 3

#endif
