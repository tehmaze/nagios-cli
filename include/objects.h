#ifndef __OBJECTS_H__
#define __OBJECTS_H__

#include <sys/file.h>
#include <Python.h>

#ifndef Py_STRUCTMEMBER_H
#include <structmember.h>
#endif

#define HOST_OFF(x) offsetof(HostObject, x)
#define SERV_OFF(x) offsetof(ServiceObject, x)

typedef struct {
    PyObject_HEAD
    char *  host_name;
    char *  plugin_output;
    char *  long_plugin_output;
    char *  perf_data;
    int     status;
    long    last_update;
    int     has_been_checked;
    int     should_be_scheduled;
    int     current_attempt;
    int     max_attempts;
    long    last_check;
    long    next_check;
    int     check_options;
    int     check_type;
    char *  check_period;
    char *  check_command;
    int     check_interval;
    int     retry_interval;
    char *  notification_period;
    long    last_state_change;
    long    last_hard_state_change;
    int     last_hard_state;
    long    last_time_up;
    long    last_time_down;
    long    last_time_unreachable;
    int     state_type;
    long    last_notification;
    long    next_notification;
    int     no_more_notifications;
    int     notifications_enabled;
    int     problem_has_been_acknowledged;
    int     acknowledgement_type;
    int     current_notification_number;
    int     accept_passive_host_checks;
    int     event_handler_enabled;
    int     checks_enabled;
    int     flap_detection_enabled;
    int     is_flapping;
    double  percent_state_change;
    double  latency;
    double  execution_time;
    int     scheduled_downtime_depth;
    int     failure_prediction_enabled;
    int     process_performance_data;
    int     obsess_over_host;
} HostObject;

PyObject *  Host_NEW(void);
void        Host_dealloc(PyObject *);
int         Host_print(PyObject *, FILE *, int);
PyObject *  Host_getattr(PyObject *, char *);
int         Host_setattr(PyObject *, char *, PyObject *);
int         Host_compare(PyObject *, PyObject *);
long        Host_hash(PyObject *);
PyObject *  Host_repr(PyObject *);

