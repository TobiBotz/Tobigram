Advanced Usage
==============

Raw API
-------

wzgram provides a high-level API that abstracts away the low-level Telegram
MTProto protocol. However, you can also access the raw API directly via
:meth:`~pyrogram.Client.invoke`.

.. code-block:: python

    from pyrogram import raw

    async def get_chat_online(app, chat_id):
        peer = await app.resolve_peer(chat_id)
        r = await app.invoke(
            raw.functions.messages.GetPeerSettings(peer=peer)
        )
        return r.settings.online

Resolving Peers
---------------

Many raw API calls require a peer object rather than a chat ID or username.
Use :meth:`~pyrogram.Client.resolve_peer` to convert:

.. code-block:: python

    peer = await app.resolve_peer("username_or_phone")
    # Returns raw.types.InputPeerUser, InputPeerChat, or InputPeerChannel

Saving Files
------------

For uploading large files with progress tracking, use
:meth:`~pyrogram.Client.save_file`.

.. code-block:: python

    async def upload_with_progress(app, file_path):
        async def progress(current, total):
            print(f"{current * 100 / total:.1f}%")

        return await app.save_file(file_path, progress=progress)
