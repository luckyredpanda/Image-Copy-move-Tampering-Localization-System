#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HelpDev - Extracts information about the Python environment easily.

Authors:
    - Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2019/04/16

License:
    MIT

"""

__version__ = "0.6.10"

import copy
import os
import platform
import re
import socket
import subprocess
import sys
import time
import warnings

import importlib_metadata

if sys.version_info >= (3, 4):
    import importlib.util

try:
    from urllib.request import urlopen
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
    from urllib2 import urlopen

# To make FileNotFoundError works on Python 2 and 3
try:
    FileNotFoundError2and3 = FileNotFoundError
except NameError:
    FileNotFoundError2and3 = OSError


QT_BINDINGS = ['PyQt4', 'PyQt5', 'PySide', 'PySide2']
"""list: values of all Qt bindings to import."""

QT_ABSTRACTIONS = ['qtpy', 'pyqtgraph', 'Qt']
"""list: values of all Qt abstraction layers to import."""

URLS = {
    'PyPI': 'https://pypi.python.org/pypi/pip',
    'Conda': 'https://repo.continuum.io/pkgs/free/',
    'GitLab': 'https://gitlab.com',
    'GitHub': 'https://github.com',
    'Google': 'https://google.com'
}


def _filter(dict_packages, expression):
    """Filter the dict_packages with expression.

    Returns:
        dict(rst): Filtered dict with that matches the expression.
    """

    expression_list = ['(' + item + ')' for item in expression.split(',')]
    expression_str = '|'.join(expression_list)
    compiled_exp = re.compile('(?i:^(' + expression_str + ')$)')
    cp_dict_packages = copy.deepcopy(dict_packages)

    for key in dict_packages.keys():
        match = re.search(compiled_exp, key)
        if not match:
            del cp_dict_packages[key]

    return cp_dict_packages


def _run_subprocess_split(command):
    """Run command in subprocess and return the splited output.

    Returns:
        str: Splited output from command execution.
    """

    output = subprocess.check_output(command, shell=False)

    if sys.version_info >= (3, 0):
        output = str(output, 'utf-8').strip()
    else:
        output = unicode(output, 'utf-8').strip()  # noqa, pylint: disable=undefined-variable

    return output


def check_installed(import_list):
    """Return a list of installed packages from import_list.

    Args:
        import_list (list(str)): List of of import names to check installation.

    Returns:
        list(str): Filtered list of installed packages.

    """

    # Disable warnings here
    warnings.filterwarnings("ignore")

    import_list_return = copy.deepcopy(import_list)
    # Using import_list_return var in for, does not work in py2.7
    # when removing the element, it reflects on for list
    # so it skips next element
    for current_import in import_list:

        spec = True
        # Copy the sys path to make sure to not insert anything
        sys_path = sys.path

        # Check import
        if sys.version_info >= (3, 4):
            spec = bool(importlib.util.find_spec(current_import))
        else:
            try:
                __import__(current_import)
            except RuntimeWarning:
                spec = True
            except Exception:  # noqa:W0703, pylint: disable=broad-except
                spec = False
            else:
                spec = True

        if not spec:
            # Remove if not available
            import_list_return.remove(current_import)

        # Restore sys path
        sys.path = sys_path

    # Restore warnings
    warnings.resetwarnings()

    return import_list_return


def print_output(info_dict):
    """Print output in a nested list format."""
    for key, sub_dict in info_dict.items():
        print('* {:-<79}'.format(key))
        for sub_key, sub_value in sub_dict.items():
            print('    - {:.<30} {}'.format(sub_key, sub_value))


def check_hardware():
    """Check hardware information.

    It uses subprocess commands for each system along with psutil library.
    So you need to install psutil library.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    cpu = ''

    # mac
    if sys.platform.startswith('darwin'):
        all_info = _run_subprocess_split(['sysctl', '-a'])
        for line in all_info.split("\n"):
            if "brand_string" in line:
                cpu = line.split(": ")[1]
                break
    # linux
    elif sys.platform.startswith('linux'):
        all_info = _run_subprocess_split(['lscpu'])
        for line in all_info.split("\n"):
            if "Model name:" in line:
                cpu = line.split(':')[1]
                break
    # windows
    elif sys.platform.startswith('win32'):
        all_info = _run_subprocess_split(['wmic', 'cpu', 'get', 'name'])
        if "Name" in all_info:
            cpu = all_info.replace('Name', '')
    try:
        import psutil
        mem = str(int(psutil.virtual_memory().total / 1000000)) + " MB"
        mem_free = str(int(psutil.virtual_memory().free / 1000000)) + " MB"
        swap = str(int(psutil.swap_memory().total / 1000000)) + " MB"
        swap_free = str(int(psutil.swap_memory().free / 1000000)) + " MB"
    except ImportError:
        mem = 'Unknown, needs psutil library'
        swap = swap_free = mem_free = mem

    info = {'HARDWARE':
            {'Machine': platform.machine(),
             'Processor': cpu.lstrip(),
             'Total Memory': mem,
             'Free Memory': mem_free,
             'Total Swap': swap,
             'Free Swap': swap_free
             }
            }

    return info


