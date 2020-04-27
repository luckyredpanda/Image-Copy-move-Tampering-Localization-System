from functools import wraps
import logging
from multiprocessing import Process, Queue
import os
import subprocess
import sys
import traceback

from utils_core.func import timeout as func_timeout

log = logging.getLogger(__name__)


class RunError(Exception):
    pass


def is_running(pid):
    """ Returns True if the given process PID is running """
    try:
        os.kill(pid, 0)

    except OSError:
        return False

    return True


def processify(timeout=None):
    """
    Decorator to run a function as a process. Copied from https://gist.github.com/schlamar/2311116

    Be sure that every argument and the return value is *pickable*.  The created process is joined, so the code does
    not run in parallel.

    E.g.

    @processify
    def f(args):
        return "this runs in a separate process"

    @processify(timeout=20)
    def long_running(args):
        time.sleep(100)
        return "this will timeout and get killed in 20 secs"
    """
    if callable(timeout):
        return _processify(timeout)

    else:
        def decorator(func):
            return _processify(func, timeout=timeout)
        return decorator


def _processify(func, timeout=None):
    def process_func(q, *args, **kwargs):
        try:
            f = func_timeout(timeout, raises=SystemExit)(func) if timeout else func
            ret = f(*args, **kwargs)

        except (SystemExit, Exception):
            ex_type, ex_value, tb = sys.exc_info()
            if ex_type == SystemExit:  # We need SystemExit to cause everything to terminate, but not re-raise later
                ex_type = TimeoutError
            error = ex_type, ex_value, ''.join(traceback.format_tb(tb))
            ret = None

        else:
            error = None

        q.put((ret, error))

    # register original function with different name
    # in sys.modules so it is pickable
    process_func.__name__ = func.__name__ + 'processify_func'
    setattr(sys.modules[__name__], process_func.__name__, process_func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        q = Queue()
        p = Process(target=process_func, args=[q] + list(args), kwargs=kwargs)
        p.start()
        ret, error = q.get()
        p.join()

        if error:
            ex_type, ex_value, tb_str = error
            message = '%s (in subprocess)\n%s' % (str(ex_value), tb_str)
            raise ex_type(message)

        return ret
    return wrapper


def silent_run(*args, **kwargs):
    """ Same as run with slient=True """
    return run(*args, silent=True, **kwargs)


def run(cmd, cwd=None, silent=None, return_output=False, raises=True, **subprocess_args):
    """
    Runs a CLI command.

    :param list/str cmd: Command with args to run.
    :param str cwd: Change directory to cwd before running
    :param bool/int silent: Suppress stdout/stderr.
                            If True, completely silent.
                            If 2, print cmd output on error.
    :param bool return_output: Return the command output. Defaults silent=True. Set silent=False to see output.
                               If True, always return output.
                               If set to 2, return a tuple of (output, success) where output is the output of the
                               command and success is exit code 0.
                               When used, it is guaranteed to always return output / other options are ignored
                               (like raises).
    :param bool raises: Raise an exception if command exits with an error code.
    :param dict subprocess_args: Additional args to pass to subprocess
    :return: Output or boolean of success depending on option selected
    :raise RunError: if the command exits with an error code and raises=True
    """

    if isinstance(cmd, str):
        cmd = cmd.split()

    cmd_str = ' '.join(cmd)

    if 'shell' in subprocess_args and subprocess_args['shell']:
        cmd = cmd_str

    log.debug('Running: %s %s', cmd_str, '[%s]' % cwd if cwd else '')

    if return_output and silent is None:
        silent = True

    try:
        if silent or return_output:
            p = subprocess.Popen(cmd, cwd=cwd, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 **subprocess_args)
            exit_code = -1

            if silent:
                output, _ = p.communicate()
                exit_code = p.returncode
            else:
                output = ''
                ch = True
                while ch:
                    ch = p.stdout.read(1)
                    sys.stdout.write(ch)
                    sys.stdout.flush()
                    output += ch
                    if p.poll() is not None and exit_code == -1:
                        exit_code = p.returncode

            output = output.decode('utf-8')

            if return_output is True:
                return output
            elif return_output == 2:
                return output, exit_code == 0

            if exit_code == 0:
                if return_output:
                    return output
                else:
                    return True

            elif raises or silent == 2:
                if output and silent:
                    print(output.strip())

        else:
            exit_code = subprocess.call(cmd, cwd=cwd, **subprocess_args)
            if exit_code == 0:
                return True

    except Exception as e:
        if raises:
            log.debug(e, exc_info=True)
            raise RunError('Command "%s" could not be run because %s' % (cmd_str, e))

    # We only get here if exit code != 0
    if raises:
        raise RunError('Command "%s" returned non-zero exit status %d' % (cmd_str, exit_code))

    return False
