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
