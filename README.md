Diary
=====

Diary is a Python script that makes timekeeping and note entry conveniently simple.

How To Use It:
--

Invoke diary.py in a terminal followed by a command with an optional argument. See the example
for a better understanding of Diary.  

Combine Diary with a file syncing service like Dropbox to bring Diary with you
wherever you go.

Commands:
--

 - `b` Appends to the end of the Diary "Begin [time stamp] [computer name]".
 - `s` Appends to the end of the Diary "Stop [time stamp] [computer name]".
 - `m` Appends to the end of the Diary  "[time stamp] [computer name]".
 - `o` Opens the Diary.
 - `c` Opens the command line version of Diary.

Options:
--------

 - `--open`  Opens the file in the default text editor after executing the command.
 - `--time-record` Prints out two weeks of time stamps relative to the current date.

Example:
-------

###Terminal

```sh
Diary$ diary b --open

Copyright (C) 2014  Charlie Thanh Le
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.

('Current Local Time:', '2014-08-04')
('Opening diary:', '/Users/charlie/Dropbox/Diary/2014-08-04.txt')
Diary$ 
```

###Text Editor


>Begin 22:27:29 521-CartA.local


###What just happened?
```sh
diary b --open
```
- created a text file with the name of the current date in the same location as the diary.py file.
- appended `Begin 22:27:29 521-CartA.local` to the text file.
- opened the text file for editing.

#Contributing
All are welcomed to edit the source, create issues, and report bugs.

License:
--------
GPL v2.0

Author:
---
Charlie Le ([@charlietle](https://twitter.com/charlietle))
