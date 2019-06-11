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
  proc_create = subprocess.Popen(["rrtest", "create", "--name", auto_dir,
      "--command", args.command])
  proc_create.wait()

  logging.debug("Checking if rrtest create is successfull")
  if proc_create.returncode != 0:
    sys.exit(1)

  # configuring the test

  # mutators is a list of mutators that is automatically applied to the
  # application
  mutators = ["FutureTimeTest()", "ReverseTimeTest()", "NullMutator()",
          "CrossdiskRenameMutator()", "UnusualFiletypeMutator()"]

  # looping through mutators to apply each mutator to the application
  for mutator in mutators:
    proc_configure = subprocess.Popen(["rrtest", "configure", "--name",
        args.cmd, "--mutator", mutator]) 
    proc_configure.wait()

    logging.debug("Checking if rrtest configure is successfull")
    if proc_configure.returncode != 0:
      logging.debug("Mutator %s failed to configure", mutator)
      sys.exit(1)
  
  # replay the test
  proc_replay = subprocess.Popen(["rreplay", args.cmd])
  proc_replay.wait()

  logging.debug("Checking if rreplay is successfull")
  if proc_replay.returncode != 0:
    sys.exit(1)

if __name__ == "__main__":
  main()
