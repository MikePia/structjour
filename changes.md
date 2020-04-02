### Version 0.9.92-Alpha.001

* Added A Risk:Reward cell to show Actual P/L:Amount Risked
* Fixed a threading bug in the sumControl.chartMage
* Added a DB migration procedure and added migration for the new RR
* Automatically save to DB when user changes the date
* Automatically load the trades from DB when user changes the date and has selected DB
* Added a back up and restore procedure available in the menu. Backup the db and settings
* Added an initialize to the backup. Meant for testing, but available for user.
* Created code to handle stock API limit reached.
* Created an automatic rollover for stock API. When one fails, try the next till one succeeds or all fail.
* Added rules to the APIChooser to implement the automatic rollover.
* Got rid of a button so now there is one button for db, one for DAS and one for IB statement
* Bug fix in handling the positions.csv.
* Set initialize defaults for logfile and db files.
* Removed user choice of outdir and made it default only.
* On first run, or runs that have lost the settings, pop up the file settings dialog before opening the program
* Automated the create dirs procedure and removed it from file settings. User can override the auto gen in a seperate menu entry.
* Updated automated tests and fixed revealed bugs

These are most of the changes discussed with Pilot Fish. Started work on the statistics piece.

