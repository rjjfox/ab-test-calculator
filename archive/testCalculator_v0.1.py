import streamlit as st
from bayesian_functions import *
from frequentist_functions import *

roboto = {'fontname': 'Roboto', 'size': '12'}
roboto_title = {'fontname': 'Roboto', 'size': '14', 'weight': 'bold'}
roboto_bold = {'fontname': 'Roboto', 'size': '12', 'weight': 'bold'}
roboto_small = {'fontname': 'Roboto', 'size': '10'}

local_css("style.css")

font = {
    'family': 'sans-serif',
    'sans-serif': 'roboto',
    'size': 11
}

plt.rc('font', **font)

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

visitors_A = st.sidebar.number_input("Visitors A", value=50000, step=100)
conversions_A = st.sidebar.number_input("Conversions A", value=1500, step=10)
visitors_B = st.sidebar.number_input("Visitors B", value=50000, step=100)
conversions_B = st.sidebar.number_input("Conversions B", value=1560, step=10)

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

    try:
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

        create_plotly_table(bayesian_data)

        """
        The below graph plots the simulated difference between the two posterior
        distributions for the variants. It highlights the potential range of
        difference between the two variants. More data will reduce the range.
        """

        st.text("")

        plot_simulation_of_difference(samples_posterior_A, samples_posterior_B)

        """
        ---

        ### Recommended Reading 

        * [Bayesian Methods for Hackers by Cameron Davidson-Pilon]\
            (https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers)
        * [Bayesian AB test calculator by AB Testguide]\
            (https://abtestguide.com/bayesian/)
        * [Beta distribution Wikipedia]\
            (https://en.wikipedia.org/wiki/Beta_distribution)
        """

    except ValueError:
        
        t = """
        <img class='error'
            src='https://www.flaticon.com/svg/static/icons/svg/595/595067.svg'>
        """
        st.markdown(t, unsafe_allow_html=True)

        """
        An error occured, please check the test data input and try again.
        
        For Bayesian calculations, the conversion rate must be between 0 and
        1.
        """


else:

    if tails == 'One-tail':
        two_tails = False
        if relative_difference < 0:
            tail_direction = 'right'
        else:
            tail_direction = 'left'
    else:
        two_tails = True
        tail_direction = 'two'

    z_score, p_value = z_test(visitors_A, conversions_A,
                              visitors_B, conversions_B, tails=tail_direction)

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
        else:
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

    create_plotly_table(frequentist_data)

    z = get_z_value(alpha=alpha, two_tailed=two_tails)

    control_cr = conversions_A/visitors_A
    variant_cr = conversions_B/visitors_B

    # standard errors
    control_se = (control_cr*(1-control_cr)/visitors_A)**0.5
    variant_se = (variant_cr*(1-variant_cr)/visitors_B)**0.5
    se_difference = (control_se**2+variant_se**2)**0.5

    """
    According to the null hypothesis, there is no difference between the means.
    The plot below shows the distribution of the difference of the means that
    we would expect under the null hypothesis.
    """

    plot_test_visualisation(
        visitors_A, conversions_A, visitors_B, conversions_B,
        alpha=alpha, tails=tail_direction
    )

    if p_value < alpha:
        f"""
        The shaded areas cover {alpha:.0%} of the distribution. It is because
        the observed mean of the variant falls into this area that we can
        reject the null hypothesis with {1-alpha:.0%} confidence.
        """
    else:
        f"""
        The shaded areas cover {alpha:.0%} of the distribution. It is because
        the observed mean of the variant does not into this area that we are
        unable to reject the null hypothesis and get a significant result. A
        difference of greater than {se_difference*z/control_cr:.2%} is needed.
        """

    """
    #### Statistical Power
    """

    """
    Power is a measure of how likely we are to detect a difference when there
    is one with 80% being the generally accepted threshold for statistical
    validity.
    """

    f"""
    An alternative way of defining power is that it is our likelihood of
    avoiding a Type II error or a false negative. Therefore the inverse of
    power is 1 - {power:.2%} = **{1-power:.2%}** which is our likelihood of a
    type II error.
    """

    plot_power(visitors_A, conversions_A, visitors_B,
               conversions_B, alpha=alpha, tails=tail_direction)

    """
    ---

    ### Recommended reading

    * [Z-test Wikipedia](https://en.wikipedia.org/wiki/Z-test)
    * [The Math Behind AB Testing by Nguyen Ngo]\
        (https://towardsdatascience.com/the-math-behind-a-b-testing-with-example-code-part-1-of-2-7be752e1d06f)
    * [AB test calculator by AB Testguide](https://www.abtestguide.com/calc/)
    """
