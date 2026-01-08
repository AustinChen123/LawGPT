import json
import os
from PIL import Image
from typing import Dict

HISTORY_FILE = "data/history/chat_history.json"
IMAGE_DIR = "data/history/images"

def save_sessions(sessions: Dict):
    """
    Save sessions to disk.
    Handles image serialization by saving them as files and storing the path.
    """
    serializable_sessions = {}
    
    for session_id, session_data in sessions.items():
        serializable_messages = []
        for msg in session_data["messages"]:
            msg_copy = msg.copy()
            # Handle Image object if present
            if "image" in msg_copy and isinstance(msg_copy["image"], Image.Image):
                # Create a unique filename for the image
                # Simple hash strategy or timestamp could work, but let's use a counter or uuid in a real app.
                # For simplicity here, we assume the UI handles uniqueness or we generate a name.
                # Let's use the session_id + index as a naive ID
                img_filename = f"{session_id}_{len(serializable_messages)}.png"
                img_path = os.path.join(IMAGE_DIR, img_filename)
                
                # Save image to disk
                msg_copy["image"].save(img_path)
                
                # Store path in JSON
                msg_copy["image_path"] = img_path
                del msg_copy["image"] # Remove the PIL object
            elif "image_path" in msg_copy:
                # Already saved, just keep the path
                pass
                
            serializable_messages.append(msg_copy)
            
        serializable_sessions[session_id] = {
            "title": session_data["title"],
            "messages": serializable_messages
        }
        
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_sessions, f, ensure_ascii=False, indent=2)

def load_sessions() -> Dict:
    """
    Load sessions from disk.
    Reconstructs PIL Images from stored paths.
    """
    if not os.path.exists(HISTORY_FILE):
        return {}
        
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        restored_sessions = {}
        for session_id, session_data in data.items():
            restored_messages = []
            for msg in session_data["messages"]:
                # Restore Image from path
                if "image_path" in msg and os.path.exists(msg["image_path"]):
                    try:
                        msg["image"] = Image.open(msg["image_path"])
                    except:
                        # If image fails to load, just ignore it
                        pass
                
                restored_messages.append(msg)
                
            restored_sessions[session_id] = {
                "title": session_data["title"],
                "messages": restored_messages
            }
        return restored_sessions
    except Exception as e:
        print(f"Error loading history: {e}")
        return {}
