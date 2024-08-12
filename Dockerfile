FROM python:3.12.3

# Set the working directory
WORKDIR /usr/src

# Copy the requirements file into the container
COPY requirements.txt /usr/src/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

ENV DATABASE_URL="mysql+mysqlconnector://refo9178_crm_impulse_user:dBVd(PlP]Z)3@reforcodev.com/refo9178_crm_impulse"
# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run uvicorn server
CMD ["uvicorn", "src.api.main:app", "--reload", "--port", "8000", "--host", "0.0.0.0"]
