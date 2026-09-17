# rrule-nv

A **recurrence rule** is a compact description of a repeating series of
dates — "every other Tuesday", "the last working day of the month" —
specified as the `RECUR` value type in
[RFC 5545 section 3.3.10](https://www.rfc-editor.org/rfc/rfc5545#section-3.3.10),
the iCalendar standard. This package parses and prints those rules and
generates the dates they describe, in novo-lang. The reference
implementations are the Rust crate [`rrule`](https://docs.rs/rrule) and
Python's [`dateutil.rrule`](https://dateutil.readthedocs.io/en/stable/rrule.html).

**Status: NOT IMPLEMENTED — interface only.** Every function is
declared with its full signature, but every body is a `todo()` that
panics when called. The package is published so its design can be
reviewed and depended on before it is implemented. Version 0.1.0 will
be the first working release.

## What a recurrence rule is

A rule is a list of **parts**, separated by semicolons, each a name and
a value: `FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR`. One part, `FREQ`, is
required and comes first. It names the **frequency**: `SECONDLY`,
`MINUTELY`, `HOURLY`, `DAILY`, `WEEKLY`, `MONTHLY` or `YEARLY`.

`INTERVAL` says how many frequency units lie between one **interval**
and the next. `COUNT` and `UNTIL` say when the rule stops, and RFC 5545
section 3.3.10 forbids both in one rule. A rule with neither generates
occurrences forever.

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

Build and test with `novo pkg build` and `novo test`. Today `novo test`
fails on purpose: every test reaches a
`not implemented: rrule-nv.<module>.<fn>` panic. The tests are the
specification the implementation will have to satisfy.

## What the package contains

| Module | Contents |
| --- | --- |
| `rruleerror` | The eleven refusals, a stable code for each, and which of them only a parser can meet. |
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

1. **`FREQ` is required and comes first.** RFC 5545 section 3.3.10. A
   rule without it is `RruleMissingFreq`.
2. **`COUNT` and `UNTIL` must not both appear.** RFC 5545 section
   3.3.10.
3. **`UNTIL`'s value type must match `DTSTART`'s.** A date-valued start
   takes a date-valued `UNTIL`. RFC 5545 section 3.3.10.
   `rruleset.check_set` reports the mismatch.
4. **Each `BY` part either expands the set or limits it, and which one
   depends on the frequency.** RFC 5545 section 3.3.10 gives the table.
   `rrulespec.part_role` answers for a given rule.
5. **`BYDAY`'s role also depends on the rest of the rule.** Under
   `MONTHLY` it expands on its own and limits beside a `BYMONTHDAY`. So
   `FREQ=MONTHLY;BYDAY=FR;BYMONTHDAY=13` is Friday the 13th, not every
   Friday and every 13th.
6. **`BYSETPOS` is applied last, to one interval's set**, and a rule
   carrying it with no other `BY` part is refused. RFC 5545 section
   3.3.10.
7. **`BYWEEKNO` is only valid under `FREQ=YEARLY`.** RFC 5545 section
   3.3.10.
8. **An ordinal in `BYDAY` is only valid under `MONTHLY` or
   `YEARLY`.** Under a weekly rule there is one of each weekday, so the
   ordinal has nothing to count. RFC 5545 section 3.3.10.
9. **`WKST` changes the answer.** It decides where a week begins, so it
   decides which occurrences of a weekly rule with an interval above
   one fall in which interval, and which week an ISO week number names.
   The default is Monday.
10. **`DTSTART` is always the first occurrence**, whether or not the
    rule would have produced it. RFC 5545 section 3.8.5.3.
    `rruleset.is_synchronized` answers whether the rule would have.
11. **`EXDATE` is applied after `RDATE`**, so a date in both is
    excluded. RFC 5545 section 3.8.5.1.
12. **The recurrence set is a set.** Duplicates are removed, so two
    rules that both produce a Monday produce it once. RFC 5545 section
    3.8.5.3.
13. **A rule with no `COUNT` and no `UNTIL` has infinitely many
    occurrences.** `rruleiter.is_bounded` answers whether a set has
    finitely many, and every call in `rruleiter` that returns a list
    takes a bound as an argument.
14. **Occurrences come out in increasing order**, so two lists may be
    compared directly.
15. **An occurrence is a wall-clock value with no time zone.** See the
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
novo test tests/rrulespec_tests.nv   # the expansion and limitation table, cell by cell
novo test tests/rruleparse_tests.nv  # the grammar both ways, and what it refuses
novo test tests/rruleiter_tests.nv   # DTSTART, RDATE and EXDATE, and the bound
```

The normative source is RFC 5545 section 3.3.10 for the grammar and the
expansion table, and section 3.8.5 for the recurrence set. The vectors
are the worked examples RFC 5545 section 3.8.5.3 prints, recomputed on
a 2026 calendar so that the weekdays can be checked by hand:
2026-01-05 is a Monday and 2026-01-07 a Wednesday.

The suite asserts that `BYMONTH` limits a weekly rule and expands a
yearly one, that `BYDAY` beside a `BYMONTHDAY` limits so that
`FREQ=MONTHLY;BYDAY=FR;BYMONTHDAY=13` is Friday the 13th, that
`BYWEEKNO` under anything but `YEARLY` is refused, that `BYSETPOS`
alone is refused, that an unknown or repeated part is refused rather
than ignored, that `COUNT` and `UNTIL` together are refused, that a
`DTSTART` the rule would not have produced is still the first
occurrence and is reported as unsynchronised, that an `EXDATE` beats an
`RDATE`, and that asking an endless rule for its occurrence count is
refused rather than attempted.

The tests compile today and fail at run, each on the
`not implemented: rrule-nv.<module>.<fn>` panic that is its body. The
suites that build a date reach calendar-nv's own `todo()` first,
because calendar-nv 0.0.2 is an interface as well. That is the expected
state of an interface release. They turn green one at a time as bodies
land.

## Implementation status

| Item | Implemented |
| --- | --- |
| `rruleerror.RruleError` and the other public types | the types are declared |
| `rruleerror.message`, `.code`, `.is_grammar_fault` | no |
| `rrulefreq.freq_name`, `.freq_named`, `.part_name`, `.part_named` | no |
| `rrulefreq.weekday_num`, `.weekday_num_text`, `.weekday_num_parse` | no |
| `rrulefreq.weekday_code`, `.weekday_coded` | no |
| `rrulespec.rule`, `.with_interval`, `.with_end`, `.with_wkst` | no |
| `rrulespec.with_by_day`, `.with_by_month`, `.with_by_monthday`, `.with_by_yearday` | no |
| `rrulespec.with_by_weekno`, `.with_by_setpos`, `.with_by_time` | no |
| `rrulespec.part_role`, `.role_name`, `.is_finite`, `.end_count`, `.check` | no |
| `rruleparse.parse`, `.parse_line`, `.print`, `.print_line` | no |
| `rruleparse.part_names`, `.is_valid`, `.describe`, `.wkst_text` | no |
| `rruleset.set`, `.with_rule`, `.with_rdate`, `.with_exdate` | no |
| `rruleset.dtstart_of`, `.is_date_valued`, `.rule_count` | no |
| `rruleset.is_synchronized`, `.check_set` | no |
| `rruleiter.cursor`, `.cursor_from`, `.cursor_position`, `.step` | no |
| `rruleiter.occurrences`, `.between`, `.after`, `.before` | no |
| `rruleiter.count_occurrences`, `.is_bounded` | no |

## Licence

Apache-2.0. See `LICENSE`.

<!-- docs/writing-a-readme.md is the style guide for this page. -->
