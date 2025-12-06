import io
import base64

from flask import Flask, render_template, request

# --- Matplotlib setup: use non-GUI backend so macOS doesn't crash ---
import matplotlib
matplotlib.use("Agg")  # IMPORTANT: no GUI windows, safe for web apps

import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)

# ---------------------- QUESTIONS CONFIG ---------------------- #
questions = {
    1: {
        "text": "Environmental regulations are strangling business initiatives in the United States.",
        "axis": "economic",
        "value": -1,  # agreeing is conservative (anti-regulation)
    },
    2: {
        "text": "The tax rate ought to be adjusted so that the wealthiest segment of the American population pays more of its fair share.",
        "axis": "economic",
        "value": +1,  # agreeing is liberal (tax the rich)
    },
    3: {
        "text": "Life begins at the moment of conception.",
        "axis": "social",
        "value": -1,  # agreeing is socially conservative
    },
    4: {
        "text": "Burning an American flag should be a protected form of expression under the First Amendment of the Constitution.",
        "axis": "social",
        "value": +1,  # agreeing is liberal / civil-libertarian
    },
    5: {
        "text": "The U.S. made a mistake in going to war in Iraq; it was a reckless enterprise that hurt us in the long run.",
        "axis": "foreign",
        "value": +1,  # agreeing is dovish / liberal
    },
    6: {
        "text": "The breakup of communism in Eastern Europe reflects the success of U.S. strategy in the Cold War; President Reagan’s military buildup and our steadfast resistance to Soviet expansionism over 50 years eventually wore the Russians down.",
        "axis": "foreign",
        "value": -1,  # agreeing is hawkish / conservative
    },
    7: {
        "text": "The best way to sustain economic growth in this country would be to lower personal income taxes across the board.",
        "axis": "economic",
        "value": -1,  # agreeing is conservative (tax cuts)
    },
    8: {
        "text": "American corporations should be prohibited from doing business with countries where there are flagrant abuses of human rights.",
        "axis": "economic",
        "value": +1,  # agreeing is liberal (human-rights-based trade limits)
    },
    9: {
        "text": "A regular moment of prayer in a public school classroom each day should be permitted.",
        "axis": "social",
        "value": -1,  # agreeing is religious conservative
    },
    10: {
        "text": "In the effort to keep America secure, we should never engage in torturing prisoners, even if they are confirmed terrorists.",
        "axis": "social",
        "value": +1,  # agreeing is liberal / civil-libertarian
    },
    11: {
        "text": "The history of the past hundred years confirms the United States to be an imperialist nation.",
        "axis": "foreign",
        "value": +1,  # agreeing is left-critique / dovish
    },
    12: {
        "text": "The U.S. could have won in Vietnam if the politicians had allowed the soldiers to fight the war the way they knew how.",
        "axis": "foreign",
        "value": -1,  # agreeing is hawkish / conservative
    },
    13: {
        "text": "Nuclear power, despite the possible health risks, should be enlarged and expanded to provide cheap and plentiful energy.",
        "axis": "economic",
        "value": -1,  # coded as pro-growth / more conservative here
    },
    14: {
        "text": "“Obamacare” did not go far enough; our nation will never be fully civilized until the federal government can guarantee universal health care.",
        "axis": "economic",
        "value": +1,  # agreeing is strongly liberal
    },
    15: {
        "text": "Children of single parents are less likely to “turn out well” in life than those from a traditional two-parent family.",
        "axis": "social",
        "value": -1,  # agreeing is socially conservative
    },
    16: {
        "text": "The U.S. Supreme Court was correct in making same-sex marriage a legal right in every state.",
        "axis": "social",
        "value": +1,  # agreeing is socially liberal
    },
    17: {
        "text": "Too often the United States has been a bully in pushing around its Latin American neighbors with the threat of military force.",
        "axis": "foreign",
        "value": +1,  # agreeing is dovish / liberal critique
    },
    18: {
        "text": "The United Nations is an example of a noble idea that will never really work.",
        "axis": "foreign",
        "value": -1,  # agreeing is skeptical / conservative
    },
    19: {
        "text": "Lowering the corporate tax rate is a good thing for business and for the country.",
        "axis": "economic",
        "value": -1,  # agreeing is conservative
    },
    20: {
        "text": "The national government needs to redouble its efforts in clamping down on those companies polluting the planet, even if entire industries are less able to compete abroad for a while.",
        "axis": "economic",
        "value": +1,  # agreeing is liberal / pro-regulation
    },
    21: {
        "text": "Taxpayer funds should never be spent in support of obscene and indecent art.",
        "axis": "social",
        "value": -1,  # agreeing is moral conservative
    },
    22: {
        "text": "Tighter restrictions on firearm ownership are required for the safety of our communities.",
        "axis": "social",
        "value": +1,  # agreeing is liberal (gun control)
    },
    23: {
        "text": "The United States should do everything it can to push Israel into a “land-for-peace” settlement with its Palestinian neighbors.",
        "axis": "foreign",
        "value": +1,  # agreeing is dovish / liberal
    },
    24: {
        "text": "The United States remains a shining beacon of democracy in the world community.",
        "axis": "foreign",
        "value": -1,  # coded as patriotic / more conservative
    },
    25: {
        "text": "Although some governmental support of the needy is necessary, the legacy of the welfare state in this country in the last seventy-five years reflects a history of waste, corruption, and misguided efforts to help those who are too lazy to help themselves.",
        "axis": "economic",
        "value": -1,  # agreeing is conservative (anti-welfare-state)
    },
    26: {
        "text": "In order to protect American jobs, the federal government ought to penalize companies that outsource work to foreign countries.",
        "axis": "economic",
        "value": +1,  # agreeing is more economic-populist / left-coded here
    },
    27: {
        "text": "State governments are better equipped than the federal government to address many of the problems facing America today.",
        "axis": "social",
        "value": -1,  # agreeing is “states’ rights” conservative
    },
    28: {
        "text": "Expanded social programs for the poor are the best strategy to prevent inner-city crime, which is largely the result of social conditions, not an individual’s choices.",
        "axis": "social",
        "value": +1,  # agreeing is liberal / structural
    },
    29: {
        "text": "American banks and financial institutions ought to do their best to give debt-ridden “Third World” nations a break in restructuring their loan repayment schedules.",
        "axis": "foreign",
        "value": +1,  # agreeing is liberal / dovish / global-justice
    },
    30: {
        "text": "A steady expansion of the U.S. military should be an important element of American foreign policy in the 21st century.",
        "axis": "foreign",
        "value": -1,  # agreeing is hawkish / conservative
    },
    31: {
        "text": "Amtrak should be privatized; the government cannot afford to subsidize a national railway system that cannot pay for itself.",
        "axis": "economic",
        "value": -1,  # agreeing is conservative / pro-privatization
    },
    32: {
        "text": "One of the greatest threats to America is its growing economic inequality, in which the very richest segment of our population controls more wealth than ever before.",
        "axis": "economic",
        "value": +1,  # agreeing is liberal (concern for inequality)
    },
    33: {
        "text": "Affirmative action programs have gone far enough: they may have made sense in the 1960s, but today they constitute a form of illegal discrimination against whites.",
        "axis": "social",
        "value": -1,  # agreeing is conservative
    },
    34: {
        "text": "We have more to fear from born-again fundamentalist Christians than from counter-culture potheads.",
        "axis": "social",
        "value": +1,  # agreeing is culturally liberal / anti-fundamentalist
    },
    35: {
        "text": "We need to tighten up on the freewheeling covert operations wing of our government; as recent leaks have illustrated, the NSA and similar agencies have too much power.",
        "axis": "foreign",
        "value": +1,  # agreeing is civil-libertarian / dovish toward secrecy
    },
    36: {
        "text": "To enhance our national security and prevent terrorist attacks, the Executive Branch has a legitimate need to intercept communications without having to disclose all its actions to Congress.",
        "axis": "foreign",
        "value": -1,  # agreeing is hawkish / security-first conservative
    },
    37: {
        "text": "Most American labor unions are bloated anachronisms that make life easier for pampered workers while undermining our global competitiveness.",
        "axis": "economic",
        "value": -1,  # agreeing is conservative / anti-union
    },
    38: {
        "text": "The government ought to regulate the financial industry more aggressively; after all, it was the deregulation of financial services that was at the root of the economic recession that started in 2008.",
        "axis": "economic",
        "value": +1,  # agreeing is liberal / pro-regulation
    },
    39: {
        "text": "The notion of legalizing recreational drugs is outlandish.",
        "axis": "social",
        "value": -1,  # agreeing is socially conservative
    },
    40: {
        "text": "Freedom of speech and assembly should be guaranteed for all, even for organizations like the Ku Klux Klan and the American Nazi Party.",
        "axis": "social",
        "value": +1,  # agreeing is civil-libertarian / ACLU-style liberal
    },
    41: {
        "text": "The recent deal the U.S. and other countries reached with Iran is a much more sensible approach than continuing economic sanctions, which only hurt the Iranian people while not changing the regime’s pursuit of a nuclear weapon.",
        "axis": "foreign",
        "value": +1,  # agreeing is dovish / liberal
    },
    42: {
        "text": "We must take a hard line in dealing with Russia, for it looks like those in power in Moscow are trying to rekindle Soviet imperial ambitions.",
        "axis": "foreign",
        "value": -1,  # agreeing is hawkish / conservative
    },
}
# -------------------------------------------------------------- #


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", questions=questions)


