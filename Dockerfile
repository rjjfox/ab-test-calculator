# Base image
FROM python:3.8.5-slim

# Copy requirements.txt from local folder to docker container
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy local code to the container image
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

CMD streamlit run app.py --server.port 8080