# ai_helper.py
import os, json
try:
    import openai
except Exception:
    openai = None

OPENAI_KEY_ENV = 'OPENAI_API_KEY'
API_MODEL = 'gpt-4o-mini'  # change if you don't have access

def init_api():
    key = os.environ.get(OPENAI_KEY_ENV)
    if not key:
        raise RuntimeError('Set environment variable OPENAI_API_KEY before running')
    if openai is None:
        raise RuntimeError('openai package not installed. pip install openai')
    openai.api_key = key

ANALYSIS_PROMPT = (
    "You are a helpful assistant. The user gives the name of an Android game. "
    "Return a short analysis describing: main actions a player takes, recommended keyboard key mappings (keyboard key -> action), "
    "and which mouse actions map to turning/aiming. Output JSON with fields: game, summary, keys (list of {key, action, android_keycode}), mouse (description)."
)

def analyze_game(game_name):
    init_api()
    prompt = ANALYSIS_PROMPT + f"\n\nGame: {game_name}\n\nRespond in strict JSON."
    resp = openai.ChatCompletion.create(
        model=API_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.2,
    )
    text = resp['choices'][0]['message']['content']
    # try to parse JSON response
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}
