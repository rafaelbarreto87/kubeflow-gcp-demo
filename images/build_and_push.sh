#!/bin/sh

PROJECT_ID=`gcloud config get-value project`
IMAGE_NAME="$1"
IMAGE_TAG="$2"
IMAGE_PATH="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG}"
docker build "${IMAGE_NAME}" -t "$IMAGE_PATH"
docker push "$IMAGE_PATH"