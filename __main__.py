import argparse

from controller.command import Command
from controller.gui import GUI

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', default='gui', choices=['gui', 'cmd'], help='the program run mode, default is gui.')
parser.add_argument('files', metavar='file', nargs='*')

args = parser.parse_args()
if args.mode == 'cmd':
    controller = Command()
elif args.mode == 'gui':
    controller = GUI()
else:
    raise Exception('Unknown mode.')

controller.start(args)