static PyMemberDef Host_members[] = {
    {"host_name", T_STRING,
        HOST_OFF(host_name), READONLY},
    {"plugin_output", T_STRING,
        HOST_OFF(plugin_output), READONLY},
    {"long_plugin_output", T_STRING,
        HOST_OFF(long_plugin_output), READONLY},
    {"perf_data", T_STRING,
        HOST_OFF(perf_data), READONLY},
    {"status", T_INT,
        HOST_OFF(status), READONLY},
    {"last_update", T_LONG,
        HOST_OFF(last_update), READONLY},
    {"has_been_checked", T_BOOL,
        HOST_OFF(has_been_checked), READONLY},
    {"should_be_scheduled", T_BOOL,
        HOST_OFF(should_be_scheduled), READONLY},
    {"current_attempt", T_INT,
        HOST_OFF(current_attempt), READONLY},
    {"max_attempts", T_INT,
        HOST_OFF(max_attempts), READONLY},
    {"last_check", T_LONG,
        HOST_OFF(last_check), READONLY},
    {"next_check", T_LONG,
        HOST_OFF(next_check), READONLY},
    {"check_options", T_INT,
        HOST_OFF(check_options), READONLY},
    {"check_type", T_INT,
        HOST_OFF(check_type), READONLY},
    {"check_period", T_STRING,
        HOST_OFF(check_period), READONLY},
    {"check_command", T_STRING,
        HOST_OFF(check_command), READONLY},
    {"last_state_change", T_LONG,
        HOST_OFF(last_state_change), READONLY},
    {"last_hard_state_change", T_STRING,
        HOST_OFF(last_hard_state_change), READONLY},
    {"last_hard_state", T_INT,
        HOST_OFF(last_hard_state), READONLY},
    {"last_time_up", T_LONG,
        HOST_OFF(last_time_up), READONLY},
    {"last_time_down", T_LONG,
        HOST_OFF(last_time_down), READONLY},
    {"last_time_unreachable", T_LONG,
        HOST_OFF(last_time_unreachable), READONLY},
    {"state_type", T_INT,
        HOST_OFF(state_type), READONLY},
    {"last_notification", T_LONG,
        HOST_OFF(last_notification), READONLY},
    {"next_notification", T_LONG,
        HOST_OFF(next_notification), READONLY},
    {"no_more_notifications", T_BOOL,
        HOST_OFF(no_more_notifications), READONLY},
    {"notifications_enabled", T_BOOL,
        HOST_OFF(notifications_enabled), READONLY},
    {"problem_has_been_acknowledged", T_BOOL,
        HOST_OFF(problem_has_been_acknowledged), READONLY},
    {"acknowledgement_type", T_INT,
        HOST_OFF(acknowledgement_type), READONLY},
    {"current_notification_number", T_INT,
        HOST_OFF(current_notification_number), READONLY},
    {"accept_passive_host_checks", T_BOOL,
        HOST_OFF(accept_passive_host_checks), READONLY},
    {"event_handler_enabled", T_BOOL,
        HOST_OFF(event_handler_enabled), READONLY},
    {"checks_enabled", T_BOOL,
        HOST_OFF(checks_enabled), READONLY},
    {"flap_detection_enabled", T_BOOL,
        HOST_OFF(flap_detection_enabled), READONLY},
    {"is_flapping", T_BOOL,
        HOST_OFF(is_flapping), READONLY},
    {"percent_state_change", T_DOUBLE,
        HOST_OFF(percent_state_change), READONLY},
    {"latency", T_DOUBLE,
        HOST_OFF(latency), READONLY},
    {"execution_time", T_DOUBLE,
        HOST_OFF(execution_time), READONLY},
    {"scheduled_downtime_depth", T_INT,
        HOST_OFF(scheduled_downtime_depth), READONLY},
    {"failure_prediction_enabled", T_BOOL,
        HOST_OFF(failure_prediction_enabled), READONLY},
    {"process_performance_data", T_BOOL,
        HOST_OFF(process_performance_data), READONLY},
    {"obsess_over_host", T_BOOL,
        HOST_OFF(obsess_over_host), READONLY},
    {NULL} /* Sentinel */
};

PyDoc_STRVAR(Host_doc,
"Host() -> host object\n\
\n\
Creates a new host object that represents a hoststatus line in the nagios\n\
status.dat file.");

static PyTypeObject HostType = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,
    "Host",
    sizeof(HostObject),
    0,
    (destructor)Host_dealloc,           /* tp_dealloc           */
    Host_print,                         /* tp_print             */
    0,                                  /* tp_getattr           */
    0,                                  /* tp_setattr           */
    Host_compare,                       /* tp_compare           */
    Host_repr,                          /* tp_repr              */
    0,                                  /* *tp_as_number        */
    0,                                  /* *tp_as_sequence      */
    0,                                  /* *tp_as_mapping       */
    Host_hash,                          /* tp_hash              */
    0,                                  /* tp_call              */
    (reprfunc)Host_repr,                /* tp_str               */
    PyObject_GenericGetAttr,            /* tp_getattro          */
    PyObject_GenericSetAttr,            /* tp_setattro          */
    0,                                  /* tp_as_buffer         */
    Py_TPFLAGS_DEFAULT,                 /* tp_flags             */
    Host_doc,                           /* tp_doc               */
    0,                                  /* tp_traverse          */
    0,                                  /* tp_clear             */
    0,                                  /* tp_richcompare       */
    0,                                  /* tp_weaklistoffset    */
    0,                                  /* tp_iter              */
    0,                                  /* tp_iternext          */
    0,                                  /* tp_methods           */
    Host_members,                       /* tp_members           */
    0,                                  /* tp_getset            */
    0,                                  /* tp_base              */
    0,                                  /* tp_dict              */
    0,                                  /* tp_descr_get         */
    0,                                  /* tp_descr_set         */
    0,                                  /* tp_dictoffset        */
    0,                                  /* tp_init              */
    PyType_GenericAlloc,                /* tp_alloc             */
    PyType_GenericNew,                  /* tp_new               */
    _PyObject_Del,                      /* tp_free              */
};

