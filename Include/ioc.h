#ifndef IOC_H
#define IOC_H

#define IOC_MAGIC 'k'
#define SETNUM _IOW(IOC_MAGIC, 1 , int)
#define GETNUM _IOR(IOC_MAGIC, 2 , int)
#define XNUM _IOWR(IOC_MAGIC,3 , int)
#define IOC_MAXNR 3

#endif
