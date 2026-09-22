import pytest

import pyrogram
from pyrogram import raw


class _Recorder:
    def __init__(self, result=True):
        self.calls = []
        self.result = result

    async def invoke(self, query, *args, **kwargs):
        self.calls.append(query)
        return self.result


@pytest.mark.asyncio
async def test_finish_sms_job_dispatches_query():
    from pyrogram.methods.smsjobs.finish_sms_job import FinishSmsJob

    class _Client(_Recorder, FinishSmsJob):
        pass

    client = _Client(result=True)
    res = await client.finish_sms_job("job123", error="Network error")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.smsjobs.FinishJob)
    assert call.job_id == "job123"
    assert call.error == "Network error"


@pytest.mark.asyncio
async def test_get_sms_job_dispatches_query():
    from pyrogram.methods.smsjobs.get_sms_job import GetSmsJob

    class _Client(_Recorder, GetSmsJob):
        pass

    dummy_job = raw.types.SmsJob(
        job_id="job123",
        phone_number="+123456789",
        text="Your code is 1234",
    )
    client = _Client(result=dummy_job)
    res = await client.get_sms_job("job123")

    assert res == dummy_job
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.smsjobs.GetSmsJob)
    assert call.job_id == "job123"


@pytest.mark.asyncio
async def test_get_sms_jobs_status_dispatches_query():
    from pyrogram.methods.smsjobs.get_sms_jobs_status import GetSmsJobsStatus

    class _Client(_Recorder, GetSmsJobsStatus):
        pass

    dummy_status = raw.types.smsjobs.Status(
        recent_sent=5,
        recent_since=0,
        recent_remains=10,
        total_sent=100,
        total_since=0,
        last_gift_slug="",
        terms_url="https://telegram.org/tos",
    )
    client = _Client(result=dummy_status)
    res = await client.get_sms_jobs_status()

    assert res == dummy_status
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.smsjobs.GetStatus)


@pytest.mark.asyncio
async def test_is_eligible_to_join_sms_jobs_dispatches_query():
    from pyrogram.methods.smsjobs.is_eligible_to_join_sms_jobs import IsEligibleToJoinSmsJobs

    class _Client(_Recorder, IsEligibleToJoinSmsJobs):
        pass

    dummy_eligibility = raw.types.smsjobs.EligibleToJoin(
        terms_url="https://telegram.org/tos",
        monthly_sent_sms=100,
    )
    client = _Client(result=dummy_eligibility)
    res = await client.is_eligible_to_join_sms_jobs()

    assert res == dummy_eligibility
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.smsjobs.IsEligibleToJoin)


@pytest.mark.asyncio
async def test_join_sms_jobs_dispatches_query():
    from pyrogram.methods.smsjobs.join_sms_jobs import JoinSmsJobs

    class _Client(_Recorder, JoinSmsJobs):
        pass

    client = _Client(result=True)
    res = await client.join_sms_jobs()

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.smsjobs.Join)


@pytest.mark.asyncio
async def test_leave_sms_jobs_dispatches_query():
    from pyrogram.methods.smsjobs.leave_sms_jobs import LeaveSmsJobs

    class _Client(_Recorder, LeaveSmsJobs):
        pass

    client = _Client(result=True)
    res = await client.leave_sms_jobs()

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.smsjobs.Leave)


@pytest.mark.asyncio
async def test_update_sms_jobs_settings_dispatches_query():
    from pyrogram.methods.smsjobs.update_sms_jobs_settings import UpdateSmsJobsSettings

    class _Client(_Recorder, UpdateSmsJobsSettings):
        pass

    client = _Client(result=True)
    res = await client.update_sms_jobs_settings(allow_international=True)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.smsjobs.UpdateSettings)
    assert call.allow_international is True


def test_client_has_smsjobs_methods():
    assert hasattr(pyrogram.Client, "finish_sms_job")
    assert hasattr(pyrogram.Client, "get_sms_job")
    assert hasattr(pyrogram.Client, "get_sms_jobs_status")
    assert hasattr(pyrogram.Client, "is_eligible_to_join_sms_jobs")
    assert hasattr(pyrogram.Client, "join_sms_jobs")
    assert hasattr(pyrogram.Client, "leave_sms_jobs")
    assert hasattr(pyrogram.Client, "update_sms_jobs_settings")
