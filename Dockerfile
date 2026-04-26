# Use a lightweight Python image
FROM python:3.12-slim

# Set the directory inside the container
WORKDIR /code

# Copy requirements first to take advantage of Docker caching
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy your app folder into the container
COPY ./app /code/app

# Run the FastAPI app using Uvicorn
# We use 0.0.0.0 so it can be accessed from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]