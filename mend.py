import pickle
import bibtexparser as btp
import click
import time
import sys

CONFIG_FILE = 'mend.config'
ALL_KEYS = ['link', 'month', 'isbn', 'eprint', 'address', 'abstract',
            'tags', 'volume', 'edition', 'issn', 'title', 'number',
            'archiveprefix', 'file', 'series', 'primaryclass', 'author',
            'publisher', 'pages', 'keyword', 'journal', 'arxivid', 'booktitle',
            'doi', 'pmid', 'url']


def create_config():
    """Creates configuration file."""
    with open(CONFIG_FILE, 'w') as config:
        config.write(
            '# Comment with "#" the lines corresponding to the keys that you DO NOT want in the processed bib file.')
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
        print('Could not find the file {}. Creating new configuration file...'.format(
            CONFIG_FILE))
        time.sleep(1)
        create_config()
        print('\n{} created. Please edit the configuration file before running the app again.\n'.format(
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


# @click.option('--bib', default='Remote.bib', help='Specify bibliography file')
# @click.command()
# @click.argument('bib_file')
@click.command()
@click.argument('bib_file')
@click.option('--dest', default=None, help='Specify the name of the output file. By default it appends "edited" to the original filename')
def main(bib_file=None, dest=None):
    good_keys = load_config()
    if not dest:
        dest = bib_file[-3:] + '_edited.bib'
    # print(good_keys)
    # bib_file = 'Remote.bib'
    with open(bib_file, 'r') as f:
        bibliography_str = f.read()
    bibliography = btp.loads(bibliography_str)
    bibliography = clean_keys(bibliography, good_keys)
    # print(bibliography.entries[3])
    save_bib(bibliography, filename=dest)


if __name__ == '__main__':
    main()
