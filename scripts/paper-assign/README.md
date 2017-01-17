An almost entirely javascript-based GUI for editing confer-format
session files.  Uses a single php file (save.php) to write the session
list back to the local file system.

The main script is in index.html.

The current version of script looks for a hard-coded confer-formatted
paper-list.json and session-list.json file in the same directory as
the main script.  Session-list should include one entry for each
session in the conference, and the script will allow users to move
papers into sessions and reorder them.  Paper-list is a list of papers.

Settings.js includes some basic settings, including the heading for
the page, a few color options, and a setting of the number of columns
to use in the layout.

Note that this tool will write the session-list.json and lock files, so these files need to be world writeable.
