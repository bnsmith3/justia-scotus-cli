# justica-scotus-cli

The Justia SCOTUS CLI is a simple command line tool that grabs information on US Supreme Court cases from the [Justia website](https://supreme.justia.com/).

## Usage
The CLI has two commands:
1. **cases**: retrieves and stores information about cases decided in a given year
2. **opinions**: retrieves and stores opinions from cases decided in a given year

To see the options that are available for each command, navigate to the directory with the `grabber.py` file, and issue the following command replacing \<command\> with the desired command:

`python grabber.py <command> --help`

## Required packages
- BeautifulSoup
- click
- pandas
- requests
- (your choice of engine to write parquet files)

\* This has only been tested with Python 3.7.
