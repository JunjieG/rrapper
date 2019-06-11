"""
<Program Name>
  crashsim

<Started>
  June 2019

<Author>
  Junjie Ge

<Purpose>
  A shorter command aimed to replace rrtest and rreplay in order to improve user experience

"""

import os
import sys
import argparse
import subprocess
import logging
from rrtest import create_test, configure_test, list_test, pack_test, analyze_test 
from rreplay import call_replay

import consts

def main():
  # initialize parser
  parser = argparse.ArgumentParser()

  # setting necessary flags
  parser.add_argument('-c', '--command',
                               dest='command',
                               required=True,
                               help='specify command for rrtest')

  # general flags to be set
  parser.add_argument('-v', '--verbosity',
                      dest='verbosity',
                      action='store_const',
                      const=logging.debug,
                      help='flag for displaying debug information')

  # parse arguments
  args = parser.parse_args()

  # configure logger
  logging.basicConfig(level=args.verbosity)

  # finding a free file name
  index = 1
  test_dir = consts.DEFAULT_CONFIG_PATH + "autotest"
  while True:
    if os.path.isdir(test_dir + str(index) + "/"):
      index += 1
    else:
      break

  auto_dir = "autotest" +  str(index) + "/"

  # creating the test
  logging.debug("----------creating test----------")
  create_test(auto_dir, args.command, args.force, args.verbosity)

  # configuring the test
  logging.debug("----------configuring test----------")
  mutators = ["FutureTimeTest()", "ReverseTimeTest()", "NullMutator()",
          "CrossdiskRenameMutator()", "UnusualFiletypeMutator()"]

  # looping through mutators to apply each mutator to the application
  for mutator in mutators:
    configure_test(auto_dir, args.mutator, args.verbosity)

  
  # replay the test
  logging.debug("----------replaying test----------")
  call_replay(auto_dir, args.verbosity)

if __name__ == "__main__":
  main()
  sys.exit(0)