@app.route("/result", methods=["POST"])
def result():
    totals = {"social": 0, "economic": 0, "foreign": 0}

    CHOICE_MULTIPLIER = {
        "agree": 1,
        "disagree": -1,
        "dontknow": 0,
    }

    for q_id, info in questions.items():
        field_name = f"q{q_id}"
        choice = request.form.get(field_name, "dontknow")
        multiplier = CHOICE_MULTIPLIER.get(choice, 0)

        axis = info["axis"]
        value = info["value"]
        totals[axis] += multiplier * value

    econ_line_url = make_economic_line_plot(totals)
    plane_url = make_social_economic_plane_plot(totals)

    # No 3D image here – the 3D plot will be done interactively in JS on the page
    return render_template(
        "result.html",
        totals=totals,
        econ_line_url=econ_line_url,
        plane_url=plane_url,
    )


# ---------------------- PLOTTING FUNCTIONS ---------------------- #

def make_economic_line_plot(totals: dict) -> str:
    economic = totals["economic"]
    limit = 12

    fig, ax = plt.subplots(figsize=(6, 1.8))

    # Horizontal axis
    ax.axhline(0, linewidth=1)

    # Vector from center to economic point (1D)
    ax.plot([0, economic], [0, 0], linewidth=2)
    ax.scatter([economic], [0], s=50)

    ax.set_xlim(-limit, limit)
    ax.set_ylim(-1, 1)

    # Remove y-axis
    ax.get_yaxis().set_visible(False)

    # Custom ticks with ABSOLUTE labels (no minus sign)
    ticks = list(range(-limit, limit + 1, 4))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(abs(t)) for t in ticks])

    ax.set_xlabel("Economic rating")

    # Show actual signed value above the point
    ax.text(economic, 0.25, f"{economic}", ha="center")

    # Ideology labels on the economic axis
    ax.text(-limit, -0.5, "Conservative", ha="left", va="center")
    ax.text(limit, -0.5, "Liberal", ha="right", va="center")

    plt.tight_layout()
    return fig_to_base64(fig)



