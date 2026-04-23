# Westminster Academic Regulations Assistant

Streamlit RAG chatbot for answering questions from the University of Westminster Handbook of Academic Regulations 2025-2026.

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

4. Run the app:

```bash
streamlit run app/streamlit_app.py
```

## Notes

- The app expects the Chroma collection at `data/chroma_db_handbook`.
- Sidebar controls let you change model, temperature, retrieved chunks, and prompt style.
- Prompt styles A, B, and C match the evaluation prompt templates in `evaluation/prompt_templates.py`.
