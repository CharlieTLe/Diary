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

import argparse
import cmd
import datetime
import json
import logging
import os
import sys
import re
import socket

from subprocess import Popen
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, InvalidToken

__app_name__ = 'Diary'
__version__ = '0.1.0'

actiondict = {'b': "Begin ", 's': "Stop ", 'm': "Mark "}

logging.getLogger().setLevel(logging.INFO)
logging.getLogger().name = __app_name__
logging.basicConfig(format='%(asctime)s [%(name)s] {%(levelname)s}: %(message)s', datefmt='%m-%d %H:%M')

logger = logging.getLogger()

default_config = {
    'key': Fernet.generate_key(),
    'editor_path': '/usr/bin/open',
    'editor_args': ['-W', '--new'],
    'timestamp_format': '%H:%M:%S',
    'diary_base': '{}/.diary'.format(os.environ['HOME'])
}

print("""
Copyright (C) 2014  Charlie Thanh Le
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
""")


# Global cipher suite
cipher_suite = None


class DiaryShell(cmd.Cmd):

    def __init__(self, config):
        self.config = config

        self.intro = 'Welcome to the Diary shell.   Type help or ? to list commands.\n'
        self.prompt = '(Diary) >'

    def do_b(self):
        """Append your diary with Begin [Timestamp] [Computer Name]."""
        write_to_diary(self.config, 'b')

    def do_s(self):
        """Append your diary with Stop [Timestamp] [Computer Name]."""
        write_to_diary(self.config, 's')

    def do_m(self):
        """Append your diary with Mark [Timestamp] [Computer Name]."""
        write_to_diary(self.config, 'm')

    def do_o(self, arg):
        """Open your diary in a text editor."""

        # Seems to pass in empty string if no arg was passed in.
        if len(arg):
            open_diary(self.config, arg)
        else:
            open_diary(self.config, 0)

    @staticmethod
    def do_timerecord(arg):
        """Print out the past x number of days of Diary entries."""
        timerecord(arg)

    @staticmethod
    def do_q(arg):
        'Quit out of the Diary Shell.'
        bye()
        return True


def encrypt_string(config, val):
    """
    Using the key from the configuration, encrypt the given string
    :param config:
    :param val:
    :return:
    """
    global cipher_suite
    if not cipher_suite:
        cipher_suite = Fernet(config['key'].encode('utf8'))

    return cipher_suite.encrypt(val)


def decrypt_string(config, val):
    """
    Using the key from the configuration, decrypt an encrypted string
    :param config:
    :param val:
    :return:
    """
    global cipher_suite
    if not cipher_suite:
        cipher_suite = Fernet(config['key'].encode('utf8'))

    try:
        return cipher_suite.decrypt(val)
    except InvalidToken as e:
        logger.warn('Failed to decrypt, perhaps it was not encrypted to begin with? {}'.format(e))


def decrypt_diary(config, filename):
    """
    Decrypt a diary file in-place
    """

    logger.info('decrypting diary "{}"'.format(filename))
    try:
        with open(filename, 'r') as f:
            raw = '\n'.join(f.readlines())
            f.close()

            decrypted = decrypt_string(config, raw)
            if decrypted:
                f = open(filename, 'w')
                f.writelines(decrypted)
                f.close()

    except IOError as e:
        logger.critical('Failed to decrypt diary file {}: {}'.format(filename, e))


def encrypt_diary(config, filename):
    """
    Encrypt a diary file in-place
    """

    logger.info('encrypting diary "{}"'.format(filename))
    try:
        with open(filename, 'r') as f:
            raw = '\n'.join(f.readlines())
            f.close()

            encrypted = encrypt_string(config, raw)
            if encrypted:
                f = open(filename, 'w')
                f.writelines(encrypted)
                f.close()

    except IOError as e:
        logger.critical('Failed to encrypt diary file {}: {}'.format(filename, e))


def diary_file(config, deltadays=0):
    # diary_path = os.path.dirname(os.path.realpath(__file__))

    fs_delim = '/'
    if os.name == 'nt':
        fs_delim = '\\'

    diary_date = datetime.today() + timedelta(days=-int(deltadays))
    return '{}{}{}.txt'.format(config['diary_base'], fs_delim, diary_date.strftime('%Y-%m-%d'))


def write_to_diary(config, command):

    filename = diary_file(config)

    # First, decrypt it
    decrypt_diary(config, filename)

    try:
        with open(filename, mode='a') as diary:
            # Append diary with a newline if content exists.
            entry = ''
            if diary.tell() is not 0:
                entry = '\n'

            entry += actiondict[command]
            diary.write('{}{} {}\n'.format(entry, datetime.today().strftime(config['timestamp_format']), socket.gethostname()))

            diary.close()

            # Now, encrypt it
            encrypt_diary(config, filename)

    except IOError as e:
        logger.critical('Failed to open diary file "{}": {}'.format(filename, e))
        sys.exit(1)


