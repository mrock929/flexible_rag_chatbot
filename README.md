# Flexible RAG Chatbot

## Pre-installation Instructions
### Docker and WSL Setup for Windows
1. Sign up for a personal Docker account
1. Go to https://docs.docker.com/desktop/setup/install/windows-install/
1. Follow the instructions to set up WSL. This will require a restart.
1. After the restart, follow the best practices for setting up WSL on the same page as above.
1. As part of the WSL setup it is recommended to use VSCode and and follow the instructions in that page for hooking them up.
1. Follow the steps to download and configure Docker Desktop and WSL: https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-containers
    1. Be sure to specifically download the Docker Desktop version linked in the above page that has the WSL 2 backend.

### Docker Setup for Mac
1. Follow the instructions at https://docs.docker.com/desktop/setup/install/mac-install/.

### Set up OpenAI API Key (Optional)
This approach should be used if the machine running this app doesn't have a strong GPU or CPU with sufficient RAM to host a local LLM. Either an OpenAI API Key or a local LLM need to be set up for the app to work.
1. Obtain an OpenAI API Key.
1. Save the key in a new `.env` file in the project root. This should look like `OPENAI_API_KEY="put key here"`.

### Set up Local LLM (Optional)
This approach should be used if the machine running this app has a strong GPU or CPU with sufficient RAM to host a local LLM. Either an OpenAI API Key or a local LLM need to be set up for the app to work.
1. TODO Instructions for downloading and running a GGUF model

## Running the app in Docker
1. Be sure Docker Desktop is running.
1. In the project root, run `docker-compose build` in a terminal.
    1. If no code changes have happened, you will only have to do this step the first time.
1. Once that completes, run `docker-compose up`
1. Once that is done you should see some URLs in the terminal. Copy the Local URL into a browser (Chrome recommended) to access the app.
1. Once you are done using the app, close the browser tab.
1. Then, use control + c to stop the docker container in the terminal.
1. Once the application has stopped, type `docker-compose down` into the terminal to stock the Docker container.

# TODO
* Switch to local GGUF model using llama-cpp-python (https://github.com/abetlen/llama-cpp-python), update docs
* Read/skim research paper (/data)
* Dig into embedding repo and implement (https://github.com/mims-harvard/Clinical-knowledge-embeddings)
* Streamlit home page - Config/data prep and chatbot pages
* Config page: Select model (volume mount /models), model params (GPU y/n, etc.), button to ingest/embed data (volume mount /data) and create db (/data/db) for use later. Select embedding method (Open AI vs medical)
* Chatbot page: Chatbot interface.
* Evaluation framework. Testing page in UI, but use promptfoo on backend
* Implement unit testing
* Add CI process
* Pick a license, make public

Nice to haves
* Cut out start of next paper from last page
* Chatbot clear history button
* Suggested prompts, some kind of article summary at top or "You can ask questions about..."
* Be able to handle "Provide a summary of the article/paper/etc."

