# Changelog

All notable changes to rrule-nv are recorded here. The format is
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
package follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the pre-1.0 rule that a breaking change bumps the MINOR number.

## [0.1.0] — 2026-09-27

RFC 5545 recurrence rules: the grammar in both directions, the
expansion table, the recurrence set and its generation.

- The generator is python-dateutil's method: a rule is prepared with
  the parts it leaves out taken from `DTSTART`, and each interval's
  days are filtered by the day parts, crossed with the time parts, and
  cut by `BYSETPOS`.  An interval is computed on its own, so a cursor
  can start at any instant, and the finer frequencies skip the days no
  part keeps.
- All forty-one examples of RFC 5545 section 3.8.5.3 generate the
  occurrences the RFC lists, and three hundred rules drawn at random
  agree with python-dateutil's first occurrences.
- The parser accepts the parts in any order, as RFC 5545 requires, and
  refuses a rule `rrulespec.check` finds a problem in.
- A search for an occurrence stops at the end of the year 9999, so a
  rule no day can satisfy answers no occurrences rather than running
  on.
- The dependency is `calendar-nv ^0.2.0`, and the toolchain floor is
  0.13.0.

Breaking changes against 0.0.1:

- `RruleUntil` carries the value type its `UNTIL` was written in, as a
  new enum `RruleUntilKind`, so `rruleset.check_set` can compare it
  with `DTSTART`'s.
- `RruleError` has four more variants: `RrulePartNotApplicable`,
  `RruleBadValue`, `RruleWrongProperty` and `RruleTimePartWithDate`.
- `RruleCursor` holds the finite part of the set as civil seconds and
  a `floor`, rather than one interval's buffer.
- A `BYMONTHDAY` beside a `BYDAY` under `MONTHLY` expands, as the RFC's
  table says.  The 0.0.1 tests expected it to limit.

## [0.0.1] — 2026-09-17

**The interface, published before anyone implements it.** Every public
type and function carries its full signature, its effect row and its
doc comment; every body is `todo()`; the release is recorded
`implemented = false`.

### Added

- `rrulespec` — the load-bearing interface, and it is
  `part_role(rule, part)`. RFC 5545 section 3.3.10 carries a table
  saying, for each frequency and each `BYxxx` part, whether the part
  EXPANDS the set the frequency generated or LIMITS it. That table is
  the whole of what a rule means, and a wrong cell in it does not
  raise anything: `FREQ=WEEKLY;BYMONTH=1` limits, an implementation
  that expanded it produces one occurrence per January per week, and
  the person who finds out is the one who missed a meeting. So the
  table is published as a total function, the generator is built out
  of it, and the suite checks it against the specification's printed
  copy. It takes the WHOLE RULE and not just the frequency, because
  the table's two footnotes are both about `BYDAY`: under `MONTHLY` it
  expands on its own and limits beside a `BYMONTHDAY`, which is the
  difference between "every Friday and every 13th" and "Friday the
  13th". A signature over the frequency alone cannot give the right
  answer, and every library shaped that way has a special case
  somewhere the table does not explain.
- `rruleiter` — **no function here answers an unbounded list.**
  `FREQ=DAILY` with no `COUNT` and no `UNTIL` is legal, infinite, and
  the first rule anybody writes; a library whose `all()` returns a
  list has exactly one behaviour for it. The unbounded form is the
  cursor, which holds a constant amount of memory, and every
  list-returning call takes a bound in its arguments — a count, or a
  window. `count_occurrences` answers `RruleUnboundedRecurrence`
  rather than trying, and `is_bounded` asks the same question first.
  The generator works an INTERVAL at a time because `BYSETPOS` does:
  "the last weekday of the month" is not a property of an occurrence.
- `rruleset` — a recurrence is a set, not a rule: `DTSTART` anchors,
  `RRULE` generates, `RDATE` adds and `EXDATE` removes, in that order,
  so a date in both `RDATE` and `EXDATE` is excluded. **`DTSTART` is
  always the first occurrence**, which is RFC 5545 section 3.8.5.3's
  normative sentence, even when the rule would never have produced it
  — the case the same section calls undefined and every reference
  implementation answers differently. `is_synchronized` is published
  so a calendar editor can warn when the rule is written rather than
  never, and so a caller who wants the other behaviour can detect it.
- `rruleparse` — two entry points, because `FREQ=WEEKLY` and
  `RRULE:FREQ=WEEKLY` are both called a rule and a parser that takes
  only one fails on half its input. Printing is canonical — the
  specification's order, upper case, defaults omitted — so two rules
  that mean the same thing print the same text and a stored rule can
  be compared as a string. The cost is stated rather than discovered:
  a rule read and printed back is not byte-identical to what arrived.
  An unknown part, a repeated part and an out-of-range value are all
  refused, because each is a rule a lenient parser turns into a
  DIFFERENT rule that runs.
- `rrulefreq` — the frequency, the nine parts as a closed enum, and
  `RruleWeekdayNum`, which carries a weekday AND an ordinal because
  `MO` and `+1MO` are different values and a library modelling `BYDAY`
  as a list of weekdays cannot say "the last Friday of the month".
- `rruleerror` — eleven refusals, with `is_grammar_fault` dividing
  what only a parser can meet from what a rule composed in a program
  reaches just as easily.

### Known

- `novo test` is red, and that is the release's expected state: every
  assertion in the API suite reaches `not implemented:
  rrule-nv.<module>.<fn>`, and the suites that build a date reach
  calendar-nv's own `todo()` first, because calendar-nv 0.0.2 is an
  interface too.
- **There is no time zone here, deliberately.** Every occurrence is a
  civil wall-clock value. Converting one to an instant is tz-nv's job
  and has its own failure mode — twice a year a wall time happened
  twice or never happened — and a recurrence library that folded that
  in could not be `core` and could not be tested without a zone
  database. The README says what a caller does with tz-nv.
- **No `RRULE` description in any language but English.**
  `rruleparse.describe` is English only; a translated description
  needs a message catalogue and a plural rule per language, which is
  i18n-nv's subject.
