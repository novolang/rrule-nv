#!/usr/bin/env python3
"""tools/rfc_examples.py — RFC 5545 section 3.8.5.3's worked examples,
written out as the occurrences each one lists, and checked against
python-dateutil's `rrule` before they are written into
`tests/rfc5545_examples_tests.nv`.

The RFC writes every example in New York time with some `UNTIL` values
in UTC.  This package has no zones, so each `UNTIL` is given here as the
New York wall time it names, which is what a caller converting it with
tz-nv would pass.  One example is written differently: "Every 3 hours
from 9:00 AM to 5:00 PM" has `UNTIL=19970902T170000Z`, which is 13:00 in
New York and would stop after 12:00, while its text and its list say
5:00 PM and include 15:00.  The vector uses 17:00 local.

Run from anywhere:  python3 tools/rfc_examples.py [path to a dateutil wheel]
"""
import datetime, os, sys

if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv[1])
from dateutil import rrule as du

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "tests", "rfc5545_examples_tests.nv")


def d(y, m, day, h=9, mi=0):
    return datetime.datetime(y, m, day, h, mi)


def days(y, m, first, last, h=9):
    return [d(y, m, x, h) for x in range(first, last + 1)]


def listed(y, m, xs, h=9):
    return [d(y, m, x, h) for x in xs]


E = []


def ex(label, start, rule, want):
    E.append((label, start, rule, want))


ex("daily for 10 occurrences", d(1997, 9, 2), "FREQ=DAILY;COUNT=10", days(1997, 9, 2, 11))
ex("daily until December 24, 1997", d(1997, 9, 2), "FREQ=DAILY;UNTIL=19971223T190000",
   days(1997, 9, 2, 30) + days(1997, 10, 1, 31) + days(1997, 11, 1, 30) + days(1997, 12, 1, 23))
ex("every other day", d(1997, 9, 2), "FREQ=DAILY;INTERVAL=2",
   listed(1997, 9, range(2, 31, 2)) + listed(1997, 10, range(2, 31, 2)) + listed(1997, 11, range(1, 30, 2)) + listed(1997, 12, [1, 3]))
ex("every 10 days, 5 occurrences", d(1997, 9, 2), "FREQ=DAILY;INTERVAL=10;COUNT=5",
   listed(1997, 9, [2, 12, 22]) + listed(1997, 10, [2, 12]))
ex("every day in January for 3 years, yearly", d(1998, 1, 1),
   "FREQ=YEARLY;UNTIL=20000131T090000;BYMONTH=1;BYDAY=SU,MO,TU,WE,TH,FR,SA",
   days(1998, 1, 1, 31) + days(1999, 1, 1, 31) + days(2000, 1, 1, 31))
ex("every day in January for 3 years, daily", d(1998, 1, 1), "FREQ=DAILY;UNTIL=20000131T090000;BYMONTH=1",
   days(1998, 1, 1, 31) + days(1999, 1, 1, 31) + days(2000, 1, 1, 31))
ex("weekly for 10 occurrences", d(1997, 9, 2), "FREQ=WEEKLY;COUNT=10",
   listed(1997, 9, [2, 9, 16, 23, 30]) + listed(1997, 10, [7, 14, 21, 28]) + listed(1997, 11, [4]))
ex("weekly until December 24, 1997", d(1997, 9, 2), "FREQ=WEEKLY;UNTIL=19971223T190000",
   listed(1997, 9, [2, 9, 16, 23, 30]) + listed(1997, 10, [7, 14, 21, 28]) + listed(1997, 11, [4, 11, 18, 25])
   + listed(1997, 12, [2, 9, 16, 23]))
ex("every other week", d(1997, 9, 2), "FREQ=WEEKLY;INTERVAL=2;WKST=SU",
   listed(1997, 9, [2, 16, 30]) + listed(1997, 10, [14, 28]) + listed(1997, 11, [11, 25]) + listed(1997, 12, [9, 23])
   + listed(1998, 1, [6, 20]) + listed(1998, 2, [3, 17]))
