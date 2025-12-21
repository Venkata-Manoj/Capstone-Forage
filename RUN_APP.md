# How to Run CapstoneForge (Local Ollama Version)

Follow these steps to set up and run the application entirely locally.

## Prerequisities

1. **Python 3.10+**: Ensure Python is installed (`python --version`).
2. **Ollama**: Download and install from [ollama.com](https://ollama.com).
3. **Node.js**: (Optional) Required if you want to run the frontend locally.

## Step 1: Backend Setup

1. **Open a terminal** in the project root.
2. Navigate to the backend folder:

    ```powershell
    cd backend
    ```

3. **Install Dependencies**:

    ```powershell
    pip install -r requirements.txt
    ```

    *Note: If you encounter permission errors, try `pip install --user -r requirements.txt`.*

## Step 2: Configure Ollama

1. **Start Ollama Service**:
    Open a separate terminal and run:

    ```powershell
    ollama serve
    ```

    *(If you installed the desktop app, it might already be running in the system tray).*

2. **Pull Required AI Models**:
    Run these commands to download the models specified in your `.env` file:

    ```powershell
    ollama pull llama3.2
    ollama pull mistral
    ```

## Step 3: Run the Backend Server

Captured from `backend/` folder:

```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

* You should see `INFO: Uvicorn running on http://0.0.0.0:8000`
* Swagger documentation is available at: [http://localhost:8000/docs](http://localhost:8000/docs)

## Step 4: Run the Frontend (Optional)

If you need to run the UI:

1. Open a new terminal.
2. Navigate to `frontend/`:

    ```powershell
    cd frontend
    ```

3. Install dependencies:

    ```powershell
    npm install
    ```

4. Start dev server:

    ```powershell
    npm run dev
    ```

## Troubleshooting

* **ModuleNotFoundError**: Run `pip install -r requirements.txt` again.
* **Ollama Connection Error**: Ensure `ollama serve` is running and `http://localhost:11434` is accessible.
* **Model Not Found**: Run `ollama pull <model_name>` for whatever model is listed in your error logs.
