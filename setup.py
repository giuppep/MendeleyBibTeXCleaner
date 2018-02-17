from setuptools import setup

setup(
    name='MendeleyBibTeXCleaner',
    version='0.1',
    py_modules=['mend'],
    install_requires=[
        'click',
        'bibtexparser'
    ],
    entry_points='''
        [console_scripts]
        mend=mend:cli
    ''',
)
