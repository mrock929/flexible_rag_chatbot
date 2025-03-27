FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to install dependencies
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY backend/ /app/backend/
COPY streamlit_app.py .
COPY .env .

# Expose the port Streamlit uses (default 8501)
EXPOSE 8501

# Define the command to run the app
CMD ["streamlit", "run", "streamlit_app.py"]
