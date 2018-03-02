/*
 * File    SeLinuxDri.c
 * Author  Alex Wang
 * Date    2018/01/29
 * version 1.0.0
 * brief   Accessing system I/O and memory under Linux
*/

#include <linux/init.h>           // Macros used to mark up functions e.g. __init __exit
#include <linux/module.h>         // Core header for loading LKMs into the kernel
#include <linux/device.h>         // Header to support the kernel Driver Model
#include <linux/kernel.h>         // Contains types, macros, functions for the kernel
#include <linux/fs.h>             // Header for the Linux file system support
#include <linux/io.h>             // Header for the Linux file system support
#include <asm/uaccess.h>          // Required for the copy to user function
#include <linux/string.h>               // String to integer
#include <linux/uaccess.h>
#include "../Include/ioc.h"
#include "../Include/selinux.h"

#define  DEVICE_NAME "SeLinux"    // The device will appear at /dev/SeLinux using this value
#define  CLASS_NAME  "SeLinux"    // The device class -- this is a character device driver

// Global variable
static int    majorNumber;                     // Stores the device number -- determined automatically
static int    numberOpens = 0;                 // Counts the number of times the device is opened
static struct class*  DriverClass  = NULL;     // The device-driver class struct pointer
static struct device* DriverDevice = NULL;     // The device-driver device struct pointer
static unsigned long pfa;
static unsigned int AccessType;
static unsigned int AccessContent[256];

MODULE_LICENSE("GPL");                                // The license type -- this affects available functionality
MODULE_AUTHOR("Alex Wang");                           // The author -- visible when you use modinfo
MODULE_DESCRIPTION("System Explorer Linux version");  // The description -- see modinfo
MODULE_VERSION("1.0.0");                              // A version number to inform users

// The function prototype
static int     DevOpen(struct inode *, struct file *);
static int     DevRelease(struct inode *, struct file *);
static ssize_t DevRead(struct file *, char *, size_t, loff_t *);
static ssize_t DevWrite(struct file *, const char *, size_t, loff_t *);
static long    DevIoctl(struct file*, unsigned int, unsigned long);
int AccessPci(unsigned int flag, unsigned long args);
int AccessMem(unsigned int flag, unsigned long args);
int AccessIo(unsigned int flag, unsigned long args);
int AccessIndex(unsigned int flag, unsigned long args);


/* @brief Devices are represented as file structure in the kernel. The file_operations structure from
 * /linux/fs.h lists the callback functions that you wish to associated with your file operations
 * using a C99 syntax structure. char devices usually implement open, read, write and release calls
 */
static struct file_operations fops =
{
	.owner = THIS_MODULE,
    .open = DevOpen,
    .read = DevRead,
    .write = DevWrite,
    .unlocked_ioctl = DevIoctl,
    .release = DevRelease
};

/* brief The device open function that is called each time the device is opened
 * This will only increment the numberOpens counter in this case.
 * @param inodep A pointer to an inode object (defined in linux/fs.h)
 * @param filep A pointer to a file object (defined in linux/fs.h)
 */
static int DevOpen(struct inode *inodep, struct file *filep){
    numberOpens++;
    printk(KERN_INFO "SeLinux Device has been opened %d time(s)\n", numberOpens);
    return 0;
}

/* brief This function is called whenever device is being read from user space i.e. data is
 * being sent from the device to the user. In this case is uses the copy_to_user() function to
 * send the buffer string to the user and captures any errors.
 * @param filep A pointer to a file object (defined in linux/fs.h)
 * @param buffer The pointer to the buffer to which this function writes the data
 * @param len The length of the b
 * @param offset The offset if required
 */
static ssize_t DevRead(struct file *filep, char *buffer, size_t len, loff_t *offset){
    unsigned int index;

    for(index = 0; index < 256; index++) {
    	*(buffer + index + 9) = (unsigned char)AccessContent[index];
    }
    //printk(KERN_INFO "Read from ASL");
    return 0;
}

/* brief This function is called whenever the device is being written to from user space i.e.
 * data is sent to the device from the user. The data is copied to the message[] array in this
 * LKM using the sprintf() function along with the length of the string.
 * @param filep A pointer to a file object
 * @param buffer The buffer to that contains the string to write to the device
 * @param len The length of the array of data that is being passed in the const char buffer
 * @param offset The offset if required
 */
