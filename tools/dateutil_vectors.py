#!/usr/bin/env python3
"""tools/dateutil_vectors.py — rules drawn at random, expanded by
python-dateutil's `rrule`, and written into
`tests/dateutil_vectors_tests.nv` with the first occurrences dateutil
answers.

The rules are drawn with a fixed seed, so a run writes the same file.
Each takes a frequency, an interval, and up to three `BYxxx` parts with
values drawn from their ranges, and ends with a `COUNT` or an `UNTIL`
or not at all.  A draw is kept only when:

  * RFC 5545 section 3.3.10 allows every part under the frequency,
    because this package refuses the ones it does not and dateutil
    runs them;
  * dateutil's first occurrence is the `DTSTART`, because RFC 5545
    section 3.8.5.3 leaves the other case undefined and the two
    libraries answer it differently;
  * dateutil answers at least one occurrence within a hundred years,
    and within a fifth of a second of computing.

The finer frequencies draw only `BYDAY` and the time parts, because a
day part under them leaves dateutil stepping through the periods of the
days it rejects one at a time.

Run from anywhere:  python3 tools/dateutil_vectors.py [path to a dateutil wheel]
"""
import datetime, os, random, signal, sys

if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv[1])
from dateutil import rrule as du

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "tests", "dateutil_vectors_tests.nv")
FREQS = ["YEARLY", "MONTHLY", "WEEKLY", "DAILY", "HOURLY", "MINUTELY", "SECONDLY"]
DAYS = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
WANT = 300
TAKE = 12


def allowed(freq, part):
    if part == "BYWEEKNO":
        return freq == "YEARLY"
    if part == "BYYEARDAY":
        return freq not in ("DAILY", "WEEKLY", "MONTHLY")
    if part == "BYMONTHDAY":
        return freq != "WEEKLY"
    return True


def draw_values(rng, part, freq):
    n = rng.randint(1, 3)
    if part == "BYMONTH":
        return sorted({rng.randint(1, 12) for _ in range(n)})
    if part == "BYMONTHDAY":
        return sorted({rng.choice([rng.randint(1, 31), -rng.randint(1, 7)]) for _ in range(n)})
    if part == "BYYEARDAY":
        return sorted({rng.choice([rng.randint(1, 366), -rng.randint(1, 30)]) for _ in range(n)})
    if part == "BYWEEKNO":
        return sorted({rng.choice([rng.randint(1, 53), -rng.randint(1, 3)]) for _ in range(n)})
    if part == "BYHOUR":
        return sorted({rng.randint(0, 23) for _ in range(n)})
    if part == "BYMINUTE":
        return sorted({rng.choice([0, 15, 30, 45, rng.randint(0, 59)]) for _ in range(n)})
    if part == "BYSECOND":
        return sorted({rng.choice([0, 30, rng.randint(0, 59)]) for _ in range(n)})
    if part == "BYSETPOS":
        return sorted({rng.choice([1, 2, -1, -2, 3]) for _ in range(n)})
    days = sorted({rng.randint(0, 6) for _ in range(n)})
    out = []
    for d in days:
        if freq in ("MONTHLY", "YEARLY") and rng.random() < 0.4:
            out.append("%d%s" % (rng.choice([1, 2, -1, 3, -2]), DAYS[d]))
        else:
            out.append(DAYS[d])
    return out


def draw(rng):
    freq = rng.choice(FREQS)
    parts = ["FREQ=" + freq]
    interval = rng.choice([1, 1, 1, 2, 3])
    if interval != 1:
        parts.append("INTERVAL=%d" % interval)
    pool = ["BYMONTH", "BYMONTHDAY", "BYYEARDAY", "BYWEEKNO", "BYDAY", "BYHOUR", "BYMINUTE",
            "BYSECOND"]
    if freq in ("HOURLY", "MINUTELY", "SECONDLY"):
        pool = ["BYDAY", "BYHOUR", "BYMINUTE", "BYSECOND"]
    chosen = [p for p in rng.sample(pool, rng.randint(0, 3)) if allowed(freq, p)]
    for p in chosen:
        parts.append("%s=%s" % (p, ",".join(str(v) for v in draw_values(rng, p, freq))))
    if chosen and rng.random() < 0.25:
        parts.append("BYSETPOS=" + ",".join(str(v) for v in draw_values(rng, "BYSETPOS", freq)))
    if rng.random() < 0.3:
        parts.append("WKST=" + rng.choice(DAYS))
    end = rng.random()
    if end < 0.3:
        parts.append("COUNT=%d" % rng.randint(1, TAKE))
    return ";".join(parts)


def stamp(t):
    return t.strftime("%Y%m%dT%H%M%S")


def give_up(signum, frame):
    raise TimeoutError()


def main():
    signal.signal(signal.SIGALRM, give_up)
    rng = random.Random(5545)
    rows = []
    tries = 0
    while len(rows) < WANT and tries < 200000:
        tries += 1
        rule = draw(rng)
        start = datetime.datetime(rng.randint(1995, 2030), rng.randint(1, 12), rng.randint(1, 28),
                                  rng.randint(0, 23), rng.choice([0, 15, 30]), rng.choice([0, 30]))
        try:
            r = du.rrulestr("RRULE:" + rule, dtstart=start)
        except Exception:
            continue
        limit = start + datetime.timedelta(days=36525)
        got = []
        signal.setitimer(signal.ITIMER_REAL, 0.2)
        try:
            for o in r:
                if o > limit or len(got) >= TAKE:
                    break
                got.append(o)
        except TimeoutError:
            got = []
        signal.setitimer(signal.ITIMER_REAL, 0)
        if not got or got[0] != start:
            continue
        rows.append("%s|%s|%s" % (stamp(start), rule, ",".join(stamp(g) for g in got)))
    with open(OUT, "w") as f:
        f.write(open(os.path.join(HERE, "dateutil_vectors_head.txt")).read())
        f.write("// DTSTART, the rule, and dateutil's first occurrences, at most %d.\n" % TAKE)
        f.write("fn vectors() -> Str\n    \"%s\"\n" % "\\n".join(rows))
        f.write(open(os.path.join(HERE, "dateutil_vectors_tail.txt")).read())
    print("%d rules kept of %d drawn" % (len(rows), tries))


if __name__ == "__main__":
    main()
