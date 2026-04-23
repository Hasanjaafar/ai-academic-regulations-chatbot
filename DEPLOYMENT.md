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

> [!IMPORTANT]
> The quotes around the key are mandatory. Do not just paste the API key by itself.

8. Deploy the app.

## 3. Share with your instructor

After deployment, Streamlit will give you a public URL ending in:

```text
.streamlit.app
```

Send that link to your instructor. They can open it in a browser and test the chatbot without installing anything.

## 4. Deploying to Render

Render is a robust alternative for hosting Python applications.

1. **Connect GitHub**: Create a new **Web Service** on [Render](https://render.com) and link your repo.
2. **Settings**:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
3. **Env Vars**: Add your `OPENAI_API_KEY` in the **Environment** tab.
4. **Memory Note**: The free tier (512MB RAM) may crash due to `torch` and `transformers`. Consider a paid instance if memory errors occur.

## 5. Deploying to Vercel

Vercel is primarily for frontend/serverless apps. To run Streamlit on Vercel, you must use the `@vercel/python` runtime.

1. **vercel.json**: Create a `vercel.json` in the root:
   ```json
   {
     "builds": [{"src": "app/streamlit_app.py", "use": "@vercel/python"}],
     "routes": [{"src": "/(.*)", "dest": "app/streamlit_app.py"}]
   }
   ```
2. **Push**: Use the Vercel CLI (`vercel`) or connect your GitHub repo.
3. **Environment**: Add `OPENAI_API_KEY` in the Vercel project settings.
**Warning**: Vercel has a 250MB limit for serverless functions, which is often exceeded by AI libraries like `torch`.

## Troubleshooting

- If the app says the OpenAI key is missing, check the platform's secrets/environment variables.
- If Chroma collection errors appear, confirm `data/chroma_db_handbook/` was pushed to GitHub.
- If dependencies take a long time, wait a few minutes on the first deployment because `torch`, `transformers`, and `sentence-transformers` are large packages.
