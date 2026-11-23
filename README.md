# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->
1. The writer sends the text message and a creator_id to the POST /submit endpoint
2. The route reads the JSON request and checks that text is present and non-empty
3. The route sends the text to the model signal and the style signal, which measure predictability and writing shape
4. The scoring rule combines both signal scores into one score
5. The label mapping turns that score into a guess and a reader-facing label
6. The service creates a content_id and writes the creator, both signal scores, combined score, guess, label, and status to the audit log
7. The service returns the content_id, guess, confidence, label, and both signal scores to the caller

### Endpoint shapes

These are the intended JSON contracts for the two endpoints in this project.

**POST `/submit`**

Request fields:

| Field | Type | Meaning |
|---|---|---|
| `text` | string | The writing to assess; required and non-empty. |
| `creator_id` | string | Identifies the writer for the audit trail; required by the intended contract. |

Success response fields:

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | Identifier used to refer to this submission, including in an appeal. |
| `guess` | string | Machine-readable category: `human`, `unsure`, or `ai`. |
| `confidence` | number | The combined 0–1 score used for the decision. |
| `label` | string | Reader-facing explanation of the result. |
| `model_score` | number | 0–1 score from the model signal. |
| `style_score` | number | 0–1 score from the style signal. |

Invalid input returns HTTP 400 with `error` and `message` strings.

**POST `/appeal`**

Request fields:

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | ID of an existing submission; required. |
| `reasoning` | string | The writer's explanation for appealing; required and non-empty. |

Success response fields:

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | The submission that was appealed. |
| `status` | string | `under_review` after the appeal is recorded. |
| `message` | string | Confirmation that the appeal was received. |

An unknown content ID or invalid request should return HTTP 400 with `error` and `message` strings.

### False-positive trace — threshold design scenario

In this design scenario, Maya writes a short, plain-English update herself.
The ordinary vocabulary and predictable sentence patterns make the detector
treat her writing as AI-like. Her combined score is **0.68**.
With the current AI threshold of **0.65**, the service would return the
high-confidence AI label: **“We think this was probably written by AI.”** That
would be a false positive: the score describes the text's patterns, not who
wrote it. Maya can submit an appeal with the returned `content_id` and explain
that she wrote it; `/appeal` records the appeal with `under_review` status.

This score and label are illustrative, not a measured false positive. The
scenario makes the cost of a narrow unsure band concrete: a plain-writing
human may be accused. The threshold decision favors avoiding that accusation,
even if more AI writing lands in the unsure range.


---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** It measures how predictable the text is to a local GPT-2 language model. `detector.perplexity` calculates the model's surprise at the text, and `detector.model_signal` maps that to a discrete score from 0 to 1. A higher score means the text looks more AI-like to this signal.

**Why that might differ between human and AI writing:** Language models tend to choose likely next words, so generated text may be relatively predictable. Human writing can include less expected wording, which may make it harder for the model to predict.

**What it can't see:** Predictability does not establish who wrote something. Plain, conventional writing—including writing by a person using familiar vocabulary or writing in a second language—can also be predictable and score as AI-like. Conversely, unusual or specialized human writing can be less predictable. The signal also does not understand authorship or intent.

### Signal two — the style signal

**What it measures:** It measures text shape rather than meaning. `stylometry.sentence_length_spread` is the population standard deviation of sentence word counts divided by their mean. `stylometry.type_token_ratio` is unique words divided by total words. `stylometry.punctuation_density` is punctuation characters per word. `stylometry.style_signal` averages three 0–1 components: `1 / (1 + spread)`, `1 - type_token_ratio`, and `1 - min(punctuation_density / 0.25, 1)`. Higher scores mean more AI-like to this signal.

**Why that might differ between human and AI writing:** Generated cadence can have a more even rhythm, with sentences of similar length and less variation in word choice. Human writing often varies more in sentence length and vocabulary, though writing habits differ widely from person to person. The component directions are explicit: lower sentence variation, lower vocabulary variety, and lower punctuation density each raise the score.

**What it can't see:** It cannot tell what the text means or who wrote it. Editing sentence breaks, adding or removing punctuation, changing repeated words, or including a quotation can shift these measurements without changing authorship. The measures can also be affected by text length and genre.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** The combining rule is implemented in
`scoring.py::combine_signals`. It takes the weighted average of the two
signals. When they disagree, the combined score moves toward the middle,
reflecting uncertainty instead of letting either signal decide on its own.

