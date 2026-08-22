Install Guide
=============

wzgram is a drop-in replacement for Pyrogram. The package on PyPI is called **wzgram**, but
the module you import is still ``pyrogram`` — existing code keeps working unchanged.

wzgram requires **Python 3.10 or newer**. Nothing else has to be installed by hand: the Rust
crypto backend and the SQLite driver come with it as wheels.


-----

Install
-------

.. code-block:: bash

    $ pip install wzgram

That is the whole thing. Verify it:

.. code-block:: bash

    $ python3 -c "import pyrogram; print(pyrogram.__version__)"

If a version number prints, you are done.

.. note::

    Do not install ``pyrogram`` and ``wzgram`` side by side. They provide the same
    ``pyrogram`` module and whichever was installed last wins, which is a confusing way to
    find out. Run ``pip uninstall pyrogram`` first if it is already there.

Use a virtual environment
-------------------------

Installing into the system Python works until two projects want different versions. A virtual
environment per project avoids that entirely:

.. code-block:: bash

    $ python3 -m venv venv
    $ source venv/bin/activate        # Windows: venv\Scripts\activate
    $ pip install wzgram

Everything installed while it is active stays inside ``venv/``. Deleting that directory
uninstalls it.

Upgrading
---------

.. code-block:: bash

    $ pip install -U wzgram

Telegram's API moves — new layers, new methods, new fields on existing types. Upgrading is
how you get them, and how you get fixes to the transfer and reconnection paths.

Development version
-------------------

The ``dev`` branch is where work lands before a release:

.. code-block:: bash

    $ pip install -U git+https://github.com/rjriajul/wzgram.git@dev

It is generally usable and occasionally not. Pin a release for anything you cannot babysit.

Building from source
--------------------

Working *on* wzgram needs one extra step, because ``pyrogram/raw/`` is generated from the TL
schema and is not committed:

.. code-block:: bash

    $ git clone https://github.com/rjriajul/wzgram.git
    $ cd wzgram
    $ pip install uv
    $ uv sync --frozen --extra dev
    $ uv run poe api            # generates pyrogram/raw/** and the error classes
    $ uv run poe test

``poe api`` is required before anything imports ``pyrogram`` from a fresh checkout. A wheel
built with ``uv run poe build`` runs the generators itself, so an installed wzgram never
needs this.

Troubleshooting
---------------

**"No module named 'pyrogram'" right after installing**
    The install went into a different Python than the one you are running. Check with
    ``python3 -m pip install wzgram`` — that form always matches the interpreter.

**"No module named 'pyrogram.raw'" from a git checkout**
    ``poe api`` has not been run. See above.

**pip starts compiling Rust**
    wzgram itself is pure Python, but its ``warpcrypto`` dependency is a Rust extension. pip
    falls back to building it from source when no wheel matches your Python version, platform
    or libc — which then needs a Rust toolchain. Upgrading pip first is usually enough, since
    an old pip rejects wheel tags it does not understand.

**A ``pyrogram`` install shadowing wzgram**
    See the note above — uninstall it.
