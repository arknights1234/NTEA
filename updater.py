import os
import sys
import json
import ctypes
import tempfile
import subprocess
import urllib.request
from pathlib import Path

# 💡 본인의 GitHub 정보로 변경하세요.
OWNER = "arknights1234"
REPO = "NTEA"
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def current_exe_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    return Path(sys.argv[0]).resolve()


def parse_version(v: str):
    v = v.lower().strip().lstrip("v")
    parts = []
    for x in v.split("."):
        try:
            parts.append(int(x))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def check_for_update(current_version: str):
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        latest_version = data.get("tag_name", "v0.0.0")
        is_available = parse_version(latest_version) > parse_version(current_version)
        
        return is_available, latest_version
        
    except Exception as e:
        print(f"업데이트 확인 실패: {e}")
        return False, "확인 실패"


def download_asset(asset_url: str, save_path: Path, progress_callback=None):
    req = urllib.request.Request(asset_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/octet-stream"})
    
    with urllib.request.urlopen(req, timeout=60) as response:
        total_size = int(response.headers.get('content-length', 0))
        
        with open(save_path, "wb") as f:
            downloaded = 0
            chunk_size = 8192
            
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                if total_size > 0 and progress_callback:
                    percent = int((downloaded / total_size) * 100)
                    current_mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    progress_callback(percent, current_mb, total_mb)


def start_updater(downloaded_file: Path, target_exe: Path):
    updater_path = app_dir() / "updater.bat"
    target_filename = target_exe.name
    old_filename = f"old_{target_filename}"

    target_dir_str = str(app_dir())
    downloaded_file_str = str(downloaded_file)
    target_exe_str = str(target_exe)

    with open(updater_path, "w", encoding="cp949") as f:
        f.write("@echo off\n")
        f.write(f"cd /d \"{target_dir_str}\"\n")

        f.write(f"taskkill /f /im \"{target_filename}\" > nul 2>&1\n")
        
        f.write(":wait_process\n")
        f.write("timeout /t 1 /nobreak > nul\n")
        
        f.write(f"if exist \"{target_filename}\" (\n")
        f.write(f"    ren \"{target_filename}\" \"{old_filename}\" > nul 2>&1\n")

        f.write(f"    if exist \"{target_filename}\" goto wait_process\n")
        f.write(")\n")
        
        f.write(f"move /y \"{downloaded_file_str}\" \"{target_exe_str}\" > nul\n")
        
        f.write(f"start \"\" \"{target_exe_str}\"\n")
        
        f.write("timeout /t 2 /nobreak > nul\n")
        f.write(f"del /f /q \"{old_filename}\" > nul 2>&1\n")
        f.write(f"start /b cmd /c del /f /q \"{str(updater_path)}\" & exit\n")

    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            str(updater_path), 
            None, 
            target_dir_str, 
            0  # 0 = 창 숨김 (SW_HIDE)
        )
    except Exception as e:
        print(f"윈도우 쉘 실행 실패: {e}")
        
    os._exit(0)


def download_and_install(progress_callback=None):
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        assets = data.get("assets", [])
        if not assets:
            print("다운로드할 에셋이 없습니다.")
            return False

        asset = assets[0]
        download_url = asset.get("browser_download_url")
        file_name = asset.get("name", "update.exe")

        if not download_url:
            print("다운로드 URL이 없습니다.")
            return False

        temp_dir = Path(tempfile.gettempdir()) / "ntea_update"
        temp_dir.mkdir(parents=True, exist_ok=True)

        downloaded_path = temp_dir / file_name

        download_asset(download_url, downloaded_path, progress_callback)

        target_exe = current_exe_path()
        start_updater(downloaded_path, target_exe)

        return True

    except Exception as e:
        print(f"업데이트 다운로드 중 오류 발생: {e}")
        return False