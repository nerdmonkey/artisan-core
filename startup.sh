#!/bin/bash

curl -L -o ./storage/core/pima-indians-diabetes-database.zip\
  https://www.kaggle.com/api/v1/datasets/download/uciml/pima-indians-diabetes-database

unzip storage/core/pima-indians-diabetes-database.zip -d storage/core/
