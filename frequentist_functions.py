import numpy as np
import pandas as pd
import scipy.stats as scs
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import streamlit as st

def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)


def percentage_format(x):
    return f"{x:.0%}"



def z_test(visitors_A, conversions_A, visitors_B, conversions_B, one_tail=False):
    """ Run a Z-test with your data, returning the Z-score and p-value.

    Parameters
    ---------
    visitors_A, visitors_B : int
        Number of sessions/users

    conversions_A, conversions_B : int
        Number of conversions

    one_tail : [False, 'left', 'right'] (optional)
        Specify what type of test; if False (default), the p-value for a two-tail
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
    if one_tail == 'left':
        p_value = scs.norm.cdf(-abs(z_score))
    elif one_tail == 'right':
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

