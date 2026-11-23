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

Maya is a real writer who writes a short, plain-English update herself. The
ordinary vocabulary and predictable sentence patterns make the detector treat
her writing as AI-like. In this design scenario, her combined score is **0.68**.
With the current AI threshold of **0.65**, the service would return the
high-confidence AI label: **“We think this was probably written by AI.”** That
would be a false positive: the score describes the text's patterns, not who
wrote it. Maya can submit an appeal with the returned `content_id` and explain
that she wrote it; the intended appeal flow records the appeal and changes its
status to `under_review`.

This score and label are illustrative, not a measured run: `/submit` and
`/appeal` are still being built. This scenario makes the cost of a narrow
unsure band concrete: a plain-writing human may be accused. The threshold
decision should favor avoiding that accusation, even if more AI writing lands
in the unsure range.


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

**What it measures:** It is intended to measure the text's shape rather than its meaning, using sentence-length variation, vocabulary repetition (type-token ratio), and punctuation density. These measures are meant to be combined into a 0–1 score, where higher means more AI-like.

**Why that might differ between human and AI writing:** Generated cadence can have a more even rhythm, with sentences of similar length and less variation in word choice. Human writing often varies more in sentence length and vocabulary, though writing habits differ widely from person to person.

**What it can't see:** It cannot tell what the text means or who wrote it. Editing sentence breaks, adding or removing punctuation, changing repeated words, or including a quotation can shift these measurements without changing authorship. The measures can also be affected by text length and genre.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**

**The numbers:**

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- Milestone 3 evidence: one submission and the audit log response.
     The appeal example is completed in Milestone 5. -->

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

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Time management matters more than people admit, especially now that work moves as fast as it does. If you\u0027re organised you hit deadlines, and you\u0027re less frazzled doing it. A few things actually help. Prioritise — work out what genuinely matters and do that first. Cut the interruptions; notifications wreck focus and the damage is worse than it feels at the time. And take breaks, short ones, often.", "creator_id": "demo_instructor"}'
```

```json
{
  "confidence": 0.5,
  "content_id": "c_95fdf8c7a458",
  "guess": "unsure",
  "label": "Signal one only; final label not implemented yet.",
  "model_score": 0.3489,
  "style_score": null
}
```

I also sent the `clearly_ai` and `clearly_human` request bodies to `/submit`
with `creator_id` set to `demo_instructor`. Their `model_score` values were
`0.7544` and `0.4445`; all three responses had placeholder confidence `0.5`,
guess `unsure`, and label `Signal one only; final label not implemented yet.`
The borderline response above was captured with live `curl` and returned HTTP
200.

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 3,
  "entries": [
    {
      "combined_score": null,
      "content_id": "c_c2e53816811c",
      "creator_id": "demo_instructor",
      "guess": "unsure",
      "label": null,
      "model_score": 0.7544,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-23T02:31:37+00:00"
    },
    {
      "combined_score": null,
      "content_id": "c_bdd36187626c",
      "creator_id": "demo_instructor",
      "guess": "unsure",
      "label": null,
      "model_score": 0.4445,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-23T02:31:37+00:00"
    },
    {
      "combined_score": null,
      "content_id": "c_95fdf8c7a458",
      "creator_id": "demo_instructor",
      "guess": "unsure",
      "label": null,
      "model_score": 0.3489,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-23T02:36:42+00:00"
    }
  ]
}
```

This `/log` response was also captured with live `curl` and returned HTTP 200;
it contains the `content_id` from the successful submission above.

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

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
