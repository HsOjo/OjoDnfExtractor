import argparse
import sys

from app import Application

parser = argparse.ArgumentParser()
parser.add_argument('files', metavar='file', nargs='*')
args = parser.parse_args()

sys.exit(Application(args).start())
