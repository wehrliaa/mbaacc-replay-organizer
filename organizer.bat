@echo off

if exist rep-organizer.pl (
	perl rep-organizer.pl
	pause
	exit 0
)

if exist rep-organizer.py (
	python3 rep-organizer.py
	pause
	exit 0
)
