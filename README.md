# Python Practice — Quiz Studio

A Streamlit app that creates interactive core Python quizzes using Google AI Studio. Students choose a topic, difficulty, and question count, answer questions with explanations, then see their score board.

## Run locally

1. Install Python 3.10 or later.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Set your Google AI Studio key as an environment variable, or create `.streamlit/secrets.toml` with:

   ```toml
   GOOGLE_AI_STUDIO_API_KEY = "your_google_ai_studio_api_key_here"
   ```

   The local secrets file is excluded by `.gitignore`; never commit a real API key.

5. Start the app:

   ```powershell
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository. Keep `.env`, `.streamlit/secrets.toml`, and `.venv/` out of the commit.
2. In Streamlit Community Cloud, create an app from the repository and set the app file path to `app.py`.
3. In the deployed app's **Settings → Secrets**, add:

   ```toml
   GOOGLE_AI_STUDIO_API_KEY = "your_real_google_ai_studio_api_key"
   ```

4. Save the secrets and deploy or reboot the app.

The key is read on the server from Streamlit Secrets and is not included in the app source or sent to the browser. If a real key has ever been committed or pushed, revoke it in Google AI Studio and create a replacement.

## Quiz options

Choose a topic, difficulty, and 3–10 questions. Each generated question has four choices, answer feedback, and an explanation. The final score board shows the total score, percentage, correct answers, and questions to practise.
