import numpy as np
import pandas as pd
import scipy.stats as scs
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
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


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)


def percentage_format(x):
    return f"{x:.0%}"



def z_test(visitors_A, conversions_A, visitors_B, conversions_B, tails='two'):
    """ Run a Z-test with your data, returning the Z-score and p-value.

    Parameters
    ---------
    visitors_A, visitors_B : int
        Number of sessions/users

    conversions_A, conversions_B : int
        Number of conversions

    tails : ['two', 'left', 'right'] (optional)
        Specify what type of test; if 'two' (default), the p-value for a two-tail
        Z-test will be returned.
        'left' specifies a one-tail Z-test where the alternative hypothesis is that
        the variant will return a better conversion rate, 'right' is the opposite.

    Returns
    -------
    z_score : float
        Number of standard deviations between the mean of the control conversion
        rate distribution and the variant conversion rate
    p_value : float
        Probability of obtaining test results at least as extreme as the observed
        results, under the conditions of the null hypothesis
    """

    # conversion rates
    control_cr = conversions_A/visitors_A
    variant_cr = conversions_B/visitors_B

    combined_cr = (conversions_A + conversions_B)/(visitors_A + visitors_B)
    combined_se = (combined_cr*(1-combined_cr) *
                   (1/visitors_A + 1/visitors_B))**0.5

    # z-score
    z_score = (variant_cr - control_cr)/combined_se

    # Calculate the p-value dependent on one or two tails
    if tails == 'left':
        p_value = scs.norm.cdf(-abs(z_score))
    elif tails == 'right':
        p_value = scs.norm.cdf(abs(z_score))
    else:
        p_value = 2*scs.norm.cdf(-abs(z_score))

    return z_score, p_value


def get_power(visitors_A, conversions_A, visitors_B, conversions_B, alpha=0.05, two_tails=True):
    """Returns observed power from test results.

    Parameters
    ---------
    visitors_A, visitors_B : int
        Number of sessions/users

    conversions_A, conversions_B : int
        Number of conversions

    alpha : float
        Default = 0.05
        Type I error level
    
    two_tails : boolean (optional)
        Default = True
        One or two-tail test

    Returns
    -------
    power
    """

    n = visitors_A + visitors_B

    control_cr = conversions_A/visitors_A
    variant_cr = conversions_B/visitors_B

    if two_tails:
        qu = scs.norm.ppf(1 - alpha/2)
    else:
        qu = scs.norm.ppf(1 - alpha)

    diff = abs(variant_cr - control_cr)
    avg_cr = (control_cr + variant_cr) / 2

    control_var = control_cr * (1 - control_cr)
    variant_var = variant_cr * (1 - variant_cr)
    avg_var = avg_cr * (1-avg_cr)

    power_lower = scs.norm.cdf(
        (n**0.5 * diff - qu * (2 * avg_var)**0.5) /
        (control_var+variant_var) ** 0.5
    )
    power_upper = 1 - scs.norm.cdf(
        (n**0.5 * diff + qu * (2 * avg_var)**0.5) /
        (control_var+variant_var) ** 0.5
    )

    power = power_lower + power_upper

    return power


def get_z_value(alpha=0.05, two_tailed=True):
    z_dist = scs.norm()
    if two_tailed:
        alpha = alpha/2
        area = 1 - alpha
    else:
        area = 1 - alpha

    z = z_dist.ppf(area)
    return z


def plot_test_visualisation(
    visitors_A, conversions_A, visitors_B, conversions_B,
    alpha=0.05, tails='two'
):
    """Plots a visualisation of the Z test and its results.

    Parameters
    ---------
    visitors_A, visitors_B : int
        Number of sessions/users

    conversions_A, conversions_B : int
        Number of conversions

    alpha : float (optional)
        Default = 0.05
        Type I error level
    
    tails : ['two', 'left', 'right'] (optional)
        Specify what type of test; if 'two' (default), the p-value for a 
        two-tail Z-test will be returned.
        'left' specifies a one-tail Z-test where the alternative hypothesis
        is that the variant will return a better conversion rate, 'right' is
        the opposite.

    Returns
    -------
    Streamlit figure plot
    """

    control_cr = conversions_A/visitors_A
    variant_cr = conversions_B/visitors_B

    relative_difference = variant_cr/control_cr - 1

    # standard errors
    control_se = (control_cr*(1-control_cr)/visitors_A)**0.5
    variant_se = (variant_cr*(1-variant_cr)/visitors_B)**0.5
    se_difference = (control_se**2+variant_se**2)**0.5

    if tails == 'two':
        is_two_tails = True
    else:
        is_two_tails = False

    z = get_z_value(alpha=alpha, two_tailed=is_two_tails)

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
        **roboto
    )

    if tails == 'left':
        ax.fill_between(
            xA, 0, yA,
            where=(
                xA > 0 + se_difference*z_test
            ),
            color='green', alpha=0.2
        )
    elif tails == 'right':
        ax.fill_between(
            xA, 0, yA,
            where=(
                xA < 0 - se_difference*z
            ),
            color='green', alpha=0.2
        )
    else:
        ax.fill_between(
            xA, 0, yA,
            where=(
                xA > 0 + se_difference*z
            ) | (
                xA < 0 - se_difference*z
            ),
            color='green', alpha=0.2
        )

    ax.get_xaxis().set_major_formatter(
        mtick.FuncFormatter(lambda x, p: format(x/control_cr, '.0%')))

    plt.xlabel('Relative difference of the means')

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


