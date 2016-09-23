# -*- coding: utf-8 -*-
from typing import List, Dict
from datetime import date, timedelta, time

from python_ruz import Lesson, Auditorium, Building
from python_ruz import utilities


def auditoriums(building_id=None) -> list:
    return Auditorium.auditoriums(building_id)


def buildings() -> list:
    return Building.buildings()


def person_lessons(from_date: date, to_date: date, email: str) -> List[Lesson.Lesson]:
    return Lesson.person_lessons(from_date, to_date, email)


def auditorium_lessons(from_date: date, to_date: date, auditorium_id: int) -> List[Lesson.Lesson]:
    return Lesson.auditorium_lessons(from_date, to_date, auditorium_id)


def auditoriums_lessons(from_date: date, to_date: date,
                        auditoriums_oids: List[int]) -> Dict[int, List[Lesson.Lesson]]:
    return Lesson.auditoriums_lessons(from_date, to_date, auditoriums_oids)


def auditorium_lessons_in_building(from_date: date, to_date: date,
                                   building_id: int = None) -> Dict[str, List[Lesson.Lesson]]:
    return Lesson.auditoriums_lessons_in_building(from_date, to_date, building_id)


def get_free_auditoriums(date: date, building_id=None, remove_intervals_smaller_than=None):
    return Lesson.get_free_auditoriums(date, building_id, remove_intervals_smaller_than)


def timeit(count=1):
    import time
    def timeit_it(method):
        def timed(*args, **kw):
            ts = time.time()
            result = None
            for i in range(count):
                result = method(*args, **kw)
            te = time.time()

            print('%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, (te - ts) / count))
            return result

        return timed

    return timeit_it


if __name__ == "__main__":
    def check_segment_inside(segment_big, segment_small):
        return segment_small[0] >= segment_big[0] and segment_small[1] <= segment_big[1]


    from collections import defaultdict
    import telegram.emoji

    X = telegram.emoji.Emoji.CROSS_MARK
    O = telegram.emoji.Emoji.WHITE_HEAVY_CHECK_MARK

    digits_emoji = [str(i) + telegram.emoji.n(b'\xE2\x83\xA3') for i in range(10)]

    pairs = [
        (time(9, 0), time(10, 20)),
        (time(10, 30), time(11, 50)),
        (time(12, 10), time(13, 30)),
        (time(13, 40), time(15, 0)),
        (time(15, 10), time(16, 30)),
        (time(16, 40), time(18, 0)),
        (time(18, 10), time(19, 30)),
        (time(19, 40), time(21, 0)),
    ]


    @timeit(1)
    def main():
        res = auditorium_lessons_in_building(date(2016, 9, 5), date(2016, 9, 5), 49)
        res = {auditorium_name:
                   {(lesson.begin_lesson.time(), lesson.end_lesson.time()) for lesson in lessons}
               for auditorium_name, lessons in res.items()}
        result_dict = defaultdict(list)

        for auditorium, lessons in res.items():
            for pair in pairs:
                result_dict[auditorium].append(pair not in lessons)

        format_string = '{:' + str(max(len(i) for i in result_dict.keys())) + 's} {}'
        print(*['{}{}-{}'.format(digits_emoji[i],
                                 pair_time[0].strftime('%H:%M'),
                                 pair_time[1].strftime('%H:%M'))
                for i, pair_time in enumerate(pairs, start=1)], sep='')
        print(format_string.format('', ''.join(i for i in digits_emoji[1:len(pairs) + 1])))
        for auditorium, availability in sorted(result_dict.items(), key=lambda x: (-len([i for i in x[1] if i]), x[0])):
            print(format_string.format(auditorium, ''.join(O if i else X for i in availability)))


    main()
