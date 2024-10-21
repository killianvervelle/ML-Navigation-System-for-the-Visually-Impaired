# Gateway

## Description 
This microservice chains the different micro-services.

## Parameters
This micro-services has the following environment variables:
- URL_PREFIX: The URL prefix if the microservice is served under a path prefix
- The different URLs to the microservices:
  - URL_PHOTO_VALIDATOR
  - URL_OBJECT_DETECTOR
  - URL_OBJECT_TO_NLP
  - URL_BUS_SCREEN_CROPPER
  - URL_BUS_SCREEN_TEXT_DETECTOR