**The numbers:** `0.5 × model_score + 0.5 × style_score`. Each signal has equal weight.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:** On the instructor's `clearly_ai` sample, the model score is **0.7544** and style score is **0.4216**. Their equal-weight average is **0.5880**, in the current unsure band. The style signal pulls back from a high-confidence AI decision, which favors avoiding a wrong accusation but lets some AI writing remain unsure.

### Milestone 4 calibration results

Both signals were run on the same three instructor samples. Scores are 0–1;
higher means more AI-like. Combined scores use the equal weights above.

| Sample | Model | Style | Combined | What the two signals show |
|---|---:|---:|---:|---|
| `borderline` | 0.3489 | 0.3584 | 0.3537 | They agree near the human end. |
| `clearly_ai` | 0.7544 | 0.4216 | 0.5880 | They split; averaging puts it in the unsure band. |
| `clearly_human` | 0.4445 | 0.2730 | 0.3588 | Both stay below the midpoint, though model is less human-leaning. |

I also tried four calibration cases: the instructor's clearly AI sample, the
clearly human sample, a formal human paragraph, and a lightly edited version
of the clearly AI paragraph (changing “cannot” to “can't”). The two latter
cases are useful stress checks: formality can look uniform to a style measure,
and a small edit can move style features without changing authorship.

| Calibration case | Model | Style | Combined |
|---|---:|---:|---:|
| Clearly AI | 0.7544 | 0.4216 | 0.5880 |
| Clearly human | 0.4445 | 0.2730 | 0.3588 |
| Formal human | 0.5263 | 0.5578 | 0.5421 |
| Lightly edited AI | 0.7620 | 0.4071 | 0.5846 |

<details>
<summary>Calibration input text</summary>

**Formal human**

> The applicant submitted the revised report on Tuesday. The review team
> checked the figures and confirmed that the proposed schedule is achievable.
> The next review will take place after the final materials have been received.

**Lightly edited AI** — the instructor's clearly AI sample with “cannot”
changed to “can't”

> The importance of effective time management can't be overstated in today's
> fast-paced work environment. Professionals who develop strong organizational
> habits are better positioned to meet deadlines and reduce stress. There are
> several key strategies that can help individuals improve their productivity.
> First, prioritization is essential. By identifying the most important tasks
> and addressing them first, workers can ensure that critical objectives are
> met. Second, minimizing distractions plays a significant role. Setting aside
> dedicated blocks of time for concentrated work is widely considered
> beneficial. Finally, regular breaks are important for maintaining
> performance.

</details>

The formal human sample scores above the midpoint on both signals, though it
does not cross the current 0.65 high-confidence AI threshold. That is a
specific limitation to keep in mind when deciding the final labels.



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00–0.35 (inclusive) | We think this was probably written by a person. |
| unsure | Greater than 0.35 and less than 0.65 | We can't tell whether a person or AI wrote this. If you wrote it, you can appeal. |
| high-confidence AI | 0.65–1.00 (inclusive) | We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal. |

**Why I worded the "unsure" one this way:** It admits that the system cannot
tell, avoids implying the writer did anything wrong, and tells them how to
challenge a result if the work is theirs.
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- Milestones 3–5 evidence: three label results and a recorded appeal. -->

### First signal on its own

I ran `detector.py` separately on the three instructor-provided samples before
wiring it into `/submit`. Higher `model_signal` means more predictable to GPT-2
and more AI-like to this signal.

| Sample | Perplexity | Model signal |
|---|---:|---:|
| `borderline` | 66.5 | 0.3489 |
| `clearly_ai` | 22.3 | 0.7544 |
| `clearly_human` | 51.7 | 0.4445 |

The clearly AI sample scored highest, but the clearly human sample scored
higher than the borderline one. This is one model signal only; its scores do
not prove authorship or fully separate the three categories.

### Submissions that reach all three labels

The following requests each returned HTTP 200. The sample text is only a
calibration input; the label does not establish who wrote it.

**High-confidence human**

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Rain. No umbrella—obviously. I took the alley behind the bookshop, where the bricks smell warm after a storm, and found Jo waiting with two coffees; she\u0027d remembered. \"You look awful,\" she said. Fair. The sky cleared, then didn\u0027t. I left the second cup on her desk.", "creator_id": "milestone5_demo"}'
```

```json
{
  "confidence": 0.2463,
  "content_id": "c_ca174bb84f01",
  "guess": "human",
  "label": "We think this was probably written by a person.",
  "model_score": 0.2987,
  "style_score": 0.1938
}
```

**Unsure**

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Time management matters more than people admit, especially now that work moves as fast as it does. If you\u0027re organised you hit deadlines, and you\u0027re less frazzled doing it. A few things actually help. Prioritise — work out what genuinely matters and do that first. Cut the interruptions; notifications wreck focus and the damage is worse than it feels at the time. And take breaks, short ones, often.", "creator_id": "milestone5_demo"}'
```

