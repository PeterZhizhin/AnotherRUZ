# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import time


async def get_url(session: aiohttp.ClientSession, url, attempt_no=1, **kwargs):
    try:
        async with session.get(url, **kwargs) as response:
            return await response.json()
    except aiohttp.ClientResponseError:
        await asyncio.sleep(attempt_no * 0.2)
        return await get_url(session, url, attempt_no=attempt_no + 1, **kwargs)


async def get_url_new(url, **kwargs):
    async with aiohttp.ClientSession() as session:
        return await get_url(session, url, **kwargs)


def timeit(times=1):
    def decorator(method):
        def timed(*args, **kwargs):
            ts = time.time()
            for i in range(times):
                print("Time #{}".format(i))
                method(*args, **kwargs)
            te = time.time()

            print("Total {:.3f} secs {:.3f} per one".format(te - ts, (te - ts) / times))

        return timed

    return decorator


def main1(session):
    loop = asyncio.get_event_loop()
    res = asyncio.ensure_future(get_url(session, 'http://ruz.hse.ru/RUZService.svc/auditoriums',
                                        params={}))
    loop.run_until_complete(res)
    res = res.result()

    tasks = []
    for faculty in res:
        task = asyncio.ensure_future(get_url(session, 'http://ruz.hse.ru/RUZService.svc/personlessons',
                                             params=dict(
                                                 fromDate='2016.09.02',
                                                 toDate='2016.09.02',
                                                 receiverType=2,
                                                 auditoriumOid=faculty['auditoriumOid']
                                             )))
        tasks.append(task)

    all_timetable = asyncio.gather(*tasks)
    loop.run_until_complete(all_timetable)
    all_timetable = all_timetable.result()
    all_timetable = {res[i]['number']: all_timetable[i] for i in range(len(res))}
    print('Done')


if __name__ == "__main__":
    with aiohttp.ClientSession() as session:
        main1(session)
