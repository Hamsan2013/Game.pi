# RasPi Game Caster

This repo contains a PySide6 GUI that launches `scrcpy` to mirror an Android phone and sends keyboard/mouse events from the Pi to the phone using `adb`.

## Quick start
1. Put your phone in Personal Hotspot mode and connect the Pi to it.
2. Pair adb over TCP (temporary USB pairing or Wireless Debugging):
   - Option A (USB temporary): Connect phone via USB, run `adb tcpip 5555`, disconnect USB.
   - Option B (Wireless debugging on device): use pairing code/pairing flow.
3. On the Pi, run: `adb connect PHONE_IP:5555`
4. Run the app: `python3 app.py`
5. Click **Start Stream** to open scrcpy (shows phone screen).
6. Use keyboard & mouse — mappings come from `mappings.json`.
7. To use AI analysis (auto-generate mapping), set environment variable `OPENAI_API_KEY` before running and press Analyze & Add Mapping.

## One-line installer (after you push to GitHub)
Replace `USERNAME` and `REPO`:

```bash
sudo bash <(curl -s https://raw.githubusercontent.com/USERNAME/REPO/main/install.sh)
```

## Notes
- Do NOT upload API keys to this repo.
- Delete any leaked API keys and create a new one before using OpenAI features.
