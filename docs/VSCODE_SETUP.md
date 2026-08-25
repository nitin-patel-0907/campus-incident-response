# 🛠️ Running the Project in VSCode

This guide explains how to execute the Campus Incident Report Analysis System directly within Visual Studio Code using our professional folder structure.

## Prerequisites
1. Ensure you have **Python 3.7+** and **Node.js** installed on your system.
2. Open the `AGENTATHON` folder in VSCode.

## 📦 Step 1: Install Dependencies

Open an Integrated Terminal in VSCode (`Ctrl + \`` or `Cmd + \``):

1. **Backend Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
2. **Frontend Dependencies** (if applicable):
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

## 🚀 Step 2: Run the Full System

We have moved all startup scripts to the `scripts/` directory. They automatically detect the core code in `src/`.

1. Open a VSCode Terminal.
2. Execute the startup script directly:
   ```powershell
   python scripts/start_demo.py
   ```
   *(Alternatively, you can run `python scripts/start_unified_server.py`)*

3. Once you see the "Application startup complete" message and "Uvicorn running on http://0.0.0.0:8080", you're good to go!

## 🌐 Step 3: Access the Application

- **Open your browser** and navigate to: `http://localhost:8080` (or the port specified in the terminal output).
- You can now use the interactive AI Insights & Evaluation Dashboard.

## 🐛 Debugging in VSCode

If you want to use VSCode's built-in debugger:
1. Go to the **Run and Debug** panel (`Ctrl + Shift + D`).
2. Click **create a launch.json file** and select **Python Debugger**.
3. Replace the contents of `.vscode/launch.json` with:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Start Demo",
               "type": "debugpy",
               "request": "launch",
               "program": "${workspaceFolder}/scripts/start_demo.py",
               "console": "integratedTerminal",
               "cwd": "${workspaceFolder}"
           }
       ]
   }
   ```
4. Press `F5` to start debugging!
