#ifndef _MMAPFILE_H_
#define _MMAPFILE_H_

#include <time.h>

typedef struct mmapfile_struct {
    char *          path;
    int             mode;
    int             fd;
    unsigned long   filesize;
    unsigned long   current_char;
    unsigned long   current_line;
    void *          mmap_buf;
} mmapfile;

extern mmapfile *   mmapfile_open(char *);
extern int          mmapfile_close(mmapfile *);
extern char *       mmapfile_readline(mmapfile *);
extern void         strip(char *);

#endif // _MMAPFILE_H_
