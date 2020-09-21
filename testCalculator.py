import streamlit as st
from scipy.stats import beta
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import math
import numpy as np
from bayesian_functions import *
from frequentist_functions import *
import plotly.graph_objects as go

roboto = {'fontname': 'Roboto', 'size': '12'}
roboto_title = {'fontname': 'Roboto', 'size': '14', 'weight': 'bold'}
roboto_bold = {'fontname': 'Roboto', 'size': '12', 'weight': 'bold'}
roboto_small = {'fontname': 'Roboto', 'size': '10'}

local_css("style.css")

"""
# AB test calculator

_Enter your test data into the sidebar and choose either a Bayesian or
Frequentist testing approach. Below is Bayesian by default._

---
"""

# Sidebar
st.sidebar.markdown("""
## Approach
""")

method = st.sidebar.radio('Bayesian vs. Frequentist',
                          ['Bayesian', 'Frequentist'])


st.sidebar.markdown("""
## Test data
""")

visitors_A = st.sidebar.number_input("Visitors A", value=80000, step=100)
conversions_A = st.sidebar.number_input("Conversions A", value=1600, step=10)
visitors_B = st.sidebar.number_input("Visitors B", value=80000, step=100)
conversions_B = st.sidebar.number_input("Conversions B", value=1696, step=10)

st.sidebar.markdown("""
## Frequentist settings
""")

alpha = 1 - st.sidebar.selectbox(
    'Significance level',
    [0.90, 0.95, 0.99],
    index=1,
    format_func=percentage_format
)
tails = st.sidebar.selectbox(
    'One vs. two tail',
    ['One-tail', 'Two-tail'],
    index=1
)


# Summary statistics
control_cr = conversions_A/visitors_A
variant_cr = conversions_B/visitors_B

relative_difference = variant_cr/control_cr - 1

control_se = (control_cr*(1-control_cr)/visitors_A)**0.5
variant_se = (variant_cr*(1-variant_cr)/visitors_B)**0.5
se_difference = (control_se**2+variant_se**2)**0.5


