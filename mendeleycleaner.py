import bibtexparser as btp
import click
import time
import sys
import fileinput
import os
import re

CONFIG_FILE_PATH = os.getenv("HOME") + '/.MendeleyBibTeXCleaner/'
CONFIG_FILE = CONFIG_FILE_PATH + 'config.ini'
ALL_KEYS = ['link', 'month', 'isbn', 'eprint', 'address', 'abstract',
            'tags', 'volume', 'edition', 'issn', 'title', 'number',
            'archiveprefix', 'file', 'series', 'primaryclass', 'author',
            'publisher', 'pages', 'keyword', 'journal', 'arxivid', 'booktitle',
            'doi', 'pmid', 'url', 'day', 'country', 'chapter', 'issue']


def create_config():
    """Creates configuration file."""
    with open(CONFIG_FILE, 'w') as config:
        config.write(
            '# Configuration file for MendeleyBibTeXCleaner\n#\n# Comment with "#" (or delete) the lines corresponding to the keys\n# that you DO NOT want in the processed bib file.')
        for key in ALL_KEYS:
            config.write(key + '\n')


def load_config():
    """Loads the configuration file. If not found, it creates the file and exists the app."""
    good_keys = []
    try:
        with open(CONFIG_FILE, 'r') as config:
            for line in config:
                if line.strip()[0] is not '#':
                    good_keys.append(line.strip())
        good_keys.append('entrytype')
        good_keys.append('id')
        return good_keys
    except:
        click.echo(click.style('\nCould not find the file {}. Creating new configuration file...'.format(
            CONFIG_FILE), fg='red'))
        time.sleep(1)
        try:
            os.makedirs(CONFIG_FILE_PATH)
            create_config()
            click.echo('\n{} created.\n Please edit the configuration file before running the app again.\n'.format(
                CONFIG_FILE))
        sys.exit(0)


def save_bib(bibliography, filename='bibliography.bib'):
    """Saves the bibiliography to a file."""
    with open(filename, 'w') as bibtex_file:
        btp.dump(bibliography, bibtex_file)


def clean_keys(bibliography, good_keys=None):
    """Takes the bibtexparser bibliography object
    and returns an object of the same type after
    removing the unwanted categories."""
    if good_keys:
        for entry in bibliography.entries:
            entry_keys = list(entry.keys())[:]
            for key in entry_keys:
                if key.lower() not in good_keys:
                    del entry[key]
    return bibliography


def rename_keys(bibliography):
    """Corrects certain keys names."""
    for entry in bibliography.entries:
        for key in entry.keys():
            if key.lower() is 'primaryclass':
                entry['archive'] = entry.pop(key)
    return bibliography


def fix_month(bib_file):
    """Fixes the 'month' field by removing braces. Both Mendeley and BibTexParser print the month withing braces (e.g. {jun}) which does not work correctly with BibTeX."""

    with fileinput.input(bib_file, inplace=True) as bibtex:
        for line in bibtex:
            if 'month' in line:
                line = re.sub(r'{(\w\w\w)}', r'\g<1>', line)
            click.echo(line.rstrip())


@click.command()
@click.argument('bib_file')
@click.option('--save-to', default=None,
              help='Specify the name of the output file. By default it appends "edited" to the original filename.')
@click.option('--overwrite', default=False, is_flag=True,
              help='Overwrites original file.')
@click.option('--month', default=False, is_flag=True,
              help="Removes braces around the 'month' field.")
def cli(bib_file=None, save_to=None, overwrite=False, month=False):
    """This app 'cleans' the BibTeX file exported by Mendeley. The user must specify in the file 'config.ini' which BibTeX fields (e.g. author, title...) should be mantained; all other fields will be deleted."""
    # Loads the keys that need to be maintained
    good_keys = load_config()

    # Sets output filename
    if overwrite:
        save_to = bib_file
    elif not save_to:
        save_to = bib_file[:-4] + '_edited.bib'

    # Defines the parser
    parser = btp.bparser.BibTexParser()
    parser.ignore_nonstandard_types = True
    parser.homogenize_fields = True
    parser.common_strings = True

    # Loads the original bibliography
    with open(bib_file, 'r') as f:
        bibliography_str = f.read()
    bibliography = btp.loads(bibliography_str, parser)

    # Renames certain non-standard keys
    bibliography = rename_keys(bibliography)

    # Cleans the bibliography
    bibliography = clean_keys(bibliography, good_keys)

    # Saves the bibliography
    save_bib(bibliography, filename=save_to)

    # If --month flag is active, it fixes the 'month' field formatting
    if month:
        fix_month(save_to)