ex("weekly on Tuesday and Thursday for five weeks, until", d(1997, 9, 2),
   "FREQ=WEEKLY;UNTIL=19971006T200000;WKST=SU;BYDAY=TU,TH",
   listed(1997, 9, [2, 4, 9, 11, 16, 18, 23, 25, 30]) + listed(1997, 10, [2]))
ex("weekly on Tuesday and Thursday for five weeks, count", d(1997, 9, 2), "FREQ=WEEKLY;COUNT=10;WKST=SU;BYDAY=TU,TH",
   listed(1997, 9, [2, 4, 9, 11, 16, 18, 23, 25, 30]) + listed(1997, 10, [2]))
ex("every other week on Monday, Wednesday and Friday", d(1997, 9, 1),
   "FREQ=WEEKLY;INTERVAL=2;UNTIL=19971223T190000;WKST=SU;BYDAY=MO,WE,FR",
   listed(1997, 9, [1, 3, 5, 15, 17, 19, 29]) + listed(1997, 10, [1, 3, 13, 15, 17, 27, 29, 31])
   + listed(1997, 11, [10, 12, 14, 24, 26, 28]) + listed(1997, 12, [8, 10, 12, 22]))
ex("every other week on Tuesday and Thursday, 8 times", d(1997, 9, 2), "FREQ=WEEKLY;INTERVAL=2;COUNT=8;WKST=SU;BYDAY=TU,TH",
   listed(1997, 9, [2, 4, 16, 18, 30]) + listed(1997, 10, [2, 14, 16]))
ex("monthly on the first Friday, 10 times", d(1997, 9, 5), "FREQ=MONTHLY;COUNT=10;BYDAY=1FR",
   [d(1997, 9, 5), d(1997, 10, 3), d(1997, 11, 7), d(1997, 12, 5), d(1998, 1, 2), d(1998, 2, 6), d(1998, 3, 6),
    d(1998, 4, 3), d(1998, 5, 1), d(1998, 6, 5)])
ex("monthly on the first Friday until December 24", d(1997, 9, 5), "FREQ=MONTHLY;UNTIL=19971223T190000;BYDAY=1FR",
   [d(1997, 9, 5), d(1997, 10, 3), d(1997, 11, 7), d(1997, 12, 5)])
ex("every other month on the first and last Sunday, 10 times", d(1997, 9, 7),
   "FREQ=MONTHLY;INTERVAL=2;COUNT=10;BYDAY=1SU,-1SU",
   listed(1997, 9, [7, 28]) + listed(1997, 11, [2, 30]) + listed(1998, 1, [4, 25]) + listed(1998, 3, [1, 29])
   + listed(1998, 5, [3, 31]))
ex("monthly on the second-to-last Monday, 6 times", d(1997, 9, 22), "FREQ=MONTHLY;COUNT=6;BYDAY=-2MO",
   [d(1997, 9, 22), d(1997, 10, 20), d(1997, 11, 17), d(1997, 12, 22), d(1998, 1, 19), d(1998, 2, 16)])
ex("monthly on the third-to-last day", d(1997, 9, 28), "FREQ=MONTHLY;BYMONTHDAY=-3",
   [d(1997, 9, 28), d(1997, 10, 29), d(1997, 11, 28), d(1997, 12, 29), d(1998, 1, 29), d(1998, 2, 26)])
ex("monthly on the 2nd and 15th, 10 times", d(1997, 9, 2), "FREQ=MONTHLY;COUNT=10;BYMONTHDAY=2,15",
   listed(1997, 9, [2, 15]) + listed(1997, 10, [2, 15]) + listed(1997, 11, [2, 15]) + listed(1997, 12, [2, 15])
   + listed(1998, 1, [2, 15]))
ex("monthly on the first and last day, 10 times", d(1997, 9, 30), "FREQ=MONTHLY;COUNT=10;BYMONTHDAY=1,-1",
   [d(1997, 9, 30), d(1997, 10, 1), d(1997, 10, 31), d(1997, 11, 1), d(1997, 11, 30), d(1997, 12, 1),
    d(1997, 12, 31), d(1998, 1, 1), d(1998, 1, 31), d(1998, 2, 1)])