def check_os():
    """Check operating system information.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    info = {'OPERATING SYSTEM':
            {'System': platform.system(),
             'Release': platform.release(),
             'Platform': platform.platform(),
             'Version': platform.version()
             }
            }

    return info


def check_thread():
    """Check threads information.

    Get information from ``sys`` library.

    Returns:
        dict(str): Dictionary filled with respective information.
    """
    info = {'THREADS': {}}

    if sys.version_info >= (3, 3):
        info['THREADS'].update(
            {'Version': sys.thread_info.version,
             'Name': sys.thread_info.name,
             'Lock': sys.thread_info.lock,
             })
    else:
        info['THREADS'].update(
            {'Version': 'Unknown, needs Python>=3.3',
             'Name': 'Unknown, needs Python>=3.3',
             'Lock': 'Unknown, needs Python>=3.3'
             })

    return info


def check_float():
    """Check float limits information.

    Get information from ``sys`` library.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    info = {'FLOAT':
            {'Epsilon': sys.float_info.epsilon,
             'Digits': sys.float_info.dig,
             'Precision': sys.float_info.mant_dig,
             'Maximum': sys.float_info.max,
             'Maximum Exp.': sys.float_info.max_exp,
             'Max. 10 Exp.': sys.float_info.max_10_exp,
             'Minimum': sys.float_info.min,
             'Miminim Exp.': sys.float_info.min_exp,
             'Min. 10 Exp.': sys.float_info.min_10_exp,
             'Radix': sys.float_info.radix,
             'Rounds': sys.float_info.rounds
             }
            }

    return info


def check_int():
    """Check int limits information.

    Get information from ``sys`` library.

    Returns:
        dict(str): Dictionary filled with respective information.
    """
    info = {'INTEGER': {}}

    if sys.version_info >= (3, 1):
        info['INTEGER'].update(
            {'Bits per Digit': sys.int_info.bits_per_digit,
             'Size of Digit': sys.int_info.sizeof_digit
             }
        )
    else:
        info['INTEGER'].update(
            {'Bits per Digit': 'Unknown, needs Python>=3.1',
             'Size of Digit': 'Unknown, needs Python>=3.1'
             }
        )
    return info


def check_network(timeout):
    """Check network connection for URLS list with timeout.

    Args:
        timeout (int): timout in seconds.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    info = {'NETWORK':
            {'Timeout': str(timeout) + 's'
             }
            }

    if timeout > 0:
        socket.setdefaulttimeout(timeout)
    else:
        info['NETWORK']['Timeout'] = 'Must be > 0s'
        return info

    for name, url in URLS.items():
        if url.lower().startswith('http'):
            urlinfo = urlparse(url)
            error = False

            # DNS
            dns_err = ''
            start = time.time()

            try:
                _ = socket.gethostbyname(urlinfo.netloc)
            except Exception as err:  # noqa:W0703 , pylint: disable=broad-except
                dns_err = str(err)
                info['NETWORK'][name] = "DNS ERROR: {}s URL: {}".format(dns_err, url)
                error = True
            dns_elapsed = time.time() - start

            # LOAD
            load_err = ''
            start = time.time()
            try:
                _ = urlopen(url, timeout=timeout)  # nosec: url is tested to skip non http
            except Exception as err:  # noqa:W0703 , pylint: disable=broad-except
                load_err = str(err)
                info['NETWORK'][name] = "LOAD ERROR: {}s URL: {}".format(load_err, url)
                error = True
            load_elapsed = time.time() - start

            if not error:
                info['NETWORK'][name] = "DNS: {:.4f}s LOAD: {:.4f}s URL: {}".format(dns_elapsed,
                                                                                    load_elapsed,
                                                                                    url)

    return info


def check_python():
    """Check Python information.

    It is Python environment dependent. Get information from ``platform``
    and ``sys`` libraries.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    info = {'PYTHON DISTRIBUTION':
            {'Version': platform.python_version(),
             'C Compiler': platform.python_compiler(),
             'C API Version': sys.api_version
             }}

    if sys.version_info >= (3, 3):
        info['PYTHON DISTRIBUTION'].update(
            {'Implementation': sys.implementation.name,
             'Implementation Version': '{}.{}.{}'.format(sys.implementation.version.major,
                                                         sys.implementation.version.minor,
                                                         sys.implementation.version.micro)
             })
    else:
        info['PYTHON DISTRIBUTION'].update(
            {'Implementation': 'Unknown, needs Python>=3.3',
             'Implementation Version': 'Unknown, needs Python>=3.3'
             })

    return info


