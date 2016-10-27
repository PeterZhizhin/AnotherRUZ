from datetime import time, timedelta

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

buildings_update_time = timedelta(days=1)
