import bibtexparser as btp
import click
import time
import sys

CONFIG_FILE = 'config.ini'
ALL_KEYS = ['link', 'month', 'isbn', 'eprint', 'address', 'abstract',
            'tags', 'volume', 'edition', 'issn', 'title', 'number',
            'archiveprefix', 'file', 'series', 'primaryclass', 'author',
            'publisher', 'pages', 'keyword', 'journal', 'arxivid', 'booktitle',
            'doi', 'pmid', 'url']


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
                if line[0] is not '#':
                    good_keys.append(line.strip())
        good_keys.append('entrytype')
        good_keys.append('id')
        return good_keys
    except:
        click.echo(click.style('\nCould not find the file {}. Creating new configuration file...'.format(
            CONFIG_FILE), fg='red'))
        time.sleep(1)
        create_config()
        click.echo('\n{} created. Please edit the configuration file before running the app again.\n'.format(
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


# def format_arXiv_entries(bibliography):


@click.command()
@click.argument('bib_file')
@click.option('--save-to', default=None, help='Specify the name of the output file. By default it appends "edited" to the original filename')
@click.option('--overwrite', default=False, is_flag=True, help='Overwrites original file.')
def cli(bib_file=None, save_to=None, overwrite=False):
    """This app 'cleans' the BibTeX file exported by Mendeley. The user must specify in the file 'config.ini' which BibTeX categories (e.g. author, title...) should be mantained; all other categories will be deleted."""
    # Loads the keys that need to be maintained
    good_keys = load_config()

    # Output filename
    if overwrite:
        save_to = bib_file
    elif not save_to:
        save_to = bib_file[:-4] + '_edited.bib'

    # Loads the original bibliography
    with open(bib_file, 'r') as f:
        bibliography_str = f.read()
    bibliography = btp.loads(bibliography_str)

    # Cleans the bibliography
    bibliography = clean_keys(bibliography, good_keys)

    # Saves the bibliography
    save_bib(bibliography, filename=save_to)

# if __name__ == '__main__':
#     main()