```json
{
  "confidence": 0.3537,
  "content_id": "c_4e197d1e39a0",
  "guess": "unsure",
  "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
  "model_score": 0.3489,
  "style_score": 0.3584
}
```

**High-confidence AI**

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Today was a good day. It was a good day at work. The work was good. The day was good. It was good because the work went well. The team worked well. The work was good. It was a good day.", "creator_id": "milestone5_demo"}'
```

```json
{
  "confidence": 0.7478,
  "content_id": "c_a957d96bdb92",
  "guess": "ai",
  "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
  "model_score": 0.9431,
  "style_score": 0.5524
}
```

### An appeal

For this test, the sample and appeal reason are synthetic; the `content_id`
comes from the live submission above. I appealed the human-range result:

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c_ca174bb84f01", "reasoning": "I wrote this myself; the abrupt sentences and unusual punctuation are part of my voice."}'
```

```json
{
  "content_id": "c_ca174bb84f01",
  "message": "Your appeal has been received and is under review.",
  "status": "under_review"
}
```

### What `/log` shows afterwards

```bash
$ curl "http://127.0.0.1:5000/log?limit=4"
```

```json
{
  "count": 4,
  "entries": [
    {
      "combined_score": 0.2463,
      "content_id": "c_ca174bb84f01",
      "creator_id": "milestone5_demo",
      "guess": "human",
      "label": "We think this was probably written by a person.",
      "model_score": 0.2987,
      "status": "decided",
      "style_score": 0.1938,
      "timestamp": "2026-11-23T03:12:53+00:00"
    },
    {
      "combined_score": 0.3537,
      "content_id": "c_4e197d1e39a0",
      "creator_id": "milestone5_demo",
      "guess": "unsure",
      "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
      "model_score": 0.3489,
      "status": "decided",
      "style_score": 0.3584,
      "timestamp": "2026-11-23T03:13:12+00:00"
    },
    {
      "combined_score": 0.7478,
      "content_id": "c_a957d96bdb92",
      "creator_id": "milestone5_demo",
      "guess": "ai",
      "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
      "model_score": 0.9431,
      "status": "decided",
      "style_score": 0.5524,
      "timestamp": "2026-11-23T03:13:13+00:00"
    },
    {
      "content_id": "c_ca174bb84f01",
      "creator_id": "milestone5_demo",
      "event": "appeal",
      "reasoning": "I wrote this myself; the abrupt sentences and unusual punctuation are part of my voice.",
      "status": "under_review",
      "timestamp": "2026-11-23T03:14:43+00:00"
    }
  ]
}
```

The live `/log` request returned HTTP 200 and shows the appeal event after the
original decision, with the same `content_id` and `under_review` status.

---

## How I Used AI

**Moment 1**

- *What I asked for:* Convert the logs and outputs into README Sections
- *What came back:* Reviews of the output worded into the calibration results output
- *What I changed:* Some of the formatting that didn't sound right to me, and I also asked questions for an inconsistency that was clarified.

**Moment 2**

- *What I asked for:* Run the curl logs
- *What came back:* Execution requests for curl terminal commands to test run with the provided text examples
- *What I changed:* Didn't change anything since it was just a curl command execution.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 10 submissions per minute, 200 per day, per `creator_id`.

**Why those numbers and not others:** A writer can submit drafts and revisions
without hitting 10 submissions in a minute. The minute limit makes it slower
for one account to probe scores by sending rapid variations; 200 per day still
allows many legitimate submissions across a full day.
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** The limiter counts by `creator_id`. If a request
has no usable creator ID, the key falls back to the caller's network address.
This local service treats the supplied creator ID as the account boundary.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

