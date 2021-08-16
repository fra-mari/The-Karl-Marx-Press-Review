![visualization](./logo.png)
## A website to visualise a NLP project on text generation with GPT-2


![gif](./press-review.gif)


---
### To Use This Code Locally
#### STEP 1: Generate the dataset and the model:

- Clone this repository;
- Go to the folder `data_and_model`:
  - install the requirements with `pip install requirements.txt`;
  - run: `python scraper_preprocesser.py` **to download the dataset on which to fine-tune the GPT-2 model** (`marx.txt`). After running the process, you should see it in a new subfolder called `training_dataset/preprocessed`;
  - **To download and fine-tune the GPT-2 model**, load the Notebook `Text-Generating_GPT-2_Finetuner_on_Colab_GPU.ipynb` into your Google Drive, <u>open it with Google Colaboratory</u> and follow the instructions to create the two files `pytorch_model.bin` and `config.json`;
  - Paste these files into the two subfolders `trained_model` to be found in: `marxist_press_review/article_collector/` and `marxist_press_review/press_review_app/`.

#### STEP 2: Setting the required environment variables

In order for this webapp to work, you will need to set <u> two environment variables</u>:
1. The password for the PostgreSQL database which will be created. Unless you do not want to change its name in the `docker-compose.yml` file, this variable must be called `POSTGRES_PASSWORD`.
2. The API key for **The Guardian Open Platform**, which you can generate upon free registration via [this link](https://bonobo.capi.gutools.co.uk/register/developer).  Unless you do not want to change its name in the `docker-compose.yml` file, this variable must be called `GUARDIAN_API_KEY`.

#### STEP 3: Running the webapp with Docker

- Go to the folder `marxist_press_review`;
  - run `docker-compose build` and wait for Docker to set up everything for you.
  - run `docker-compose up` and wait for the log to confirm that the webapp has correctly started (something like `press_review_app_1   | 2021-08-16 15:38:21,336: INFO:  * Running on http://<ANY-ADDRESS-ENDING-BY-:5000/>`. );
  - wait for another while, as the software downloads the most recent articles from _The Guardian_'s API to PostgreSQL (the log will confirm that your API key works correctly by printing lines such as: `2021-08-16 15:40:12,819: INFO: Successfully connected to https://content.guardianapis.com/search?section=world: scraping...`);
- open the address `http://localhost:5000` in your browser and the website should appear. Have fun talking with Karl Marx!

---

### Further Reading

* Alammar, J. (2019), *The Illustrated GPT-2 (Visualizing Transformer Language Models)*, URL: https://jalammar.github.io/illustrated-gpt2/.
* Radford, A. *et al.* (2019), “Language Models are Unsupervised Multitask Learners”, *OpenAi Blog*, URL: https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf.
* Vaswani, A. *et al.* (2017), “Attention is All You Need”, 31st Conference on Neural Information Processing Systems (*NIPS* 2017), Long Beach (CA), URL: https://arxiv.org/abs/1706.03762.

---
### To Do:
- Add more documentation;
- host on GCP;
- tests

