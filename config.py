# config.py
# Created by William Winslade on 28 Jan 2025

from dotenv import load_dotenv
import os

env_file = ".env.development.local"

load_dotenv(dotenv_path=env_file)

# Ubibot API Key
UBIBOT_API_KEY = os.getenv("UBIBOT_API_KEY")
if not UBIBOT_API_KEY:
  raise ValueError("Missing UbiBot API Key -- Check ")

# Ubibot Channel value. Not sure if it is actually a secret or not, but playing it safe
UBIBOT_CHANNEL = os.getenv("UBIBOT_CHANNEL")