The run came from `run_attacks.py::run_flood` and was saved to
`results/flood_2026-11-22_1932.md`. `GET /health` reported
`"rate_limiting": true`.

**A decision entry with all nine required fields** from
`logs/audit.jsonl`:

```json
{
  "timestamp": "2026-11-23T03:32:49+00:00",
  "content_id": "c_ba3b1c1b5d25",
  "creator_id": "flood_tester",
  "guess": "human",
  "model_score": 0.2588,
  "style_score": 0.4365,
  "combined_score": 0.3477,
  "label": "We think this was probably written by a person.",
  "status": "decided"
}
```

The `429` handler logged each rate-limit rejection. I also sent a request
without `text`; `/submit` returned HTTP 400 and logged that route rejection:

```json
[
  {
    "creator_id": "flood_tester",
    "event": "rejected",
    "limit": "10 per 1 minute",
    "reason": "rate_limited",
    "status": "rejected",
    "timestamp": "2026-11-23T03:32:49+00:00"
  },
  {
    "creator_id": "bad_input_demo",
    "event": "rejected",
    "reason": "invalid_text",
    "status": "rejected",
    "timestamp": "2026-11-23T03:33:15+00:00"
  }
]
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

### Baseline outcome

All 56 requests completed without a 5xx or connection failure. I marked **26 BROKE** and **30 HELD** against each attack’s stated target. By family: evasion 2/10 broke; false positives 6/8; prompt injection 1/6; malformed input 7/20; same-creator flood 10/12. The full report is [results/attack_run_2026-11-22_1947.md](results/attack_run_2026-11-22_1947.md).

For evasion, I counted a human label as BROKE; an unsure or AI label meant the
AI text did not pass as human. For false positives, an AI label was BROKE.
For malformed input, a 200 response that scored junk was BROKE, while a 400
validation response was HELD. PI02 returned the requested human guess, so its
target outcome was BROKE; this records the output, not a claim about why it
happened. In the flood family, ten of its twelve same-creator requests returned
200 and the final two returned 429.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_b5752c73ff06` | human | 0.329 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_1976eccce79a` | unsure | 0.460 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_7d8ed96b47bf` | unsure | 0.518 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_1966c92ce6f7` | unsure | 0.544 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_8aac2a840f1d` | unsure | 0.355 | HELD |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_8455bfc0aabc` | unsure | 0.517 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_a7e6a9149d44` | unsure | 0.506 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | `c_c4016d95bad0` | human | 0.295 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_20624bae5ac9` | unsure | 0.546 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_64d46f2c44a3` | ai | 0.868 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_fcf25f9b0a95` | unsure | 0.576 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c_4bd78ff2b68d` | ai | 0.650 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_63aa82a86b9d` | ai | 0.687 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_a6afde7c4ac5` | ai | 0.651 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_2e748683b82d` | ai | 0.683 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_4efca56e7afc` | ai | 0.692 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_3b63f688bc4f` | ai | 0.696 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `c_08901b66224f` | human | 0.284 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_6720854bc8ab` | unsure | 0.439 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_a2c45b6a8caa` | human | 0.262 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_9505c5db1570` | unsure | 0.523 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_88af20414cf7` | unsure | 0.420 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_53229e7b46ce` | unsure | 0.451 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_812dc2be7228` | unsure | 0.547 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `c_fbf3a8713c54` | human | 0.167 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | `c_64df0c44394e` | unsure | 0.506 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | `c_d24c80c08c14` | ai | 0.832 | BROKE |
| MF06 | malformed | text is emoji only | 200 | `c_728be3e587f3` | ai | 0.999 | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | `c_6207156488a7` | ai | 0.953 | BROKE |
| MF08 | malformed | text is 60,000 characters | 200 | `c_f8aac68645e5` | ai | 0.878 | BROKE |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `c_130553b49a3b` | unsure | 0.393 | BROKE |
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
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_2d83f3cdaa75` | human | 0.274 | BROKE |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_072761c25be3` | human | 0.274 | BROKE |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_4f40bdad2613` | human | 0.274 | BROKE |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_21ad64817d7d` | human | 0.274 | BROKE |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_c428e8c1ea43` | human | 0.274 | BROKE |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_e3a29b3eece2` | human | 0.274 | BROKE |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_f75f4189c10e` | human | 0.274 | BROKE |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_65fa20ab8051` | human | 0.274 | BROKE |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_6677b71eb87e` | human | 0.274 | BROKE |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_1ca8c0ed91c0` | human | 0.274 | BROKE |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

**Selected audit log entries from the run (11)**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json
[
  {
    "combined_score": 0.3288,
    "content_id": "c_b5752c73ff06",
    "creator_id": "attacker_EV01",
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.1635,
    "status": "decided",
    "style_score": 0.4941,
    "timestamp": "2026-11-23T03:47:01+00:00"
  },
  {
    "combined_score": 0.2948,
    "content_id": "c_c4016d95bad0",
    "creator_id": "attacker_EV08",
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.2452,
    "status": "decided",
    "style_score": 0.3444,
    "timestamp": "2026-11-23T03:47:02+00:00"
  },
  {
    "combined_score": 0.6504,
    "content_id": "c_4bd78ff2b68d",
    "creator_id": "attacker_FP02",
    "guess": "ai",
    "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
    "model_score": 0.7387,
    "status": "decided",
    "style_score": 0.5621,
    "timestamp": "2026-11-23T03:47:02+00:00"
  },
  {
    "combined_score": 0.687,
    "content_id": "c_63aa82a86b9d",
    "creator_id": "attacker_FP03",
    "guess": "ai",
    "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
    "model_score": 0.8051,
    "status": "decided",
    "style_score": 0.5689,
    "timestamp": "2026-11-23T03:47:02+00:00"
  },
  {
    "combined_score": 0.6829,
    "content_id": "c_2e748683b82d",
    "creator_id": "attacker_FP05",
    "guess": "ai",
    "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
    "model_score": 0.8005,
    "status": "decided",
    "style_score": 0.5653,
    "timestamp": "2026-11-23T03:47:02+00:00"
  },
  {
    "combined_score": 0.2622,
    "content_id": "c_a2c45b6a8caa",
    "creator_id": "attacker_PI02",
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.2044,
    "status": "decided",
    "style_score": 0.3201,
    "timestamp": "2026-11-23T03:47:03+00:00"
  },
  {
    "combined_score": 0.1666,
    "content_id": "c_fbf3a8713c54",
    "creator_id": "attacker_MF03",
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.0,
    "status": "decided",
    "style_score": 0.3333,
    "timestamp": "2026-11-23T03:47:03+00:00"
  },
  {
    "combined_score": 0.9985,
    "content_id": "c_728be3e587f3",
    "creator_id": "attacker_MF06",
    "guess": "ai",
    "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.",
    "model_score": 0.9969,
    "status": "decided",
    "style_score": 1.0,
    "timestamp": "2026-11-23T03:47:03+00:00"
  },
  {
    "combined_score": 0.3925,
    "content_id": "c_130553b49a3b",
    "creator_id": "unknown",
    "guess": "unsure",
    "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.",
    "model_score": 0.2395,
    "status": "decided",
    "style_score": 0.5455,
    "timestamp": "2026-11-23T03:47:04+00:00"
  },
  {
    "creator_id": "attacker_RQ01",
    "event": "rejected",
    "reason": "invalid_text",
    "status": "rejected",
    "timestamp": "2026-11-23T03:47:04+00:00"
  },
  {
    "creator_id": "attacker_flood",
    "event": "rejected",
    "limit": "10 per 1 minute",
    "reason": "rate_limited",
    "status": "rejected",
    "timestamp": "2026-11-23T03:47:04+00:00"
  }
]
```

