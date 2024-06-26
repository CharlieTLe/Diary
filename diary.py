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
__version__ = '0.1.2'

actiondict = {'b': "Begin ", 's': "Stop ", 'm': "Mark "}
actionregex = '' + '|'.join([v for k, v in actiondict.items()])

fs_delim = '/'
if os.name == 'nt':
    fs_delim = '\\'

logging.getLogger().setLevel(logging.INFO)
logging.getLogger().name = __app_name__
logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s')

logger = logging.getLogger()

default_config = {
    'key': Fernet.generate_key(),
    'editor_path': '/usr/bin/open',
    'editor_args': ['-W', '--new'],
    'timestamp_format': '%H:%M:%S',
    'diary_base': '{}/.diary'.format(os.environ['HOME'])
}

# Global cipher suite
cipher_suite = None


class DiaryShell(cmd.Cmd):
    intro = 'Welcome to the Diary shell. Type help or ? to list commands.\n'
    prompt = '(Diary) > '

    def __init__(self, config):
        cmd.Cmd.__init__(self)

        self.config = config

    def do_b(self, arg):
        """Append your diary with Begin [Timestamp] [Computer Name]."""
        write_to_diary(self.config, 'b')

    def do_s(self, arg):
        """Append your diary with Stop [Timestamp] [Computer Name]."""
        write_to_diary(self.config, 's')

    def do_m(self, arg):
        """Append your diary with Mark [Timestamp] [Computer Name]."""
        write_to_diary(self.config, 'm')

    def do_o(self, arg):
        """Open your diary in a text editor."""

        # Seems to pass in empty string if no arg was passed in.
        if len(arg):
            open_diary(self.config, arg)
        else:
            open_diary(self.config, 0)

    def do_timestamps(self, arg):
        """Print out the past x number of days of Diary entries."""
        if arg:
            timestamps(self.config, days=int(arg))
        else:
            timestamps(self.config)

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

    logger.debug('decrypting diary "{}"'.format(filename))
    try:
        with open(filename, 'r') as f:
            raw = f.read()

        if raw:
            decrypted = decrypt_string(config, raw)
            if decrypted:
                with open(filename, 'w') as f:
                    f.writelines(decrypted)

    except IOError as e:
        logger.critical('Failed to decrypt diary file {}: {}'.format(filename, e))


def encrypt_diary(config, filename):
    """
    Encrypt a diary file in-place
    """

    logger.debug('encrypting diary "{}"'.format(filename))
    try:
        with open(filename, 'r') as f:
            raw = f.read()

        if raw:
            encrypted = encrypt_string(config, raw)
            if encrypted:
                with open(filename, 'w') as f:
                    f.writelines(encrypted)

    except IOError as e:
        logger.critical('Failed to encrypt diary file {}: {}'.format(filename, e))


def diary_file(config, deltadays=0):

    diary_date = datetime.today() + timedelta(days=-int(deltadays))
    return '{}{}{}.txt'.format(config['diary_base'], fs_delim, diary_date.strftime('%Y-%m-%d'))


def write_to_diary(config, command):

    filename = diary_file(config)

    if os.path.isfile(filename):
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
        logger.debug("Canceled, hopefully you've saved your changes!")

    encrypt_diary(config, filename)


def bye():
    logger.info('Diary is exiting...')


def timestamps(config, days=14):
    """
    Prints out lines beginning with action words in the last x amount of days
    :param config:
    :param days: number of days to print lines for
    :return:
    """
    last_diary_file = None
    for days_ago in range(days, -1, -1):
        try:
            filename = diary_file(config, deltadays=days_ago)
            with open(filename, "r") as diary:
                if last_diary_file:
                    logger.warning("Diary entries between {} through {} could not be found.".format(last_diary_file, filename.split(fs_delim)[-1]))
                    last_diary_file = None

                decrypt_diary(config, filename)

                for line in diary:
                    if re.search(actionregex, line):
                        logger.info("{}: {}".format(filename.split(fs_delim)[-1], line))

                encrypt_diary(config, filename)

        except IOError as e:
            last_diary_file = filename.split(fs_delim)[-1]
            pass


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
        if os.path.exists(config_path):
            logger.warning('Another config exists at: "{}"'.format(config_path)) 
            return False

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
    parser = argparse.ArgumentParser(description="Appends time stamps to a text file named after the current day.", 
                                     formatter_class=argparse.RawTextHelpFormatter)

    default_config_path = os.environ['HOME'] + '/.diary.conf.json'
    parser.add_argument('--config', '-c', dest='config_path', type=str, default=default_config_path,
            help='path to diary configuration json\ndefault: {}'.format(default_config_path))

    parser.add_argument('--open', '-o', action="store_true", help="open file appending time stamp.")

    commands_parser = parser.add_subparsers(dest='command', help='Sub commands')

    commands_parser.add_parser('create_config', help='Generate default configuration file')
    commands_parser.add_parser('version', help='Displays the version number')
    commands_parser.add_parser('help', help='Displays full help message')

    commands_parser.add_parser('b', help='Appends Begin and the timestamp to the EOF')
    commands_parser.add_parser('s', help='Appends Stop and the timestamp to the EOF')
    commands_parser.add_parser('m', help='Appends Mark and the timestamp to the EOF')

    commands_parser.add_parser('o',  help="Opens today's diary for editing")
    commands_parser.add_parser('c', help='Open up the cli version of Diary')

    timestamps_parser = commands_parser.add_parser('timestamps', help='Prints out timestamps from the previous diary entries')
    timestamps_parser.add_argument('since_days_ago', nargs='?', default=14, help='How many days ago since the present to print timestamps from.')

    return parser, parser.parse_args()


def main():
    """
    Main application entry point
    """

    parser, args= get_args()

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

    if args.command in actiondict.keys():
        write_to_diary(config, args.command)

    if args.open is True or args.command == "o":
        open_diary(config)

    if args.command == 'timestamps':
        timestamps(config, int(args.since_days_ago))

    if args.command == 'c':
        try:
            DiaryShell(config).cmdloop()
        except KeyboardInterrupt:
            bye()

if __name__ == '__main__':
    main()
