#!/usr/bin/perl
# A simple script that gives your MBAACC replays more descriptive names.
#
# THIS SCRIPT WILL MOVE YOUR REPLAY FILES AROUND, AND GIVE THEM NEW NAMES. IF
# THAT CONCERNS YOU, MAKE A BACKUP BEFORE RUNNING THIS SCRIPT. PLEASE. YOU HAVE
# BEEN WARNED.
#
# I have written lots and lots of comments, so people not familiar with Perl
# can still understand what this script does, and why.

use 5.010;                         # use only features from perl v5.10 
use strict; use warnings;          # prevents stuff from silently breaking

use File::Copy "move";             # cross-platform `mv`
use File::Path "make_path";        # cross-platform `mkdir -p`
use POSIX "strftime";              # format UNIX timestamps to sane datetime formats
use Time::Local "timelocal_posix"; # format sane datetime formats to UNIX timestamps

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
sub _binsearch {
	my ($target_file, $list) = @_;

	# Parse the given filename with a regex, and extract the date at the end
	my @d;
	if ($target_file =~ /^.+?_(\d{12})\.rep$/) {
		@d = unpack "(A2)*", $1;
	} else {
		print STDERR "WARNING: Couldn't get valid date from file ReplayVS/$target_file. Skipping...\n";
		return;
	}

	# Convert the time to a UNIX timestamp, since that's how time is recorded
	# in the results.csv file
	my $target = timelocal_posix($d[5], $d[4], $d[3], $d[2], $d[1]-1, $d[0]+100);

	# Binary search
	my $lo = 0;
	my $hi = @$list - 1;
	my $c = 0;
	while ($lo <= $hi) {
		my $m = int(($lo + $hi) / 2);
		(my $test = (split ',', $list->[$m])[6]) =~ s/\r//g;

		if ($target > $test) {
			if ($target - $test < 40) {
				return ($list->[$m], $test);
			}
			$lo = $m + 1;
			$c++;
			next;
		}

		if ($target < $test) {
			$hi = $m - 1;
			$c++;
			next;
		}
	}

	print STDERR "WARNING: Couldn't find entry in results.csv corresponding to file ReplayVS/$target_file. Skipping...\n";
	return;
}

# Program starts here

my $exit;

unless (-f "MBAA.exe") {
	print STDERR "ERROR: This doesn't seem to be your MBAACC installation folder.\n";
	exit 1;
}

unless (-f "cccaster.v3.1.exe") {
	print STDERR "ERROR: You don't have CCCaster version 3.1 installed.\n";
	exit 1;
}

# Save the contents of the results.csv file into an array @results, where each
# item in the array is a single line from the file. the `chomp` is there to
# remove trailing newline characters from each line, which will mess some
# calculations and parsing done later.
unless (open FH, '<', 'results.csv') {
	print STDERR "ERROR: The results.csv file wasn't found. Go play some matches!\n";
	close FH;
	exit 1;
}
chomp(my @results = <FH>);
close FH;

if (scalar @results == 0) {
	print STDERR "ERROR: Your results.csv file is empty. Go play some matches!\n";
	$exit = 1;
}

# Check if the results.csv has been tampered with in a way that makes the
# calculations and parsing done later impossible to do. Most notably:
#
# 1. Each line must have exactly 7 fields, separated by commas (as of CCCaster
#    version 3.1004)
# 2. The time recorded, located in the 7th field, must be a 10-digit number.
#    This might change after January 19, 2038, assuming that 1. I'll still be
#    playing this game, and 2. CCCaster won't be affected by the Y2K38 bug by
#    then.
for my $i (0 .. $#results) {
	unless ($results[$i] =~ /^.*?,.*?,[0-3],.*?,.*?,[0-3],[0-9]{10}\r?$/) {
		print STDERR "ERROR: Line number ${\($i + 1)} of your results.csv file has been tampered with:\n";
		print STDERR "       $results[$i].\n";
		$exit = 1;
	}
}

# Save the list of replay files (files ending in .rep) into an array @replays
unless (chdir "ReplayVS") {
	print STDERR "ERROR: You don't have a ReplayVS folder.\n";
	exit 1;
}
my @replays = <*.rep>;
chdir "..";

if (scalar @replays == 0) {
	print STDERR "ERROR: No replay files were found in your ReplayVS folder.\n";
	$exit = 1;
}

exit 1 if $exit;

# Sort the entries in results.csv chronologically (by the value in the 7th
# column, which is the time the matches happened), just in case they weren't
# already.
@results = sort { (split ',', $a)[6] <=> (split ',', $b)[6] } @results;

# Create a new folder called "organized" inside the ReplayVS folder. The
# renamed replay files will be moved into here.
make_path "ReplayVS/organized";
for my $replay (@replays) {
	# Get the entry in the results.csv that corresponds to the replay file.
	# $line is the entry that corresponds to the file, and $res_epoch is the
	# time registered in that line, formatted as a UNIX timestamp. If a
	# corresponding entry couldn't be found, skip to the next replay file in
	# the list.
	my ($line, $res_epoch) = _binsearch $replay, \@results or next;

	# Convert the UNIX timestamp to a more human-readable format.
	my $res_date = strftime "%Y-%m-%d-%H-%M-%S", localtime $res_epoch;

	# Split the line from results.csv into different fields, using commas as
	# the separators
	my @s = split ',', $line;

	# Truncate nicknames to a maximum of 20 characters, so the filename
	# doesn't become too long. Also put a "..." at the end, to indicate that
	# there are more characters in the nickname.
	$s[0] = substr($s[0], 0, 20) . "..." if length $s[0] > 20;
	$s[3] = substr($s[3], 0, 20) . "..." if length $s[3] > 20;

	# This is the structure of the new filename.
	#
	# $res_date = The date and time the match happened
	# $s[0]     = Your nickname
	# $s[1]     = Your character's name and moon
	# $s[2]     = Your score
	# $s[3]     = Your opponent's nickname
	# $s[4]     = Their character's name and moon
	# $s[5]     = Their score
	my $filename = "$res_date,$s[0],$s[1],$s[2],$s[3],$s[4],$s[5].rep";

	# Create a new folder for the person you've played against in the replay.
	# If you've played with two or more people that use the same nickname,
	# well, tough. Either ask them to change it, or manually rename the folder
	# and files yourself. There's no way to do that programmatically without
	# making a LOT of assumptions.
	make_path "ReplayVS/organized/$s[3]";
	
	# Move the replay file into the aforementioned folder, with a new and
	# improved filename.
	move "ReplayVS/$replay", "ReplayVS/organized/$s[3]/$filename";
}

print "done\n";
