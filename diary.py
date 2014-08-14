#!/usr/bin/env python

# Python script that makes timekeeping and note entry conveniently simple.
# Copyright (C) 2014  Charlie Thanh Le
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

print("""
Copyright (C) 2014  Charlie Thanh Le
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
""")

class DiaryShell(cmd.Cmd):
    intro = 'Welcome to the Diary shell.   Type help or ? to list commands.\n'
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
        bye()
        return True

parser = argparse.ArgumentParser(description="Appends time stamps to a text file named after the current day.")
parser.add_argument('command', help="b to begin, s to stop, o to open, m to mark, c to cmd")
parser.add_argument('--open', action="store_true", help="open file appending time stamp.")
parser.add_argument('--time-record', action="store_true", help="print out two weeks of time stamps")
args = parser.parse_args()

def diary_file():
    diary_path = os.path.dirname(os.path.realpath(__file__))

    if os.name == "nt":
        diary_path += '\\'
    else:
        diary_path += "/"
        
    return diary_path + strftime("%Y-%m-%d", localtime()) + ".txt"

actiondict = {'b': "Begin ", 's': "Stop ", 'm': "Mark "}

def write_to_diary(command):
    with open(diary_file(), "a") as diary:

      # Append diary with a newline if content exists.
      entry = ""
      if diary.tell() is not 0:
          entry = '\n'

      entry += actiondict[command]
      diary.write(entry + strftime("%H:%M:%S") + " " + socket.gethostname())

def open_diary():
    print ("Opening diary:", diary_file())

    if os.name == "nt":
        os.system("start " + diary_file())
    else:
        os.system("open " + diary_file())

def bye():
    print("Diary is exiting...")

if args.command not in ['o', 'c']:
    write_to_diary(args.command)
	
if args.open == True or args.command == "o":
    open_diary()

def timerecord(days=14):
    mydate = datetime.date.today()
    pastdate = mydate + datetime.timedelta(days=-int(days))
    increment = datetime.timedelta(days=1)

    while pastdate <= mydate:
        try:
          diary_date_file = pastdate.strftime("%Y-%m-%d") + ".txt"
          print(diary_date_file)

          with open(diary_path + diary_date_file, "r") as diary:
            for line in diary:
              search = re.search(r"^(Begin )|^(Stop )|^(Mark )", line)
              if search:
                  print(line)
        except IOError as e:
          pass

        pastdate = pastdate + increment

if args.time_record == True:
    timerecord()

if args.command == 'c':
    try:
        DiaryShell().cmdloop()
    except KeyboardInterrupt:
        bye()