Install Guide
=============

Being a modern Python framework, wzgram requires an up to date version of Python 3 to be installed in your system.
We recommend using the latest versions of both Python 3 and pip.


-----

Install wzgram
--------------

.. code-block:: bash

    $ pip install git+https://github.com/rjriajul/wzgram.git

Bleeding Edge
-------------

You can install the development version from the development branch:

.. code-block:: bash

    $ pip install git+https://github.com/rjriajul/wzgram.git@dev

Verifying
---------

To verify that wzgram is correctly installed, open a Python shell and import it.
If no error shows up you are good to go.

.. parsed-literal::

    >>> from pyrogram import __version__
    >>> __version__
    '3.0.12'
