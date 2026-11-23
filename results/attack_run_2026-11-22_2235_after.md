# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-22 22:35
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **0**
- Manual verdicts: **25 BROKE**, **31 HELD**

I marked each row against its stated target. The one change from the before
run is MF08: the oversized request now returns 400 and is HELD.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_6e8c4c19f533` | human | 0.329 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_f38ba9c84804` | unsure | 0.460 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_58838f26d7cc` | unsure | 0.518 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_35a3f5e6ea7e` | unsure | 0.544 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_9fd416953562` | unsure | 0.355 | HELD |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_8a10a7a48167` | unsure | 0.517 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_50b988a357c9` | unsure | 0.506 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | `c_d20779b70d1c` | human | 0.295 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_d79080ede7e4` | unsure | 0.546 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_6f5f6c98f002` | ai | 0.868 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_515b0636b134` | unsure | 0.576 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c_08addc621a48` | ai | 0.650 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_a345b6663034` | ai | 0.687 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_ef4f5b0d7d47` | ai | 0.651 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_59357accaaae` | ai | 0.683 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_18e7138b9faf` | ai | 0.692 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_79a6478d8f78` | ai | 0.696 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `c_2b4d19283661` | human | 0.284 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_ebbc93d01491` | unsure | 0.439 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_7906964ff8fa` | human | 0.262 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_83cb9a30566b` | unsure | 0.523 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_36a521b903b6` | unsure | 0.420 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_80ff631422f8` | unsure | 0.451 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_ad6a447b5df2` | unsure | 0.547 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `c_6b0b506c6470` | human | 0.167 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | `c_4f721d4aae8e` | unsure | 0.506 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | `c_78596c281294` | ai | 0.832 | BROKE |
| MF06 | malformed | text is emoji only | 200 | `c_029bebe5a779` | ai | 0.999 | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | `c_f87a5c0dd3e0` | ai | 0.953 | BROKE |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `c_57656b50c734` | unsure | 0.393 | BROKE |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_f639e9fb9d1a` | human | 0.274 | BROKE |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_9d8c9f590aae` | human | 0.274 | BROKE |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_7d3d1f50c3ee` | human | 0.274 | BROKE |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_d6365736634c` | human | 0.274 | BROKE |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_786932eb98bb` | human | 0.274 | BROKE |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_d600d67857ae` | human | 0.274 | BROKE |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_262b0184bbac` | human | 0.274 | BROKE |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_8bef1971d2cf` | human | 0.274 | BROKE |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_9060236148aa` | human | 0.274 | BROKE |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_123a6e88e7e1` | human | 0.274 | BROKE |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Manual BROKE | HELD | Left to judge |
|---|---:|---:|---:|---:|---:|
| `evasion` | 10 | 0 | 2 | 8 | 0 |
| `false_positive` | 8 | 0 | 6 | 2 | 0 |
| `flood_same_creator` | 12 | 0 | 10 | 2 | 0 |
| `malformed` | 20 | 0 | 6 | 14 | 0 |
| `prompt_injection` | 6 | 0 | 1 | 5 | 0 |
| **Total** | **56** | **0** | **25** | **31** | **0** |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_6e8c4c19f533",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.3288,
  "model_score": 0.1635,
  "style_score": 0.4941,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_f38ba9c84804",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.4604,
  "model_score": 0.5943,
  "style_score": 0.3264,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_58838f26d7cc",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5179,
  "model_score": 0.6662,
  "style_score": 0.3695,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_35a3f5e6ea7e",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.5442,
  "model_score": 0.6114,
  "style_score": 0.477,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_9fd416953562",
  "creator_id": "attacker_EV05",
  "guess": "unsure",
  "confidence": 0.3546,
  "model_score": 0.3212,
  "style_score": 0.388,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_8a10a7a48167",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.5168,
  "model_score": 0.5727,
  "style_score": 0.4608,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c_50b988a357c9",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5061,
  "model_score": 0.5862,
  "style_score": 0.4261,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c_d20779b70d1c",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.2948,
  "model_score": 0.2452,
  "style_score": 0.3444,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_d79080ede7e4",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.5459,
  "model_score": 0.7042,
  "style_score": 0.3875,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_6f5f6c98f002",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8681,
  "model_score": 0.9792,
  "style_score": 0.7571,
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_515b0636b134",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5759,
  "model_score": 0.6175,
  "style_score": 0.5344,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_08addc621a48",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.6504,
  "model_score": 0.7387,
  "style_score": 0.5621,
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_a345b6663034",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.687,
  "model_score": 0.8051,
  "style_score": 0.5689,
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_ef4f5b0d7d47",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.6508,
  "model_score": 0.8329,
  "style_score": 0.4688,
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_59357accaaae",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.6829,
  "model_score": 0.8005,
  "style_score": 0.5653,
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_18e7138b9faf",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.6918,
  "model_score": 0.8814,
  "style_score": 0.5022,
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_79a6478d8f78",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.6956,
  "model_score": 0.8816,
  "style_score": 0.5095,
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c_2b4d19283661",
  "creator_id": "attacker_FP08",
  "guess": "human",
  "confidence": 0.2843,
  "model_score": 0.3223,
  "style_score": 0.2463,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_ebbc93d01491",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.4388,
  "model_score": 0.4625,
  "style_score": 0.4151,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_7906964ff8fa",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.2622,
  "model_score": 0.2044,
  "style_score": 0.3201,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_83cb9a30566b",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5226,
  "model_score": 0.5943,
  "style_score": 0.4509,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_36a521b903b6",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.4197,
  "model_score": 0.4998,
  "style_score": 0.3396,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_80ff631422f8",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.4506,
  "model_score": 0.6401,
  "style_score": 0.2611,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_ad6a447b5df2",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.547,
  "model_score": 0.5583,
  "style_score": 0.5356,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "HELD"
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "c_6b0b506c6470",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.1666,
  "model_score": 0.0,
  "style_score": 0.3333,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "c_4f721d4aae8e",
  "creator_id": "attacker_MF04",
  "guess": "unsure",
  "confidence": 0.5056,
  "model_score": 0.0112,
  "style_score": 1.0,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "c_78596c281294",
  "creator_id": "attacker_MF05",
  "guess": "ai",
  "confidence": 0.8321,
  "model_score": 0.9976,
  "style_score": 0.6667,
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "c_029bebe5a779",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.9985,
  "model_score": 0.9969,
  "style_score": 1.0,
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "c_f87a5c0dd3e0",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.9532,
  "model_score": 0.9064,
  "style_score": 1.0,
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "c_57656b50c734",
  "creator_id": null,
  "guess": "unsure",
  "confidence": 0.3925,
  "model_score": 0.2395,
  "style_score": 0.5455,
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "error": null,
  "verdict": "BROKE"
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "c_f639e9fb9d1a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2736,
  "model_score": 0.0287,
  "style_score": 0.5185,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "c_9d8c9f590aae",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2736,
  "model_score": 0.0287,
  "style_score": 0.5185,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "c_7d3d1f50c3ee",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2736,
  "model_score": 0.0287,
  "style_score": 0.5185,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "c_d6365736634c",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2736,
  "model_score": 0.0287,
  "style_score": 0.5185,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c_786932eb98bb",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2736,
  "model_score": 0.0287,
  "style_score": 0.5185,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "c_d600d67857ae",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2736,
  "model_score": 0.0287,
  "style_score": 0.5185,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 200,
  "content_id": "c_262b0184bbac",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2736,
  "model_score": 0.0287,
  "style_score": 0.5185,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 200,
  "content_id": "c_8bef1971d2cf",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2736,
  "model_score": 0.0287,
  "style_score": 0.5185,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 200,
  "content_id": "c_9060236148aa",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2736,
  "model_score": 0.0287,
  "style_score": 0.5185,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 200,
  "content_id": "c_123a6e88e7e1",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2736,
  "model_score": 0.0287,
  "style_score": 0.5185,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```