ex("every 18 months on the 10th to the 15th, 10 times", d(1997, 9, 10),
   "FREQ=MONTHLY;INTERVAL=18;COUNT=10;BYMONTHDAY=10,11,12,13,14,15",
   days(1997, 9, 10, 15) + days(1999, 3, 10, 13))
ex("every Tuesday, every other month", d(1997, 9, 2), "FREQ=MONTHLY;INTERVAL=2;BYDAY=TU",
   listed(1997, 9, [2, 9, 16, 23, 30]) + listed(1997, 11, [4, 11, 18, 25]) + listed(1998, 1, [6, 13, 20, 27])
   + listed(1998, 3, [3, 10, 17, 24, 31]))
ex("yearly in June and July, 10 times", d(1997, 6, 10), "FREQ=YEARLY;COUNT=10;BYMONTH=6,7",
   [d(y, m, 10) for y in range(1997, 2002) for m in (6, 7)])
ex("every other year in January to March, 10 times", d(1997, 3, 10), "FREQ=YEARLY;INTERVAL=2;COUNT=10;BYMONTH=1,2,3",
   [d(1997, 3, 10)] + [d(y, m, 10) for y in (1999, 2001, 2003) for m in (1, 2, 3)])
ex("every third year on the 1st, 100th and 200th day, 10 times", d(1997, 1, 1),
   "FREQ=YEARLY;INTERVAL=3;COUNT=10;BYYEARDAY=1,100,200",
   [d(1997, 1, 1), d(1997, 4, 10), d(1997, 7, 19), d(2000, 1, 1), d(2000, 4, 9), d(2000, 7, 18), d(2003, 1, 1),
    d(2003, 4, 10), d(2003, 7, 19), d(2006, 1, 1)])
ex("every 20th Monday of the year", d(1997, 5, 19), "FREQ=YEARLY;BYDAY=20MO",
   [d(1997, 5, 19), d(1998, 5, 18), d(1999, 5, 17)])
ex("Monday of week number 20", d(1997, 5, 12), "FREQ=YEARLY;BYWEEKNO=20;BYDAY=MO",
   [d(1997, 5, 12), d(1998, 5, 11), d(1999, 5, 17)])
ex("every Thursday in March", d(1997, 3, 13), "FREQ=YEARLY;BYMONTH=3;BYDAY=TH",
   listed(1997, 3, [13, 20, 27]) + listed(1998, 3, [5, 12, 19, 26]) + listed(1999, 3, [4, 11, 18, 25]))
ex("every Thursday in June, July and August", d(1997, 6, 5), "FREQ=YEARLY;BYDAY=TH;BYMONTH=6,7,8",
   listed(1997, 6, [5, 12, 19, 26]) + listed(1997, 7, [3, 10, 17, 24, 31]) + listed(1997, 8, [7, 14, 21, 28])
   + listed(1998, 6, [4, 11, 18, 25]) + listed(1998, 7, [2, 9, 16, 23, 30]) + listed(1998, 8, [6, 13, 20, 27])
   + listed(1999, 6, [3, 10, 17, 24]) + listed(1999, 7, [1, 8, 15, 22, 29]) + listed(1999, 8, [5, 12, 19, 26]))
ex("the first Saturday after the first Sunday", d(1997, 9, 13), "FREQ=MONTHLY;BYDAY=SA;BYMONTHDAY=7,8,9,10,11,12,13",
   [d(1997, 9, 13), d(1997, 10, 11), d(1997, 11, 8), d(1997, 12, 13), d(1998, 1, 10), d(1998, 2, 7), d(1998, 3, 7),
    d(1998, 4, 11), d(1998, 5, 9), d(1998, 6, 13)])
ex("U.S. Presidential Election day", d(1996, 11, 5), "FREQ=YEARLY;INTERVAL=4;BYMONTH=11;BYDAY=TU;BYMONTHDAY=2,3,4,5,6,7,8",
   [d(1996, 11, 5), d(2000, 11, 7), d(2004, 11, 2)])
