## Gateway Application

### Overview

FastAPI microservice that acts as a gateway for chaining various image processing services.

### Technologies Used

- FastAPI: Web framework for building APIs.
- Pydantic: Data validation and settings management.
- MongoDB: Database for storing image processing history.
- Docker: Containerization for easy deployment.

### File Structure

- main.py: Entry point for the FastAPI application, sets up routes and middleware.
- models.py: Data models for processing responses and pipeline history.
- init.py: Initializes environment variables for microservice URLs and MongoDB such as:
  - URL_PHOTO_VALIDATOR
  - URL_OBJECT_DETECTOR
  - URL_OBJECT_TO_NLP
  - URL_BUS_SCREEN_CROPPER
  - URL_BUS_SCREEN_TEXT_DETECTOR
- request.py: Contains logic for executing image processing pipelines

### Instructions for Running the Project
1) Clone the repository.
2) Build and start services using Docker Compose: ``docker-compose up``.
3) Access the API at http://localhost:8000.

### Key Functionalities
- Image Processing: Processes images with various modes (description, tracking).
- Pipeline History: Tracks processing history and results.

### Environment Variables
- URL_PREFIX: Prefix for API routes.
- MONGO_INITDB_ROOT_USERNAME: MongoDB username.
- MONGO_INITDB_ROOT_PASSWORD: MongoDB password.

### Future Improvements
- Improve error handling.
- Optimize API performance.