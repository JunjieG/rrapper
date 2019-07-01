#!/usr/bin/env python2.7
# pylint: disable=missing-docstring, bad-indentation, too-many-locals
"""
<Program Name>
  rrtest

<Started>
  July 2018

<Author>
  Alan Cao

<Purpose>
  Automates the creation of CrashSimulator-compliant tests.

  This application-level script enables the user to perform a preemptive record and
  replay execution, such that a strace segment is produced. This strace can then
  be compared against a ReplaySession debug log in order to determine corresponding
  events and trace lines, such that a final test can be produced and stored. Once
  complete, a user can utilize `rreplay` in order to execute another replay execution.

"""

from __future__ import print_function

import os
import sys
import argparse
import subprocess
import re
import logging
import shutil
import errno
import ConfigParser

from posix_omni_parser import Trace
from mutator.Null import NullMutator                        # noqa: F401
from mutator.CrossdiskRename import CrossdiskRenameMutator  # noqa: F401
from mutator.FutureTime import FutureTimeMutator            # noqa: F401
from mutator.ReverseTime import ReverseTimeMutator          # noqa: F401
from mutator.UnusualFiletype import UnusualFiletypeMutator  # noqa: F401
from checker.checker import NullChecker                     # noqa: F401

import consts

def list_test():
  # print only filenames of tests in DEFAULT_CONFIG_PATH
  print("\nAvailable Tests:\n----------------")
  for test in os.listdir(consts.DEFAULT_CONFIG_PATH):
    # check if file is a directory, since tests are generated as them
    if os.path.isdir(os.path.join(consts.DEFAULT_CONFIG_PATH, test)):
      print(test)

  print("")
  return 1
    
def pack_test(name, verbosity):
  # check for mandatory arguments (obsolete)
  #  man_options = ['name']
  #  for opt in man_options:
  #    if not args.__dict__[opt]:
  #      parser.print_help()
  #      sys.exit(1)

  # perform a rr pack on the test directory
  test_dir = consts.DEFAULT_CONFIG_PATH + name
  subprocess.Popen(["rr", "pack", test_dir])

  # zip up specified directory with zipf handle
  shutil.make_archive(name, 'zip', test_dir)

  print("Packed up trace and stored as {}".format(name + ".zip"))
  return 1

def analyze_test(tracename, checker, verbosity):
  # man_options = ['tracename']
  # for opt in man_options:
  #   if not args.__dict__[opt]:
  #     parser.print_help()
  #     sys.exit(1)
  pickle_file = consts.DEFAULT_CONFIG_PATH + "syscall_definitions.pickle"
  trace = Trace.Trace(tracename, pickle_file)
  checker = eval(checker)
  for i in trace.syscalls:
    checker.transition(i)
  print(checker.is_accepting())


def main():
  print("Obsolete")
  sys.exit(1)

if __name__ == '__main__':
  main()
