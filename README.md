# MBAACC Replay Organizer

A simple script that gives your MBAACC replays more descriptive names. Versions in Python 3 and Perl are available.

Turns this...

```
ReplayVS/
├── AKIHA_SxAOKO_240510124159.rep
├── AKIHA_SxAOKO_240510124334.rep
├── AKIHA_SxAOKO_240510124451.rep
├── AKIHA_SxAOKO_240510125515.rep
├── AKIHA_SxNANAYA_240510105121.rep
├── AKIHA_SxNANAYA_240510105255.rep
└── ...
```

Into this...

```
("s" is each player's score)
ReplayVS/
└── organized/
    ├── Alice/
    │   │   date and time (24h) nick1   char1     s nick2 char2    s
    │   ├── 2024-05-09-12-25-35,wehrlia,C-S.Akiha,0,Alice,C-Nanaya,2.rep
    │   ├── 2024-05-09-12-25-35,wehrlia,C-S.Akiha,0,Alice,C-Nanaya,2.rep
    │   ├── 2024-07-29-13-27-03,wehrlia,C-S.Akiha,1,Alice,C-Nanaya,2.rep
    │   └── ...
    ├── Bob/
    │   ├── 2024-02-08-11-06-00,wehrlia,C-S.Akiha,2,Bob,C-Nero,0.rep
    │   ├── 2024-03-08-15-07-56,wehrlia,C-S.Akiha,2,Bob,C-Nero,1.rep
    │   ├── 2024-03-09-17-09-20,wehrlia,C-S.Akiha,2,Bob,C-Nero,1.rep
    │   └── ...
    ├── Jane/
    │   ├── 2024-04-10-10-41-58,wehrlia,C-S.Akiha,1,Jane,F-Aoko,2.rep
    │   └── 2024-05-01-19-43-33,wehrlia,C-S.Akiha,0,Jane,F-Aoko,2.rep
    ├── John/
    │   └── 2024-01-20-11-10-59,wehrlia,C-S.Akiha,0,John,F-P.Ciel,2.rep
    └── localP1/ (local matches)
        └── 2023-12-23-18-04-51,localP2,C-S.Akiha,2,localP1,C-Nero,0.rep
```

DISCLAIMER: THIS SCRIPT WILL MOVE YOUR REPLAY FILES AROUND, AND GIVE THEM NEW NAMES. IF THAT CONCERNS YOU, BACKUP YOUR REPLAYS BEFORE RUNNING THIS SCRIPT. PLEASE. YOU HAVE BEEN WARNED.

## Requirements

- Either Perl version 5.10 or later (if using the Perl version), or Python 3.x (if using the Python version).
- CCCaster v3.1

## Caveats

- Will probably not be very useful for replays of local matches, since the nicknames of each player will be "localP2" and "localP1".
- These scripts have so far only been tested on a Linux system. If something doesn't work and you're on a different OS, either open an issue or contact me via Discord (@wehrlia).

## Installation and usage

The replay files must be located inside the `ReplayVS` folder, and your `results.csv` file must be in the same folder as the script. None of the files should be modified in any way. If any of those conditions aren't met, the script will print an error message and exit, without modifying anything.

### Windows

Copy `organizer.bat` and one of the scripts to your MBAACC installation folder, then run `organizer.bat`.

Note that `organizer.bat` hasn't been actually tested (yet), since I don't have access to a Windows system. Again, make a backup before running it, and let me know how it went.

### Linux, \*BSD, or MacOS

Copy one of the scripts to your MBAACC installation folder, then run it from your terminal:

```bash
$ cd path/to/MBAACC/
$ perl rep-organizer.pl
```

or

```bash
$ cd path/to/MBAACC/
$ python3 rep-organizer.py
```

## Perl or Python?

In a nutshell, both versions do the exact same thing. Pick whichever you prefer.

This script was originally written in Perl, but after considering the fact that Python is a little easier to setup on Windows compared to (Strawberry) Perl, I rewrote it in Python. I personally prefer the Perl version, since that's my preferred language for this kind of stuff.

## Licensing

This is public domain software. No warranty, provided "as is", etc. Do whatever you want with it. Giving credit is not mandatory, but appreciated.
