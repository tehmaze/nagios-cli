import datetime


class Field(object):
    def __init__(self, raw):
        self.raw = raw
        self.value = self.parse(raw)

    def __str__(self):
        return str(self.value)

    def parse(self, raw):
        return raw


class Boolean(Field):
    def __str__(self):
        return ['false', 'true'][int(self.value)]

    def parse(self, raw):
        return bool(int(raw))


class String(Field):
    pass


class Number(Field):
    def parse(self, raw):
        return int(raw)


class Float(Field):
    def parse(self, raw):
        return float(raw)


class Percentage(Float):
    def __str__(self):
        return '%.02f%%' % (self.value,)


class State(Number):
    states = ['ok', 'warning', 'critical', 'unknown']

    def __str__(self):
        return self.states[self.value]


class Time(Field):
    def parse(self, raw):
        value = int(raw)
        if value:
            return datetime.datetime.fromtimestamp(value)


class Type(Number):
    types = []

    def __str__(self):
        try:
            return self.types[self.value]
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
    acknowledgement_type            = AcknowledgementType,
    active_checks_enabled           = Boolean,
    author                          = String,
    check_command                   = String,
    check_execution_time            = Float,
    check_interval                  = Float,
    check_latency                   = Float,
    check_options                   = CheckOptionType,
    check_period                    = String,
    check_type                      = CheckType,
    comment_data                    = String,
    comment_id                      = Number,
    current_attempt                 = Number,
    current_event_id                = Number,
    current_notification_id         = Number,
    current_notification_number     = Number,
    current_problem_id              = Number,
    current_state                   = State,
    entry_time                      = Time,
    entry_type                      = EntryType,
    event_handler                   = String,
    event_handler_enabled           = Boolean,
    expire_time                     = Time,
    expires                         = Boolean,
    failure_prediction_enabled      = Boolean,
    flap_detection_enabled          = Boolean,
    has_been_checked                = Boolean,
    host_name                       = String,
    is_flapping                     = String,
    last_check                      = Time,
    last_event_id                   = Number,
    last_hard_state                 = State,
    last_hard_state_change          = Time,
    last_notification               = Time,
    last_problem_id                 = Number,
    last_state_change               = Time,
    last_time_critical              = Time,
    last_time_down                  = Time,
    last_time_ok                    = Time,
    last_time_unknown               = Time,
    last_time_unreachable           = Time,
    last_time_up                    = Time,
    last_time_warning               = Time,
    last_update                     = Time,
    long_plugin_output              = String,
    max_attempts                    = Number,
    modified_attributes             = Number,
    next_check                      = Time,
    next_notification               = Time,
    no_more_notifications           = Boolean,
    notification_period             = String,
    notifications_enabled           = Boolean,
    obsess_over_host                = Boolean,
    obsess_over_service             = Boolean,
    passive_checks_enabled          = Boolean,
    percent_state_change            = Percentage,
    performance_data                = String,
    persistent                      = Boolean,
    plugin_output                   = String,
    problem_has_been_acknowledged   = Boolean,
    process_performance_data        = Boolean,
    retry_interval                  = Float,
    scheduled_downtime_depth        = Number,
    service_description             = String,
    should_be_scheduled             = Boolean,
    state_type                      = StateType,
)
