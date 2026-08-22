Available Types
===============

This page is about wzgram types. All types listed here are available through the ``pyrogram.types`` package.
Unless required as argument to a client method, most of the types don't need to be manually instantiated because they
are only returned by other methods. You also don't need to import them, unless you want to type-hint your variables.

.. code-block:: python

    from pyrogram.types import User, Message, ...

.. note::

    Optional fields always exist inside the object, but they could be empty and contain the value of ``None``.
    Empty fields aren't shown when, for example, using ``print(message)`` and this means that
    ``hasattr(message, "photo")`` always returns ``True``.

    To tell whether a field is set or not, do a simple boolean check: ``if message.photo: ...``.

-----

.. currentmodule:: pyrogram.types

Users & Chats
-------------

.. autosummary::
    :nosignatures:

    {user_and_chats}

.. toctree::
    :hidden:

    {user_and_chats}

Messages & Media
----------------

.. autosummary::
    :nosignatures:

    {messages_media}

.. toctree::
    :hidden:

    {messages_media}

Bot keyboards & Commands
-------------------------

.. autosummary::
    :nosignatures:

    {bots_and_keyboards}

.. toctree::
    :hidden:

    {bots_and_keyboards}

Inline Mode
------------

.. autosummary::
    :nosignatures:

    {inline_mode}

.. toctree::
    :hidden:

    {inline_mode}

Input Content
--------------

.. autosummary::
    :nosignatures:

    {input_content}

.. toctree::
    :hidden:

    {input_content}

Listeners
---------

.. autosummary::
    :nosignatures:

    {listeners}

.. toctree::
    :hidden:

    {listeners}

-----

Authorization
-------------

.. autosummary::
    :nosignatures:

    {authorization}

.. toctree::
    :hidden:

    {authorization}

-----

Enums
=====

This page lists all available enums from the ``pyrogram.enums`` package.

.. code-block:: python

    from pyrogram.enums import ParseMode, ChatAction, ...

.. currentmodule:: pyrogram.enums

.. autosummary::
    :nosignatures:

    {enums}

.. toctree::
    :hidden:

    {enums}
