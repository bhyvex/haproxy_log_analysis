# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from haproxy import DELTA_REGEX
from haproxy import START_REGEX


def filter_ip(ip):
    """Filter :class:`.HaproxyLogLine` objects by IP.

    :param ip: IP that you want to filter to.
    :type ip: string
    :returns: a function that filters by the provided IP.
    :rtype: function
    """
    def filter_func(log_line):
        return log_line.get_ip() == ip

    return filter_func


def filter_ip_range(ip_range):
    """Filter :class:`.HaproxyLogLine` objects by IP range.

    Both *192.168.1.203* and *192.168.1.10* are valid if the provided ip
    range is ``192.168.1`` whereas *192.168.2.103* is not valid (note the
    *.2.*).

    :param ip_range: IP range that you want to filter to.
    :type ip_range: string
    :returns: a function that filters by the provided IP range.
    :rtype: function
    """
    def filter_func(log_line):
        ip = log_line.get_ip()
        if ip:
            return ip.startswith(ip_range)

    return filter_func


def filter_path(path):
    """Filter :class:`.HaproxyLogLine` objects by their request path.

    :param path: part of a path that needs to be on the request path.
    :type path: string
    :returns: a function that filters by the provided path.
    :rtype: function
    """
    def filter_func(log_line):
        return path in log_line.http_request_path

    return filter_func


def filter_ssl():
    """Filter :class:`.HaproxyLogLine` objects that from SSL connections.

    :returns: a function that filters SSL log lines.
    :rtype: function
    """
    def filter_func(log_line):
        return log_line.is_https()

    return filter_func


def filter_slow_requests(slowness):
    """Filter :class:`.HaproxyLogLine` objects by their response time.

    :param slowness: minimum time, in milliseconds, a server needs to answer
      a request. If the server takes more time than that the log line is
      accepted.
    :type slowness: string
    :returns: a function that filters by the server response time.
    :rtype: function
    """
    def filter_func(log_line):
        slowness_int = int(slowness)
        return slowness_int <= log_line.time_wait_response

    return filter_func


def filter_time_frame(start, delta):
    """Filter :class:`.HaproxyLogLine` objects by their connection time.

    :param start:
    :type start: string
    :param delta:
    :type delta: string
    :returns: a function that filters by the time a request is made.
    :rtype: function
    """
    start_value = start
    delta_value = delta
    end_value = None

    if start_value is not '':
        start_value = _date_str_to_datetime(start_value)

    if delta_value is not '':
        delta_value = _delta_str_to_timedelta(delta_value)

    if start_value is not '' and delta_value is not '':
        end_value = start_value + delta_value

    def filter_func(log_line):
        if start_value is '':
            return True
        elif start_value > log_line.accept_date:
            return False

        if end_value is None:
            return True
        elif end_value < log_line.accept_date:
            return False

        return True

    return filter_func


def _date_str_to_datetime(date):
    matches = START_REGEX.match(date)

    raw_date_input = '{0}/{1}/{2}'.format(
        matches.group('day'),
        matches.group('month'),
        matches.group('year')
    )
    date_format = '%d/%b/%Y'
    if matches.group('hour'):
        date_format += ':%H'
        raw_date_input += ':{0}'.format(matches.group('hour'))
    if matches.group('minute'):
        date_format += ':%M'
        raw_date_input += ':{0}'.format(matches.group('minute'))
    if matches.group('second'):
        date_format += ':%S'
        raw_date_input += ':{0}'.format(matches.group('second'))

    return datetime.strptime(raw_date_input, date_format)


def _delta_str_to_timedelta(delta):
    matches = DELTA_REGEX.match(delta)

    value = int(matches.group('value'))
    time_unit = matches.group('time_unit')

    if time_unit == 's':
        return timedelta(seconds=value)
    elif time_unit == 'm':
        return timedelta(minutes=value)
    elif time_unit == 'h':
        return timedelta(hours=value)
    if time_unit == 'd':
        return timedelta(days=value)