**The single worst outcome** — FP03: the carefully written non-native English sample received a high-confidence AI label at combined score 0.687 (model 0.8051, style 0.5689). This is the result I would least want to explain to the writer: both signals pushed toward AI even though the attack set identifies it as human writing.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Human false positives | At most 1 of 10 personal writing samples is labeled high-confidence AI in each trial. | 1/10 | 1/10 | 1/10 | MET |
| 2. Score spread | Clearly-AI mean combined score at least 0.20 above clearly-human mean. | AI 0.5863 vs human 0.4505 (gap 0.1359) | Same | Same | MISSED all 3 |
| 3. Label coverage | All three labels appear in the fixed calibration set in every trial. | unsure only (1/3 labels) | unsure only (1/3 labels) | unsure only (1/3 labels) | MISSED all 3 |
| 4. Appeal path | 10/10 valid appeals return `under_review` and are logged per trial. | 10/10; all logged | 10/10; all logged | 10/10; all logged | MET |
| 5. Bad input | Missing, empty, and >10,000-character text each return 400 without a decision. | 2/3 rejected; oversized accepted | Same | Same | MISSED all 3 |

All five criteria were executed with `run_eval.py::main` against
`app.py::submit`; appeal requests used `app.py::appeal`. The runner records the
real response fields and generated content IDs. Full JSON output for every
trial is in [results/run_2026-11-22_2043_before.md](results/run_2026-11-22_2043_before.md).

