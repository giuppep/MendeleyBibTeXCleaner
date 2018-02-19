from setuptools import setup

setup(
    name='MendeleyBibTeXCleaner',
    version='0.3',
    py_modules=['mendeleycleaner'],
    install_requires=[
        'click',
        'bibtexparser'
    ],
    entry_points='''
        [console_scripts]
        mendeleycleaner=mendeleycleaner:cli
    ''',
)
