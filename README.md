# rrule-nv

A **recurrence rule** is a compact description of a repeating series of
dates — "every other Tuesday", "the last working day of the month" —
specified as the `RECUR` value type in
[RFC 5545 section 3.3.10](https://www.rfc-editor.org/rfc/rfc5545#section-3.3.10),
the iCalendar standard. This package parses and prints those rules and
generates the dates they describe, in novo-lang. The reference
implementations are the Rust crate [`rrule`](https://docs.rs/rrule) and
Python's [`dateutil.rrule`](https://dateutil.readthedocs.io/en/stable/rrule.html).

## What a recurrence rule is

A rule is a list of **parts**, separated by semicolons, each a name and
a value: `FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR`. One part, `FREQ`, is
required and comes first. It names the **frequency**: `SECONDLY`,
`MINUTELY`, `HOURLY`, `DAILY`, `WEEKLY`, `MONTHLY` or `YEARLY`.

`INTERVAL` says how many frequency units lie between one **interval**
and the next. `COUNT` and `UNTIL` say when the rule stops, and RFC 5545
section 3.3.10 forbids both in one rule. A rule with neither generates
occurrences forever. RFC 5545 asks for `FREQ` first for older readers
and requires a reader to accept the parts in any order, and this
package does both.

Nine further parts begin with `BY`. Each takes a list of values.

| Part | Values |
| --- | --- |
| `BYSECOND` | 0 to 60 |
| `BYMINUTE` | 0 to 59 |
| `BYHOUR` | 0 to 23 |
| `BYDAY` | a weekday, optionally with an ordinal: `MO`, `+1MO`, `-1SU` |
| `BYMONTHDAY` | 1 to 31, or -31 to -1 |
| `BYYEARDAY` | 1 to 366, or -366 to -1 |
| `BYWEEKNO` | 1 to 53, or -53 to -1, only under `FREQ=YEARLY` |
| `BYMONTH` | 1 to 12 |
| `BYSETPOS` | 1 to 366, or -366 to -1 |

Each `BY` part does one of two things to the set of dates the frequency
generated. It **expands** the set, producing one date per value, or it
**limits** the set, keeping only the dates that agree with one of its
values. Which of the two it does depends on the frequency, and RFC 5545
section 3.3.10 gives the answer in a table. `BYSETPOS` is different: it
is applied last, to the set the other parts produced for one interval,
and selects by position.

A rule does not describe a series on its own. RFC 5545 section 3.8.5
builds the **recurrence set** from four properties: `DTSTART` is the
first occurrence and the anchor, `RRULE` generates, `RDATE` adds
individual dates and `EXDATE` removes them. Exclusion is applied last.

Every date in this package is one of
[calendar-nv](https://novo-lang.org/packages/calendar-nv)'s civil
values: a wall clock, with no time zone. That is what a recurrence
means. A daily 09:00 meeting stays at 09:00 across a daylight-saving
change, and the instant it names moves by an hour.

## Install

```
novo pkg add rrule-nv
```

rrule-nv needs a novo-lang toolchain of 0.13.0 or newer.

## Example

```novo
use civil
use rruleiter
use rruleparse
use rruleset

fn main() [io]
    // Where the series starts. The time of day travels with it.
    match civil.date(2026, 1, 5)
        Err(_) => println("not a date")
        Ok(start) =>
            // Every other week on Monday, Wednesday and Friday.
            match rruleparse.parse("FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR")
                Err(_) => println("not a recurrence rule")
                Ok(rule) =>
                    let at = civil.datetime(start, civil.midnight())
                    let series = rruleset.with_rule(rruleset.set(at, true), rule)
                    // The bound is an argument. There is no call here
                    // that runs forever.
                    for o in rruleiter.occurrences(series, 6)
                        println("${o.date.year}-${o.date.month}-${o.date.day}")
```

Build with `novo pkg build` and run the suites with `novo test`.

## What the package contains

| Module | Contents |
| --- | --- |
| `rruleerror` | The fifteen refusals, a stable code for each, and which of them only text can carry. |
| `rrulefreq` | The frequency, the nine `BY` parts, and the weekday-with-an-ordinal that `BYDAY` is made of. |
| `rrulespec` | The rule as a value, its builders, and the table saying what each part does in it. |
| `rruleparse` | The `RECUR` grammar in both directions, and an English description. |
| `rruleset` | A `DTSTART` with its rules, added dates and removed dates. |
| `rruleiter` | Generating the occurrences: a cursor, a bounded list, a window, and the neighbours of an instant. |

## How to choose an entry point

**`rruleparse.parse` takes a `RECUR` value**, such as
`FREQ=DAILY;COUNT=3`. `parse_line` takes a whole iCalendar content
line, such as `RRULE:FREQ=DAILY;COUNT=3`.

**`rrulespec.rule` builds a rule in a program**, with one `with_`
function per part.

**`rruleiter.occurrences` answers the first `n` occurrences.** Use it
when a fixed number is wanted.

**`rruleiter.between` answers every occurrence in a window.** Use it
for a calendar view, which knows the dates it is painting.

**`rruleiter.cursor` and `rruleiter.step` walk the series one date at a
time.** They are the only form that works for a rule with no end.

**`rruleiter.after` answers the next occurrence.** A scheduler that
knows where it is calls this and nothing else.

## The rules a user needs

1. **`FREQ` is required.** RFC 5545 section 3.3.10. A
   rule without it is `RruleMissingFreq`.
2. **`COUNT` and `UNTIL` must not both appear.** RFC 5545 section
   3.3.10.
3. **`UNTIL`'s value type must match `DTSTART`'s.** A date-valued start
   takes a date-valued `UNTIL`. RFC 5545 section 3.3.10.
   `rruleset.check_set` reports the mismatch. A date `UNTIL` includes
   the whole of its day. An `UNTIL` written in UTC is compared with the
   wall-clock occurrences as written, so a caller whose `DTSTART` has a
   time zone converts it to that zone's wall time first.
4. **Each `BY` part either expands the set or limits it, and which one
   depends on the frequency.** RFC 5545 section 3.3.10 gives the table.
   `rrulespec.part_role` answers for a given rule.
5. **`BYDAY`'s role also depends on the rest of the rule.** Under
   `MONTHLY` it expands on its own and limits beside a `BYMONTHDAY`. So
   `FREQ=MONTHLY;BYDAY=FR;BYMONTHDAY=13` is Friday the 13th, not every
   Friday and every 13th. Under `YEARLY` an ordinal counts within the
   month when `BYMONTH` is present and within the year otherwise, so
   `FREQ=YEARLY;BYDAY=20MO` is the twentieth Monday of the year.
6. **A part the table marks not applicable is refused.** `BYYEARDAY`
   under `DAILY`, `WEEKLY` or `MONTHLY`, and `BYMONTHDAY` under
   `WEEKLY`, are `RrulePartNotApplicable`.
7. **`BYSETPOS` is applied last, to one interval's set**, and a rule
   carrying it with no other `BY` part is refused. RFC 5545 section
   3.3.10.
8. **`BYWEEKNO` is only valid under `FREQ=YEARLY`.** RFC 5545 section
   3.3.10.
9. **An ordinal in `BYDAY` is only valid under `MONTHLY` or
   `YEARLY`.** Under a weekly rule there is one of each weekday, so the
   ordinal has nothing to count. RFC 5545 section 3.3.10.
10. **`WKST` changes the answer.** It decides where a week begins, so it
    decides which occurrences of a weekly rule with an interval above
    one fall in which interval, and which week an ISO week number names.
    The default is Monday.
11. **`DTSTART` is always the first occurrence**, whether or not the
    rule would have produced it, and a `COUNT` counts it. RFC 5545
    section 3.8.5.3. `rruleset.is_synchronized` answers whether the rule
    would have. python-dateutil does not yield an unsynchronised
    `DTSTART`, so the two libraries differ for such a set.
12. **The parts a rule leaves out come from `DTSTART`.** A yearly rule
    with no day part recurs on `DTSTART`'s month and day, a monthly one
    on its day of the month, and a weekly one on its weekday. Every
    frequency coarser than a second takes the time of day it does not
    name from `DTSTART`. A day that does not exist is skipped: the 30th
    of a monthly rule has no February occurrence.
13. **`EXDATE` is applied after `RDATE`**, so a date in both is
    excluded. RFC 5545 section 3.8.5.1.
14. **The recurrence set is a set.** Duplicates are removed, so two
    rules that both produce a Monday produce it once. RFC 5545 section
    3.8.5.3.
15. **A rule with no `COUNT` and no `UNTIL` has infinitely many
    occurrences.** `rruleiter.is_bounded` answers whether a set has
    finitely many, and every call in `rruleiter` that returns a list
    takes a bound as an argument.
16. **Occurrences come out in increasing order**, so two lists may be
    compared directly.
17. **A generator stops at the end of the year 9999.** A rule whose
    parts no day satisfies, such as `FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=30`,
    has no occurrences, and a search for one ends there. Times are whole
    seconds: the nanoseconds of a `DTSTART` are dropped.
18. **An occurrence is a wall-clock value with no time zone.** See the
    next section.

## Time zones

This package has none, and the omission is the design.

RFC 5545 defines a recurrence on the local calendar. `FREQ=DAILY` from
a 09:00 start means 09:00 every day, on the wall clock, and the
instants those wall times name are not a fixed distance apart: twice a
year one of them moves by an hour.

So every occurrence here is a
[calendar-nv](https://novo-lang.org/packages/calendar-nv) `CivilDateTime`,
which is a date and a time of day and nothing else. A caller that needs
an instant converts each occurrence with
[tz-nv](https://novo-lang.org/packages/tz-nv), which is where the two
cases a conversion can meet are answered: a wall time that happened
twice, and a wall time that did not happen at all.

The consequence for a caller is that a year of occurrences can be
generated in a test with no clock and no time-zone database.

## What is not included

- **Time zones.** See above.
- **A clock.** No function here asks what time it is.
  `rruleiter.after` takes the instant to search from.
- **`EXRULE`.** RFC 5545 deprecated it in section 3.8.5.2 and the
  successor specification removed it. A caller reading an old calendar
  that carries one generates its occurrences separately and passes them
  as `EXDATE` values.
- **The rest of iCalendar.** Folding, escaping, parameters and the
  `VEVENT` object model are
  [ical-nv](https://novo-lang.org/packages/ical-nv)'s.
- **Descriptions in other languages.** `rruleparse.describe` writes
  English. A translated description needs a message catalogue and a
  plural rule per language, which is
  [i18n-nv](https://novo-lang.org/packages/i18n-nv)'s subject.
- **Reading a calendar file.** Opening a file costs `[fs]`, and this
  package declares no effects.

## Related packages

- [calendar-nv](https://novo-lang.org/packages/calendar-nv) supplies
  every date type used here. This package depends on it.
- [ical-nv](https://novo-lang.org/packages/ical-nv) is the iCalendar
  object model, and it depends on this package for the `RRULE`
  property. Take it when reading or writing a `.ics` file; take this
  one when the rule is all that is wanted.
- [tz-nv](https://novo-lang.org/packages/tz-nv) turns a wall-clock
  occurrence into an instant. See the Time zones section.
- [cron-nv](https://novo-lang.org/packages/cron-nv) is the other
  recurrence grammar. A cron expression describes when to run a job and
  has no start date; a recurrence rule describes a series anchored at
  one. Take cron-nv for a scheduler, this package for a calendar.
- [chrono-nv](https://novo-lang.org/packages/chrono-nv) reads the
  clock. Take it to find out what time it is, then pass the answer in.

## Tests

```bash
novo test tests/rrulespec_tests.nv          #  7 tests: the table's footnotes, the defaults, the checks
novo test tests/table_tests.nv              #  6 tests: the whole table, every check, every name and refusal
novo test tests/rruleparse_tests.nv         #  5 tests: the grammar both ways, and what it refuses
novo test tests/grammar_tests.nv            #  4 tests: every value read and refused, the print, the sentence
novo test tests/rruleiter_tests.nv          #  6 tests: DTSTART, RDATE and EXDATE, and the bound
novo test tests/generator_tests.nv          # 11 tests: the generator at its edges
novo test tests/rfc5545_examples_tests.nv   #  1 test:  every example RFC 5545 section 3.8.5.3 prints
novo test tests/dateutil_vectors_tests.nv   #  1 test:  300 rules drawn at random, against python-dateutil
bash tests/coverage.sh                      # 815 of 815 lines of src/, merged over the suites
```

The normative source is RFC 5545 section 3.3.10 for the grammar and the
expansion table, and section 3.8.5 for the recurrence set.
`tests/rfc5545_examples_tests.nv` holds all forty-one examples section
3.8.5.3 prints, with every occurrence each one lists, written by
`tools/rfc_examples.py`. The RFC writes them in New York time with some
`UNTIL` values in UTC, and each `UNTIL` there is the New York wall time
it names.

`tools/dateutil_vectors.py` draws rules at random with a fixed seed,
expands each with python-dateutil's `rrule`, and writes the first twelve
occurrences into `tests/dateutil_vectors_tests.nv`. It keeps a rule only
when both libraries give it one meaning: every part allowed under its
frequency, and a `DTSTART` the rule produces. The suites need no Python
when they run. `tests/generator_tests.nv` takes its series from
python-dateutil too.

## Licence

Apache-2.0. See `LICENSE`.

<!-- docs/writing-a-readme.md is the style guide for this page. -->
