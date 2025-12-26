import matplotlib.pyplot as plt
import scipy.stats as scs
import matplotlib.ticker as mtick
import seaborn as sns
import streamlit as st
from functions import round_decimals_down
from fonts import FONT_DEFAULT, FONT_TITLE


class Bayesian(object):
    """
    A class used to represent test data for Bayesian analysis

    ...

    Attributes
    ---------
    visitors_A, visitors_B : int
        The number of visitors in either variation
    conversions_A, conversions_B : int
        The number of conversions in either variation
    control_cr, variant_cr : float
        The conversion rates for A and B, labelled with A as the control and
        B as the variant
    relative_difference : float
        The percentage difference between A and B

    Methods
    -------
    generate_posterior_samples
        Creates samples for the posterior distributions for A and B
    calculate_probabilities
        Calculate the likelihood that the variants are better
    plot_bayesian_probabilities
        Plots a horizontal bar chart of the likelihood of either variant being
        the winner
    plot_simulation_of_difference
        Plots a histogram showing the distribution of the differences between
        A and B highlighting how much of the difference shows a positve diff
        vs a negative one.

    """

    def __init__(self, visitors_A, conversions_A, visitors_B, conversions_B):
        self.visitors_A = visitors_A
        self.conversions_A = conversions_A
        self.visitors_B = visitors_B
        self.conversions_B = conversions_B
        self.control_cr = conversions_A / visitors_A
        self.variant_cr = conversions_B / visitors_B
        self.relative_difference = self.variant_cr / self.control_cr - 1

    def generate_posterior_samples(self):
        """Creates samples for the posterior distributions for A and B"""

        alpha_prior = 1
        beta_prior = 1

        posterior_A = scs.beta(
            alpha_prior + self.conversions_A,
            beta_prior + self.visitors_A - self.conversions_A,
        )

        posterior_B = scs.beta(
            alpha_prior + self.conversions_B,
            beta_prior + self.visitors_B - self.conversions_B,
        )

        samples = 50000
        self.samples_posterior_A = posterior_A.rvs(samples)
        self.samples_posterior_B = posterior_B.rvs(samples)

    def calculate_probabilities(self):
        """Calculate the likelihood that the variants are better"""

        self.prob_A = (self.samples_posterior_A > self.samples_posterior_B).mean()
        self.prob_B = (self.samples_posterior_A <= self.samples_posterior_B).mean()

    def plot_bayesian_probabilities(self, labels=["A", "B"]):
        """
        Plots a horizontal bar chart of the likelihood of either variant being
        the winner
        """

        fig, ax = plt.subplots(figsize=(10, 4), dpi=150)

        snsplot = ax.barh(
            labels[::-1], [self.prob_B, self.prob_A], color=["#77C063", "#DC362D"]
        )

        # Display the probabilities by the bars
        # Parameters for ax.text based on relative bar sizes
        if self.prob_A < 0.2:
            A_xpos = self.prob_A + 0.01
            A_alignment = "left"
            A_color = "black"
            B_xpos = self.prob_B - 0.01
            B_alignment = "right"
            B_color = "white"
        elif self.prob_B < 0.2:
            A_xpos = self.prob_A - 0.01
            A_alignment = "right"
            A_color = "white"
            B_xpos = self.prob_B + 0.01
            B_alignment = "left"
            B_color = "black"
        else:
            A_xpos = self.prob_A - 0.01
            A_alignment = "right"
            A_color = "white"
            B_xpos = self.prob_B - 0.01
            B_alignment = "right"
            B_color = "white"

        # Plot labels using previous parameters
        ax.text(
            A_xpos,
            snsplot.patches[1].get_y() + snsplot.patches[1].get_height() / 2.1,
            f"{self.prob_A:.2%}",
            horizontalalignment=A_alignment,
            color=A_color,
            **FONT_DEFAULT,
        )
        ax.text(
            B_xpos,
            snsplot.patches[0].get_y() + snsplot.patches[0].get_height() / 2.1,
            f"{self.prob_B:.2%}",
            horizontalalignment=B_alignment,
            color=B_color,
            **FONT_DEFAULT,
        )

        # Title
        ax.text(
            ax.get_xlim()[0],
            ax.get_ylim()[1] * 1.2,
            "Bayesian test result",
            **FONT_TITLE,
        )

        # Subtitle
        ax.text(
            ax.get_xlim()[0],
            ax.get_ylim()[1] * 1.1,
            "The bars show the likelihood of each variant being the better"
            " experience",
            **FONT_DEFAULT,
        )

        ax.xaxis.grid(color="lightgrey")
        ax.set_axisbelow(True)
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(1))
        sns.despine(left=True, bottom=True)
        ax.tick_params(axis="both", which="both", bottom=False, left=False)
        fig.tight_layout()

        st.write(fig)

    def plot_simulation_of_difference(self):
        """
        Plots a histogram showing the distribution of the differences between
        A and B highlighting how much of the difference shows a positve diff
        vs a negative one.
        """

        fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

        difference = self.samples_posterior_B / self.samples_posterior_A - 1

        greater = difference[difference > 0]
        lower = difference[difference < 0]

        sns.histplot(greater, binwidth=0.01, color="#77C063")

        if lower.size != 0:
            lower_limit = round_decimals_down(lower.min())

            sns.histplot(
                lower, binwidth=0.01, binrange=(lower_limit, 0), color="#DC362D"
            )

        ax.get_yaxis().set_major_formatter(
            mtick.FuncFormatter(lambda x, p: format(x / len(difference), ".0%"))
        )

        # Title
        ax.text(
            ax.get_xlim()[0],
            ax.get_ylim()[1] * 1.2,
            "Posterior simulation of the difference",
            **FONT_TITLE,
        )

        # Subtitle
        ax.text(
            ax.get_xlim()[0],
            ax.get_ylim()[1] * 1.12,
            "Highlights the relative difference of the posterior" " distributions",
            **FONT_DEFAULT,
        )

        # Set grid lines as grey and display behind the plot
        ax.yaxis.grid(color="lightgrey")
        ax.set_axisbelow(True)

        # Remove y axis line and label and dim the tick labels
        sns.despine(left=True)
        ax.set_ylabel("")
        ax.tick_params(axis="y", colors="lightgrey")

        ax.set_xlabel("Relative conversion rate increase")
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(1))
        fig.tight_layout()

        st.write(fig)
