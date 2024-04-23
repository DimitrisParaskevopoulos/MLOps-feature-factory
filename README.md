# Feature Engineering Pipeline
This project streamlines the process of feature engineering within a machine learning operations (MLOps) framework using an automated tool named Featuretools. It's designed to efficiently generate meaningful features from raw data, facilitating more effective predictive models.

## Table of Contents
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setting Up](#setting-up)
  - [Running](#running)
- [Usage](#usage)
- [Logger](#logger)
- [Actions](#actions)

## Getting Started

Step-by-step instructions for setting up and running the app.

### Prerequisites

- [Docker](https://www.docker.com/) - Make sure Docker and Docker-compose are installed.

### Setting Up
 ```
git clone https://github.com/DimitrisParaskevopoulos/MLOps-feature-factory.git
 ```
 ```
cd your-local-path/MLOps-feature-factory
 ```

### Running
 ```
docker-compose up -d --build
 ```

## Usage
1. Use the FastAPI endpoint at http://localhost:8000/get_raw_data/{ID} to get raw data for specific player ID.

2. Use the API endpoint at http://localhost:8000/get_features/{ID} to get features extracted for specific player ID.
For example you can get stats for the ID you requested:
   A) COUNT
   B) MEAN, SUM, MAX, MIN
   C) SKEW, STD
   D) MODE, NUM_UNIQUE

## Logger
Write log messages to the /app/logs/app.log file within the container, and you can access the log file on the host machine within the specified logs directory.

## Github Actions
This workflow is typical for a continuous integration setup, where code changes pushed to the main branch trigger a series of steps to build a Docker image and push it to Docker hub. 
This workflow is also designed for continuous deployment, where changes to the repository trigger a series of steps to update and run a Docker container to an EC2 instance.
Coming soon...