import os
import json

CONFIG_FILE = "config.json"

# 초기 기본값 설정
DEFAULT_CONFIG = {
    "daily_quest": {},
    "fishing_settings": {},
    "event_racing_setting": {},
    "nanally_superjump_setting": {},
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"설정 파일 로드 실패(초기값으로 대체): {e}")
        return DEFAULT_CONFIG

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"설정 파일 저장 실패: {e}")