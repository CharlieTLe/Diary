#!/usr/bin/env python

# Python script that makes timekeeping and note entry conveniently simple.
# Copyright (C) 2014 Charlie Thanh Le
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from time import localtime, strftime
from subprocess import call
import argparse, socket, datetime, re, os, cmd

'''
Copyright (C) 2014  Charlie Thanh Le
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
'''

class DiaryShell(cmd.Cmd):
  intro = 'Welcome to the Diary shell. Type help or ? to list commands.\n'
  prompt = '(Diary) >'

  def do_b(self, arg):
    'Append your diary with Begin [Timestamp] [Computer Name].'
    write_to_diary('b')
  def do_s(self, arg):
    'Append your diary with Stop [Timestamp] [Computer Name].'
    write_to_diary('s')
  def do_m(self, arg):
    'Append your diary with Mark [Timestamp] [Computer Name].'
    write_to_diary('m')
  def do_o(self, arg):
    'Open your diary in a text editor.'
    open_diary()
  def do_timerecord(self, arg):
    'Print out the past x number of days of Diary entries.'
    timerecord(arg)
  def do_q(self, arg):
    'Quit out of the Diary Shell.'

# sets diary file-name
def diary_file():
  diary_path = os.path.dirname(os.path.realpath(__file__))
  if os.name == "nt":
    diary_path += '\\'
  else:
    diary_path += "/" 
  return diary_path + strftime("%Y-%m-%d", localtime()) + ".txt"

# saves diary
def write_to_diary(command):
  with open(diary_file(), "a") as diary:
    # Append diary with a newline if content exists.
    entry = ""
    if diary.tell():
      entry = '\n'
    entry += actiondict[command]
    diary.write(entry + strftime("%H:%M:%S") + " " + socket.gethostname())

# opens diary
def open_diary():
  print "Opening diary:", diary_file()
  if os.name == "nt":
    os.system("start " + diary_file())
  else:
    os.system("open " + diary_file())

# records the time
def timerecord(days):
  mydate = datetime.date.today()
  pastdate = mydate + datetime.timedelta(days=-int(days))
  increment = datetime.timedelta(days=1)
  while pastdate <= mydate:
    diary_date_file = pastdate.strftime("%Y-%m-%d") + ".txt"
    print(diary_date_file)
    with open(diary_path + diary_date_file, "r") as diary:
      for line in diary:
        search = re.search(r"^(Begin )|^(Stop )|^(Mark )", line)
        if search:
          print(line)
    pastdate += increment

parser = argparse.ArgumentParser()
parser.add_argument('command', help="b: begin, s: stop, o: open, m: mark, c: cmd")
parser.add_argument('--open', action="store_true", help="Opens the file.")
parser.add_argument('--time-record', action="store_true", help="Print diary-records.")
args = parser.parse_args()

actiondict = {'b': "Begin ", 's': "Stop ", 'm': "Mark "}

if args.open or args.command == "o":
  open_diary()
if args.command not in ['o', 'c']:
  write_to_diary(args.command)
if args.time_record:
  timerecord()
if args.command == 'c':
  DiaryShell().cmdloop()