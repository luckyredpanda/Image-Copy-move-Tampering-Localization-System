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


import argparse
import sys

import helpdev


def parse_args():
    """Parse arguments.

    Returns:
        argparse.Namespace: parsed arguments.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=__doc__.split("\n")[0])

    parser.add_argument('--hardware', action='store_true',
                        help="CPU, memory and architecture (PEI)")
    parser.add_argument('--os', action='store_true',
                        help="Operating system (PEI)")
    parser.add_argument('--thread', action='store_true',
                        help="Threads specification in the system (PEI)")
    parser.add_argument('--network', nargs='?', const=5, default=None, type=int,
                        help="Network information, DNS and load for usual sites (PEI). "
                             "NETWORK timeout defaults to 5s. 0 is disabled.")

    parser.add_argument('--distributions', action='store_true',
                        help="All options for distributions below (PED)")
    parser.add_argument('--python', action='store_true',
                        help="Python distribution (PED)")
    parser.add_argument('--conda', action='store_true',
                        help="Conda/Anaconda Python distribution (PED)")

    parser.add_argument('--qt', action='store_true',
                        help="All options for Qt below (PEAD)")
    parser.add_argument('--qt-bindings', action='store_true',
                        help="Available Qt bindings (PyQt/Pyside) (PEAD)")
    parser.add_argument('--qt-abstractions', action='store_true',
                        help="Available Qt abstractions (QtPy/Qt.Py/PyQtGraph) (PEAD)")

    parser.add_argument('--packages', nargs='?', const="", default=None, type=str,
                        help="All options for packages below, except '-e' (PED)"
                        "Filter PACKAGE(s) to report. Accepts regex, separator is ','")
    parser.add_argument('--packages-pip', action='store_true',
                        help="PIP installed packages + PIP check (PED)")
    parser.add_argument('--packages-pip-e', action='store_true',
                        help="PIP locally installed packages + PIP check (PED)")
    parser.add_argument('--packages-conda', action='store_true',
                        help="CONDA installed packages (PED)")
    parser.add_argument('--packages-conda-e', action='store_true',
                        help="CONDA locally installed packages (PED)")

    parser.add_argument('--numbers', action='store_true',
                        help="All options for numbers below (PEI)")
    parser.add_argument('--float', action='store_true',
                        help="Float representation in the system (PEI)")
    parser.add_argument('--int', action='store_true',
                        help="Integer representation in the system (PEI)")

    parser.add_argument('--personal', action='store_true',
                        help="All options for personal information below (PEAD)")
    parser.add_argument('--path', action='store_true',
                        help="Show Python current paths i.e. 'sys.path' (PEAD)")
    parser.add_argument('--scope', action='store_true',
                        help="Show Python current scope i.e. 'dir()' (PEAD)")

    parser.add_argument('--all', action='store_true',
                        help="Run all options above, except 'personal' (PEAD)")
    parser.add_argument('--all-for-sure', action='store_true',
                        help="Run all options above, INCLUDING 'PERSONAL' (PEAD)")

    parser.add_argument('--version', '-v', action='version',
                        version='v{}'.format(helpdev.__version__))

    arguments = parser.parse_args()

    return arguments


def main():  # noqa:R701,R0912
    """Main function."""
    args = parse_args()

    info = {}

    # To not repeat the test
    if args.all_for_sure:
        args.all = True

    no_args = len(sys.argv) <= 1

    # Commom hardware, OS and Thread info
    if args.hardware or args.all or no_args:
        info.update(helpdev.check_hardware())
    if args.os or args.all or no_args:
        info.update(helpdev.check_os())
    if args.thread or args.all or no_args:
        info.update(helpdev.check_thread())

    # Network info
    if args.network:
        info.update(helpdev.check_network(args.network))

    # Distribution info
    if args.python or args.all or no_args or args.distributions:
        info.update(helpdev.check_python())
    if args.conda or args.all or no_args or args.distributions:
        info.update(helpdev.check_conda())

    # Qt, binding and abstraction info
    if args.qt_bindings or args.qt or args.all or no_args:
        info.update(helpdev.check_qt_bindings())
    if args.qt_abstractions or args.qt or args.all or no_args:
        info.update(helpdev.check_qt_abstractions())

    # Numbers info
    if args.float or args.all or args.numbers:
        info.update(helpdev.check_float())
    if args.int or args.all or args.numbers:
        info.update(helpdev.check_int())

    # Packages, PIP and Conda info
    if args.packages_pip or args.all or args.packages or args.packages == '':
        info.update(helpdev.check_python_packages(packages=args.packages))
    if args.packages_pip_e:
        info.update(helpdev.check_python_packages(edit_mode=True, packages=args.packages))
    if args.packages_conda or args.all or args.packages or args.packages == '':
        info.update(helpdev.check_conda_packages(packages=args.packages))
    if args.packages_conda_e or args.all:
        info.update(helpdev.check_conda_packages(edit_mode=True, packages=args.packages))

    # Personal info for self-check, not executed when --all is passed
    # Needs to use all-for-sure to be listed
    # This may contains personal folder adresses, be carefull sharing
    if args.path or args.all_for_sure or args.personal:
        info.update(helpdev.check_path())
    if args.scope or args.all_for_sure or args.personal:
        info.update(helpdev.check_scope())

    helpdev.print_output(info)
