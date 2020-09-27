from scipy.stats import beta
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import math
import plotly.graph_objects as go
import streamlit as st

roboto = {'fontname': 'Roboto', 'size': '12'}
roboto_title = {'fontname': 'Roboto', 'size': '14', 'weight': 'bold'}
roboto_bold = {'fontname': 'Roboto', 'size': '12', 'weight': 'bold'}
roboto_small = {'fontname': 'Roboto', 'size': '10'}

font = {
    'family': 'sans-serif',
    'sans-serif': 'roboto',
    'size': 11
}

plt.rc('font', **font)


def create_plotly_table(data):
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(data.keys()),
            line_color='white', fill_color='white',
            font=dict(size=12, color='black'),
            align="left",
        ),
        cells=dict(
            values=[data.get(k) for k in data.keys()],
            align="left",
            fill=dict(color=[['#F9F9F9', '#FFFFFF']*5]),
        )
    )
    ])

    fig.update_layout(
        autosize=False,
        height=150,
        margin=dict(
            l=20,
            r=20,
            b=10,
            t=30,
        )
    )

    st.write(fig)


@st.cache
def generate_posterior_samples(
        visitors_A, conversions_A, visitors_B, conversions_B
        ):

    alpha_prior = 1
    beta_prior = 1

    posterior_A = beta(
        alpha_prior + conversions_A,
        beta_prior + visitors_A - conversions_A
    )

    posterior_B = beta(
        alpha_prior + conversions_B,
        beta_prior + visitors_B - conversions_B
    )

    samples = 50000
    samples_posterior_A = posterior_A.rvs(samples)
    samples_posterior_B = posterior_B.rvs(samples)

    return samples_posterior_A, samples_posterior_B


def plot_bayesian_probabilities(probabilities, labels=['A', 'B']):
    fig, ax = plt.subplots(figsize=(10, 4), dpi=150)

    snsplot = ax.barh(
        labels[::-1], probabilities, color=['#77C063', '#DC362D']
        )

    ax.xaxis.grid(color='lightgrey')
    ax.set_axisbelow(True)

    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1))
    sns.despine(left=True, bottom=True)
    ax.tick_params(
        axis='both',
        which='both',
        bottom=False,
        left=False
    )

    ax.text(
        ax.get_xlim()[0],
        ax.get_ylim()[1]*1.2,
        'Bayesian test result',
        **roboto_title
    )

    ax.text(
        ax.get_xlim()[0],
        ax.get_ylim()[1]*1.1,
        'The bars show the likelihood of each variant being the better'
        ' experience',
        **roboto
    )

    prob_A = probabilities[0]
    prob_B = probabilities[1]

    # Value annotations conditional on size of bars
    if prob_A < 0.2:
        A_xpos = prob_A + 0.01
        A_alignment = 'left'
        A_color = 'black'
        B_xpos = prob_B - 0.01
        B_alignment = 'right'
        B_color = 'white'
    elif prob_B < 0.2:
        A_xpos = prob_A - 0.01
        A_alignment = 'right'
        A_color = 'white'
        B_xpos = prob_B + 0.01
        B_alignment = 'left'
        B_color = 'black'
    else:
        A_xpos = prob_A - 0.01
        A_alignment = 'right'
        A_color = 'white'
        B_xpos = prob_B - 0.01
        B_alignment = 'right'
        B_color = 'white'

    ax.text(
        A_xpos,
        snsplot.patches[0].get_y()+snsplot.patches[0].get_height()/2.1,
        f"{prob_A:.2%}",
        horizontalalignment=A_alignment,
        color=A_color,
        **roboto
    )

    ax.text(
        B_xpos,
        snsplot.patches[1].get_y()+snsplot.patches[1].get_height()/2.1,
        f"{prob_B:.2%}",
        horizontalalignment=B_alignment,
        color=B_color,
        **roboto
    )

    fig.tight_layout()

    st.write(fig)


def round_decimals_down(number: float, decimals: int = 2):
    """
    Returns a value rounded down to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.ceil(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor


# Plot with colour split for less/greater than 0
def plot_simulation_of_difference(samples_A, samples_B):

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    difference = samples_B/samples_A-1

    greater = difference[difference > 0]
    lower = difference[difference < 0]

    sns.histplot(
        greater, binwidth=0.01,
        color='#77C063'
    )

    if lower.size != 0:
        lower_limit = round_decimals_down(lower.min())

        sns.histplot(
            lower, binwidth=0.01,
            binrange=(lower_limit, 0),
            color='#DC362D'
        )

    ax.yaxis.grid(color='lightgrey')
    ax.set_axisbelow(True)
    ax.set_ylabel('')

    ax.set_xlabel('Relative conversion rate increase')

    ax.get_yaxis().set_major_formatter(
        mtick.FuncFormatter(lambda x, p: format(x/len(difference), '.0%')))

    sns.despine(left=True)

    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1))

    ax.tick_params(axis=u'both', which=u'both', length=0)
    ax.tick_params(axis='y', colors='lightgrey')

    ax.text(
        ax.get_xlim()[0],
        ax.get_ylim()[1]*1.2,
        'Posterior simulation of the difference',
        **roboto_title
    )

    ax.text(
        ax.get_xlim()[0],
        ax.get_ylim()[1]*1.12,
        'Highlights the relative difference of the posterior distributions',
        **roboto
    )

    fig.tight_layout()

    st.write(fig)
