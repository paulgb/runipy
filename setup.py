from setuptools import setup

import runipy

setup(name = 'runipy',
    version = runipy.__version__,
    description = 'Run IPython notebooks from the command line',
    url = 'https://github.com/paulgb/runipy',
    author = 'Paul Butler',
    author_email = 'paulgb@gmail.com',
    classifiers = [
        'Framework :: IPython',
    ],
    install_requires = [
        'Jinja2>=2.7.1',
        'Pygments>=1.6',
        'ipython>=1.1.0',
        'pyzmq>=13.1.0',
    ],
    packages = ['runipy'],
    entry_points = {
        'console_scripts': [
            'runipy = runipy.main:main'
        ]
    },
)
