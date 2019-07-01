#!/usr/bin/env python2.7
# pylint: disable=missing-docstring, bad-indentation, too-many-locals
"""
<Program Name>
  configure_test

<Started>
  July 2019

<Author>
  Alan Cao, Junjie Ge

<Purpose>
  Using given mutators, configures the specified test. Writes all opporunities
  found in the ~/.crashsim/<test_name>/config.ini file
"""

import os
import re
import logging
import ConfigParser

from posix_omni_parser import Trace
from mutator.Null import NullMutator                        # noqa: F401
from mutator.CrossdiskRename import CrossdiskRenameMutator  # noqa: F401
from mutator.FutureTime import FutureTimeMutator            # noqa: F401
from mutator.ReverseTime import ReverseTimeMutator          # noqa: F401
from mutator.UnusualFiletype import UnusualFiletypeMutator  # noqa: F401
from checker.checker import NullChecker                     # noqa: F401

import consts

def configure_test(name, mutator, verbosity, trace_line=0, sniplen=5):
    # The configure command requires a name be specified (obsolete)
    # man_options = ['name']
    # for opt in man_options:
    #   if not args.__dict__[opt]:
    #     parser.print_help()
    #     sys.exit(1)

    # if we specify a mutator, we cannot specify a traceline
    if mutator and trace_line:
        print("You must not specifiy a trace line when you have specified a mutator.")
        return 0

    # check if config file exists
    test_dir = consts.DEFAULT_CONFIG_PATH + name + "/"
    if not os.path.exists(test_dir):
      print("Test '{}' does not exist. Create before attempting to configure!" \
              .format(name))
      return 0

    # read config file for rr test directory
    config = ConfigParser.ConfigParser()
    config.read(test_dir + "config.ini")
    testname = config.get("rr_recording", "rr_dir")

    # open trace file for reading
    with open(test_dir + consts.STRACE_DEFAULT, 'r') as trace_file:
      trace_lines = trace_file.readlines()

   # strip and breakdown pid
    pid = trace_lines[0].split()[0]

    if mutator:
      #config.set("request_handling_process", "mutator", args.mutator)
      # use the mutator to identify the line we are interested in
      identify_mutator = eval(mutator)
      pickle_file = consts.DEFAULT_CONFIG_PATH + 'syscall_definitions.pickle'
      syscalls = Trace.Trace(test_dir + consts.STRACE_DEFAULT, pickle_file).syscalls

      # ignore syscalls before the 'syscall_xxx()' marker
      for i in range(len(syscalls)):
        if 'syscall_' in syscalls[i].name:
          break

      off_set = i
      syscalls=syscalls[i:]

      lines = identify_mutator.identify_lines(syscalls)
      for i in range(len(lines)):
        lines[i] += off_set

      lines_count = len(lines)

      if (lines_count == 0):
        print("{} did not find any simulation opportunities."
              .format(mutator))
        return 1

      sections = config.sections()
      mutator_flag = len(sections) - 1 
      print(mutator_flag) 

      for j in range(lines_count):
        config.add_section("request_handling_process"+str(j + mutator_flag))
        config.set("request_handling_process"+str(j + mutator_flag), "event", None)
        config.set("request_handling_process"+str(j + mutator_flag), "pid", None)
        config.set("request_handling_process"+str(j + mutator_flag), "trace_file", test_dir + consts.STRACE_DEFAULT)
        config.set("request_handling_process"+str(j + mutator_flag), "trace_start", 0)
        config.set("request_handling_process"+str(j + mutator_flag), "trace_end", 0)

        identified_syscall_list_index = lines[j]

        config.set("request_handling_process"+str(j + mutator_flag), "mutator", mutator)

        # we must multiply by 2 here because the mutator is looking at a list
        # of parsed system call objects NOT the trace file itself.  This means
        # index A in the list of system calls corresponds with line number (A * 2)
        # in the trace file because including the rr event lines (which, again,
        # are NOT present in the list of system call objects) DOUBLES the number
        # of lines in the file
        identified_trace_file_index = identified_syscall_list_index * 2
        identified_trace_line = trace_lines[identified_trace_file_index]


        event_line = trace_lines[(identified_trace_file_index) - 1]
        user_event = int(event_line.split('+++ ')[1].split(' +++')[0])
        # now we must generate a new trace snippet that will be used to drive the test.
        # This snip will be sniplen (default 5) system calls in length and will have
        # the rr event number lines from the main recording STRIPPED OUT.
        lines_written = 0

        with open(test_dir + "trace_snip"+str(j + mutator_flag)+".strace", 'wb') as snip_file:
          for i in range(0, sniplen * 2, 2):
            try:
              snip_file.write(trace_lines[identified_trace_file_index + i])
              lines_written += 1
            except IndexError:
              break

        config.set("request_handling_process"+str(j + mutator_flag), "trace_file", test_dir + "trace_snip"+str(j + mutator_flag) + ".strace")
        config.set("request_handling_process"+str(j + mutator_flag), "event", user_event)
        config.set("request_handling_process"+str(j + mutator_flag), "pid", pid)
        config.set("request_handling_process"+str(j + mutator_flag), "trace_end", lines_written)

        # write final changes to config file
        with open(test_dir + "config.ini", 'w+') as config_file:
          config.write(config_file)
      return 1

    if trace_line:
      # offset by -1 because line numbers start counting from 1
      config.add_section("request_handling_process")
      config.set("request_handling_process", "event", None)
      config.set("request_handling_process", "pid", None)
      config.set("request_handling_process", "trace_file", test_dir + consts.STRACE_DEFAULT)
      config.set("request_handling_process", "trace_start", 0)
      config.set("request_handling_process", "trace_end", 0)

      identified_trace_file_index = int(trace_line - 1)
      identified_trace_line = trace_lines[identified_trace_file_index]
      if re.match(r'[0-9]+\s+\+\+\+\s+[0-9]+\s+\+\+\+', identified_trace_line):
        print('It seems like you have chosen a line containing an rr event '
              'number rather than a line containing a system call.  You '
              'must select a line containing a system call')
        return 0

      event_line = trace_lines[(identified_trace_file_index) - 1]
      user_event = int(event_line.split('+++ ')[1].split(' +++')[0])

      lines_written = 0
      with open(test_dir + "trace_snip.strace", 'wb') as snip_file:
        for i in range(0, sniplen * 2, 2):
          try:
            snip_file.write(trace_lines[identified_trace_file_index + i])
            lines_written += 1
          except IndexError:
            break

      config.set("request_handling_process", "trace_file", test_dir + "trace_snip.strace")
      config.set("request_handling_process", "event", user_event)
      config.set("request_handling_process", "pid", pid)
      config.set("request_handling_process", "trace_end", lines_written)
      # write final changes to config file
      with open(test_dir + "config.ini", 'w+') as config_file:
        config.write(config_file)
    # We want the event JUST BEFORE our chosen system call so we must go
    # back 2 lines from the chosen trace line
      return 1

