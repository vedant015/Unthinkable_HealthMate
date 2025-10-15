# Unthinkable_HealthMate

# Healthcare Symptom Checker

A web-based chat application that helps users understand their health symptoms.  
**Note:** This tool is for educational purposes only and does not provide medical advice.

## Features
- Chat with an AI assistant about your symptoms.
- Get possible conditions and recommended next steps.
- Previous conversations are stored locally using SQLite.
- Multiple chat sessions with unique session IDs.

## Tech Stack
- **Backend:** Flask
- **Database:** SQLite
- **AI Integration:** OpenAI/GitHub LLM API
- **Frontend:** HTML, CSS, JavaScript

## How it Works
1. User enters symptoms in the chat interface.
2. Flask server sends the input to the LLM API.
3. LLM returns a structured JSON response with:
   - Possible conditions
   - Recommended next steps
   - Disclaimer
4. Messages and sessions are stored in SQLite for future reference.

## Safety Measures
- Does
