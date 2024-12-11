#!/usr/bin/python3
# A simple script that gives your MBAACC replays more descriptive names.
#
# THIS SCRIPT WILL MOVE YOUR REPLAY FILES AROUND, AND GIVE THEM NEW NAMES. IF
# THAT CONCERNS YOU, MAKE A BACKUP BEFORE RUNNING THIS SCRIPT. PLEASE. YOU HAVE
# BEEN WARNED.
#
# I have written lots and lots of comments, so people not familiar with Python
# 3 can still understand what this script does, and why.

import glob # match a list of files with glob matching
import os   # file manipulation (moving, renaming...) shenanigans
import re   # regular expression stuff
import sys  # only for sys.stderr
import time # time format conversion stuff

# Binary search algorithm, with a few tweaks.
#
# To understand how this works, first one needs to keep in mind that...
#
# 1. The only way to consistently pair a replay with an entry in results.csv is
#    using the timestamps.
# 2. The time of each match as recorded by CCCaster is never the same as the
#    one written in the replay filename, even if they are referring to the same
#    match. In fact, the replay's recorded time is at least 1 second more than
#    the one in results.csv, and in some rare occasions, the difference between
#    the two can be anything between 2 and 20 seconds. There is no fixed amount
#    and, as far as I know, no way to predict how big the difference will be.
#
# Because of that, in order to optimize the process of matching replay files
# with results.csv entries (in the case of someone having a huge results.csv
# file, or lots and lots of replay files to organize), a simple binary search
# algorithm that looks for an exact match, or even storing things in a hash and
# checking if a certain key is defined wouldn't work, because there will never
# be an exact, or even consistent match. So here, I'm checking two things:
#
# 1. Is the target value (date in the replay file) larger than the current
#    value being tested (entry in results.csv)?
# 2. If the above applies, is the difference between the two values smaller
#    than 40?
#
# I arbitrarily picked 40, because I'm assuming the difference between the two
# values will never be as big as that, but that *can* come to bite someone's
# ass later, although the chances are REALLY small. The biggest gap between
# both values I've seen personally was 22. I could maybe pick a value as high
# as 50, but then I'd be assuming that people wouldn't be having 50 second long
# matches, which, in my opinion, is more likely to happen than the actual gap
# between the two values to be 50. There's no easy way around this, i.e.
# without having to make an educated guess.
def _binsearch(target_file, results):
	target = None

	# Parse the given filename with a regex, and extract the date at the end
	p = re.compile(r"^.*?_(\d{12})\.rep$")
	match = p.match(target_file)
	if match.group(1):
		# Convert the time to a UNIX timestamp, since that's how time is recorded
		# in the results.csv file
		target = int(time.mktime(time.strptime(match.group(1),"%y%m%d%H%M%S")))
	else:
		print(f"WARNING: Couldn't get valid date from file {target_file}. Skipping...", file=sys.stderr)
		return None, None
	
	# Binary search
	lo = 0
	hi = len(results) - 1
	c = 0
	while lo <= hi:
		m = int((lo + hi) / 2)
		test = int(results[m].split(',')[6])

		if target > test:
			if target - test < 40:
				return results[m], test
			lo = m + 1
			c += 1
			continue

		if target < test:
			hi = m - 1
			c += 1
			continue

	print(f"WARNING: Couldn't find entry in results.csv corresponding to file {target_file}. Skipping...", file=sys.stderr)
	return None, None