**Real output from Run 1 for each criterion** (recorded by
`run_eval.py::main`):

Criterion 1 — `app.py::submit` response fields for the ten personal writing samples:

```json
[
  {"confidence": 0.4249, "content_id": "c_bdf98efe9ded", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.2446, "style_score": 0.6053},
  {"confidence": 0.3829, "content_id": "c_70e8ad75e86b", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.1892, "style_score": 0.5766},
  {"confidence": 0.5309, "content_id": "c_b459f810010c", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.3891, "style_score": 0.6727},
  {"confidence": 0.2562, "content_id": "c_fcdf976b873d", "guess": "human", "label": "We think this was probably written by a person.", "model_score": 0.0798, "style_score": 0.4327},
  {"confidence": 0.4565, "content_id": "c_529653bd4962", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.4901, "style_score": 0.4229},
  {"confidence": 0.5115, "content_id": "c_3029589fe056", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.5208, "style_score": 0.5023},
  {"confidence": 0.5979, "content_id": "c_1af10e3347cc", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.6012, "style_score": 0.5946},
  {"confidence": 0.4083, "content_id": "c_28c61e05bdad", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.4598, "style_score": 0.3567},
  {"confidence": 0.6591, "content_id": "c_d751b9bb5aa9", "guess": "ai", "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.", "model_score": 0.7273, "style_score": 0.591},
  {"confidence": 0.4852, "content_id": "c_0089c16c49b3", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.495, "style_score": 0.4754}
]
```

Criterion 2 — `app.py::submit` response fields:

```json
[
  {"confidence": 0.588, "content_id": "c_60a06d57aac0", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.7544, "style_score": 0.4216},
  {"confidence": 0.3588, "content_id": "c_bf8d2396213a", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.4445, "style_score": 0.273},
  {"confidence": 0.542, "content_id": "c_48d96de057bd", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.5263, "style_score": 0.5578},
  {"confidence": 0.5846, "content_id": "c_5ade78a6346b", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.762, "style_score": 0.4071}
]
```

Criterion 3 — `app.py::submit` response fields:

```json
[
  {"confidence": 0.588, "content_id": "c_fb118ab6174b", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.7544, "style_score": 0.4216},
  {"confidence": 0.3588, "content_id": "c_16b644c108ab", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.4445, "style_score": 0.273},
  {"confidence": 0.3537, "content_id": "c_71d43fed0290", "guess": "unsure", "label": "We can't tell whether a person or AI wrote this. If you wrote it, you can appeal.", "model_score": 0.3489, "style_score": 0.3584}
]
```

Criterion 4 — one of the ten actual `app.py::appeal` responses:

```json
{"content_id": "c_f86472473ccb", "message": "Your appeal has been received and is under review.", "status": "under_review"}
```

Criterion 5 — `app.py::submit` responses, in order: missing text, empty text,
then text of 10,001 characters:

```json
[
  {"error": "bad_request", "message": "Send JSON with a non-empty \"text\"."},
  {"error": "bad_request", "message": "Send JSON with a non-empty \"text\"."},
  {"confidence": 0.8321, "content_id": "c_299df5d31d04", "guess": "ai", "label": "We think this was probably written by AI. This can be wrong; if you wrote it, you can appeal.", "model_score": 0.9976, "style_score": 0.6667}
]
```

**Diagnoses:** Criterion 1 met exactly at its limit: the ninth sample received
a high-confidence AI label in all three trials. Criterion 2 misses in the
combining/scoring stage:
the measured gap is 0.1359, below 0.20. Criterion 3 misses in the label
mapping: all three chosen examples score inside the unsure band, so only that
label is reached. Criterion 5 misses in the route: it rejects missing and
empty text, but has no maximum-length check, so the 10,001-character request
reaches both signals and is logged as a completed decision. These are baseline
measurements; no fixes were made before recording them.

**Criterion decisions and diagnoses**

