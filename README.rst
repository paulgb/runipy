|Travis Build Status| |Coveralls| |License| |PyPI| |Anaconda| |Gitter|

--------------

``runipy``: run IPython as a script
=====================================

The IPython notebook provides an interactive interface to a Python interpreter.

- **Literate programming**: the IPython notebook is an ideal format for
  writing "literate" programs, in which the code is part of a larger multi-media
  document. ``runipy`` lets you run such programs directly, without first
  converting to a pure Python script.
- **Report generation**: ``runipy`` can run the notebook and convert it into HTML
  in one go, making it an easy way to automate reports.
- **Data pipeline**: if you use IPython notebooks to create a data pipeline,
  ``runipy`` lets you automate that pipeline without losing the notebook
  formatting.

Requirements
------------

``runipy`` currently supports IPython versions 2.4.x, 3.2.x and the current development
version of 4.x.

Installation
------------

The easiest way to install ``runipy`` is with ``pip``::

    $ pip install runipy

Command-line use
----------------

To run a ``.ipynb`` file as a script, run::

    $ runipy MyNotebook.ipynb

To save the output of each cell back to the notebook file, run::

    $ runipy -o MyNotebook.ipynb

To save the notebook output as a *new* notebook, run::

    $ runipy MyNotebook.ipynb OutputNotebook.ipynb

To run a ``.ipynb`` file and generate an ``HTML`` report, run::

    $ runipy MyNotebook.ipynb --html report.html

Passing Arguments
-----------------

You can pass arguments to the notebook through environment variables.
The use of environment variables is OS- and shell- dependent, but in a
typical UNIX-like environment they can be passed on the command line
before the program name::

    $ myvar=value runipy MyNotebook.ipynb

Here is one way this can be done from pure python::

    from os import environ
    from subprocess import call

    environ['myvar'] = 'value'
    call(["runipy", "MyNotebook.ipynb"])

Then in the notebook, to access myvar::

    from os import environ
    myvar = environ['myvar']

``environ`` is just a ``dict``, so you can use ``.get()`` to fall back on
a default value::

    from os import environ
    myvar = environ.get('myvar', 'default!')

Stdin / Stdout
--------------

``runipy`` can read stdin and stdout and sit in a UNIX pipeline::

    $ runipy --stdout < MyNotebook.ipynb > OutputNotebook.ipynb

    $ cat MyNotebook.ipynb | runipy --stdout > OutputNotebook.ipynb


Programmatic use
----------------

It is also possible to run IPython notebooks from Python, using::

    from runipy.notebook_runner import NotebookRunner
    from IPython.nbformat.current import read

    notebook = read(open("MyNotebook.ipynb"), 'json')
    r = NotebookRunner(notebook)
    r.run_notebook()

and you can enable ``pylab`` with::

    r = NotebookRunner(notebook, pylab=True)
    
The notebook is stored in the object and can be saved using::

    from IPython.nbformat.current import write
    write(r.nb, open("MyOtherNotebook.ipynb", 'w'), 'json')

`run_notebook()` takes two optional arguments. The first, `skip_exceptions`, 
takes a boolean value (`False` by default). If `True`, exceptions will be ignored
and the notebook will continue to execute cells after encountering an exception.
The second argument is `progress_callback`, which must be either `None` or a
function that takes one argument. This function is called after execution of
each cell with the 0-based index of the cell just evaluated. This can be useful
for tracking progress of long-running notebooks.

Credit
------

Portions of the code are based on code by `Min RK <https://github.com/minrk>`_

Thanks to Kyle Kelley, Nitin Madnani, George Titsworth, Thomas Robitaille,
Andrey Tatarinov, Matthew Brett, Adam Haney, Nathan Goldbaum, Adam Ginsburg,
Gustavo Bragança, Tobias Brandt, Andrea Zonca, Aaron O'Leary, Simon Guillot,
Fernando Correia, Takashi Nishibayashi, Simon Conseil, Thomas French,
Martin Fitzpatrick, Giuseppe Ottaviano, John Kirkham, Tao Luo, and
Christopher Prohm for patches, documentation fixes, and suggestions.

.. |Travis Build Status| image:: https://travis-ci.org/paulgb/runipy.svg?branch=master
    :target: https://travis-ci.org/paulgb/runipy

.. |Coveralls| image:: https://coveralls.io/repos/paulgb/runipy/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/paulgb/runipy?branch=master

.. |License| image:: https://img.shields.io/badge/license-BSD-blue.svg
   :alt: BSD License
   :target: https://raw.githubusercontent.com/paulgb/runipy/master/LICENSE

.. |PyPI| image:: https://img.shields.io/pypi/v/runipy.svg
   :target: https://pypi.python.org/pypi/runipy

.. |Anaconda| image:: https://anaconda.org/conda-forge/runipy/badges/version.svg
   :target: https://anaconda.org/conda-forge/runipy

.. |Gitter| image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/paulgb/runipy
   :target: https://gitter.im/paulgb/runipy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
