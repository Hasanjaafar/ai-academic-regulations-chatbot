# Deployment Guide

Use Streamlit Community Cloud to create a shareable link for marking.

## 1. Push the project to GitHub

Make sure these files/folders are included in the repository:

- `app/streamlit_app.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `data/chroma_db_handbook/`
- `data/processed/academic_handbook_2025_26_chunks.json`

Do not commit `.env`.

## 2. Create the Streamlit app

1. Go to https://share.streamlit.io.
2. Sign in with GitHub.
3. Click **Create app**.
4. Select your repository and branch.
5. Set the main file path to:

```text
app/streamlit_app.py
```

6. Open **Advanced settings** and choose Python `3.11` if prompted.
7. In **Secrets**, add:

```toml
OPENAI_API_KEY = "your_openai_api_key_here"
```

8. Deploy the app.

## 3. Share with your instructor

After deployment, Streamlit will give you a public URL ending in:

```text
.streamlit.app
```

Send that link to your instructor. They can open it in a browser and test the chatbot without installing anything.

## Troubleshooting

- If the app says the OpenAI key is missing, check the Streamlit app secrets.
- If Chroma collection errors appear, confirm `data/chroma_db_handbook/` was pushed to GitHub.
- If dependencies take a long time, wait a few minutes on the first deployment because `torch`, `transformers`, and `sentence-transformers` are large packages.
