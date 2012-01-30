import datetime


class Field(object):
    def __call__(self, raw):
        return raw


class Boolean(Field):
    def __call__(self, raw):
        print raw
        return ['false', 'true'][int(raw)]


class String(Field):
    pass


class Number(Field):
    pass


class Float(Field):
    pass


class Percentage(Field):
    def __call__(self, raw):
        return '%.02f%%' % (float(raw),)


class State(Field):
    states = ['ok', 'warning', 'critical', 'unknown']

    def __call__(self, raw):
        return self.states[int(raw)]


class Time(Field):
    def __call__(self, raw):
        value = int(raw)
        if value:
            return str(datetime.datetime.fromtimestamp(value))
        else:
            return 'never'


class Type(Field):
    types = []

    def __call__(self, raw):
        try:
            return self.types[int(raw)]
        except IndexError:
            return 'n/a'


class AcknowledgementType(Type):
    types = ['none', 'normal', 'sticky']


class CheckOptionType(Type):
    types = ['none', 'force execution', 'fresheness check', 'orphan check']


class CheckType(Type):
    types = ['active', 'passive']


class StateType(Type):
    types = ['soft', 'hard']


class EntryType(Type):
    types = ['unknown', 'user comment', 'downtime comment',
        'flapping comment', 'acknowledgement comment']


# Mapping of nagios (status.dat) fields to python types
FIELDS = dict(
    acknowledgement_type            = AcknowledgementType(),
    active_checks_enabled           = Boolean(),
    author                          = String(),
    check_command                   = String(),
    check_execution_time            = Float(),
    check_interval                  = Float(),
    check_latency                   = Float(),
    check_options                   = CheckOptionType(),
    check_period                    = String(),
    check_type                      = CheckType(),
    comment_data                    = String(),
    comment_id                      = Number(),
    current_attempt                 = Number(),
    current_event_id                = Number(),
    current_notification_id         = Number(),
    current_notification_number     = Number(),
    current_problem_id              = Number(),
    current_state                   = State(),
    entry_time                      = Time(),
    entry_type                      = EntryType(),
    event_handler                   = String(),
    event_handler_enabled           = Boolean(),
    expire_time                     = Time(),
    expires                         = Boolean(),
    failure_prediction_enabled      = Boolean(),
    flap_detection_enabled          = Boolean(),
    has_been_checked                = Boolean(),
    host_name                       = String(),
    is_flapping                     = String(),
    last_check                      = Time(),
    last_event_id                   = Number(),
    last_hard_state                 = State(),
    last_hard_state_change          = Time(),
    last_notification               = Time(),
    last_problem_id                 = Number(),
    last_state_change               = Time(),
    last_time_critical              = Time(),
    last_time_down                  = Time(),
    last_time_ok                    = Time(),
    last_time_unknown               = Time(),
    last_time_unreachable           = Time(),
    last_time_up                    = Time(),
    last_time_warning               = Time(),
    last_update                     = Time(),
    long_plugin_output              = String(),
    max_attempts                    = Number(),
    modified_attributes             = Number(),
    next_check                      = Time(),
    next_notification               = Time(),
    no_more_notifications           = Boolean(),
    notification_period             = String(),
    notifications_enabled           = Boolean(),
    obsess_over_host                = Boolean(),
    obsess_over_service             = Boolean(),
    passive_checks_enabled          = Boolean(),
    percent_state_change            = Percentage(),
    performance_data                = String(),
    persistent                      = Boolean(),
    plugin_output                   = String(),
    problem_has_been_acknowledged   = Boolean(),
    process_performance_data        = Boolean(),
    retry_interval                  = Float(),
    scheduled_downtime_depth        = Number(),
    service_description             = String(),
    should_be_scheduled             = Boolean(),
    state_type                      = StateType(),
)