# Bayesian Method
if method == 'Bayesian':

    samples_posterior_A, samples_posterior_B = generate_posterior_samples(
        visitors_A, conversions_A, visitors_B, conversions_B)

    prob_A = (samples_posterior_A > samples_posterior_B).mean()
    prob_B = (samples_posterior_A <= samples_posterior_B).mean()

    f"""
    There is a {prob_B:.2%} chance that variant B provides a better experience
    with the expected difference being on average {relative_difference:.2%}
    (relative).
    """

    st.text("")

    plot_bayesian_probabilities(probabilities=[prob_B, prob_A])

    bayesian_data = {
        "<b>Variant</b>": ['A', 'B'],
        "<b>Visitors</b>": [f"{visitors_A:,}", f"{visitors_B:,}"],
        "<b>Conversions</b>": [conversions_A, conversions_B],
        "<b>Conversion rate</b>": [f"{control_cr:.2%}", f"{variant_cr:.2%}"],
        "<b>Uplift</b>": ['', f"{relative_difference:.2%}"],
        "<b>Likelihood of being better</b>": [f"{prob_A:.2%}", f"{prob_B:.2%}"]
    }

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(bayesian_data.keys()),
            line_color='white', fill_color='white',
            font=dict(size=12, color='black'),
            align="left",
        ),
        cells=dict(
            values=[bayesian_data.get(k) for k in bayesian_data.keys()],
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

    """
    The below graph plots the simulated difference between the two posterior
    distributions for the variants. It highlights the potential range of
    difference between the two variants. More data will reduce the range.
    """

    st.text("")

    plot_simulation_of_difference(samples_posterior_A, samples_posterior_B)

else: # Frequentist

    if tails == 'One-tail':
        two_tails=False
        if relative_difference < 0:
            tail_direction = 'right'
        else:
            tail_direction = 'left'
    else:
        two_tails=True
        tail_direction = False

    z_score, p_value = z_test(visitors_A, conversions_A,
                              visitors_B, conversions_B, one_tail=tail_direction)                      

    power = get_power(visitors_A, conversions_A,
                      visitors_B, conversions_B,
                      alpha=alpha, two_tails=two_tails)

    if p_value < alpha:
        t = """
        <h3 class='frequentist_title'>Significant</h3>
        <img class='frequentist_icon' 
            src='https://www.flaticon.com/svg/static/icons/svg/1533/1533913.svg'>
        """
        st.markdown(t, unsafe_allow_html=True)

        if relative_difference < 0:
            t = """
            <p>B's conversion rate is <span class='lower'>"""\
                + '{:.2%}'.format(abs(relative_difference)) + \
                """ lower</span> than A's CR."""
            st.markdown(t, unsafe_allow_html=True)
        else: # higher
            t = """
            <p>B's conversion rate is <span class='higher'>"""\
                + '{:.2%}'.format(abs(relative_difference)) + \
                """ higher</span> than A's CR."""
            st.markdown(t, unsafe_allow_html=True)
        
        f"""
        You can be {1-alpha:.0%} confident that the result is true and due to
        the changes made. There is a {alpha:.0%} that the result is a false
        positive or type I error meaning the result is due to random chance.
        """
        

    else:
        t = """
        <h3 class='frequentist_title'>Not significant</h3>
        <img class='frequentist_icon' 
            src='https://www.flaticon.com/svg/static/icons/svg/1533/1533919.svg'>
        """
        st.markdown(t, unsafe_allow_html=True)

        f"""
        There is not enough evidence to prove that there is a 
        {relative_difference:.2%} difference in the conversion rates between
        variants A and B.
        """
        
        """
        Either collect more data to to achieve greater precision in your test,
        or conclude the test as inconclusive.
        """

    frequentist_data = {
        "<b>Variant</b>": ['A', 'B'],
        "<b>Visitors</b>": [f"{visitors_A:,}", f"{visitors_B:,}"],
        "<b>Conversions</b>": [conversions_A, conversions_B],
        "<b>Conversion rate</b>": [f"{control_cr:.2%}", f"{variant_cr:.2%}"],
        "<b>Uplift</b>": ['', f"{relative_difference:.2%}"],
        "<b>Power</b>": ["", f"{power:.4f}"],
        "<b>Z-score</b>": ["", f"{z_score:.4f}"],
        "<b>P-value</b>": ["", f"{p_value:.4f}"]
    }

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(frequentist_data.keys()),
            line_color='white', fill_color='white',
            font=dict(size=12, color='black'),
            align="left",
        ),
        cells=dict(
            values=[frequentist_data.get(k) for k in frequentist_data.keys()],
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

    z_value_for_alpha = get_z_value(alpha=alpha, two_tailed=two_tails)

    control_cr = conversions_A/visitors_A
    variant_cr = conversions_B/visitors_B

    # standard errors
    control_se = (control_cr*(1-control_cr)/visitors_A)**0.5
    variant_se = (variant_cr*(1-variant_cr)/visitors_B)**0.5

    # standard error of the difference
    se_difference = (control_se**2+variant_se**2)**0.5

    """
    According to the null hypothesis, there is no difference between the means.
    The plot below shows the distribution of the difference of the means that we 
    would expect under the null hypothesis. 
    """

    # Z-test visualisation
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    xA = np.linspace(0-4*se_difference, 0+4*se_difference, 1000)
    yA = scs.norm(0, se_difference).pdf(xA)
    ax.plot(xA, yA, c='#181716')

    diff = variant_cr - control_cr

    ax.axvline(x=diff, ymax=ax.get_ylim()[1],
                 c='tab:orange', alpha=0.5, linestyle='--')
    ax.text(
        ax.get_xlim()[0]+(ax.get_xlim()[1]-ax.get_xlim()[0])*0.8,
        ax.get_ylim()[1]*0.8,
        "Observed\ndifference: {:.2%}".format(
            relative_difference),
        color='tab:orange',
        # rotation=270,
        **roboto
    )

    if tail_direction == 'left':
        ax.fill_between(
            xA, 0, yA,
            where=(
                xA > 0 + se_difference*z_value_for_alpha
            ),
            color='green', alpha=0.2
        )
    elif tail_direction == 'right':
        ax.fill_between(
            xA, 0, yA,
            where=(
                xA < 0 - se_difference*z_value_for_alpha
            ),
            color='green', alpha=0.2
        )
    else:
        ax.fill_between(
            xA, 0, yA,
            where=(
                xA > 0 + se_difference*z_value_for_alpha
            ) | (
                xA < 0 - se_difference*z_value_for_alpha
            ),
            color='green', alpha=0.2
        )

    ax.get_xaxis().set_major_formatter(
        mtick.FuncFormatter(lambda x, p: format(x/control_cr, '.0%')))

    # ax.xaxis.set_major_formatter(mtick.PercentFormatter(1))
    plt.xlabel('Relative difference of the means')
    plt.ylabel('PDF')

    ax.text(
        ax.get_xlim()[0],
        ax.get_ylim()[1]*1.25,
        'Z-test visualisation',
        **roboto_title
    )

    ax.text(
        ax.get_xlim()[0],
        ax.get_ylim()[1]*1.18,
        "Displays the expected distribution of the difference between the means under the null hypothesis.",
        **roboto
    )

    sns.despine(left=True)
    ax.get_yaxis().set_visible(False)
    fig.tight_layout()

    st.write(fig)

    if p_value < alpha:
        f"""
        The shaded areas cover {alpha:.0%} of the distribution. It is because the
        observed mean of the variant falls into this area that we can reject the 
        null hypothesis with {1-alpha:.0%} confidence.
        """
    else:
        f"""
        The shaded areas cover {alpha:.0%} of the distribution. It is because
        the observed mean of the variant does not into this area that we are
        unable to reject the null hypothesis and get a significant result. A 
        difference of greater than 
        {se_difference*z_value_for_alpha/control_cr:.2%} is needed.
        """

    """
    #### Statistical Power
    """

    """
    Power is a measure of how likely we are to detect a difference when there is one
    with 80% being the generally accepted threshold for statistical validity. 
    """

    f"""
    An alternative way of defining power is that it is our likelihood of avoiding
    a Type II error or a false negative. Therefore the inverse of power is 
    1 - {power:.2%} = **{1-power:.2%}** which is our likelihood of a type II error.
    """

    # Power plot
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    
    
    xA = np.linspace(control_cr-4*control_se, control_cr+4*control_se, 1000)
    yA = scs.norm(control_cr, control_se).pdf(xA)
    ax.plot(xA, yA, label='A')
    # ax.axvline(x=control_cr, c='red', alpha=0.5, linestyle='--')
    
    if tail_direction == 'left':
        ax.axvline(
            x=control_cr+control_se*z_value_for_alpha,
            c='tab:blue', alpha=0.5, linestyle='--'
        )
        ax.text(
            control_cr+control_se*z_value_for_alpha,
            max(yA)*0.4,
            "Critical value",
            color='tab:blue',
            rotation=270,
            **roboto_small
        )
    elif tail_direction == 'right':
        ax.axvline(
            x=control_cr-control_se*z_value_for_alpha,
            c='tab:blue', alpha=0.5, linestyle='--'
        )
        ax.text(
            control_cr-control_se*z_value_for_alpha,
            max(yA)*0.4,
            "Critical value",
            color='tab:blue',
            rotation=270,
            **roboto_small
        )
    else:
        ax.axvline(
            x=control_cr-control_se*z_value_for_alpha,
            c='tab:blue', alpha=0.5, linestyle='--'
        )
        ax.text(
            control_cr-control_se*z_value_for_alpha,
            max(yA)*0.4,
            "Critical value",
            color='tab:blue',
            rotation=270,
            **roboto_small
        )

        ax.axvline(
            x=control_cr+control_se*z_value_for_alpha,
            c='tab:blue', alpha=0.5, linestyle='--'
        )
        ax.text(
            control_cr+control_se*z_value_for_alpha,
            max(yA)*0.4,
            "Critical value",
            color='tab:blue',
            rotation=270,
            **roboto_small
        )
    
    ax.text(
        control_cr,
        max(yA)*1.03,
        "A",
        color='tab:blue',
        horizontalalignment='center',
        **roboto_bold
    )

    xB = np.linspace(variant_cr-4*variant_se, variant_cr+4*variant_se, 1000)
    yB = scs.norm(variant_cr, variant_se).pdf(xB)
    ax.plot(xB, yB, label='B')

    ax.text(
        variant_cr,
        max(yB)*1.03,
        "B",
        color='tab:orange',
        horizontalalignment='center',
        **roboto_bold
    )

    if relative_difference > 0:
        ax.fill_between(
            xB, 0, yB,
            where=(xB > control_cr + control_se*z_value_for_alpha),
            color='green', alpha=0.2
        )
    else:
        ax.fill_between(
            xB, 0, yB,
            where=(xB < control_cr - control_se*z_value_for_alpha),
            color='green', alpha=0.2
        )

    ax.text(
        ax.get_xlim()[0]+(ax.get_xlim()[1]-ax.get_xlim()[0])*0.8,
        ax.get_ylim()[1]*0.8,
        f"Power: {power:.2%}",
        horizontalalignment='left',
        **roboto
    )

    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1))
    plt.xlabel('Converted Proportion')

    ax.text(
        ax.get_xlim()[0],
        ax.get_ylim()[1]*1.25,
        'Statistical power',
        **roboto_title
    )

    ax.text(
        ax.get_xlim()[0],
        ax.get_ylim()[1]*1.17,
        "Illustrates the likelihood of avoiding a false negative/type II error",
        **roboto
    )

    sns.despine(left=True)
    ax.get_yaxis().set_visible(False)
    fig.tight_layout()

    st.write(fig)


# TODO: Add frequentist plots to frequentist_functions.py
# TODO: Add references section for both approaches
# FIXME: Enable the plots to handle different sig levels and one vs. two tail
# TODO: Create plots as functions
# TODO: Add explanations and formulas to pages