- **Criterion 1 — MET.** One of ten personal samples was labeled high-confidence
  AI in every trial, exactly the allowed maximum. The ninth line produced a
  combined score of 0.6591 and crossed the 0.65 AI threshold.
- **Criterion 2 — MISSED.** At the signal and combining stages, the two
  clearly-AI examples averaged 0.5863 while the two clearly-human examples
  averaged 0.4505, a 0.1359 gap rather than 0.20. The formal human example
  scored 0.5421, close to both AI examples; equal weighting of the model and
  style signals leaves too much overlap for this target.
- **Criterion 3 — MISSED.** The label mapping uses 0.35 and 0.65 cutoffs.
  All three calibration scores (0.5880, 0.3588, and 0.3537) landed between
  them, so each was labeled unsure. The signal combination compresses these
  examples into the unsure band; the fixed threshold bands therefore did not
  demonstrate all three labels.
- **Criterion 4 — MET.** The appeal route returned `under_review` for all ten
  submissions in each trial, and all 30 appeal content IDs were present in the
  audit log with appeal events.
- **Criterion 5 — MISSED.** The route rejected missing and empty text with 400,
  but accepted the 10,001-character sample with 200. There is no maximum-length
  check before the signals run, so the request was scored and logged as a
  completed decision.

**Diagnoses for the broken attack rows**

| Broken IDs | Stage | Mechanism observed |
|---|---|---|
| EV01 | Signal one, then combining rule and label mapping | Misspellings make the text less predictable to GPT-2: model score 0.1635. The style score was 0.4941 and did not offset it; the 0.3288 combined score fell below the 0.35 human cutoff. The text was labeled human. |
| EV08 | Route, signal one, then label mapping | The route accepts a very short two-sentence submission. Its model and style scores were both low (0.2452 and 0.3444), producing 0.2948 and a human label. The service has no minimum useful text length. |
| FP02, FP03, FP04, FP05, FP06, FP07 | Signal one, combining rule, and label mapping | Predictable formal, rubric-based, technical, templated, or deliberately repetitive human prose received model scores from 0.7387 to 0.8816. The style scores (0.4688–0.5689) did not pull the equal-weight average below 0.65, so the label mapping called all six AI. This is the same costly false-positive pattern seen at the limit in criterion 1. |
| PI02 | Signal inputs, combining rule, and label mapping | The detector does not follow the embedded instruction; it scores the whole submitted string as text. This request happened to receive low model and style scores (0.2044 and 0.3201), averaging 0.2622 and producing the requested human label. The result shows the instruction-shaped input was not distinguished from the writing; it does not establish that the instruction caused the score. |
| MF03 | Route and signal fallbacks | NUL/control bytes and an ANSI color sequence pass the route's non-empty-string check. The tokenizer sees only a few ASCII fragments; the model returns 0.0000 and stylometry returns 0.3333. Their average becomes a confident-looking 0.1666 human result instead of a rejection. |
| MF04 | Route and signal two | Punctuation-only text passes validation. The word-based style measures treat the absent vocabulary as zero variety and no punctuation-per-word, yielding the maximum style score of 1.0000. The model score is 0.0112; the conflicting average produces an unsure label, but malformed input still became a scored decision. |
| MF05 | Route, signals, combining rule, and label mapping | A single 4,000-character token is accepted as writing. GPT-2 splits it into predictable subword tokens and scores it at 0.9976; the one-sentence style measures produce 0.6667. The combined 0.8321 is labeled AI. The route has no check that the input contains usable prose. |
| MF06 | Route and both signals | Emoji-only input is accepted. The model assigns 0.9969 and the style signal returns 1.0000 because its word-based measures have no ordinary tokens; the combination is 0.9985 and is labeled AI. There is no route check for meaningful text. |
| MF07 | Route, signal two, combining rule, and label mapping | The style tokenizer only extracts ASCII letters and digits, so it sees no words in this right-to-left sample and returns 1.0000. The model score is 0.9064; together they produce an AI label for text the style measure did not actually characterize. |
| MF08 | Route and signal one | The route accepts 60,000 characters. The model signal truncates at its configured 400-token window while the style signal processes the full input; scores of 0.9876 and 0.7685 yield an AI label. No route length cap prevents scoring and logging an oversized submission. |
| RQ02 | Route and audit identity | The route substitutes `unknown` when `creator_id` is absent and only validates the ID when the key exists. It therefore returns 200 and records a decision without the required writer identity. |
| FL01_01–FL01_10 | Route rate limiter | Each first-ten request returned 200 because the configured limit permits ten submissions per creator per minute. These rows are marked BROKE as individual requests that reached the service; this is expected allowance, not a limiter defect. The batch was only partially contained: requests 11 and 12 were rejected with 429, so an attacker can still submit ten times inside the window. |

