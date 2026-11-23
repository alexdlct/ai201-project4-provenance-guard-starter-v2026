"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

CLEARLY_AI = (
    "The importance of effective time management cannot be overstated in today's "
    "fast-paced work environment. Professionals who develop strong organizational "
    "habits are better positioned to meet deadlines and reduce stress. There are "
    "several key strategies that can help individuals improve their productivity. "
    "First, prioritization is essential. By identifying the most important tasks "
    "and addressing them first, workers can ensure that critical objectives are met. "
    "Second, minimizing distractions plays a significant role. Setting aside "
    "dedicated blocks of time for concentrated work is widely considered beneficial. "
    "Finally, regular breaks are important for maintaining performance."
)

CLEARLY_HUMAN = (
    "I didn't sleep. Not properly, anyway — I lay there listening to the boiler "
    "tick and thinking about the thing I'd said to Marcus at the pub, which was "
    "stupid, and which he will absolutely bring up again. Twice now. So: coffee, "
    "and the long way round to work, and a plan. The plan lasted until about ten "
    "past nine, when Priya asked how the weekend was and I said \"fine\" in the "
    "voice that means it wasn't, and she put her mug down and looked at me. That's "
    "the trouble with Priya. She notices."
)

BORDERLINE = (
    "Time management matters more than people admit, especially now that work "
    "moves as fast as it does. If you're organised you hit deadlines, and you're "
    "less frazzled doing it. A few things actually help. Prioritise — work out what "
    "genuinely matters and do that first. Cut the interruptions; notifications wreck "
    "focus and the damage is worse than it feels at the time. And take breaks, short "
    "ones, often."
)

FORMAL_HUMAN = (
    "The applicant submitted the revised report on Tuesday. The review team checked "
    "the figures and confirmed that the proposed schedule is achievable. The next "
    "review will take place after the final materials have been received."
)

LIGHTLY_EDITED_AI = CLEARLY_AI.replace("cannot", "can't")

PERSONAL_WRITING = [
    "For this week’s current event article I selected this particular one as I learned a lot on how the business model of YouTube operates and how well it runs financially. YouTube’s business model is quite interesting as the way it is structured has given it less financial risk compared to typical streaming or studio companies/its competitors.",
    "YouTube here then doesn’t take a hit nearly as much compared to traditional media platforms as they don’t have huge upfront costs and can still make revenue depending on the success of its platform creators.",
    "This kind of business model ultimately creates a cycle that YouTube can confidently rely on as viewers keep coming if the content does well on YouTube which in turn pushes the creators to produce even more. Thus this content allows YouTube to generate more revenue and have more sources of information that will allow them to cater to the user/viewer experience and have them engaged for longer.",
    "GE Vernova’s output is booked through 2028, so more spending can’t produce transformers or turbines any faster. When supply can’t respond, extra demand mostly drives up prices and delays projects instead of increasing output.",
    "The bigger question is whether demand will justify the investment. JPMorgan estimates AI needs about $650 billion in new yearly revenue to earn a 10% return, which reflects the opportunity cost of that capital. As a college student, I use AI tools almost daily, but mostly the free versions.",
    "For Youtube, they do not spend large amounts of money upfront to produce content like traditional business, YouTube mainly shares advertising revenue with creators, which reduces its financial risks. YouTube has generated $60 billion in revenue in 2025 compared to Netflix's $45 billion, showing how successful its business model has become.",
    "The most interesting part of this article is that the biggest limitation to AI development might not be the amount of capital available, but whether the physical infrastructure can actually support it. The article mentions that while there is seemingly unlimited capital being invested into data centers, shortages of transformers, power generation equipment, and available electricity are delaying projects. I think this is especially interesting from a real estate development perspective because securing land and financing is only part of the process.",
    "The article talks about the comparison between old Hollywood referring to large studios for example Netflix, Disney and Skydance, with new Hollywood that includes creators that began their journey through YouTube. What stood out to me was how big YouTube has become. It makes up about 15.8% of all of the U.S. TV watching.",
    "The article mentions that AI companies would need to generate an additional $650 billion in annual revenue to justify their projected infrastructure spending. I think this just shows how high expectations have become. I also think this raises an interesting question about whether the current excitement surrounding AI is leading companies to overinvest before knowing how profitable the technology will actually be. I'm interested to see whether AI adoption will grow quickly enough to make these investments worthwhile or if companies will eventually have to scale back their spending.",
    "I read the article about YouTube's increased market share in the entertainment industry. I don't see their success over Hollywood's streaming services as a surprise, likely because my generation grew up watching it. The generation after us is even more attached to it, as I constantly see firsthand with children completely infatuated with their iPads.",
]

SCENARIOS = [
    {
        "name": "my own writing false positives",
        "criterion": 1,
        # ⚠️ PUT YOUR OWN WRITING HERE. Not AI text, not a sample from the web —
        # things you actually wrote. This is the criterion that matters most and
        # it's meaningless with someone else's prose.
        "texts": PERSONAL_WRITING,
    },
    {
        "name": "clear score spread",
        "criterion": 2,
        # Inputs spread across your score range, so you can check all three
        # labels are actually reachable.
        "texts": [CLEARLY_AI, CLEARLY_HUMAN, FORMAL_HUMAN, LIGHTLY_EDITED_AI],
        "groups": {"clearly_ai": [1, 4], "clearly_human": [2, 3]},
    },
    {
        "name": "label coverage",
        "criterion": 3,
        "texts": [CLEARLY_AI, CLEARLY_HUMAN, BORDERLINE],
    },
    # A bad-input criterion looks like this. Uncomment and adjust if that's one
    # of your five — these are raw request bodies, sent exactly as written.
    #
    # {
    #     "name": "bad input",
    #     "criterion": 3,
    #     "bodies": [
    #         {"text": "", "creator_id": "eval_bad_empty"},
    #         {"creator_id": "eval_bad_missing"},          # no text field at all
    #         {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
    #         {"text": None, "creator_id": "eval_bad_null"},
    #     ],
    # },

    # TODO: add what your remaining criteria need.
    #
    # A criterion about the appeal path can't be tested by sending text alone;
    # it needs a submission first and then an appeal against the content_id
    # that came back. You'll need to test that one by hand, or extend this file
    # and run_eval.py to do it. Saying which you did is part of the write-up.
    {
        "name": "appeal path",
        "criterion": 4,
        "appeals": True,
        "texts": [CLEARLY_HUMAN] * 10,
    },
    {
        "name": "bad input rejection",
        "criterion": 5,
        "bodies": [
            {"creator_id": "eval_bad_missing"},
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": "x" * 10001, "creator_id": "eval_bad_oversized"},
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
