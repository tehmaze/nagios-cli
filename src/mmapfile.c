#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <Python.h>
#include "common.h"
#include "mmapfile.h"

mmapfile *mmapfile_open(char *filename) {
    mmapfile *new_mmapfile = NULL;
    int fd = 0;
    void *mmap_buf = NULL;
    struct stat statbuf;
    int mode = O_RDONLY;
    unsigned long filesize = 0L;

    if (filename == NULL)
        return NULL;

    // Allocate memory
    if ((new_mmapfile = (mmapfile *) malloc(sizeof(mmapfile))) == NULL) {
        PyErr_SetString(PyExc_RuntimeError, strerror(errno));
        return NULL;
    }

    // Open file
    if ((fd = open(filename, mode)) == -1) {
        PyErr_SetString(PyExc_IOError, strerror(errno));
        my_free(new_mmapfile);
        return NULL;
    }

    // File info
    if ((fstat(fd, &statbuf)) == -1) {
        PyErr_SetString(PyExc_IOError, strerror(errno));
        close(fd);
        my_free(new_mmapfile);
        return NULL;
    }

    // File size
    filesize = (unsigned long) statbuf.st_size;

    if (filesize > 0) {
        // mmap() the file
        if ((mmap_buf = (void *) mmap(0, filesize,
            PROT_READ, MAP_PRIVATE, fd, 0)) == MAP_FAILED) {
            PyErr_SetString(PyExc_IOError, strerror(errno));
            close(fd);
            my_free(new_mmapfile);
            return NULL;
        }
    } else {
        mmap_buf = NULL;
    }

    // Export info
    new_mmapfile->path = (char *) strdup(filename);
    new_mmapfile->fd = fd;
    new_mmapfile->filesize = filesize;
    new_mmapfile->current_char = 0L;
    new_mmapfile->current_line = 0L;
    new_mmapfile->mmap_buf = mmap_buf;

    return new_mmapfile;
}

int mmapfile_close(mmapfile *old_mmapfile) {
    if (old_mmapfile == NULL)
        return ERROR;

    if (old_mmapfile->filesize > 0L)
        munmap(old_mmapfile->mmap_buf, old_mmapfile->filesize);

    close(old_mmapfile->fd);

    my_free(old_mmapfile->path);
    my_free(old_mmapfile);

    return OK;
}

char *mmapfile_readline(mmapfile *cur_mmapfile) {
    char *buf = NULL;
    unsigned long x = 0L;
    int len = 0;

    if (cur_mmapfile == NULL)
        return NULL;

    // Empty file
    if (cur_mmapfile->filesize == 0L)
        return NULL;

    // EOF
    if (cur_mmapfile->current_char >= cur_mmapfile->filesize)
        return NULL;

    // Find the end of the string (of buffer)
    for (x = cur_mmapfile->current_char; x < cur_mmapfile->filesize; ++x) {
        if (*((char *)(cur_mmapfile->mmap_buf) + x) == '\n') {
            ++x;
            break;
        }
    }

    len = (int)(x - cur_mmapfile->current_char);

    // Allocate memory for line
    if ((buf = (char *)malloc(len + 1)) == NULL)
        return NULL;

    // Copy string
    memcpy(buf, ((char *)(cur_mmapfile->mmap_buf) + cur_mmapfile->current_char), len);
    buf[len] = 0;

    // Update position
    cur_mmapfile->current_char = x;
    cur_mmapfile->current_line++;

    return buf;
}

void strip(char *buffer) {
    register int x, z;
    int len;

    if(buffer == NULL || buffer[0] == '\x0')
        return;

    /* strip end of string */
    len = (int)strlen(buffer);
    for(x = len - 1; x >= 0; x--) {
        switch(buffer[x]) {
            case ' ':
            case '\n':
            case '\r':
            case '\t':
                buffer[x] = '\x0';
                continue;
        }
        break;
    }

    /* if we stripped all of it, just return */
    if(!x)
        return;

    /* save last position for later... */
    z = x;

    /* strip beginning of string (by shifting) */
    /* NOTE: this is very expensive to do, so avoid it whenever possible */
    for(x = 0;; x++) {
        switch(buffer[x]) {
            case ' ':
            case '\n':
            case '\r':
            case '\t':
                continue;
        }
        break;
    }

    if(x > 0 && z > 0) {
        /* new length of the string after we stripped the end */
        len = z + 1;

        /* shift chars towards beginning of string to remove leading whitespace */
        for(z = x; z < len; z++)
            buffer[z - x] = buffer[z];
        buffer[len - x] = '\x0';
    }
}