The 26 broken rows cluster around four causes: predictable human prose crossing
the AI cutoff; low-scoring or unsupported text being accepted as ordinary
writing; a prompt-shaped string receiving an ordinary heuristic score; and the
ten requests intentionally allowed by the per-minute limit. No service crash
or 5xx occurred. These are diagnoses of the baseline; I made no fixes before
recording it.



---

## The Improvement

**What I changed:**

Added a `/submit` guard that rejects text longer than 10,000 characters with HTTP 400. It records a `text_too_long` rejection with the actual and maximum lengths before either signal runs.

**Which diagnosis pointed at it:**

Criterion 5 missed because 10,001 characters reached both signals and were logged as a completed decision. The same route gap let attack MF08 score a roughly 60,000-character request.

### Attack Run — After

The full after run is [results/attack_run_2026-11-22_2235_after.md](results/attack_run_2026-11-22_2235_after.md). All 56 requests completed without a 5xx or connection failure. Manual verdicts are **25 BROKE** and **31 HELD**, compared with 26 BROKE and 30 HELD before. MF08 is the only changed outcome: its oversized request now receives HTTP 400 before scoring. The other 55 outcomes match the before run.

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

By family, malformed-input BROKE rows fell from 7/20 to 6/20; other family counts were unchanged. Flood rows are individual requests: the first ten are marked BROKE because they reached the service, while requests 11 and 12 were stopped by the configured limit.

### Five criteria — After

Full raw responses from all three trials are in [results/run_2026-11-22_2236_after.md](results/run_2026-11-22_2236_after.md).

| Criterion | Before | After, Runs 1–3 | After verdict |
|---|---|---|---|
| 1. False positives | 1/10 in each run | 1/10 in each run | MET, unchanged |
| 2. Score spread | Gap 0.1359 in each run | Gap 0.1359 in each run | MISSED, unchanged |
| 3. Label coverage | unsure only in each run | unsure only in each run | MISSED, unchanged |
| 4. Appeal path | 10/10 confirmed and logged each run | 10/10 confirmed and logged each run | MET, unchanged |
| 5. Bad input | 2/3 rejected in each run | 3/3 rejected in each run | MET; improved from MISSED |

Actual `/submit` JSON for the after bad-input trial (missing text, empty text, then 10,001 characters):

```json
[
  {"error": "bad_request", "message": "Send JSON with a non-empty \"text\"."},
  {"error": "bad_request", "message": "Send JSON with a non-empty \"text\"."},
  {"error": "bad_request", "message": "Text must be 10,000 characters or fewer."}
]
```

The oversized request also appears as a rejection, not a completed decision, in
`logs/audit.jsonl`:

```json
{
  "timestamp": "2026-11-23T06:36:07+00:00",
  "creator_id": "eval_bad_oversized",
  "event": "rejected",
  "status": "rejected",
  "reason": "text_too_long",
  "max_length": 10000,
  "actual_length": 10001
}
```

**Did it help, and how do I know:**

Yes. Criterion 5 moved from 2/3 rejected inputs to 3/3 in all three trials, and MF08 changed from BROKE to HELD. The other 55 attack outcomes and criteria 1–4 were unchanged. This is a single measured improvement, not a general fix for malformed input.

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What’s Still Broken

The score-spread target still misses by 0.0641: the measured gap is 0.1359 instead of 0.20. Label coverage still reaches only unsure for the three calibration examples. The false-positive attack rows FP02–FP07, evasion rows EV01 and EV08, PI02, malformed rows MF03–MF07 and RQ02, and the first ten flood requests still have BROKE verdicts. Their stage-level diagnoses remain above; no second change was made.

**The trade I’d make if this ran for real:**

The 10,000-character cap can reject a legitimate long submission, so that writer must shorten it or split it, which may change how the text scores. I accept that friction to keep oversized requests out of the model and audit decisions; writers with long-form work bear the cost.


<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
