# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1.

<!-- Your criterion. It must name a number. -->

Across each of three trials, no more than 1 of 10 human-written calibration
samples is labeled high-confidence AI.

**Why this target:** A false accusation can damage a writer's trust in the
service. Allowing one borderline miss recognizes that a small sample and a
noisy signal cannot guarantee zero false positives, while keeping the target
strict.



---

## 2.

<!-- Your criterion. -->

In each of three trials, the average combined score for the clearly-AI
calibration samples is at least 0.20 higher than the average for the
clearly-human samples.

**Why this target:** The detector should separate clear examples enough to be
useful, while a 0.20 gap leaves room for genuinely ambiguous writing to
overlap instead of pretending the signals can prove authorship.



---

## 3.

<!-- Your criterion. -->

Each of the three labels—high-confidence human, unsure, and high-confidence
AI—is returned by at least one sample in the fixed calibration set in every
trial.

**Why this target:** A label that cannot be reached is dead UI and prevents the
service from communicating the intended range of certainty.



---

## 4.

<!-- Your criterion. -->

For 10 valid appeals with existing content IDs, all 10 responses confirm
`under_review`, and all 10 appeals appear in the audit log with their
content ID and reasoning.

**Why this target:** An appeal is the writer's route to challenge a wrong
decision. Requiring both the status change and a durable record makes it
possible to confirm that the request was received and review it later.



---

## 5.

<!-- Your criterion. -->

Requests with missing `text`, empty `text`, or text longer than 10,000
characters return HTTP 400; none of these rejected requests is sent to either
signal or logged as a completed decision.

**Why this target:** Clear rejection avoids confusing errors and prevents
needless model work on malformed or excessively large submissions. The
10,000-character cap gives a concrete boundary that callers can understand.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
