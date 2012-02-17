#include <Python.h>
#include "common.h"
#include "status.h"
#include "objects.h"

PyObject *
parse_status(PyObject *self, PyObject *args)
{
    PyObject *result = NULL;
    PyListObject *hosts = NULL;
    PyListObject *services = NULL;
    char *filename = NULL;

    if (!PyArg_ParseTuple(args, "s", &filename)) {
        return 0;
    }

    hosts = (PyListObject *) PyList_New(0);
    if (hosts == NULL)
        return 0;
    services = (PyListObject *) PyList_New(0);
    if (services == NULL)
        return 0;

    if (read_status_data(filename, hosts, services) == ERROR)
        return NULL;

    result = PyTuple_New(2);
    PyTuple_SetItem(result, 0, (PyObject *) hosts);
    PyTuple_SetItem(result, 1, (PyObject *) services);
    return result;
}

static PyMethodDef module_methods[] = {
    {"parse_status", parse_status, METH_VARARGS, "Parse the status.dat file"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_parser(void) {
    PyObject *m;

    //HostType.tp_new = PyType_GenericNew;
    //if (PyType_Ready(&HostType) < 0)
    //    return;

    m = Py_InitModule3("_parser", module_methods,
        "Nagios status file parser");

    if (m == NULL)
        return;

    //Py_INCREF(&HostType);
    //PyModule_AddObject(m, "Host", (PyObject *) &HostType);
}

