### Version 0.9.92-Alpha.003, June 2, 2020
* Change the layout so that the right widgets expand the right amount.
* The charts resize to fill space
* A calendar widget popup added to the front dateEdit.
* Moved qt form files and generated python code to their own directory
* Migration to fix mixed values, binary or Numeric for TradeSum.mktval
* Fix realRR to display a percentage of R when the pnl is a loss.
* Time or time zone issues in the finnhub REST API fixed.
* Daily Summary includes a couple charts in place of the middle table.
* Add tags combobox to summaryForm backed by db--simlar to how strategies are done but using sqlalchemy declarative models.
* Moved dailyNotes from the dailyForm to summaryForm.
* DailyForm layout uses splitters. Sections can be resized a bit.
* Stock charts have an annotation showing the data source.
* Focus on tags is required for the selected tags to show. 'Fixed' it by setting the focus whenever populateTags is called.
* Add a daily pnl label is on the front page.
* A proof of concept a statistics hub with user controlsa and three charts is launched from file menu
* Bug fix- added a method to fix sqlite errors in pnl field.

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

