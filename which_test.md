# Which statistical test should we use?

## Z test

The Z-test tests the mean of a distribution when the distribution of the mean can be
approximated by a normal distribution. 

As a result of the Central Limit Theorem, when our sample size is large, the Z-test is ideal
for testing whether two experiences are significantly different. A general rule of thumb for
what counts as 'large' would be a sample of n>50. The Z-test can also be used when
the population variance is known although this is uncommon.

For smaller sample sizes or where the population variance is not known, we would use the
Student's t-test. I have found the t-test slightly more complicated computationally in the past.
Thankfully there's no reason to use it over the Z-test unless if working with unequal sample
sizes. In this case we would use [Welch's t-test](https://en.wikipedia.org/wiki/Welch%27s_t_test)
over the Z-test.

[[Wikipedia entry about the Z-test](https://en.wikipedia.org/wiki/Z-test)]

_Note: there is an [argument](http://daniellakens.blogspot.com/2015/01/always-use-welchs-t-test-instead-of.html) that the classic Student's t-test is never needed because we can use
Welch's t-test for equal sample sizes as well._