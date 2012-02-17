#ifndef __STATUS_H__
#define __STATUS_H__

#include <sys/time.h>
#include <Python.h>

// Max length of plugin output (including perf data)
#define MAX_PLUGIN_OUTPUT_LENGTH                8192

#define XSDDEFAULT_NO_DATA               0
#define XSDDEFAULT_INFO_DATA             1
#define XSDDEFAULT_PROGRAMSTATUS_DATA    2
#define XSDDEFAULT_HOSTSTATUS_DATA       3
#define XSDDEFAULT_SERVICESTATUS_DATA    4
#define XSDDEFAULT_CONTACTSTATUS_DATA    5
#define XSDDEFAULT_HOSTCOMMENT_DATA      6
#define XSDDEFAULT_SERVICECOMMENT_DATA   7
#define XSDDEFAULT_HOSTDOWNTIME_DATA     8
#define XSDDEFAULT_SERVICEDOWNTIME_DATA  9

/* HOST STATUS structure */
typedef struct hoststatus_struct {
    char *  host_name;
    char *  plugin_output;
    char *  long_plugin_output;
    char *  perf_data;
    int     status;
    time_t  last_update;
    int     has_been_checked;
    int     should_be_scheduled;
    int     current_attempt;
    int     max_attempts;
    time_t  last_check;
    time_t  next_check;
    int     check_options;
    int     check_type;
    char *  check_period;
    char *  check_command;
    time_t  last_state_change;
    time_t  last_hard_state_change;
    int     last_hard_state;
    time_t  last_time_up;
    time_t  last_time_down;
    time_t  last_time_unreachable;
    int     state_type;
    time_t  last_notification;
    time_t  next_notification;
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
} hoststatus;

/* SERVICE STATUS structure */
typedef struct servicestatus_struct {
    char *  host_name;
    char *  description;
    char *  plugin_output;
    char *  long_plugin_output;
    char *  perf_data;
    int     max_attempts;
    int     current_attempt;
    int     status;
    time_t  last_update;
    int     has_been_checked;
    int     should_be_scheduled;
    time_t  last_check;
    time_t  next_check;
    int     check_options;
    int     check_type;
    int     checks_enabled;
    time_t  last_state_change;
    time_t  last_hard_state_change;
    int     last_hard_state;
    time_t  last_time_ok;
    time_t  last_time_warning;
    time_t  last_time_unknown;
    time_t  last_time_critical;
    int     state_type;
    time_t  last_notification;
    time_t  next_notification;
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
} servicestatus;

int read_status_data(char *, PyListObject *, PyListObject *, char *);

#endif // __STATUS_H__
