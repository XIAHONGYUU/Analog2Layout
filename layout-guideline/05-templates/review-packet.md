# Review Packet — <stage> / <module>

> Source outline for the HTML packet. The HTML generator must embed the latest
> SVG/PNG, metrics, decision cards, check status and approval record. One page
> for the reviewer; details behind links.

```text
stage: A0 | A1 | A2 | A3 | A4 | A5
module:
date:
owner:
status: proposed | review | approved | rejected | waived
decision_required:
recommendation:
```

## 1. Latest result

- Primary image: `<versioned SVG/PNG>`
- Hash: `<sha256>`
- What changed since the last review:

## 2. Metrics

| metric | current | previous | note |
| --- | ---: | ---: | --- |
| bbox (µm) |  |  |  |
| area (µm²) |  |  |  |
| effective area (µm²) |  |  |  |
| utilization |  |  |  |
| aspect |  |  |  |
| gap / margin |  |  |  |

## 3. Checks

| check | severity | status | evidence |
| --- | --- | --- | --- |
|  | HARD / REQUIRED_AT_IP / RECOMMENDED / HEURISTIC / NOT_CHECKED | PASS / FAIL / WAIVED / N/A |  |

Waivers are reviewed together at stage acceptance.

## 4. Decisions

- D-xxx:
- D-xxx:

## 5. Open questions / assumptions

- U-xxx:
- A-xxx:

## 6. Approval

```text
approve / reject / waive:
owner:
date:
reason:
```

## 7. Details

- Geometry JSON:
- Manifest:
- Rule document:
- Freeze record:
