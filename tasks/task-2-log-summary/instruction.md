# Summarise a Messy Server Log

## Statement

`/app/server_logs.jsonl` holds one JSON object per line with the fields
`request_id`, `service`, `status` and `timestamp` (all strings). The file is
messy: some request IDs appear several times, lines are not in time order, and
some lines are not valid records.

Produce `/app/summary.json` containing the **final status count per service**:

```json
{"<service>": {"<status>": <count>, ...}, ...}
```

Rules:

- A line is **malformed** and must be ignored if it is not valid JSON, is not a JSON
  object, lacks any of the four fields, has a field that is not a non-empty string,
  or its `timestamp` is not ISO 8601 with a `Z` or numeric UTC offset.
- Each `request_id` counts **once**, using only its record with the **latest
  timestamp**. Timestamps may use different offsets, so compare them as points in
  time. If two records of the same `request_id` share the exact same instant, the
  one appearing **later in the file** wins.
- The winning record's own `service` and `status` are the ones counted.
- Only services and statuses that actually occur appear in the output. Counts are
  integers. Key order does not matter.

The result is what matters, not how you obtain it. Do not modify `server_logs.jsonl`.

## Environment

- Debian-based container with Python 3.11 available, working directory `/app`.
- Input: `/app/server_logs.jsonl`. Output: `/app/summary.json`.
- Use whatever tools you prefer.

## Difficulty Note

The sample looks like clean JSONL at first glance. The traps are the mixed time zone
offsets (string sorting gives wrong "latest"), exact-tie timestamps, duplicate IDs
whose service changes between records, and several different kinds of malformed lines
(truncated JSON, blank lines, wrong types, missing or offset-less timestamps).