def check_python_packages(edit_mode=False, packages=None):
    """Check PIP installed packages filtering for packages.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    all_packages = ''

    if edit_mode:
        all_packages = _run_subprocess_split(['pip', 'list', '-e'])
    else:
        # list all packages, including in editable mode
        all_packages = _run_subprocess_split(['pip', 'list'])

    # split lines and remove table name
    line_packages = all_packages.split("\n")[2:]

    info = {'PYTHON PACKAGES': {}}

    # clean spaces, create a list and insert in the dictionary
    for line in line_packages:
        splitted = line.split(' ')
        cleaned = ' '.join(splitted).split()
        info['PYTHON PACKAGES'][cleaned[0]] = cleaned[1]

    if packages:
        info['PYTHON PACKAGES'] = _filter(info['PYTHON PACKAGES'], packages)

    return info


def check_conda():
    """Check Conda Python distribution information.

    It is Python/Conda environment dependent.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    info = {'CONDA DISTRIBUTION': {}}

    try:
        all_info = _run_subprocess_split(['conda', 'info'])
    except (subprocess.CalledProcessError, FileNotFoundError2and3):
        info['CONDA DISTRIBUTION']['Status'] = 'Conda not available!'
    else:
        for line in all_info.split("\n"):
            if "conda version : " in line:
                info['CONDA DISTRIBUTION']['Version'] = line.split(" : ")[1]
            elif "conda-build version : " in line:
                info['CONDA DISTRIBUTION']['Build'] = line.split(" : ")[1]

    return info


def check_conda_packages(edit_mode=False, packages=None):
    """Check conda inslalled packages information filtering for packages.

    It is Python/Conda environment dependent.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    info = {'CONDA PACKAGES': {}}
    all_packages = ''

    try:
        if not edit_mode:
            all_packages = _run_subprocess_split(['conda', 'list', '--no-pip', '--export'])
        else:
            all_packages = _run_subprocess_split(['conda', 'list', '--no-pip',
                                                  '--export', '--develop'])
    except (subprocess.CalledProcessError, FileNotFoundError2and3):
        info['CONDA PACKAGES']['Status'] = 'Conda not available!'
    else:
        # split lines and remove head
        line_packages = all_packages.split("\n")[3:]

        # clean spaces, create a list and insert in the dictionary
        for line in line_packages:
            splitted = line.split('=')
            cleaned = ' '.join(splitted).split()
            info['CONDA PACKAGES'][cleaned[0]] = cleaned[1]

    if packages:
        info['CONDA PACKAGES'] = _filter(info['CONDA PACKAGES'], packages)

    return info


def check_qt_bindings():
    """Check all Qt bindings related information.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    info = {'QT BINDINGS': {}}

    for binding in installed_qt_bindings():
        binding_version, qt_version = qt_binding_information(binding)
        info['QT BINDINGS'][binding + ' Version'] = binding_version
        info['QT BINDINGS'][binding + ' Qt Version'] = qt_version

    if not info['QT BINDINGS']:
        info['QT BINDINGS']['Status'] = 'No Qt binding available!'

    return info


