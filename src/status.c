#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include "common.h"
#include "status.h"
#include "mmapfile.h"

#include <Python.h>
#include "objects.h"

// Macros used by the parser
#define TO_STR(val)  (char *) strdup(val)
#define TO_INT(val)  atoi(val)
#define TO_BOOL(val) (atoi(val) > 0) ? TRUE : FALSE
#define TO_DOUBLE(val) strtod(val, NULL)
#define TO_LONG(val) strtoul(val, NULL, 10)

char *unescape_newlines(char *buffer) {
    register int x, y;

    for (x = 0, y = 0; buffer[x] != (char) 0; ++x) {
        if (buffer[x] == '\\') {
            // Unescape newlines
            if (buffer[x + 1] == 'n') {
                buffer[y++] = '\n';
                x++;
            }

            if (buffer[x + 1] == 0) {
                buffer[y++] = buffer[x + 1];
                x++;
            }
        } else {
            buffer[y++] = buffer[x];
        }
    }
    buffer[y] = 0;
    return buffer;
}

int read_status_data(char *filename, PyListObject *hosts, PyListObject *services) {
    int result = OK;

#ifdef NO_MMAP
    char input[MAX_PLUGIN_OUTPUT_LENGTH] = "";
    FILE *fp = NULL;
#else
    char *input = NULL;
    mmapfile *statusfile = NULL;
#endif
    int data_type = XSDDEFAULT_NO_DATA;
    char *var = NULL;
    char *val = NULL;
    HostObject *temp_host = NULL;
    servicestatus *temp_service = NULL;

    if (hosts == NULL)
        return ERROR;
    if (services == NULL)
        return ERROR;

#ifdef NO_MMAP
    if ((fp = fopen(filename, "r")) == NULL)
        return ERROR;
#else
    if ((statusfile = mmapfile_open(filename)) == NULL) {
        return ERROR;
    }
#endif

    // Read status file
    while (1) {

#ifdef NO_MMAP
        strcpy(input, "");
        if (fgets(input, sizeof(input), fp) == NULL)
            break;
#else
        // Free memory
        my_free(input);
        // Read next line
        if ((input = mmapfile_readline(statusfile)) == NULL)
            break;
#endif

        strip(input);

        // Blank lines and comments
        if (input[0] == '#' || input[0] == 0)
            continue;

        else if (
            !strcmp(input, "info {")            ||
            !strcmp(input, "programstatus {")   ||
            !strcmp(input, "contactstatus {")   ||
            !strcmp(input, "hostcomment {")     ||
            !strcmp(input, "servicecomment {")  ||
            !strcmp(input, "hostdowntime {")    ||
            !strcmp(input, "servicedowntime {")) {
                // Ignored
                data_type = XSDDEFAULT_NO_DATA;
                continue;
            }

        else if (!strcmp(input, "hoststatus {")) {
                // Host status object
                data_type = XSDDEFAULT_HOSTSTATUS_DATA;
                temp_host = (HostObject *)Host_NEW();
            }

        else if (!strcmp(input, "servicestatus {")) {
                // Service status object
                data_type = XSDDEFAULT_SERVICESTATUS_DATA;
                temp_service = (servicestatus *) malloc(sizeof(servicestatus));
                if (temp_service) {
                    temp_service->host_name = NULL;
                    temp_service->description = NULL;
                    temp_service->plugin_output = NULL;
                    temp_service->long_plugin_output = NULL;
                    temp_service->perf_data = NULL;
                    temp_service->check_options = 0;
                }
            }

        else if (!strcmp(input, "}")) {
                // End of block
                switch (data_type) {
                    case XSDDEFAULT_NO_DATA:
                        continue;

                    case XSDDEFAULT_HOSTSTATUS_DATA:
                        if (temp_host->host_name == NULL) {
                            temp_host = NULL;
                            continue;
                        }
#ifdef DEBUG
                        else {
                            printf("got end of hoststatus for %s\n",
                                temp_host->host_name);
                        }
#endif

                        PyList_Append((PyObject *)hosts, (PyObject *)temp_host);
                        temp_host = NULL;
                        break;

                    case XSDDEFAULT_SERVICESTATUS_DATA:
                        if (temp_service->host_name == NULL) {
                            temp_service = NULL;
                            continue;
                        }

                        PyList_Append((PyObject *)services, (PyObject *)temp_service);
                        temp_service = NULL;
                        break;
                }
            }

        else if (data_type != XSDDEFAULT_NO_DATA) {
                var = strtok(input, "=");
                val = strtok(NULL, "\n");

                if (val == NULL)
                    continue;

                switch (data_type) {
                    case XSDDEFAULT_INFO_DATA:
                        break;

                    case XSDDEFAULT_HOSTSTATUS_DATA:
                        if (temp_host == NULL)
                            break;
                        else if (!strcmp(var, "host_name"))
                            temp_host->host_name = TO_STR(val);
                        else if (!strcmp(var, "has_been_checked"))
                            temp_host->has_been_checked = TO_BOOL(val);
                        else if (!strcmp(var, "should_be_scheduled"))
                            temp_host->should_be_scheduled = TO_BOOL(val);
                        else if (!strcmp(var, "check_execution_time"))
                            temp_host->execution_time = TO_DOUBLE(val);
                        else if (!strcmp(var, "check_latency"))
                            temp_host->latency = TO_DOUBLE(val);
                        else if (!strcmp(var, "current_state"))
                            temp_host->status = TO_INT(val);
                        else if (!strcmp(var, "last_hard_state"))
                            temp_host->last_hard_state = TO_INT(val);
                        else if (!strcmp(var, "plugin_output")) {
                            temp_host->plugin_output = TO_STR(val);
                            unescape_newlines(temp_host->plugin_output);
                            }
                        else if (!strcmp(var, "long_plugin_output")) {
                            temp_host->long_plugin_output = TO_STR(val);
                            unescape_newlines(temp_host->long_plugin_output);
                            }
                        else if (!strcmp(var, "performance_data"))
                            temp_host->perf_data = TO_STR(val);
                        else if (!strcmp(var, "current_attempt"))
                            temp_host->current_attempt = TO_INT(val);
                        else if (!strcmp(var, "max_attempts"))
                            temp_host->max_attempts = TO_INT(val);
                        else if (!strcmp(var, "last_check"))
                            temp_host->last_check = TO_LONG(val);
                        else if (!strcmp(var, "next_check"))
                            temp_host->next_check = TO_LONG(val);
                        else if (!strcmp(var, "check_options"))
                            temp_host->check_options = TO_INT(val);
                        else if (!strcmp(var, "current_attempt"))
                            temp_host->current_attempt = TO_BOOL(val);
                        else if (!strcmp(var, "max_attempts"))
                            temp_host->max_attempts = TO_BOOL(val);
                        else if (!strcmp(var, "last_check"))
                            temp_host->last_check = TO_LONG(val);
                        else if (!strcmp(var, "next_check"))
                            temp_host->next_check = TO_LONG(val);
                        else if (!strcmp(var, "check_options"))
                            temp_host->check_options = TO_INT(val);
                        else if (!strcmp(var, "current_attempt"))
                            temp_host->current_attempt = TO_BOOL(val);
                        else if (!strcmp(var, "state_type"))
                            temp_host->next_check = TO_INT(val);
                        else if (!strcmp(var, "last_state_change"))
                            temp_host->last_state_change = TO_LONG(val);
                        else if (!strcmp(var, "last_hard_state_change"))
                            temp_host->last_hard_state_change = TO_LONG(val);
                        else if (!strcmp(var, "last_time_up"))
                            temp_host->last_time_up = TO_LONG(val);
                        else if (!strcmp(var, "last_time_down"))
                            temp_host->last_time_down = TO_LONG(val);
                        else if (!strcmp(var, "last_time_unreachable"))
                            temp_host->last_time_unreachable = TO_LONG(val);
                        else if (!strcmp(var, "last_notification"))
                            temp_host->last_notification = TO_LONG(val);
                        else if (!strcmp(var, "next_notification"))
                            temp_host->next_notification = TO_LONG(val);
                        else if (!strcmp(var, "no_more_notifications"))
                            temp_host->no_more_notifications = TO_BOOL(val);
                        else if (!strcmp(var, "current_notification_number"))
                            temp_host->current_notification_number = TO_INT(val);
                        else if (!strcmp(var, "notifications_enabled"))
                            temp_host->notifications_enabled = TO_BOOL(val);
                        else if (!strcmp(var, "problem_has_been_acknowledged"))
                            temp_host->problem_has_been_acknowledged = TO_BOOL(val);
                        else if (!strcmp(var, "acknowledgement_type"))
                            temp_host->acknowledgement_type = TO_INT(val);
                        else if (!strcmp(var, "active_checks_enabled"))
                            temp_host->checks_enabled = TO_BOOL(val);
                        else if (!strcmp(var, "passive_checks_enabled"))
                            temp_host->accept_passive_host_checks = TO_BOOL(val);
                        else if (!strcmp(var, "event_handler_enabled"))
                            temp_host->event_handler_enabled = TO_BOOL(val);
                        else if (!strcmp(var, "flap_detection_enabled"))
                            temp_host->flap_detection_enabled = TO_BOOL(val);
                        else if (!strcmp(var, "failure_prediction_enabled"))
                            temp_host->failure_prediction_enabled = TO_BOOL(val);
                        else if (!strcmp(var, "process_performance_data"))
                            temp_host->process_performance_data = TO_BOOL(val);
                        else if (!strcmp(var, "obsess_over_host"))
                            temp_host->obsess_over_host = TO_BOOL(val);
                        else if (!strcmp(var, "last_update"))
                            temp_host->last_update = TO_LONG(val);
                        else if (!strcmp(var, "is_flapping"))
                            temp_host->is_flapping = TO_BOOL(val);
                        else if (!strcmp(var, "percent_state_change"))
                            temp_host->percent_state_change = TO_DOUBLE(val);
                        else if (!strcmp(var, "scheduled_downtime_depth"))
                            temp_host->scheduled_downtime_depth = TO_INT(val);
                        else if (!strcmp(var, "check_type"))
                            temp_host->check_type = TO_INT(val);
                        else if (!strcmp(var, "check_period"))
                            temp_host->check_period = TO_STR(val);
                        else if (!strcmp(var, "check_command"))
                            temp_host->check_command = TO_STR(val);
                        else if (!strcmp(var, "check_interval"))
                            temp_host->check_interval = TO_INT(val);
                        else if (!strcmp(var, "retry_interval"))
                            temp_host->retry_interval = TO_INT(val);
                        else if (!strcmp(var, "notification_period"))
                            temp_host->notification_period = TO_STR(val);
#ifdef DEBUG
                        else
                            printf("unknown variable \"%s\" for hoststatus\n", var);
#endif

                        break;

                    case XSDDEFAULT_SERVICESTATUS_DATA:
                        if (temp_service == NULL)
                            break;
                        else if (!strcmp(var, "host_name"))
                            temp_service->host_name = TO_STR(val);
                        else if(!strcmp(var, "service_description"))
                            temp_service->description = TO_STR(val);
                        else if(!strcmp(var, "has_been_checked"))
                            temp_service->has_been_checked = TO_BOOL(val);
                        else if(!strcmp(var, "should_be_scheduled"))
                            temp_service->should_be_scheduled = TO_BOOL(val);
                        else if(!strcmp(var, "check_execution_time"))
                            temp_service->execution_time = TO_DOUBLE(val);
                        else if(!strcmp(var, "check_latency"))
                            temp_service->latency = TO_DOUBLE(val);
                        else if(!strcmp(var, "check_type"))
                            temp_service->check_type = TO_INT(val);
                        else if(!strcmp(var, "current_state"))
                            temp_service->status = TO_INT(val);
                        else if(!strcmp(var, "last_hard_state"))
                            temp_service->last_hard_state = TO_INT(val);
                        else if(!strcmp(var, "current_attempt"))
                            temp_service->current_attempt = TO_INT(val);
                        else if(!strcmp(var, "max_attempts"))
                            temp_service->max_attempts = TO_INT(val);
                        else if(!strcmp(var, "state_type"))
                            temp_service->state_type = TO_INT(val);
                        else if(!strcmp(var, "last_state_change"))
                            temp_service->last_state_change = TO_LONG(val);
                        else if(!strcmp(var, "last_hard_state_change"))
                            temp_service->last_hard_state_change = TO_LONG(val);
                        else if(!strcmp(var, "last_time_ok"))
                            temp_service->last_time_ok = TO_LONG(val);
                        else if(!strcmp(var, "last_time_warning"))
                            temp_service->last_time_warning = TO_LONG(val);
                        else if(!strcmp(var, "last_time_unknown"))
                            temp_service->last_time_unknown = TO_LONG(val);
                        else if(!strcmp(var, "last_time_critical"))
                            temp_service->last_time_critical = TO_LONG(val);
                        else if(!strcmp(var, "plugin_output")) {
                            temp_service->plugin_output = TO_STR(val);
                            unescape_newlines(temp_service->plugin_output);
                            }
                        else if(!strcmp(var, "long_plugin_output")) {
                            temp_service->long_plugin_output = TO_STR(val);
                            unescape_newlines(temp_service->long_plugin_output);
                            }
                        else if(!strcmp(var, "performance_data"))
                            temp_service->perf_data = TO_STR(val);
                        else if(!strcmp(var, "last_check"))
                            temp_service->last_check = TO_LONG(val);
                        else if(!strcmp(var, "next_check"))
                            temp_service->next_check = TO_LONG(val);
                        else if(!strcmp(var, "check_options"))
                            temp_service->check_options = TO_INT(val);
                        else if(!strcmp(var, "current_notification_number"))
                            temp_service->current_notification_number = TO_INT(val);
                        else if(!strcmp(var, "last_notification"))
                            temp_service->last_notification = TO_LONG(val);
                        else if(!strcmp(var, "next_notification"))
                            temp_service->next_notification = TO_LONG(val);
                        else if(!strcmp(var, "no_more_notifications"))
                            temp_service->no_more_notifications = TO_BOOL(val);
                        else if(!strcmp(var, "notifications_enabled"))
                            temp_service->notifications_enabled = TO_BOOL(val);
                        else if(!strcmp(var, "active_checks_enabled"))
                            temp_service->checks_enabled = TO_BOOL(val);
                        else if(!strcmp(var, "passive_checks_enabled"))
                            temp_service->accept_passive_service_checks = TO_BOOL(val);
                        else if(!strcmp(var, "event_handler_enabled"))
                            temp_service->event_handler_enabled = TO_BOOL(val);
                        else if(!strcmp(var, "problem_has_been_acknowledged"))
                            temp_service->problem_has_been_acknowledged = TO_BOOL(val);
                        else if(!strcmp(var, "acknowledgement_type"))
                            temp_service->acknowledgement_type = TO_INT(val);
                        else if(!strcmp(var, "flap_detection_enabled"))
                            temp_service->flap_detection_enabled = TO_BOOL(val);
                        else if(!strcmp(var, "failure_prediction_enabled"))
                            temp_service->failure_prediction_enabled = TO_BOOL(val);
                        else if(!strcmp(var, "process_performance_data"))
                            temp_service->process_performance_data = TO_BOOL(val);
                        else if(!strcmp(var, "obsess_over_service"))
                            temp_service->obsess_over_service = TO_BOOL(val);
                        else if(!strcmp(var, "last_update"))
                            temp_service->last_update = TO_LONG(val);
                        else if(!strcmp(var, "is_flapping"))
                            temp_service->is_flapping = TO_BOOL(val);
                        else if(!strcmp(var, "percent_state_change"))
                            temp_service->percent_state_change = TO_DOUBLE(val);
                        else if(!strcmp(var, "scheduled_downtime_depth"))
                            temp_service->scheduled_downtime_depth = TO_INT(val);
                }
            }
    }

    return result;
}
