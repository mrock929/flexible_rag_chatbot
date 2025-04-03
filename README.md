# Flexible RAG Chatbot
This repo contains a flexible RAG chatbot that can be run on any computer with Docker to answer questions about text information in PDFs.

## Pre-installation Instructions
This app requires Docker and Ollama to be installed on your computer in order to work. Follow the instructions below for your operating system to set these tools up.

### Docker and WSL Setup for Windows
1. Sign up for a personal Docker account (https://app.docker.com/signup)
1. Go to https://docs.docker.com/desktop/setup/install/windows-install/
1. Follow the instructions to set up WSL. This will require a restart.
1. After the restart, follow the best practices for setting up WSL on the same page as above.
1. As part of the WSL setup it is recommended to use VSCode and and follow the instructions in that page for connecting VSCode and WSL.
1. Follow the steps to download and configure Docker Desktop and WSL: https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-containers
    1. Be sure to specifically download the Docker Desktop version linked in the above page that has the WSL 2 backend.
1. After installing Docker Desktop, login and verify your account by going to your profile, Account Settings, then Personal access tokens. It should send you an email to verify your account. After that, return to the Personal access tokens screen and confirm you can see at least one token in the table before proceeding.

### Docker Setup for Mac
1. Sign up for a personal Docker account (https://app.docker.com/signup)
1. Follow the instructions at https://docs.docker.com/desktop/setup/install/mac-install/ to install Docker Desktop.
1. After installing Docker Desktop, login and verify your account by going to your profile, Account Settings, then Personal access tokens. It should send you an email to verify your account. After that, return to the Personal access tokens screen and confirm you can see at least one token in the table before proceeding.

## Setup Instructions
### Set up the app
1. Clone the repo at the location of your choosing on your computer by navigating there in a terminal, and then running `git clone https://github.com/mrock929/flexible_rag_chatbot.git`.
1. Enter the project, e.g. `cd flexible_rag_chatbot`.

### Data Setup
1. Put the PDF file(s) you want to ask questions about into the `flexible_rag_chatbot/data/` directory. This chatbot will only ingest PDF files, and will ingest every PDF file in that directory. Do not put the PDF files in subdirectories. The PDF files must be "text" PDF files. They are correctly formatted if you open the PDF and can highlight specific words. If you can't do this then you need to run something like Adobe Acrobat's "Scan & OCR" capability to convert the PDFs to the text format.
    1. The provided PDF file is already present in this location, so nothing needs to be done if no other PDF files are desired.
1. If you want to update these PDF files after starting the app for the first time (if the files changed or new data is added to /data), delete the /data/chromadb folder and restart the app.

### Set up Local LLM
1. Install Ollama for your operating system here https://github.com/ollama/ollama?tab=readme-ov-file#ollama.
1. Update an environment variable to change the Ollama model save path to the models folder in this directory. Instructions for changing environment variables on different operating systems for Ollama are here https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server.
1. Following the environment variable editing instructions above, change the `OLLAMA_MODELS` environment variable to be the path to the models directory in this project. For example `C:\projects\flexible_rag_chatbot\models\` on Windows or `~/username/projects/flexible_rag_chatbot/models/` on Mac.
1. If you used a terminal to set the environment variable, close out of the terminal.
1. Quit Ollama. It will likely either be in your top bar on Mac or in your task bar on PC. The icon is a white llama head.
1. Start Ollama.
1. Follow the instructions below the Model library section (https://github.com/ollama/ollama?tab=readme-ov-file#model-library) to determine an appropriately sized model for your hardware. 
    1. Llama 3.2 is recommended for weak systems. Gemma3 is comparable, but slightly slower.
    1. For stronger systems, Phi 4 works better than Llama 3.2, but is generally much slower.
    1. Models to avoid:
        1. deepseek-r1: Includes its chain of thought reasoning in output.
        1. mistral: Very poor at following directions, so it does not restrict itself to the supplied context. This can lead to inaccurate or irrelevant answers.
    1. If you intend to run the testing suite, the Phi 4 model or larger is highly recommended. Gemma 3 27b also works well, but is slower. Phi 4 requires 16 GB of RAM to run. If you use a smaller model, the test suite will likely fail due to the model's inability to format the output correctly.
1. Download the model using `ollama pull <model name>`, for example `ollama pull llama3.2`. This will likely need to be done from your default terminal application and location (Command Prompt in Windows for example) unless you have updated the PATH for Ollama. You should now see the model name within the project directory under `/models/manifests/registry.ollama.ai/library/`. If you don't, be sure you set your environment variable correctly, restart Ollama, and try again.

## Running the app
1. Start Docker Desktop.
1. Start Ollama.
1. In the project root, run `docker-compose build` in a terminal. This may take a few minutes.
    1. If no code changes have happened, you will only have to do this step the first time you start the chatbot.
1. Once that completes, run `docker-compose up chatbot`
1. Once that is done you should see some URLs in the terminal. Copy the Local URL into a browser (Chrome recommended) to access the app.
1. Select the model you want to use from the sidebar and then use the chat interface to ask the model questions about your documents. You can use the "Clear History" button to clear the chat history and start a new conversation. You can provide feedback on model performance with the "Good" and "Bad" buttons.
    1. On computers with less than 16 GB RAM or when using a larger model this can be very slow. If the model is running you will see a "Running" animation in the top right of the screen.
    1. Example prompts can be found in `/testing/chatbot_tests_quality.csv` in the first column (input).
    1. If the chatbot returns a message that says, "I don't know the answer." that means it didn't have sufficient context to answer the question. Try rephrasing your question with additional context to enable the chatbot to accurately answer your question.
1. Once you are done using the app, close the browser tab.
1. Then, use `Control + c` to stop the Docker container in the terminal.
1. Once the application has stopped (sometimes it visually hangs, so start typing anyways once you see something like "Container container-name Stopped"), run `docker-compose down` in the terminal to stop the Docker container.

## Running the testing framework
The testing framework is only recommended for developers working on this codebase.
You need at least 16 GB of RAM to effectively run the testing framework.

1. Start Docker Desktop and Ollama.
1. Open /backend/custom_provider.py and set the `LOCAL_TESTING_MODEL` value (line 8) to be the name of the model you want to test. This name should be identical to the model name you used when downloading the model using Ollama, e.g. `"llama3.2"`. Make sure the model name is enclosed in double quotes. Save your changes.
1. Open /backend/custom_eval_provider.py and set the `LOCAL_EVAL_MODEL` value (line 7) to be the name of the model you want to use for evaluation. This model should be different (preferably larger) than the local testing model. This model must have at least 14B parameters or the testing suite will likely fail. The recommended model is `"phi4"`. Save your changes.
1. In the project root, run `docker-compose build` in a terminal.
    1. If no code changes have happened, you will only have to do this step the first time.
1. Once that completes, run `docker-compose run tests` to run the promptfoo-based test suite. Results will be saved to `/testing/promptfoo_test_output.json`. This will take several minutes.
    1. If you plan to do multiple test runs, for example with multiple models, be sure to rename this file before running the tests again so you don't lose your results.
    1. By default this will run the quality tests (tests of model output quality). If you want to run the model latency tests, change the `tests` line in the `/testing/promptfooconfig.yaml` to have `chatbot_tests_latency` instead of `chatbot_tests_quality` in the csv filename. When running the latency tests, the `--max-concurrency 1` flag should be added to the end of the tests service command in the `docker-compose yaml` file. This ensures the full resources are available to run the model. This is especially important for larger models or weaker computer. Save your changes.
1. Once the tests finish, run `docker-compose down` to stop the Docker container. You can review the high level test results in the table displayed in the terminal. Details can be found in the `/testing/promptfoo_test_output.json` file.
