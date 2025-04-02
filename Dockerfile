FROM python:3.11

# Install Node.js and associated tools (needed for npm, which is needed for promptfoo)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    lsb-release \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs 

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to install dependencies
COPY requirements.txt .

# Install the required Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install PromptFoo using npm
RUN npm install promptfoo

# Copy the application files into the container
COPY backend/ /app/backend/
COPY streamlit_app.py .

# Expose the port Streamlit uses (default 8501)
EXPOSE 8501

# Define the command to run the app
CMD ["streamlit", "run", "streamlit_app.py"]