def make_social_economic_plane_plot(totals: dict) -> str:
    economic = totals["economic"]
    social = totals["social"]
    limit = 12

    fig, ax = plt.subplots(figsize=(5, 5))

    # Axes lines
    ax.axhline(0, linewidth=1)
    ax.axvline(0, linewidth=1)

    # # Vector from origin to (economic, social)
    # ax.quiver(
    #     0, 0,
    #     economic, social,
    #     angles="xy",
    #     scale_units="xy",
    #     scale=1,
    #     width=0.008,
    # )

    # # Point at the tip
    ax.scatter([economic], [social], s=50)

    # Optional projections to axes
    ax.plot([economic, economic], [0, social], linestyle="--")
    ax.plot([0, economic], [social, social], linestyle="--")

    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)

    ax.set_xlabel("Economic")
    ax.set_ylabel("Social")

    # Custom ticks with ABSOLUTE labels (no minus sign)
    ticks = list(range(-limit, limit + 1, 4))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(abs(t)) for t in ticks])
    ax.set_yticks(ticks)
    ax.set_yticklabels([str(abs(t)) for t in ticks])

    # Quadrant labels
    ax.text(+limit * 0.5, +limit * 0.5, "Liberal",      ha="center", va="center")
    ax.text(-limit * 0.5, +limit * 0.5, "Libertarian",  ha="center", va="center")
    ax.text(-limit * 0.5, -limit * 0.5, "Conservative", ha="center", va="center")
    ax.text(+limit * 0.5, -limit * 0.5, "Populist",     ha="center", va="center")

    # Economic side labels
    # ax.text(-limit, -limit * 0.05, "Conservative", ha="left", va="top")
    # ax.text(limit, -limit * 0.05, "Liberal", ha="right", va="top")

    # Coordinate label at the point
    ax.text(
        economic,
        social,
        f"({economic}, {social})",
        ha="left",
        va="bottom",
    )

    plt.tight_layout()
    return fig_to_base64(fig)



def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    image_png = buf.getvalue()
    buf.close()
    plt.close(fig)
    return base64.b64encode(image_png).decode("ascii")


if __name__ == "__main__":
    app.run(debug=True)