def main():
	exitflag = None

	if not os.path.isfile("MBAA.exe"):
		print("ERROR: This doesn't seem to be your MBAACC installation folder.", file=sys.stderr)
		exit(1)

	if not os.path.isfile("cccaster.v3.1.exe"):
		print("ERROR: You don't have CCCaster version 3.1 installed.", file=sys.stderr)
		exit(1)

	# Save the contents of the results.csv file into an array @results, where
	# each item in the array is a single line from the file. the `translate` is
	# there to remove newline and carriage return characters from each line,
	# which will mess some calculations and parsing done later.
	#
	# The "encoding='ascii', errors='ignore'" part is included to remove non-
	# ascii characters, since those cause encoding-related Python errors, and bugs
	# inside MBAACC's replay selection menu. There *is* a better way to solve
	# this without deleting characters, by using the unidecode library, but that
	# would add a third-party dependency, which I'm extremely against for simple
	# scripts like this. Another way would be writing my own character replacement
	# function, but that would make the whole script much more complicated to
	# understand, while also being a TON of (tedious) work for somewhat minimal
	# gain.
	#
	# The "newline='\n'" part is to ensure that a line is only counted on a LF
	# (line feed) character, instead of on a CR (carriage return) character.
	# Don't ask me how, but someone in NA had a CR character in their nickname,
	# and that broke this script.
	try:
		with open('results.csv', encoding='ascii', errors='ignore', newline='\n') as file:
			#results = [line.rstrip("\r\n") for line in file]
			results = [line.translate(str.maketrans('', '', "\r\n")) for line in file]
			
	except FileNotFoundError:
		print("ERROR: The results.csv file wasn't found. Go play some matches!", file=sys.stderr)
		exit(1)

	if len(results) == 0:
		print("ERROR: Your results.csv file is empty. Go play some matches!", file=sys.stderr)
		exitflag = 1
	
	# Check if the results.csv has been tampered with in a way that makes the
	# calculations and parsing done later impossible to do. Most notably:
	#
	# 1. Each line must have exactly 7 fields, separated by commas (as of
	#    CCCaster version 3.1004).
	# 2. The time recorded, located in the 7th field, must be a 10-digit
	#    number. This might change after January 19, 2038, assuming that 1.
	#    I'll still be playing this game, and 2. CCCaster won't be affected by
	#    the Y2K38 bug by then.
	p = re.compile('^.*?,.*?,[0-3],.*?,.*?,[0-3],[0-9]{10}$')
	for i, line in enumerate(results):
		if not p.match(line):
			print(f"ERROR: Line number {i} of your results.csv file has been tampered with:", file=sys.stderr)
			print(f"       {line}", file=sys.stderr)
			exitflag = 1

	# Save the list of replay files (files ending in .rep) into a list
	# called replays
	try:
		os.chdir("./ReplayVS")
	except FileNotFoundError:
		print("ERROR: You don't have a ReplayVS folder.", file=sys.stderr)
		exit(1)

	replays = glob.glob("*.rep")
	os.chdir("..")

	if len(replays) == 0:
		print("ERROR: No replay files were found in your ReplayVS folder.", file=sys.stderr)
		exitflag = 1

	if exitflag:
		exit(1)

	# Count the number of files that were moved
	movecount = 0

	# Sort the entries in results.csv chronologically (by the value in the 7th
	# column, which is the time the matches happened), just in case they
	# weren't already.
	results = sorted(results, key=lambda f: f.split(',')[6])

	# Create a new folder called "!organized" inside the ReplayVS folder. The
	# renamed replay files will be moved into here.
	os.makedirs("ReplayVS/!organized", exist_ok=True)
	for replay in replays:
		# Get the entry in the results.csv that corresponds to the replay file.
		# `line` is the entry that corresponds to the file, and `res_epoch` is
		# the time registered in that line, formatted as a UNIX timestamp. If a
		# corresponding entry couldn't be found, skip to the next replay file
		# in the list.
		line, res_epoch = _binsearch(replay, results)
		if not line:
			continue

		# Convert the UNIX timestamp to a more human-readable format.
		res_date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(res_epoch))

		# Split the line from results.csv into different fields, using commas
		# as the separators
		s = line.split(',')

		# Strip whitespace from nicknames, because filenames can't start nor end with whitespaces on Windows
		s[0] = s[0].strip()
		s[3] = s[3].strip()

		# If the nickname was only composed of non-ascii characters, which were
		# removed, change the nickname to "unicode name"
		#
		# TODO: check if the nickname now consists only of spaces. not an error that
		# has come up yet, but *might*...
		if len(s[0]) == 0: s[0] = "unicode name";
		if len(s[3]) == 0: s[3] = "unicode name";

		# Truncate nicknames to a maximum of 20 characters, so the filename
		# doesn't become too long.
		if len(s[0]) > 20: s[0] = s[0][:20]
		if len(s[3]) > 20: s[3] = s[3][:20]

		# Remove problematic characters from nicknames
		s[0] = s[0].translate(str.maketrans('', '', "'\":"))
		s[3] = s[3].translate(str.maketrans('', '', "'\":"))

		# This is the structure of the new filename.
		#
		# res_date = The date and time the match happened
		# s[0]     = Your nickname
		# s[1]     = Your character's name and moon
		# s[2]     = Your score
		# s[3]     = Your opponent's nickname
		# s[4]     = Their character's name and moon
		# s[5]     = Their score
		filename = f"{res_date},{s[0]},{s[1]},{s[2]},{s[3]},{s[4]},{s[5]}.rep"

		# Create a new folder for the person you've played against in the
		# replay. If you've played with two or more people that use the same
		# nickname, well, tough. Either ask them to change it, or manually
		# rename the folder and files yourself. There's no way to do that
		# programmatically without making a LOT of assumptions.
		os.makedirs(f"ReplayVS/!organized/{s[3]}", exist_ok=True)

		# Move the replay file into the aforementioned folder, with a new and
		# improved filename.
		os.rename(f"ReplayVS/{replay}", f"ReplayVS/!organized/{s[3]}/{filename}")

		movecount += 1
	
	print(f"Done. {movecount} replay(s) moved.")

if __name__ == "__main__":
    main()