ex("the third of Tuesday, Wednesday or Thursday, 3 times", d(1997, 9, 4), "FREQ=MONTHLY;COUNT=3;BYDAY=TU,WE,TH;BYSETPOS=3",
   [d(1997, 9, 4), d(1997, 10, 7), d(1997, 11, 6)])
ex("the second-to-last weekday of the month", d(1997, 9, 29), "FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-2",
   [d(1997, 9, 29), d(1997, 10, 30), d(1997, 11, 27), d(1997, 12, 30), d(1998, 1, 29), d(1998, 2, 26), d(1998, 3, 30)])
ex("every 3 hours from 9:00 to 17:00", d(1997, 9, 2), "FREQ=HOURLY;INTERVAL=3;UNTIL=19970902T170000",
   [d(1997, 9, 2, 9), d(1997, 9, 2, 12), d(1997, 9, 2, 15)])
ex("every 15 minutes, 6 times", d(1997, 9, 2), "FREQ=MINUTELY;INTERVAL=15;COUNT=6",
   [d(1997, 9, 2, 9, 0), d(1997, 9, 2, 9, 15), d(1997, 9, 2, 9, 30), d(1997, 9, 2, 9, 45), d(1997, 9, 2, 10, 0),
    d(1997, 9, 2, 10, 15)])
ex("every hour and a half, 4 times", d(1997, 9, 2), "FREQ=MINUTELY;INTERVAL=90;COUNT=4",
   [d(1997, 9, 2, 9, 0), d(1997, 9, 2, 10, 30), d(1997, 9, 2, 12, 0), d(1997, 9, 2, 13, 30)])
twenty = [d(1997, 9, day, h, m) for day in (2, 3) for h in range(9, 17) for m in (0, 20, 40)]
ex("every 20 minutes from 9:00 to 16:40, daily", d(1997, 9, 2), "FREQ=DAILY;BYHOUR=9,10,11,12,13,14,15,16;BYMINUTE=0,20,40", twenty)
ex("every 20 minutes from 9:00 to 16:40, minutely", d(1997, 9, 2), "FREQ=MINUTELY;INTERVAL=20;BYHOUR=9,10,11,12,13,14,15,16", twenty)
ex("WKST=MO decides the days", d(1997, 8, 5), "FREQ=WEEKLY;INTERVAL=2;COUNT=4;BYDAY=TU,SU;WKST=MO",
   listed(1997, 8, [5, 10, 19, 24]))
ex("WKST=SU decides them differently", d(1997, 8, 5), "FREQ=WEEKLY;INTERVAL=2;COUNT=4;BYDAY=TU,SU;WKST=SU",
   listed(1997, 8, [5, 17, 19, 31]))
ex("an invalid date is skipped", d(2007, 1, 15), "FREQ=MONTHLY;BYMONTHDAY=15,30;COUNT=5",
   [d(2007, 1, 15), d(2007, 1, 30), d(2007, 2, 15), d(2007, 3, 15), d(2007, 3, 30)])


def stamp(t):
    return t.strftime("%Y%m%dT%H%M%S")


def check(label, start, rule, want):
    text = rule.replace("UNTIL=", "UNTIL=").split(";")
    r = du.rrulestr("RRULE:" + rule, dtstart=start)
    got = list(r[:len(want)])
    if got != want:
        sys.exit("dateutil disagrees with the RFC on %s: %s" % (label, [stamp(g) for g in got]))


def main():
    rows = []
    for label, start, rule, want in E:
        check(label, start, rule, want)
        rows.append("%s|%s|%s|%s" % (label, stamp(start), rule, ",".join(stamp(w) for w in want)))
    with open(OUT, "w") as f:
        f.write(open(os.path.join(HERE, "rfc_examples_head.txt")).read())
        f.write("// Label, DTSTART, the rule, and every occurrence the example lists.\n")
        f.write("fn examples() -> Str\n    \"%s\"\n" % "\\n".join(rows))
        f.write(open(os.path.join(HERE, "rfc_examples_tail.txt")).read())
    print("%d examples, every one agreed by dateutil" % len(E))


if __name__ == "__main__":
    main()
