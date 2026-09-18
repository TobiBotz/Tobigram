Polls
=====

*Bot API 9.6 — April 2026*

Polls grew from "pick one of ten strings" into something closer to a form: quizzes can have
more than one right answer, options can be added after the poll is live, and results can stay
hidden until it closes.


-----

Sending a poll
--------------

.. code-block:: python

    from pyrogram import enums

    await app.send_poll(
        chat_id="me",
        question="Which layer are we on?",
        options=["226", "227", "228"],
        type=enums.PollType.QUIZ,
        correct_option_ids=[2],
        explanation="228 since July.",
        open_period=600,
    )

Options are plain strings or :obj:`~pyrogram.types.InputPollOption` objects. The question and
the explanation accept a :obj:`~pyrogram.types.FormattedText` if you want entities in them.

Multiple correct answers
------------------------

``correct_option_ids`` takes a list, so a quiz can accept several answers as right. The older
single-valued ``correct_option_id`` still works and is folded into the list for you.

.. code-block:: python

    await app.send_poll(
        chat_id="me",
        question="Which of these are async?",
        options=["send_message", "rnd_id", "get_chat"],
        type=enums.PollType.QUIZ,
        correct_option_ids=[0, 2],
    )

Poll behaviour flags
--------------------

``send_poll`` carries the switches that decide how the poll behaves once it is live:

- ``allows_multiple_answers`` — a regular poll where voters pick several options
- ``allows_revoting`` — a voter may change their mind
- ``shuffle_options`` — each voter sees a different order
- ``allow_adding_options`` — voters may append options of their own
- ``hide_results_until_closes`` — nobody sees the tally until the poll ends
- ``members_only`` — only subscribers may vote
- ``country_codes`` — restrict voting by country
- ``open_period`` / ``close_date`` — close it automatically

Voting and reading results
--------------------------

.. code-block:: python

    await app.vote_poll(chat_id, message_id, options=[0])
    await app.retract_vote(chat_id, message_id)

    poll = await app.get_poll_results(chat_id, message_id)

    for option in poll.options:
        print(option.text, option.voter_count, f"{option.vote_percentage}%")

    await app.stop_poll(chat_id, message_id)

:meth:`~pyrogram.Client.get_poll_stats` returns who voted for what in a non-anonymous poll,
and :meth:`~pyrogram.Client.add_poll_option` appends an option to a live poll that allows it.

New poll votes reach a bot through :meth:`~pyrogram.Client.on_poll`.

Gotchas
-------

- ``correct_option_ids`` must be a list of ``int``. It was a bytes field before layer 228 and
  a leftover ``bytes`` there fails deep inside serialisation, not at the call.
- A quiz with no ``explanation`` is legal but wastes the one moment the voter is paying
  attention to why they were wrong.
- ``send_poll`` accepts ``explanation_media``, ``description`` and ``description_media``, and
  currently **drops them**: nothing in this layer carries a poll description, and the
  solution media field is not wired up. They are accepted so code written against the Bot API
  shape does not break, not because they do anything.
- Option media has the same limitation: :obj:`~pyrogram.types.InputPollOption` takes a
  ``media``, but only its text reaches the wire.
