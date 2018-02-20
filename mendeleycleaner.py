import bibtexparser as btp
import click
import time
import sys
import fileinput
import os
import re
from subprocess import call

CONFIG_FILE_PATH = os.getenv("HOME") + '/.MendeleyBibTeXCleaner/'
CONFIG_FILE = CONFIG_FILE_PATH + 'config.ini'
DEFAULT_KEYS = ['author', 'title', 'journal', 'pages', 'volume',
                'year', 'url', 'doi', 'archive', 'archiveprefix',
                'primaryclass', 'arxivid', 'eprint', 'isbn']
EDITOR = os.environ.get('EDITOR', 'vim')


@click.version_option(prog_name='MendeleyBibTeXCleaner',
                      message='\n%(prog)s by giuppep, version %(version)s.\
                      \nhttps://github.com/giuppep/MendeleyBibTeXCleaner\n')
@click.group()
def cli():
    """This app 'cleans' the BibTeX file exported by Mendeley. The user must specify in the file 'config.ini' which BibTeX fields (e.g. author, title...) should be mantained; all other fields will be deleted."""
    pass


def create_config():
    """Creates configuration file."""
    try:
        if not os.path.isdir(CONFIG_FILE_PATH):
            os.makedirs(CONFIG_FILE_PATH)
        with open(CONFIG_FILE, 'w') as config:
            config.write(
                '# Configuration file for MendeleyBibTeXCleaner\n#\n# Comment with "#" (or delete) the lines corresponding to the BibTeX fields\n# that you DO NOT want in the processed bib file.\n# If you want to include additional BibTeX fields, simply add them at the\n# end of this file.\n')
            for key in DEFAULT_KEYS:
                config.write(key + '\n')
        click.echo('\n{} created.\nRun the "config" command to edit the default configuration.\n'.format(
            CONFIG_FILE))
    except:
        click.echo(click.style(
            'ERROR, could not create configuration file!', fg='red'))
    sys.exit(0)


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
        click.echo(click.style('\nCould not find the file {}.\nCreating new configuration file...'.format(
            CONFIG_FILE), fg='red'))
        time.sleep(1)
        create_config()


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
        if 'primaryclass' in entry.keys():
            entry['archive'] = entry.pop('primaryclass')
        if 'link' in entry.keys():
            entry['url'] = entry.pop('link')
    return bibliography


def fix_year(bib_str):
    """BibTexParser has some issue with the year not being within braces..."""
    return re.sub(r'year = (\d\d\d\d)', r'year = {\g<1>}', bib_str)


def fix_title_month(bib_file, fix_month):
    """Fixes a problem with capitalisation in the title. This is because BibTexParser strips all braces from the title. If the fix_month flag is turned on then it also fixes the 'month' field by removing braces. Both Mendeley and BibTexParser print the month within braces (e.g. {jun}) which does not work correctly with BibTeX."""

    with fileinput.input(bib_file, inplace=True) as bibtex:
        for line in bibtex:
            if 'title' in line:
                line = re.sub(r'([^\\|{|{A-Z])([A-Z]\w*)',
                              r'\g<1>{\g<2>}', line)
                line = re.sub(r'‐|–', '-', line)
            if fix_month:
                if 'month' in line:
                    line = re.sub(r'{(\w\w\w)}', r'\g<1>', line)
            click.echo(line.rstrip())


@cli.command()
def config():
    """Opens the configuration file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'a') as config_file:
            call([EDITOR, config_file.name])
    else:
        click.echo(click.style('\nCould not find the configuration file {}.\nCreating new configuration file...'.format(
            CONFIG_FILE), fg='red'))
        time.sleep(1)
        create_config()


@cli.command()
@click.argument('bib_file')
@click.option('--save-to', default=None,
              help='Specify the name of the output file. By default it appends "edited" to the original filename.')
@click.option('--overwrite', default=False, is_flag=True,
              help='Overwrites original file.')
@click.option('--month', default=False, is_flag=True,
              help="Removes braces around the 'month' field.")
def clean(bib_file=None, save_to=None, overwrite=False, month=False):
    """This command 'cleans' the BibTeX file"""
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
    bibliography_str = fix_year(bibliography_str)
    bibliography = btp.loads(bibliography_str, parser)

    # Renames certain non-standard keys
    bibliography = rename_keys(bibliography)

    # Cleans the bibliography
    bibliography = clean_keys(bibliography, good_keys)

    # Saves the bibliography
    save_bib(bibliography, filename=save_to)

    # Fixes the title output
    # If --month flag is active, it fixes the 'month' field formatting
    fix_title_month(save_to, month)
