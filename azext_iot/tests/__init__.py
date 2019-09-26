# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import io
from datetime import datetime
from threading import Event, Thread

from azure.cli.core import AzCli
from contextlib import contextmanager


DEVICE_DEVICESCOPE_PREFIX = "ms-azure-iot-edge://"


@contextmanager
def capture_output():
    class stream_buffer_tee(object):
        def __init__(self):
            self.stdout = sys.stdout
            self.buffer = io.StringIO()

        def write(self, message):
            self.stdout.write(message)
            self.buffer.write(message)

        def flush(self):
            self.stdout.flush()
            self.buffer.flush()

        def get_output(self):
            return self.buffer.getvalue()

        def close(self):
            self.buffer.close()

    _stdout = sys.stdout
    buffer_tee = stream_buffer_tee()
    sys.stdout = buffer_tee
    try:
        yield buffer_tee
    finally:
        sys.stdout = _stdout
        buffer_tee.close()


class DummyCliOutputProducer(AzCli):
    """A dummy CLI instance can be used to facilitate automation"""
    def __init__(self, commands_loader_cls=None, **kwargs):
        import os

        from azure.cli.core import MainCommandsLoader
        from azure.cli.core.commands import AzCliCommandInvoker
        from azure.cli.core.azlogging import AzCliLogging
        from azure.cli.core.cloud import get_active_cloud
        from azure.cli.core.parser import AzCliCommandParser
        from azure.cli.core._config import GLOBAL_CONFIG_DIR, ENV_VAR_PREFIX
        from azure.cli.core._help import AzCliHelp
        from azure.cli.core._output import AzOutputProducer

        from knack.completion import ARGCOMPLETE_ENV_NAME

        super(DummyCliOutputProducer, self).__init__(
            cli_name='az',
            config_dir=GLOBAL_CONFIG_DIR,
            config_env_var_prefix=ENV_VAR_PREFIX,
            commands_loader_cls=commands_loader_cls or MainCommandsLoader,
            parser_cls=AzCliCommandParser,
            logging_cls=AzCliLogging,
            help_cls=AzCliHelp,
            invocation_cls=AzCliCommandInvoker,
            output_cls=AzOutputProducer)

        self.data['headers'] = {}  # the x-ms-client-request-id is generated before a command is to execute
        self.data['command'] = 'unknown'
        self.data['completer_active'] = ARGCOMPLETE_ENV_NAME in os.environ
        self.data['query_active'] = False

        loader = self.commands_loader_cls(self)
        setattr(self, 'commands_loader', loader)

        self.cloud = get_active_cloud(self)

    def get_cli_version(self):
        from azure.cli.core import __version__ as cli_version
        return cli_version


def validate_min_python_version(major, minor, error_msg=None, exit_on_fail=True):
    """ If python version does not match AT LEAST requested values, will throw non 0 exit code."""
    version = sys.version_info
    result = False
    if version.major > major:
        return True
    if major == version.major:
        result = (version.minor >= minor)

    if not result:
        if exit_on_fail:
            msg = error_msg if error_msg else 'Python version {}.{} or higher required for this functionality.'.format(
                major, minor)
            sys.exit(msg)

    return result


def execute_onthread(**kwargs):
    """
    Experimental generic helper for executing methods without return values on a background thread

    Args:
        kwargs: Supported kwargs are 'interval' (int) to specify intervals between calls
                'method' (func) to specify method pointer for execution
                'args' (list) to specify method arguments
                'max_runs' (int) indicate an upper bound on number of executions
                'return_handle' (bool) indicates whether to return a Thread handle

    Returns:
        Event(): Object to set the event cancellation flag
        or if 'return_handle'=True
        Event(), Thread(): Event object to set the cancellation flag, Executing Thread object
    """

    interval = kwargs.get('interval')
    method = kwargs.get('method')
    method_args = kwargs.get('args')
    max_runs = kwargs.get('max_runs')
    handle = kwargs.get('return_handle')

    if not interval:
        interval = 2
    if not method:
        raise ValueError('kwarg "method" required for execution')
    if not method_args:
        method_args = []

    cancellation_token = Event()

    def method_wrap(max_runs=None):
        runs = 0
        while not cancellation_token.wait(interval):
            if max_runs:
                if runs >= max_runs:
                    break
            method(*method_args)
            runs += 1

    op = Thread(target=method_wrap, args=(max_runs,))
    op.start()

    if handle:
        return cancellation_token, op

    return cancellation_token


def calculate_millisec_since_unix_epoch_utc():
    now = datetime.utcnow()
    epoch = datetime.utcfromtimestamp(0)
    return int(1000 * (now - epoch).total_seconds())
