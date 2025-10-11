import sys
import os
import re
import joblib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai_debt_collector.types import AgentState

def preprocess_transcripts(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text

def load_model():
    model_path = os.path.join(os.path.dirname(__file__), '../../call-analysis-nlp/models/trained_model.pkl')
    vectorizer_path = os.path.join(os.path.dirname(__file__), '../../call-analysis-nlp/models/trained_model_vectorizer.pkl')
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    return model, vectorizer

def feedback_node(state: AgentState) -> AgentState:
    # Get the conversation transcript
    messages = state.get("messages", [])
    transcript = "".join([msg for msg in state["messages"] if "Borrower:" in msg or "User:" in msg])
    
    if not transcript:
        state["feedback_txt"] = "No conversation to analyze."
        return state
    
    # Preprocess
    processed = preprocess_transcripts(transcript)
    
    # Load model and predict
    model, vectorizer = load_model()
    X = vectorizer.transform([processed])
    score = model.predict(X)[0]
    
    # Generate feedback based on score
    if score >= 95:
        feedback = f"Excellent performance! Score: {score:.1f}/100. Keep up the great work."
    elif score >= 90:
        feedback = f"Good job! Score: {score:.1f}/100. Minor improvements possible."
    elif score >= 80:
        feedback = f"Fair performance. Score: {score:.1f}/100. Focus on key areas."
    else:
        feedback = f"Needs improvement. Score: {score:.1f}/100. Review best practices."
    
    state["feedback_txt"] = feedback
    return state