static ssize_t DevWrite(struct file *filep, const char *buffer, size_t len, loff_t *offset){
    unsigned char pfaChar[9] = {0};
    unsigned char AccessTypeChar[4] = {SE_PCI_TOKEN, SE_MEM_TOKEN, SE_IO_TOKEN, SE_INDEX_TOKEN};
    int index = 0;

    // Get Type from user
    AccessType = 0xFF;
    for (index = 0; index < sizeof(AccessTypeChar); index++) {
    	if((unsigned int)(*buffer) == (unsigned int)(AccessTypeChar[index])) break;
    }
    if(index >= sizeof(AccessTypeChar)) {
    	printk(KERN_INFO "SeLinux: AccessType is wrong\n");
    	return 0;
    }
    AccessType = (unsigned int)index;
    printk(KERN_INFO "SeLinux: AccessType is %d\n", AccessType);

    // Get Address from user
    for (index = 0; index < 8; index++) {
    	pfaChar[index] = *(buffer + 1 + index);
    }
    kstrtoul(pfaChar, 16, &pfa);
    printk(KERN_INFO "SeLinux: pfa is %lx\n", pfa);
    // Get content from user
    for (index = 0; index < 256; index++) {
    	AccessContent[index] = (unsigned int)(*(buffer + 9 + index) & 0xFF);
    }

    return 0;
}

long DevIoctl(struct file *filp, unsigned int cmd, unsigned long args)
{
	printk(KERN_INFO "SeLinux IOCTL: AccessType is %d\n", AccessType);

    switch (AccessType) {
        case SE_PCI_CODE:
            AccessPci(cmd, args); 
            break;
        case SE_MEM_CODE:
            AccessMem(cmd, args); 
            break;
        case SE_IO_CODE:
            AccessIo(cmd, args); 
            break;
        case SE_INDEX_CODE:
            AccessIndex(cmd, args); 
            break;
        //default: /* redundant. as cmd was checked against MAXNR */
        //    printk(KERN_INFO "SeLinux: ioctl default\n");
        //    return -ENOTTY;
     }    

     return 0;
}

/* brief The device release function that is called whenever the device is closed/released by
 * the userspace program
 * @param inodep A pointer to an inode object (defined in linux/fs.h)
 * @param filep A pointer to a file object (defined in linux/fs.h)
 */
static int DevRelease(struct inode *inodep, struct file *filep){
   printk(KERN_INFO "SeLinux Device successfully closed\n");
   return 0;
}

/* brief The LKM initialization function
 * The static keyword restricts the visibility of the function to within this C file. The __init
 * macro means that for a built-in driver (not a LKM) the function is only used at initialization
 * time and that it can be discarded and its memory freed up after that point.
 * return returns 0 if successful
 */
static int __init DriverInit(void){
   
    printk(KERN_INFO "Initializing the SeLinux Driver \n");

    // Try to dynamically allocate a major number for the device -- more difficult but worth it
    majorNumber = register_chrdev(0, DEVICE_NAME, &fops);
    if (majorNumber<0){
        printk(KERN_ALERT "SeLinux Driver failed to register a major number\n");
        return majorNumber;
    }
    printk(KERN_INFO "Registered correctly with major number %d\n", majorNumber);

    // Register the device class
    DriverClass = class_create(THIS_MODULE, CLASS_NAME);
    if (IS_ERR(DriverClass)){                // Check for error and clean up if there is
        unregister_chrdev(majorNumber, DEVICE_NAME);
        printk(KERN_ALERT "Failed to register device class\n");
        return PTR_ERR(DriverClass);          // Correct way to return an error on a pointer
    }
    printk(KERN_INFO "Device class registered correctly\n");

    // Register the device driver
    DriverDevice = device_create(DriverClass, NULL, MKDEV(majorNumber, 0), NULL, DEVICE_NAME);
    if (IS_ERR(DriverDevice)){               // Clean up if there is an error
        class_destroy(DriverClass);           // Repeated code but the alternative is goto statements
        unregister_chrdev(majorNumber, DEVICE_NAME);
        printk(KERN_ALERT "Failed to create the device\n");
        return PTR_ERR(DriverDevice);
    }
    printk(KERN_INFO "Device class created correctly\n"); // Made it! device was initialized


   
    return 0;
}

/* brief The LKM cleanup function
 * Similar to the initialization function, it is static. The __exit macro notifies that if this
 * code is used for a built-in driver (not a LKM) that this function is not required.
 */
