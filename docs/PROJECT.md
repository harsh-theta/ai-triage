### AI Triage Demo: A Step-by-Step Build Plan

This document provides a comprehensive, phased plan to develop a fully functional AI Triage demo using your specified tech stack.

**Project Goal:** Create a compelling proof-of-concept that demonstrates intelligent, protocol-guided patient triage, emergency detection, and data capture for EMRs.

**Tech Stack:**
* **Frontend:** React, Vite, shadcn/ui, Tailwind CSS
* **Backend:** Python, FastAPI
* **AI Orchestration:** LangGraph
* **LLM:** Google Gemini API
* **Database:** Not required for this demo. Conversation state will be managed in memory per session.

---

### Phase 0: Foundation & Setup (Estimated Time: 1-2 hours)

This phase ensures your development environment is ready for both frontend and backend work.

1.  **Project Structure:** Create a root directory for your project (e.g., `ai-triage-demo`) and inside it, create two folders: `frontend` and `backend`.

2.  **Backend Setup (in the `backend` folder):**
    * Create and activate a Python virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```
    * Install necessary Python packages:
        ```bash
        pip install fastapi "uvicorn[standard]" langgraph langchain-google-genai python-dotenv pydantic
        ```
    * Create a `.env` file and add your Google API key:
        ```
        GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```
    * Create your main application file: `touch main.py`

3.  **Frontend Setup (in the `frontend` folder):**
    * Create a new React project using Vite:
        ```bash
        npm create vite@latest . -- --template react
        ```
        (Choose `.` to install in the current `frontend` directory).
    * Install npm dependencies: `npm install`
    * Initialize shadcn/ui and Tailwind CSS. This is a guided process:
        ```bash
        npx shadcn-ui@latest init
        ```
        (Accept the defaults, they align with Vite's structure).
    * Install a few essential shadcn/ui components to start:
        ```bash
        npx shadcn-ui@latest add button input card toast sonner
        ```
    * Install `axios` for making API requests: `npm install axios`

---

### Phase 1: Backend Development (FastAPI & LangGraph) (Estimated Time: 4-6 hours)

This is the core logic of your application. We'll build the "brain" that powers the conversation.

1.  **FastAPI Boilerplate (`main.py`):**
    * Set up a basic FastAPI app.
    * Configure CORS middleware to allow your frontend to communicate with it.
    * Define Pydantic models for the API request (`UserInput`) and response (`AIResponse`).

2.  **Define LangGraph State:**
    * Create a `TypedDict` for your graph's state. It should include fields like `messages` (list), `patient_data` (dict), and `current_protocol` (str).

3.  **Implement Graph Nodes (The Triage Logic):**
    * Create separate Python functions for each logical step (node):
        * `start_conversation`: Provides the initial greeting.
        * `analyze_complaint`: Takes the user's first message, uses Gemini to classify it (e.g., "headache," "emergency," "routine"), and extracts the chief complaint. This node decides which path to take.
        * `routine_triage_node`: Asks general follow-up questions.
        * `headache_protocol_node`: Asks specific questions related to headaches (e.g., "Is the pain sharp or dull?").
        * `summarize_and_finish`: Creates the final EMR summary.
        * `emergency_node`: A terminal node that simply flags an emergency.

4.  **Wire the Graph:**
    * Instantiate `GraphState` and `StatefulGraph`.
    * Add all your nodes to the graph.
    * Define the conditional edges. This is the key to your agent's intelligence:
        * From `analyze_complaint`, create edges that route to `headache_protocol_node`, `emergency_node`, or `routine_triage_node` based on the classification result.
        * Set the entry point to `start_conversation`.

5.  **Create the Main API Endpoint (`/chat`):**
    * This endpoint will receive the user's message.
    * It will invoke your compiled LangGraph, passing in the current conversation state.
    * The graph will run until it hits a point where it needs user input again.
    * The endpoint will return the AI's response, the updated EMR data, and the current system state (e.g., "emergency_detected").

---

### Phase 2: Frontend Development (React & shadcn/ui) (Estimated Time: 3-5 hours)

Now we build the user-facing interface that makes the demo look and feel professional.

1.  **Build UI Components:**
    * `ChatLayout.jsx`: The main component holding the chat window and the side panel.
    * `MessageBubble.jsx`: A component to render AI vs. User messages differently.
    * `ChatInput.jsx`: The input bar with the send button, using shadcn's `Input` and `Button`.
    * `EMRPreview.jsx`: A side panel component using a `Card` to display the structured JSON data received from the backend.
    * `SystemStatus.jsx`: A small component to show the current state (e.g., "Following Headache Protocol").

2.  **State Management:**
    * Use React's `useState` hook in your main `App.jsx` to manage the conversation history (`messages`), the `emrData` object, and any loading states.

3.  **API Integration:**
    * Create a service function using `axios` to handle the `POST` request to your `/chat` endpoint on the FastAPI server.
    * When the user sends a message, call this function. On success, update your React state with the response from the backend (the AI's new message, updated EMR data, etc.).

4.  **Implement the Emergency Handover:**
    * When the API response indicates an emergency (`"status": "emergency_detected"`), trigger a full-screen modal or a "Sonner" toast with a critical alert style.
    * The UI should become non-interactive (disable the input field) to mimic a system lockdown and handover. The message should clearly state: *"An emergency has been detected. We are immediately connecting you to a human doctor."*

---

### Phase 3: Integration, Polish & Demo Prep (Estimated Time: 2-3 hours)

This final phase brings everything together and prepares you for the client presentation.

1.  **Run End-to-End:** Start both the FastAPI server (`uvicorn main:app --reload`) and the React dev server (`npm run dev`) simultaneously.
2.  **Test the 3 Core Paths:**
    * **Routine:** Start with "I have a stomach ache" and ensure it follows the general path.
    * **Protocol-Specific:** Start with "I have a terrible headache" and verify it asks the specific headache-related questions.
    * **Emergency:** Start with "I have chest pain and difficulty breathing" and confirm the emergency overlay is triggered immediately.
3.  **Add Polish:**
    * Implement "AI is typing..." indicators to make the interaction feel more natural.
    * Use shadcn's `Toast` for non-critical notifications (e.g., "Triage Complete").
    * Ensure the chat window automatically scrolls to the latest message.
4.  **Prepare Demo Script:**
    * Write down the exact phrases you will use to demonstrate the three paths. This ensures a smooth and impressive presentation. Explain what is happening "behind the scenes" (in LangGraph and the EMR data panel) as you go.