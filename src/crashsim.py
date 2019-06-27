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

import sys
import argparse
import subprocess
import logging
import os

from rrtest import create_test, configure_test, list_test, pack_test, analyze_test 
from rreplay import call_replay

import consts

def main():
  # initialize parser
  parser = argparse.ArgumentParser(
          formatter_class=argparse.RawDescriptionHelpFormatter,
          description=('''
  _____               _      _____ _
 / ____|             | |    / ____(_)
| |     _ __ __ _ ___| |__ | (___  _ _ __ ___
| |    | '__/ _` / __| '_ \ \___ \| | '_ ` _ \\
| |____| | | (_| \__ \ | | |____) | | | | | | |
 \_____|_|  \__,_|___/_| |_|_____/|_|_| |_| |_|

                  '''))


  # general flags to be set
  parser.add_argument('-v', '--verbosity',
                      dest='verbosity',
                      action='store_const',
                      const=logging.debug,
                      help='flag for displaying debug information')
  
  parser.add_argument('-e', '--explain',
                      dest='explain',
                      nargs='+',
                      help='explain the reports in more detail')
  
  parser.add_argument('-d', '--debug',
                      dest='debug',
                      nargs='+',
                      help='lets the user to identify exactly where the bug is')

  parser.add_argument('-n', '--name',
                      dest='name',
                      help='optinal name for the test')

  parser.add_argument('-m', '--mutator',
                      dest='mutator',
                      nargs='+',
                      help='''define the mutator to be applied to the test, if
                      no mutator given then a default set will be run.''')

  parser.add_argument('-f', '--force',
                      dest='force',
                      default='YES',
                      help='force overwrite create of the test')

  # required app to run 
  parser.add_argument('myapp',
                      nargs='?',
                      default=None,
                      help='the application to be tested')

  try:
    sys.argv[1]
  except:
    parser.print_help()
    sys.exit(1)


  # parse arguments
  (args, remaining) = parser.parse_known_args()
  if remaining:
    remaining = ' '.join(remaining)
    args.myapp = args.myapp + ' ' + remaining

  # create an autogenerated name if no name given
  if args.name == None:
    index = 1
    test_dir = consts.DEFAULT_CONFIG_PATH + 'autotest'
    while True:
      if os.path.isdir(test_dir + str(index) + '/'):
        index += 1
      else:
        break
    args.name = 'autotest' + str(index) + '/'

  # Set of default mutators
  if args.mutator == None:
    args.mutator = ["ReverseTimeMutator()", "FutureTimeMutator()",
                    "UnusualFiletypeMutator()", "CrossdiskRenameMutator()", "NullMutator()"]
  
  print(args)
  # configure logger
  logging.basicConfig(level=args.verbosity)

  if args.explain == None and args.debug == None:
    # creating the test
    logging.debug("----------creating test----------")
    create_test(args.name, args.myapp, args.force, args.verbosity)


    # configuring the test
    logging.debug("----------configuring test----------")
    configure_test(args.name, args.mutator, args.verbosity)
    
    # replay the test
    logging.debug("----------replaying test----------")
    call_replay(args.name, args.verbosity)

if __name__ == "__main__":
  main()
  sys.exit(0)