def open_diary(config, deltadays=0):

    filename = diary_file(config, deltadays)
    if not os.path.isfile(filename):
        open(filename, 'a').close()

    # decrypt it
    decrypt_diary(config, filename)

    logger.info('Opening diary: {}'.format(filename))
    print('\n\t -- You must completely close the application before this script will be able to continue --\n'),

    args = [config['editor_path']] + config['editor_args'] + [filename]
    try:
        Popen(args).wait()

    except KeyboardInterrupt:
        logger.info("Canceled, hopefully you've saved your changes!")

    encrypt_diary(config, filename)


def bye():
    logger.info('Diary is exiting...')


def timerecord(days=14):
    mydate = datetime.today()
    pastdate = mydate + timedelta(days=-int(days))
    increment = timedelta(days=1)

    while pastdate <= mydate:
        try:
            diary_date_file = '{}.txt'.format(pastdate.strftime('%Y-%m-%d'))
            logger.info('Diary filename: {}'.format(diary_date_file))

            with open(diary_date_file + diary_date_file, "r") as diary:
                for line in diary:
                    search = re.search(r"^(Begin )|^(Stop )|^(Mark )", line)
                    if search:
                        print(line)

        except IOError as e:
            logger.critical('Failed to open diary file: {}'.format(e))
            sys.exit(1)

        pastdate = pastdate + increment


def ensure_base_path(config):
    """
    Ensures the base path for saving diary files exists
    :param config:
    :return:
    """

    if not os.path.exists(config['diary_base']):
        try:
            os.makedirs(config['diary_base'], mode=0o700)
        except OSError as e:
            logger.critical('Failed to create diary base directory "{}": {}'.format(config['diary_base'], e))


def create_config(config_path):
    """
    Generates and saves a default configuration json file
    """

    perms = 0o600

    try:
        with open(config_path, mode='w') as f:
            f.writelines(json.dumps(default_config, indent=4))
            f.close()
            os.chmod(config_path, perms)

    except IOError as e:
        logger.critical('Failed to save configuration file "{}": {}'.format(config_path, e))
        sys.exit(1)

    except OSError as e:
        logger.critical('Failed to set file permissions on configuration file "{}": {}'.format(config_path, e))
        sys.exit(1)

    logger.info('Successfully created configuration file "{}"'.format(config_path))

    return True


def get_config(config_path):
    if not config_path or not os.path.exists(config_path):

        example_conf = json.dumps(default_config, indent=4)

        logger.critical('Configuration file missing, please create one ("{}")\n'.format(config_path))
        print('Example configuration:\n{}\nYou may also run with the "create_config" option to generate one\n'
              .format(example_conf))

        sys.exit(1)

    try:
        with open(config_path, 'r') as f:
            config = json.loads(''.join(f.readlines()))
            f.close()

    except IOError as e:
        logger.critical('Failed to open configuration file "{}": {}'.format(config_path, e))
        sys.exit(1)

    except ValueError as e:
        logger.critical('Failed to parse configuration file "{}": {}'.format(config_path, e))
        sys.exit(1)

    # Must have the following values
    for field in ['key', 'editor_path', 'timestamp_format', 'diary_base']:
        if field not in config:
            logger.critical('Configuration value "{}" missing from {}'.format(field, config_path))
            sys.exit(1)

    return config


def get_args():
    parser = argparse.ArgumentParser(description="Appends time stamps to a text file named after the current day.")

    default_config_path = os.environ['HOME'] + '/.diary.conf.json'
    parser.add_argument('--config', '-c', dest='config_path', type=str, default=default_config_path,
                        help='path to diary configuration json')

    parser.add_argument('--open', '-o', action="store_true", help="open file appending time stamp.")
    parser.add_argument('--time-record', '-t', action="store_true", help="print out two weeks of time stamps")

    commands_parser = parser.add_subparsers(dest='command', help='Sub commands')

    commands_parser.add_parser('create_config', help='Generate default configuration file')
    commands_parser.add_parser('version', help='Displays the version number')
    commands_parser.add_parser('help', help='Displays full help message')
    commands_parser.add_parser('b', help='Begin')
    commands_parser.add_parser('s', help='Stop')
    commands_parser.add_parser('o',  help='Open')
    commands_parser.add_parser('m', help='Mark')
    commands_parser.add_parser('c', help='Command')

    return parser, parser.parse_args()


def main():
    """
    Main application entry point
    """

    parser, args = get_args()

    if args.command == 'help':
        parser.print_help()
        return

    if args.command == 'version':
        print('{}: Version {}'.format(__app_name__, __version__))

    # General configuration file
    if args.command == 'create_config':
        create_config(args.config_path)
        return

    config = get_config(args.config_path)

    # ensure base path exists
    ensure_base_path(config)

    if args.command not in ['o', 'c']:
        write_to_diary(config, args.command)

    if args.open is True or args.command == "o":
        open_diary(config)

    if args.time_record is True:
        timerecord()

    if args.command == 'c':
        try:
            DiaryShell(config).cmdloop()
        except KeyboardInterrupt:
            bye()

if __name__ == '__main__':
    main()