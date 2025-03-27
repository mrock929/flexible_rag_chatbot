# RAG Chatbot

## Pre-installation Instructions
### Docker and WSL Setup for Windows
1. Sign up for a personal Docker account
1. Go to https://docs.docker.com/desktop/setup/install/windows-install/
1. Follow the instructions to set up WSL. This will require a restart.
1. After the restart, follow the best practices for setting up WSL on the same page as above.
1. As part of the WSL setup it is recommended to use VSCode and and follow the instructions in that page for hooking them up.
1. Follow the steps to download and configure Docker Desktop and WSL: https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-containers
    1. Be sure to specifically download the Docker Desktop version linked in the above page that has the WSL 2 backend.

### Set up OpenAI API Key
1. Obtain an OpenAI API Key
1. Save the key in a new `.env` file in the project root. This should look like `OPENAI_API_KEY="put key here"`

## Running the app in Docker (future)
1. In the project root, run `docker build -t rag_chatbot .` in the terminal in VSCode.
    1. If no code changes have happened, you will only have to do this step the first time.
1. Once that completes, run `docker run -p 8501:8501 rag_chatbot`
1. Once that is done, put `http://localhost:8501` into your browser (Chrome recommended) to access the app.
1. Once you are done using the app, close the browser.
1. Then, use control + c to stop the docker container in the VSCode terminal.

## Running the app locally (current)
1. Clone the repo from github
1. Create a virtual environment and enter it
1. Run `pip install -r requirements.txt` from the project root
1. Run `streamlit run .\streamlit_app.py` on windows or `streamlit run ./streamlit_app.py` on Linux/Mac. The app should open automatically in a browser window.
1. To turn off the app, do not close the browser window, instead click Control + c in VSCode. Then the browser window can be closed


TODO
* Add to new repo on github
* Switch to local GGUF model using llama-cpp-python (https://github.com/abetlen/llama-cpp-python)
* Read/skim research paper (/data)
* Dig into embedding repo and implement (https://github.com/mims-harvard/Clinical-knowledge-embeddings)
* Streamlit home page - Config/data prep and chatbot pages
* Config page: Select model (volume mount /models), model params (GPU y/n, etc.), button to ingest/embed data (volume mount /data) and create db (/data/db) for use later. Select embedding method (Open AI vs medical)
* Chatbot page: Chatbot interface.
* Evaluation framework. Testing page in UI, but use promptfoo on backend
* Switch over to Docker
* Implement unit testing
* Add CI process
* Pick a license, make public

Nice to haves
* Cut out start of next paper from last page
* Chatbot clear history button
* Suggested prompts, some kind of article summary at top or "You can ask questions about..."
* Be able to handle "Provide a summary of the article/paper/etc."

