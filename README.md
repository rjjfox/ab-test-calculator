# AB Test Calculator

An AB test significance calculator with options to use Bayesian or Frequentist statistics. Calculations come through basic SciPy.stats methods, the web app is built with Streamlit and hosted on Heroku. [See it live here](https://ab-test-calculator-app.streamlit.app/).

<p align="center">
  <img src="./img/testcalculator.gif" width="738" alt="test calculator in use">
</p>

See also my [AB test sample size calculator](https://github.com/rjjfox/ab-test-samplesize).

## Table of Contents

- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [Built With](#built-with)
- [License](#license)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

## Installing

Clone/fork the repo onto your local machine.

It is then recommended to use a virtual environment to install the dependencies using the requirements.txt file.

```cli
pip install -r requirements.txt
```

With these installed, you simply need to run

```cli
streamlit run app.py
```

### Docker

Alternatively, with Docker, use the following command and then navigate to localhost.

```cli
docker run -p 80:8080 ryanfox212/ab-test-calculator
```

## Deployment

Deployed using Streamlit's Community Cloud free service for Streamlit apps.

## Built With

- [Streamlit](https://www.streamlit.io/) - The web application framework used
- [SciPy](https://www.scipy.org/) - For the statistical methods
- [Seaborn](https://seaborn.pydata.org/) - For vizualisations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
