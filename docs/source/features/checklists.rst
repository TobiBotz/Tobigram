Checklists
==========

*Bot API 9.1 — July 2025*

A checklist is a to-do list that lives inside a message. Everyone in the chat sees the same
list, and — if the author allows it — everyone can tick items off or add their own. The
message updates in place for all of them.


-----

Sending one
-----------

A checklist is sent with :meth:`~pyrogram.Client.send_checklist` and built from
:obj:`~pyrogram.types.InputChecklist` and :obj:`~pyrogram.types.InputChecklistTask`:

.. code-block:: python

    from pyrogram.types import InputChecklist, InputChecklistTask

    await app.send_checklist(
        chat_id="me",
        checklist=InputChecklist(
            title="Release 4.0",
            tasks=[
                InputChecklistTask(id=1, text="Bump the layer"),
                InputChecklistTask(id=2, text="Regenerate the docs"),
                InputChecklistTask(id=3, text="Tag and publish"),
            ],
            others_can_add_tasks=True,
            others_can_mark_tasks_as_done=True,
        ),
    )

Task ids are **yours to assign** and must be unique within the checklist. They are how you
refer to a task later, so keep them stable — reusing an id for different text is what makes
a checklist edit look like a rewrite to everyone watching.

Ticking items off
-----------------

.. code-block:: python

    await app.mark_checklist_tasks_as_done(
        chat_id="me",
        message_id=message_id,
        marked_as_done_task_ids=[1, 2],
        marked_as_not_done_task_ids=[3],
    )

Both lists are keyword-only and either may be omitted. The method returns the message id of
the service message Telegram posts about the change.

Adding and editing
------------------

:meth:`~pyrogram.Client.add_checklist_tasks` appends without touching the rest:

.. code-block:: python

    await app.add_checklist_tasks(
        chat_id="me",
        message_id=message_id,
        tasks=[InputChecklistTask(id=4, text="Announce it")],
    )

:meth:`~pyrogram.Client.edit_message_checklist` replaces the whole checklist — title,
tasks, permissions — with a new :obj:`~pyrogram.types.InputChecklist`. Use it to rename or
remove tasks; use ``add_checklist_tasks`` when you only want to append.

Reading one back
----------------

``message.checklist`` holds a :obj:`~pyrogram.types.Checklist`:

.. code-block:: python

    checklist = message.checklist

    for task in checklist.tasks:
        done = "x" if task.completion_date else " "
        print(f"[{done}] {task.id} {task.text}")
        if task.completed_by:
            print(f"      by {task.completed_by.first_name}")

Note the two pairs of permission flags. ``others_can_add_tasks`` is what the author set;
``can_add_tasks`` is whether *you* may, which also accounts for who you are in that chat.
Read the ``can_*`` pair before offering a button that would fail.

Gotchas
-------

- :meth:`~pyrogram.Client.add_checklist_tasks` and
  :meth:`~pyrogram.Client.mark_checklist_tasks_as_done` are user-session methods. A bot can
  send and edit a checklist, but ticking items is something people do.
- A task has no boolean "done" field. Completion is ``completion_date`` being set, with
  ``completed_by`` naming who did it.
- Checklists cannot be mixed with media. The message is a checklist or it is not.
