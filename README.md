# ai-paraphraser-be
The Paraphrasing API provides an endpoint that generates paraphrased versions of input text using a pretrained NLP model. 

The backend is built using FastAPI with a modular domain-based architecture. PostgreSQL stores user accounts and paraphrasing history, while the Hugging Face Transformers library provides the paraphrasing model. Optional file uploads are stored in S3, with only metadata persisted in the database. Model inference is abstracted into a dedicated ML service, loaded once at startup for performance.