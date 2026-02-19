import re

def clean_text(text):
    """
    Remove extra whitespace and non-printable characters.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def format_time(seconds):
    """
    Format seconds into a readable string.
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    return f"{seconds/60:.2f}m"
