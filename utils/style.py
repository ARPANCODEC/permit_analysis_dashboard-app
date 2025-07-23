import base64
from pathlib import Path

def set_style():
    """Set app styling and logos"""
    logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
    
    try:
        logo_image = base64.b64encode(open(logo_path, "rb").read()).decode()
    except FileNotFoundError:
        logo_image = ""
    
    return f"""
    <style>
        .stApp {{
            background-color: #f0f2f6;
        }}
        
        .main .block-container {{
            background-color: white;
            border-radius: 10px;
            padding: 2rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .corner-logo {{
            position: fixed;
            top: 1em;
            z-index: 1000;
            height: 3.5em;
        }}
        .left-logo {{
            left: 1em;
        }}
        .right-logo {{
            right: 1em;
        }}
        
        .title-container {{
            text-align: center;
            margin: 1em 0 2em 0;
        }}
        .title-container h1 {{
            color: #2c3e50;
        }}
        
        @media (max-width: 768px) {{
            .corner-logo {{
                height: 2.5em;
            }}
        }}
    </style>
    
    {f'<img class="corner-logo left-logo" src="data:image/png;base64,{logo_image}">' if logo_image else ''}
    {f'<img class="corner-logo right-logo" src="data:image/png;base64,{logo_image}">' if logo_image else ''}
    """