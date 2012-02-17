#include "status.h"
#include "objects.h"

#define PyBool(v) (v > 0) ? Py_True : Py_False

static long string_hash(PyStringObject *a)
{
    register Py_ssize_t len;
    register unsigned char *p;
    register long x;

    if (a->ob_shash != -1)
        return a->ob_shash;
    len = Py_SIZE(a);
    p = (unsigned char *) a->ob_sval;
    x = *p << 7;
    while (--len >= 0)
        x = (1000003*x) ^ *p++;
    x ^= Py_SIZE(a);
    if (x == -1)
        x = -2;
    a->ob_shash = x;
    return x;
}

PyObject *
Host_NEW()
{
    HostObject *object = PyObject_NEW(HostObject, &HostType);
    if (object != NULL) {
        object->host_name = NULL;
        object->plugin_output = NULL;
        object->long_plugin_output = NULL;
    }

    return (PyObject *)object;
}

void
Host_dealloc(self)
    PyObject *self;
{
    PyMem_DEL(self);
}

int
Host_print(self, fp, flags)
    PyObject *self;
    FILE *fp;
    int flags;
{
    HostObject *object = (HostObject *)self;
    fprintf(fp, "%s", object->host_name);
    return 0;
}

int
Host_compare(self, them)
    PyObject *self;
    PyObject *them;
{
    HostObject *a = (HostObject *)self;
    HostObject *b = (HostObject *)them;
    return strcmp(a->host_name, b->host_name);
}

long
Host_hash(self)
    PyObject *self;
{
    HostObject *object = (HostObject *)self;
    return string_hash((PyStringObject *)
        PyString_FromString(object->host_name));
}

PyObject *
Host_repr(self)
    PyObject *self;
{
    HostObject *object = (HostObject *)self;
    char buf[128];
    sprintf(buf, "<Host %s>", object->host_name);
    return PyString_FromString(buf);
}

PyObject *
Service_NEW()
{
    ServiceObject *object = PyObject_NEW(ServiceObject, &ServiceType);
    if (object != NULL) {
        object->host_name = NULL;
        object->plugin_output = NULL;
        object->long_plugin_output = NULL;
    }

    return (PyObject *)object;
}

void
Service_dealloc(self)
    PyObject *self;
{
    PyMem_DEL(self);
}

int
Service_print(self, fp, flags)
    PyObject *self;
    FILE *fp;
    int flags;
{
    ServiceObject *object = (ServiceObject *)self;
    fprintf(fp, "%s", object->host_name);
    return 0;
}

int
Service_compare(self, them)
    PyObject *self;
    PyObject *them;
{
    ServiceObject *a = (ServiceObject *)self;
    ServiceObject *b = (ServiceObject *)them;
    return strcmp(a->host_name, b->host_name);
}

long
Service_hash(self)
    PyObject *self;
{
    ServiceObject *object = (ServiceObject *)self;
    return string_hash((PyStringObject *)
        PyString_FromString(object->host_name));
}

PyObject *
Service_repr(self)
    PyObject *self;
{
    ServiceObject *object = (ServiceObject *)self;
    char buf[128];
    sprintf(buf, "<Service %s>", object->host_name);
    return PyString_FromString(buf);
}