typedef struct {
    PyObject_HEAD
    char *  host_name;
    char *  description;
    char *  plugin_output;
    char *  long_plugin_output;
    char *  perf_data;
    int     max_attempts;
    int     current_attempt;
    int     status;
    long    last_update;
    int     has_been_checked;
    int     should_be_scheduled;
    long    last_check;
    long    next_check;
    int     check_options;
    int     check_type;
    int     checks_enabled;
    long    last_state_change;
    long    last_hard_state_change;
    int     last_hard_state;
    long    last_time_ok;
    long    last_time_warning;
    long    last_time_unknown;
    long    last_time_critical;
    int     state_type;
    long    last_notification;
    long    next_notification;
    int     no_more_notifications;
    int     notifications_enabled;
    int     problem_has_been_acknowledged;
    int     acknowledgement_type;
    int     current_notification_number;
    int     accept_passive_service_checks;
    int     event_handler_enabled;
    int     flap_detection_enabled;
    int     is_flapping;
    double  percent_state_change;
    double  latency;
    double  execution_time;
    int     scheduled_downtime_depth;
    int     failure_prediction_enabled;
    int     process_performance_data;
    int     obsess_over_service;
} ServiceObject;

PyObject *  Service_NEW(void);
void        Service_dealloc(PyObject *);
int         Service_print(PyObject *, FILE *, int);
PyObject *  Service_getattr(PyObject *, char *);
int         Service_setattr(PyObject *, char *, PyObject *);
int         Service_compare(PyObject *, PyObject *);
long        Service_hash(PyObject *);
PyObject *  Service_repr(PyObject *);

static PyMemberDef Service_members[] = {
    {"host_name", T_STRING,
        SERV_OFF(host_name), READONLY},
    {"description", T_STRING,
        SERV_OFF(description), READONLY},
    {"plugin_output", T_STRING,
        SERV_OFF(plugin_output), READONLY},
    {"long_plugin_output", T_STRING,
        SERV_OFF(long_plugin_output), READONLY},
    {"perf_data", T_STRING,
        SERV_OFF(perf_data), READONLY},
    {"max_attempts", T_INT,
        SERV_OFF(max_attempts), READONLY},
    {"current_attempt", T_INT,
        SERV_OFF(current_attempt), READONLY},
    {"status", T_INT,
        SERV_OFF(status), READONLY},
    {"last_update", T_LONG,
        SERV_OFF(last_update), READONLY},
    {"has_been_checked", T_BOOL,
        SERV_OFF(has_been_checked), READONLY},
    {"should_be_scheduled", T_BOOL,
        SERV_OFF(should_be_scheduled), READONLY},
    {"last_check", T_LONG,
        SERV_OFF(last_check), READONLY},
    {"next_check", T_LONG,
        SERV_OFF(next_check), READONLY},
    {"check_options", T_INT,
        SERV_OFF(check_options), READONLY},
    {"check_type", T_INT,
        SERV_OFF(check_type), READONLY},
    {"checks_enabled", T_BOOL,
        SERV_OFF(checks_enabled), READONLY},
    {"last_state_change", T_LONG,
        SERV_OFF(last_state_change), READONLY},
    {"last_hard_state_change", T_LONG,
        SERV_OFF(last_hard_state_change), READONLY},
    {"last_hard_state", T_INT,
        SERV_OFF(last_hard_state), READONLY},
    {"last_time_ok", T_LONG,
        SERV_OFF(last_time_ok), READONLY},
    {"last_time_warning", T_LONG,
        SERV_OFF(last_time_warning), READONLY},
    {"last_time_unknown", T_LONG,
        SERV_OFF(last_time_unknown), READONLY},
    {"last_time_critical", T_LONG,
        SERV_OFF(last_time_critical), READONLY},
    {"state_type", T_INT,
        SERV_OFF(state_type), READONLY},
    {"last_notification", T_LONG,
        SERV_OFF(last_notification), READONLY},
    {"next_notification", T_LONG,
        SERV_OFF(next_notification), READONLY},
    {"no_more_notifications", T_BOOL,
        SERV_OFF(no_more_notifications), READONLY},
    {"notifications_enabled", T_BOOL,
        SERV_OFF(notifications_enabled), READONLY},
    {"problem_has_been_acknowledged", T_BOOL,
        SERV_OFF(problem_has_been_acknowledged), READONLY},
    {"acknowledgement_type", T_INT,
        SERV_OFF(acknowledgement_type), READONLY},
    {"current_notification_number", T_INT,
        SERV_OFF(current_notification_number), READONLY},
    {"accept_passive_service_checks", T_BOOL,
        SERV_OFF(accept_passive_service_checks), READONLY},
    {"event_handler_enabled", T_BOOL,
        SERV_OFF(event_handler_enabled), READONLY},
    {"flap_detection_enabled", T_BOOL,
        SERV_OFF(flap_detection_enabled), READONLY},
    {"is_flapping", T_BOOL,
        SERV_OFF(is_flapping), READONLY},
    {"percent_state_change", T_DOUBLE,
        SERV_OFF(percent_state_change), READONLY},
    {"latency", T_DOUBLE,
        SERV_OFF(latency), READONLY},
    {"execution_time", T_DOUBLE,
        SERV_OFF(execution_time), READONLY},
    {"scheduled_downtime_depth", T_INT,
        SERV_OFF(scheduled_downtime_depth), READONLY},
    {"failure_prediction_enabled", T_BOOL,
        SERV_OFF(failure_prediction_enabled), READONLY},
    {"process_performance_data", T_BOOL,
        SERV_OFF(process_performance_data), READONLY},
    {"obsess_over_service", T_BOOL,
        SERV_OFF(obsess_over_service), READONLY},
    {NULL} /* Sentinel */
};