def plot_power(
    visitors_A, conversions_A, visitors_B, conversions_B,
    alpha=0.05, tails='two'
):
    """Returns a streamlit plot figure visualising Power based on the
    results of an AB test.

    Parameters
    ---------
    visitors_A, visitors_B : int
        Number of sessions/users

    conversions_A, conversions_B : int
        Number of conversions

    alpha : float (optional)
        Default = 0.05
        Type I error level
    
    tails : ['two', 'left', 'right'] (optional)
        Specify what type of test; if 'two' (default), the p-value for a 
        two-tail Z-test will be returned.
        'left' specifies a one-tail Z-test where the alternative hypothesis
        is that the variant will return a better conversion rate, 'right' is
        the opposite.

    Returns
    -------
    Streamlit figure plot
    """
    
    control_cr = conversions_A/visitors_A
    variant_cr = conversions_B/visitors_B

    control_se = (control_cr*(1-control_cr)/visitors_A)**0.5
    variant_se = (variant_cr*(1-variant_cr)/visitors_B)**0.5

    if tails == 'two':
        is_two_tails = True
    else:
        is_two_tails = False

    power = get_power(visitors_A, conversions_A,
                      visitors_B, conversions_B,
                      alpha=alpha, two_tails=is_two_tails)

    z = get_z_value(alpha=alpha, two_tailed=is_two_tails)

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    xA = np.linspace(control_cr-4*control_se, control_cr+4*control_se, 1000)
    yA = scs.norm(control_cr, control_se).pdf(xA)
    ax.plot(xA, yA, label='A')

    ax.text(
        control_cr,
        max(yA)*1.03,
        "A",
        color='tab:blue',
        horizontalalignment='center',
        **roboto_bold
    )

    # Add critical value lines
    if tails == 'left':
        ax.axvline(
            x=control_cr+control_se*z,
            c='tab:blue', alpha=0.5, linestyle='--'
        )
        ax.text(
            control_cr+control_se*z,
            max(yA)*0.4,
            "Critical value",
            color='tab:blue',
            rotation=270,
            **roboto_small
        )
    elif tails == 'right':
        ax.axvline(
            x=control_cr-control_se*z,
            c='tab:blue', alpha=0.5, linestyle='--'
        )
        ax.text(
            control_cr-control_se*z,
            max(yA)*0.4,
            "Critical value",
            color='tab:blue',
            rotation=270,
            **roboto_small
        )
    else:
        ax.axvline(
            x=control_cr-control_se*z,
            c='tab:blue', alpha=0.5, linestyle='--'
        )
        ax.text(
            control_cr-control_se*z,
            max(yA)*0.4,
            "Critical value",
            color='tab:blue',
            rotation=270,
            **roboto_small
        )

        ax.axvline(
            x=control_cr+control_se*z,
            c='tab:blue', alpha=0.5, linestyle='--'
        )
        ax.text(
            control_cr+control_se*z,
            max(yA)*0.4,
            "Critical value",
            color='tab:blue',
            rotation=270,
            **roboto_small
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

    # Fill in the power and annotate
    if variant_cr > control_cr:
        ax.fill_between(
            xB, 0, yB,
            where=(xB > control_cr + control_se*z),
            color='green', alpha=0.2
        )
    else:
        ax.fill_between(
            xB, 0, yB,
            where=(xB < control_cr - control_se*z),
            color='green', alpha=0.2
        )

    ax.text(
        ax.get_xlim()[0]+(ax.get_xlim()[1]-ax.get_xlim()[0])*0.8,
        ax.get_ylim()[1]*0.8,
        f"Power: {power:.2%}",
        horizontalalignment='left',
        **roboto
    )

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

    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1))
    plt.xlabel('Converted Proportion')

    sns.despine(left=True)
    ax.get_yaxis().set_visible(False)
    fig.tight_layout()

    st.write(fig)
