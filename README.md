Diary
=====

Diary is a Python script that makes timekeeping and note entry conveniently simple.

Installation
---

Run `install.sh`

How To Use It
---

```sh
usage: diary [-h] [--config CONFIG_PATH] [--open] [--time-record]
             {create_config,version,help,b,s,o,m,c} ...

Appends time stamps to a text file named after the current day.

positional arguments:
  {create_config,version,help,b,s,o,m,c}
                        Sub commands
    create_config       Generate default configuration file
    version             Displays the version number
    help                Displays full help message
    b                   Begin
    s                   Stop
    o                   Open
    m                   Mark
    c                   Command

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG_PATH, -c CONFIG_PATH
                        path to diary configuration json
                        default: /Users/charliele/.diary.conf.json
  --open, -o            open file appending time stamp.
  --time-record, -t     print out two weeks of time stamps
```

Combine Diary with a file syncing service like iCloud to bring Diary with you
wherever you go.

Commands
-------

* `b` Appends to the end of the Diary "Begin [time stamp] [computer name]".
* `s` Appends to the end of the Diary "Stop [time stamp] [computer name]".
* `m` Appends to the end of the Diary  "[time stamp] [computer name]".
* `o` Opens the Diary.
* `c` Opens the command line version of Diary.
* `create_config` Creates a configuration file that holds editor preferences and the key for encrpyting/decrypting your diary.

Options
--------

* `--open`  Opens the file in the default text editor after executing the command.
* `--time-record` Prints out two weeks of time stamps relative to the current date.
* `--config` Override the default config path to load the configuration for diary.

Example
-------

Terminal

```sh
$ diary create_config
INFO [Diary]: Successfully created configuration file "/Users/charliele/.diary.conf.json"

$ diary --open b

Copyright (C) 2014  Charlie Thanh Le
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.

02-23 21:35 [Diary] {INFO}: decrypting diary "/Users/charliele/.diary/2017-02-23.txt"
02-23 21:35 [Diary] {INFO}: encrypting diary "/Users/charliele/.diary/2017-02-23.txt"
02-23 21:35 [Diary] {INFO}: decrypting diary "/Users/charliele/.diary/2017-02-23.txt"
02-23 21:35 [Diary] {INFO}: Opening diary: /Users/charliele/.diary/2017-02-23.txt

   -- You must completely close the application before this script will be able to continue --
```

The text editor of your choice will open editing.

After you close the process that edits the file...

```sh
02-23 21:35 [Diary] {INFO}: encrypting diary "/Users/charliele/.diary/2017-02-23.txt"
```

Breakdown
---

```sh
diary --open b
```

* configuration file is loaded with the editor and key to encrypt/decrypt the diary
* creates/loads text file for today
* appended `Begin 21:35:14 Charlies-MacBook-Pro.local` to the text file.
* opened the text file for editing

Contributing
---

All are welcomed to edit the source, create issues, and report bugs.

License
--------

GPL v2.0

Author
---

Charlie Le ([@charlietle](https://twitter.com/charlietle))