PyDoc_STRVAR(Service_doc,
"Service() -> service object\n\
\n\
Creates a new service object that represents a servicestatus line in the\n\
nagios status.dat file.");

static PyTypeObject ServiceType = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,
    "Host",
    sizeof(HostObject),
    0,
    (destructor)Service_dealloc,        /* tp_dealloc           */
    Service_print,                      /* tp_print             */
    0,                                  /* tp_getattr           */
    0,                                  /* tp_setattr           */
    Service_compare,                    /* tp_compare           */
    Service_repr,                       /* tp_repr              */
    0,                                  /* *tp_as_number        */
    0,                                  /* *tp_as_sequence      */
    0,                                  /* *tp_as_mapping       */
    Service_hash,                       /* tp_hash              */
    0,                                  /* tp_call              */
    (reprfunc)Service_repr,             /* tp_str               */
    PyObject_GenericGetAttr,            /* tp_getattro          */
    PyObject_GenericSetAttr,            /* tp_setattro          */
    0,                                  /* tp_as_buffer         */
    Py_TPFLAGS_DEFAULT,                 /* tp_flags             */
    Service_doc,                        /* tp_doc               */
    0,                                  /* tp_traverse          */
    0,                                  /* tp_clear             */
    0,                                  /* tp_richcompare       */
    0,                                  /* tp_weaklistoffset    */
    0,                                  /* tp_iter              */
    0,                                  /* tp_iternext          */
    0,                                  /* tp_methods           */
    Service_members,                    /* tp_members           */
    0,                                  /* tp_getset            */
    0,                                  /* tp_base              */
    0,                                  /* tp_dict              */
    0,                                  /* tp_descr_get         */
    0,                                  /* tp_descr_set         */
    0,                                  /* tp_dictoffset        */
    0,                                  /* tp_init              */
    PyType_GenericAlloc,                /* tp_alloc             */
    PyType_GenericNew,                  /* tp_new               */
    _PyObject_Del,                      /* tp_free              */
};

#endif // __OBJECTS_H__
