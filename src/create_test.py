#!/usr/bin/env python2.7
# pylint: disable=missing-docstring, bad-indentation, too-many-locals
"""
<Program Name>
  create_test

<Started>
  July 2019

<Author>
  Alan Cao, Junjie Ge

<Purpose>
  Creates and initializes the test in ~/.crashsim/test_folder 

"""

from __future__ import print_function

import os
import subprocess
import re
import logging
import shutil
import ConfigParser
import errno

from mutator.Null import NullMutator                        # noqa: F401
from mutator.CrossdiskRename import CrossdiskRenameMutator  # noqa: F401
from mutator.FutureTime import FutureTimeMutator            # noqa: F401
from mutator.ReverseTime import ReverseTimeMutator          # noqa: F401
from mutator.UnusualFiletype import UnusualFiletypeMutator  # noqa: F401
from checker.checker import NullChecker                     # noqa: F401

import consts

def rr_copy(src, dest):
  """
  <Purpose>
    Utilizes shutil's high-level copytree method in order
    to copy any filetype (including dirs) from one destination
    to another. It also ensures that ENOTDIR is handled properly by
    attempting a regular copy.

  <Returns>
    None

  """

  try:
    # check if path is a directory
    if os.path.isdir(src):
      for item in os.listdir(src):
        s_file = os.path.join(src, item)
        d_file = os.path.join(dest, item)
        if os.path.isdir(s_file):
          shutil.copytree(s_file, d_file)
        else:
          shutil.copy2(s_file, d_file)

    # otherwise copy the filetype normally
    else:
      shutil.copytree(src, dest)
  except OSError as exc:
    if exc.errno == errno.ENOTDIR:
      shutil.copy(src, dest)
    else:
      raise

def create_test(name, command, force, verbosity):
  # check for mandatory arguments (obsolete)
  #man_options = ['name', 'command']
  #for opt in man_options:
  #  if not args.__dict__[opt]:
  #    parser.print_help()
  #    sys.exit(1)

  # initialize test directory in ~/.crashsim/xxxxx
  test_dir = consts.DEFAULT_CONFIG_PATH + name + "/"
  if os.path.isdir(test_dir) and force != 'YES':
    print('A test with path {} already exists'.format(test_dir))
    return 0
  elif os.path.isdir(test_dir) and force == 'YES':
    logging.debug('Overwriting %s', test_dir)
    shutil.rmtree(test_dir)

  os.makedirs(test_dir)

  # call rr to record the command passed, store results within test directory
  # subprocess.call with shell=True is used, such that shell command formatting is
  # preserved. TODO: improve, if necessary.
  rr_create_record = ['rr', 'record', '-n', '-q', command]
  ret = subprocess.call(" ".join(rr_create_record), shell=True)
  if ret != 0:
    print('`rr record` failed [exit status: {}]'.format(ret))
    return 0

  # retrieve latest trace through latest-trace linked file
  testname = os.path.realpath(consts.RR_TEST_CONFIG_PATH + "latest-trace")

  # copy rr recorded test into our own directory
  rr_copy(testname, test_dir)

  # copy rr produced strace into our own directory
  rr_copy(consts.STRACE_DEFAULT, test_dir + consts.STRACE_DEFAULT)

  # remove the exit call and the counter for the exit call
  with open(test_dir + consts.STRACE_DEFAULT, "r") as fh:
    lines = fh.readlines()
    lines = lines[:-2]
    lines[-1] = lines[-1][:-1] # removse the \n from the end of last line

  with open(test_dir + consts.STRACE_DEFAULT, "w") as fh:
    fh.writelines(lines)

  # create INI config file
  config = ConfigParser.ConfigParser()
  config.add_section("rr_recording")
  config.set("rr_recording", "rr_dir", test_dir)

  # write config file
  with open(test_dir + "config.ini", 'wb') as config_file:
    config.write(config_file)

  # output trace to STDOUT for user to determine proper trace line
  with open(test_dir + consts.STRACE_DEFAULT, 'r') as trace:
    lineno=0
    line='<init>'
    last_endchar = '\n'
    while True:
      line = trace.readline()
      line = re.sub(r'^[0-9]+\s+', '', line)
      if len(line) == 0:
        # append a newline at the end of output
        print('')
        break
      lineno += 1
      if last_endchar == '\n':
        endchar = ''
      print('LINE ' + str(lineno) + ': ' + line, end=endchar)
      last_endchar = line[-1]
  return 1
