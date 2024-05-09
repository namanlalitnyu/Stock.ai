# Stock.ai
Retrieval Augmented Generation (RAG) Application, a recommendation system designed specifically for the domain of academic research on stock prediction using Large Language Model (LLM), LangChain, and Prompt Engineering and deployed on Google Cloud using Virtual Machine and Docker.

#### The project offers 3 modes: Question Answer, Recommendation, and LLM interaction
The application has the following User Interface:
1. User enters its query.
2. The RAG recommends the top 3 similar articles, along with their publication links based on the input query.
3. A summary is presented to the user representing the significance of each research article presented to the user.

<img width="1440" alt="Screenshot 2024-05-07 at 1 46 43 PM" src="https://github.com/namanlalitnyu/Stockmarket.ai/assets/149608140/1d5cb5a8-7090-4551-b56b-d2ab5836bc62">


### Steps for running the application locally:
1. The initial requirement is to install "Docker" and "Docker-compose" on your machine.
2. Run "git clone https://github.com/namanlalitnyu/Stock.ai" in your local.
3. Since we are using ChatGPT 3.5 Turbo API for LLM results, we need to replace the OpenAI key. Goto UI > stockai-app > src > constants > app.constants.ts. Replace the "openAIKey: test" value with your API key.
4. Go to the root directory, and run "docker-compose build" (This generates the build for both the Docker images of frontend and backend).
5. Once the build is completed, run "docker-compose up" (This will start both the backend and frontend applications).
6. Goto the URL: "localhost:8080" and test our product.


