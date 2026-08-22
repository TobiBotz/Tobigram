Examples
========

This page contains example scripts to show you what wzgram looks like in practice.

Every script is working right away (provided you correctly set up your credentials), meaning you can simply copy-paste
and run. The only things you have to change are session names and target chats, where applicable.

.. note::

    These scripts assume the session has already been authorized. A **first** login also
    needs ``api_id`` and ``api_hash`` passed to :obj:`~pyrogram.Client`, bots included — see
    :doc:`../auth`.

The examples listed below can be treated as building blocks for your own applications and are meant to be simple enough
to give you a basic idea.

-----

.. csv-table::
    :header: Example, Description
    :widths: auto
    :align: center

    :doc:`hello_world`, "Demonstration of basic API usage"
    :doc:`echo_bot`, "Echo every private text message"
    :doc:`tg_business_echo_bot`, "Reply back the same message, in `Business <https://core.telegram.org/bots/business>`_ Chats"
    :doc:`welcome_bot`, "An example Welcome Bot, updated to support the `new Telegram Updates <https://t.me/BotNews/57>`_"
    :doc:`get_chat_history`, "Get the full message history of a chat"
    :doc:`get_chat_members`, "Get all the members of a chat"
    :doc:`get_dialogs`, "Get all of your dialog chats"
    :doc:`callback_queries`, "Handle callback queries (as bot) coming from inline button presses"
    :doc:`inline_queries`, "Handle inline queries (as bot) and answer with results"
    :doc:`use_inline_bots`, "Query an inline bot (as user) and send a result to a chat"
    :doc:`bot_keyboards`, "Send normal and inline keyboards using regular bots"
    :doc:`send_voice`, "Download audio file and reupload as Voice Message with waveforms"
    :doc:`raw_updates`, "Handle raw updates (old, should be avoided)"
    :doc:`tg_guest_message_echo_bot`, "Reply to guest messages, without joining the chat"
    :doc:`conversation_bot`, "Ask questions and wait for the answers inline"
    :doc:`ephemeral_message_bot`, "Reply in a group so that only one user sees it"
    :doc:`rich_message`, "Send a structured document as a single message"

Each :doc:`feature page </features/index>` carries a working example of its own, and
:doc:`/topics/advanced-usage` covers calling raw TL functions directly when no high-level
method exists yet.

.. toctree::
    :hidden:

    hello_world
    echo_bot
    tg_business_echo_bot
    welcome_bot
    get_chat_history
    get_chat_members
    get_dialogs
    callback_queries
    inline_queries
    use_inline_bots
    bot_keyboards
    send_voice
    raw_updates
    tg_guest_message_echo_bot
    conversation_bot
    ephemeral_message_bot
    rich_message