static void __exit DriverExit(void){
    device_destroy(DriverClass, MKDEV(majorNumber, 0));     // remove the device
    class_unregister(DriverClass);                          // unregister the device class
    class_destroy(DriverClass);                             // remove the device class
    unregister_chrdev(majorNumber, DEVICE_NAME);             // unregister the major number
    printk(KERN_INFO "Goodbye from the LKM!\n");
}

/* brief Access Pci register
 * args save the offset and data to be writen
 * return returns 0 if successful
 */
int AccessPci(unsigned int flag, unsigned long args) {
    unsigned int data;
    unsigned int index;
    unsigned long address = pfa;

    printk(KERN_INFO "AccessPci!\n");

    if(flag == SETNUM) {
            copy_from_user(&data,(unsigned int __user *)args,2);
            pfa = pfa + ((data >> 8) & 0xFF);
            outl((pfa & ~0x03), 0xCF8);
            outb((data & 0xFF), (pfa & 0x03) + 0xCFC);
    }

    // Always read from H/W
    pfa = address;
    for(index = 0; index < 256; index += 4) {
        //AccessContent[index] = 255 - index;
        outl(pfa + index, 0xCF8);
        data = inl(0xCFC);
        AccessContent[index + 0] = (data >> (8*0)) & 0xFF;
        AccessContent[index + 1] = (data >> (8*1)) & 0xFF;
        AccessContent[index + 2] = (data >> (8*2)) & 0xFF;
        AccessContent[index + 3] = (data >> (8*3)) & 0xFF;
    }

	return 0;
}


/* brief Access Memory register
 * args save the offset and data to be writen
 * return returns 0 if successful
 */
int AccessMem(unsigned int flag, unsigned long args) {
    unsigned int data;
    unsigned int index;
    void *address = memremap(pfa, 256, MEMREMAP_WB);

    //data = ioread16(address);
    printk(KERN_INFO "AccessMem!\n");
    if(address == NULL)
    	printk(KERN_INFO "memremap fail!\n");
    if(flag == SETNUM) {
        data = 0;
        copy_from_user(&data,(unsigned int __user *)args,2);
        address = address + ((data >> 8) & 0xFF);            
        iowrite8((data & 0xFF), address);            
     }

    // Always read from I/O
    address = memremap(pfa, 256, MEMREMAP_WB);
    for(index = 0; index < 256; index++) {
        data = ioread8(address + index);
        AccessContent[index] = (data >> (8*0)) & 0xFF;
    }

	return 0;
}

/* brief Access I/O register
 * args save the offset and data to be writen
 * return returns 0 if successful
 */
int AccessIo(unsigned int flag, unsigned long args) {
    unsigned int data;
    unsigned int index;
    unsigned long address = pfa;

    printk(KERN_INFO "AccessIo!\n");
    if(flag == SETNUM) {
        data = 0;
        copy_from_user(&data,(unsigned int __user *)args,2);
        pfa = pfa + ((data >> 8) & 0xFF);            
        outb((data & 0xFF), pfa);            
     }

    // Always read from I/O
    pfa = address;
    for(index = 0; index < 256; index++) {
        data = inb(pfa + index);
        AccessContent[index] = (data >> (8*0)) & 0xFF;
    }

	return 0;
}

/* brief Access Index register
 * args save the offset and data to be writen
 * return returns 0 if successful
 */
int AccessIndex(unsigned int flag, unsigned long args) {
    unsigned int data;
    unsigned int index;
    unsigned int IndexPort;
    unsigned int DataPort;

    IndexPort = (pfa >> 16) & 0xFFFF;
    DataPort = (pfa >> 0) & 0xFFFF;
    printk(KERN_INFO "AccessIndex!\n");
    
    if(flag == SETNUM) {
        data = 0;
        copy_from_user(&data,(unsigned int __user *)args,2);
        pfa = (data >> 8) & 0xFF;            
        outb(pfa, IndexPort);
        outb((data & 0xFF), DataPort);
    }	

    // Always read from Index I/O
    for(index = 0; index < 256; index++) {
    	outb(index, IndexPort);
    	AccessContent[index] = inb(DataPort) & 0xFF;
    }
    
	return 0;
}

/* brief A module must use the module_init() module_exit() macros from linux/init.h, which
 * identify the initialization function at insertion time and the cleanup function (as
 * listed above)
 */
module_init(DriverInit);
module_exit(DriverExit);
