# Flexible RAG Chatbot
This repo contains a flexible RAG chatbot that can be quickly and easily spun up on any machine running Docker to answer questions about text information in PDFs.

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

## Setup Instructions
### Set up the app
1. Clone the repo.

### Data Setup
1. Put the PDF file(s) you want to ask questions about into the /data directory. This chatbot will only ingest PDF files, and will ingest every PDF file in that directory. Do not put the PDF files in subdirectories. The PDF files must be "text" PDF files. They are correctly formatted if you open the PDF and can highlight specific words. If you can't do this then you need to run something like Adobe Acrobat's "Scan & OCR" capability to convert the PDFs to the text format.
1. If you want to update these PDF files after starting the app for the first time (if the files changed or new data is added to /data), delete the /data/chromadb folder and restart the app.

### Set up OpenAI API Key (Optional)
This approach should be used if the machine running this app doesn't have a strong GPU or CPU with sufficient RAM to host a local LLM. Either an OpenAI API Key or a local LLM need to be set up for the app to work.
1. Obtain an OpenAI API Key.
1. Save the key in a new `.env` file in the project root. This contents of this file should look like `OPENAI_API_KEY="put key here"`.

### Set up Local LLM (Optional)
This approach should be used if the machine running this app has a strong GPU or CPU with sufficient RAM to host a local LLM. Either an OpenAI API Key or a local LLM need to be set up for the app to work.
1. Install Ollama for your operating system here https://github.com/ollama/ollama?tab=readme-ov-file#ollama.
1. Update an environment variable to change the Ollama model save path to the models folder in this directory. Instructions for changing environment variables on different operating systems for Ollama are here https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server.
1. Following the environment variable editing instructions above, change the `OLLAMA_MODELS` environment variable to be the path to the models directory in this project. For example `C:\projects\flexible_rag_chatbot\models\` on Windows.
1. Follow the instructions below the Model library section (https://github.com/ollama/ollama?tab=readme-ov-file#model-library) to determine an appropriately sized model for your hardware.
1. Download the model using `ollama pull <model name>`, for example `ollama pull llama3.2`. This will likely need to be done from your default command line application and location (Command Prompt in Windows for example) unless you have updated the PATH for Ollama. You should now see the model name within the project directory under `/models/manifests/registry.ollama.ai/library/`.

## Running the app
1. Start Docker Desktop.
1. Start Ollama.
1. In the project root, run `docker-compose build` in a terminal.
    1. If no code changes have happened, you will only have to do this step the first time.
1. Once that completes, run `docker-compose up chatbot`
1. Once that is done you should see some URLs in the terminal. Copy the Local URL into a browser (Chrome recommended) to access the app.
1. Select the model you want to use from the sidebar and then use the chat interface to ask the model questions about your documents. You can use the "Clear History" button to clear the chat history and start a new conversation.
1. Once you are done using the app, close the browser tab.
1. Then, use Control + c to stop the Docker container in the terminal.
1. Once the application has stopped (sometimes it visually hangs, so start typing anyways once you see something like "Container container-name Stopped"), type `docker-compose down` into the terminal to stop the Docker container.

## Running the testing framework in Docker
1. Start Docker Desktop and Ollama.
1. In the project root, run `docker-compose build` in a terminal.
    1. If no code changes have happened, you will only have to do this step the first time.
1. Once that completes, run `docker-compose run tests` to run the promptfoo-based test suite. Results will be saved to /data/promptfoo_test_output.json.
    1. If you plan to do multiple test runs, for example with multiple models, be sure to rename this file before running the tests again.
1. Once you are done testing, run `docker-compose down` to stop the Docker container.

# TODO
* Separate interview branch for below
* Remove openai - test and confirm
* Error handling for no open source models installed
* Get promptfoo working without having to set up embedding model each time
* Set up test cases for promptfoo
* For local model, make sure it only uses the context - revisit later, may be tied to model size (ability to follow system prompt, test this)
* Consider adding # embed_fcn = embedding_functions.HuggingFaceEmbeddingFunction(api_key="", model_name="medicalai/ClinicalBERT") back into manage_db if needed (need to add actual api_key), pair it with Switch chunker to from_pretrained("medicalai/ClinicalBERT")
* Once prompt is set, check some prompt hacking queries
* Add thumbs up/down per response. Log this data along with query, reponse, sources, etc. in DB for RL or other improvements later.
* For CI, likely just describe
* Error handling/logging
* Consider adding a doc similarity threshold for retriever, trying other retrievers
* Implement unit testing
* Pick a license, make public

Nice to haves
* Cut out start of next paper from last page and first 2 pages
* Suggested prompts, some kind of article summary at top or "You can ask questions about..."
* Use a medical embedding model