def check_qt_abstractions():
    """Check all Qt abstractions related information.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    info = {'QT ABSTRACTIONS': {}}

    for abstraction in installed_qt_abstractions():
        abs_v, bind, bind_var, imp_name, status = qt_abstraction_information(abstraction)
        info['QT ABSTRACTIONS'][abstraction + ' Version'] = abs_v
        info['QT ABSTRACTIONS'][abstraction + ' Binding'] = bind
        info['QT ABSTRACTIONS'][abstraction + ' Binding Variable'] = bind_var
        info['QT ABSTRACTIONS'][abstraction + ' Import Name'] = imp_name
        info['QT ABSTRACTIONS'][abstraction + ' Status'] = status

    if not info['QT ABSTRACTIONS']:
        info['QT ABSTRACTIONS']['Status'] = 'No Qt abstractions available!'

    return info


def installed_qt_bindings():
    """Return a list of qt bindings available.

    Returns:
        list(str): List filled with respective information.
    """
    return check_installed(import_list=QT_BINDINGS)


def installed_qt_abstractions():
    """Return a list of qt abstraction layers available.

    Returns:
        dict(str): Dictionary filled with respective information.
    """
    return check_installed(import_list=QT_ABSTRACTIONS)


def qt_abstraction_information(import_name):  # noqa:R0912
    """Get abstraction layer version and binding (default or current if in use).

    Note:
        - The name of the installed package can differ from the import name.
          This is an weird thing from PIP/CONDA, e.g, the abstraction 'qt.py'
          is imported as 'Qt'.
        - Since each package is build as it is, sometimes we are not able to
          define its information, e.g, Qt.py is installed but no binding is.
          This will cause an error that, for now, it is impossible to us to
          show any other information about it, e.g, version. We need to deal
          with a better way.
        - This function should be called with pre-defined list of installed
          packages passed throuw import_name, do not use it to try import.

    Todo:
        - Add info installed (y/n), imported (y/n), importable/status (error).

    Args:
        import_name (str): Import name of abstraction for Qt.

    Raises:
        ImportError: When the import is not found.

    Returns:
        tuple: (abstraction version,
                environment variable,
                binding variable,
                import name,
                status)
    """

    # Copy the sys path to make sure to not insert anything
    sys_path = sys.path

    api_version = ''
    env_var = ''
    binding_var = ''
    status = 'OK'

    if import_name == 'pyqtgraph':
        try:
            from pyqtgraph import __version__ as api_version  # analysis:ignore
        except ImportError:
            raise ImportError('PyQtGraph cannot be imported.')
        except Exception as err:  # noqa:W0703, pylint: disable=broad-except
            api_version = importlib_metadata.version('pyqtgraph')
            status = "ERROR - " + str(err)

        if 'PYQTGRAPH_QT_LIB' not in os.environ:
            env_var = 'Not set or inexistent'
        else:
            env_var = os.environ['PYQTGRAPH_QT_LIB']

        binding_var = "os.environ['PYQTGRAPH_QT_LIB']"

    elif import_name == 'qtpy':
        try:
            from qtpy import __version__ as api_version  # analysis:ignore
        except ImportError:
            raise ImportError('QtPy cannot be imported.')
        except RuntimeError as err:
            env_var = 'No Qt binding found'
            api_version = importlib_metadata.version('qtpy')
            status = "ERROR - " + str(err)

        if 'QT_API' not in os.environ:
            env_var = 'Not set or inexistent'
        else:
            env_var = os.environ['QT_API']

        binding_var = "os.environ['QT_API']"

    elif import_name == 'Qt':
        try:
            from Qt import __version__ as api_version  # analysis:ignore
            from Qt import __binding__ as env_var  # analysis:ignore
        except ImportError as err:
            # this error is the same if a problem with binding appears
            # as this function should be used with already known installed
            # packages, this error will appears when binding problem is found
            # raise ImportError('Qt.py cannot be imported.')
            api_version = 'Not set or inexistent'
            env_var = 'Not set or inexistent'
            status = "ERROR - " + str(err)

        binding_var = "Qt.__binding__"

    else:
        return ('', '', '', '', '')

    # restore sys.path
    sys.path = sys_path

    return (api_version, env_var, binding_var, import_name, status)


def qt_binding_information(import_name):
    """Get binding information of version and Qt version.

    Note:
        The name of the installed package can differ from the import name.
        This is an weird thing from PIP/CONDA, e.g, the binding 'pyqt5'
        in PIP is 'pyqt' in Conda and both are imported as 'PyQt5'.

    Args:
        import_name (str): Import name of binding for Qt.

    Raises:
        ImportError: When the import is not found.

    Returns:
        tuple: (binding version,
                qt version)
    """

    # copy sys.path
    sys_path = sys.path

    if import_name == 'PyQt4':
        try:
            from PyQt4.Qt import PYQT_VERSION_STR as api_version  # analysis:ignore
            from PyQt4.Qt import QT_VERSION_STR as qt_version  # analysis:ignore
        except ImportError:
            raise ImportError('PyQt4 cannot be imported.')

    elif import_name == 'PyQt5':
        try:
            from PyQt5.QtCore import PYQT_VERSION_STR as api_version  # analysis:ignore
            from PyQt5.QtCore import QT_VERSION_STR as qt_version  # analysis:ignore
        except ImportError:
            raise ImportError('PyQt5 cannot be imported.')

    elif import_name == 'PySide':
        try:
            from PySide import __version__ as api_version  # analysis:ignore
            from PySide.QtCore import __version__ as qt_version  # analysis:ignore
        except ImportError:
            raise ImportError('PySide cannot be imported.')

    elif import_name == 'PySide2':
        try:
            from PySide2 import __version__ as api_version  # analysis:ignore
            from PySide2.QtCore import __version__ as qt_version  # analysis:ignore
        except ImportError:
            raise ImportError('PySide2 cannot be imported.')
    else:
        return ('', '')

    # restore sys.path
    sys.path = sys_path

    return (api_version, qt_version)


def check_path():
    """Check Python path from ``sys`` library.

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    info = {'PATHS': {}}

    info['PATHS']['Python'] = sys.executable
    for num, path in enumerate(sys.path):
        info['PATHS'][num] = path

    return info


def check_scope():
    """Check Python scope or dir().

    Returns:
        dict(str): Dictionary filled with respective information.
    """

    info = {'SCOPE': {}}

    for num, path in enumerate(dir()):
        info['SCOPE'][num] = path

    return info
