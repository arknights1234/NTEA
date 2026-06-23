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
    """프로그램이 위치한 실제 하드디스크 디렉토리 경로를 반환합니다."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def current_exe_path() -> Path:
    """현재 실행 중인 파일의 절대 경로를 반환합니다."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    return Path(sys.argv[0]).resolve()


def parse_version(v: str):
    """v1.0.0 형태의 버전을 숫자 튜플 (1, 0, 0) 형태로 변환합니다."""
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
    """
    현재 버전과 GitHub 최신 버전을 비교합니다.
    GUI 호환 반환 값: (업데이트 가능 여부, 최신 버전 문자열)
    """
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        latest_version = data.get("tag_name", "v0.0.0")
        is_available = parse_version(latest_version) > parse_version(current_version)
        
        # GUI 코드에서 [is_update_available, latest_v] 형태로 받으므로 이에 맞춤
        return is_available, latest_version
        
    except Exception as e:
        print(f"업데이트 확인 실패: {e}")
        return False, "확인 실패"


def download_asset(asset_url: str, save_path: Path):
    """GitHub 자산을 바이너리 파일로 다운로드합니다."""
    req = urllib.request.Request(asset_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/octet-stream"})
    with urllib.request.urlopen(req, timeout=60) as response, open(save_path, "wb") as f:
        f.write(response.read())


def start_updater(downloaded_file: Path, target_exe: Path):
    """
    [파이썬 3.14 DLL 오류 완전 봉쇄 버전]
    배치 파일 내부에서 기존 프로세스가 완전히 종료될 때까지 무한 루프로 대기한 후,
    파일이 확실히 풀려났을 때 이름 변경(ren) 및 교체를 진행합니다.
    """
    updater_path = app_dir() / "updater.bat"
    target_filename = target_exe.name
    old_filename = f"old_{target_filename}"

    target_dir_str = str(app_dir())
    downloaded_file_str = str(downloaded_file)
    target_exe_str = str(target_exe)

    # 1. 프로세스 종료 대기 루프가 포함된 안전한 배치 파일 생성
    with open(updater_path, "w", encoding="cp949") as f:
        f.write("@echo off\n")
        f.write(f"cd /d \"{target_dir_str}\"\n")
        
        # 💡 [핵심] 기존 실행 파일 프로세스를 강제 종료 명령 하달
        f.write(f"taskkill /f /im \"{target_filename}\" > nul 2>&1\n")
        
        # 💡 [핵심] 프로세스가 메모리와 디스크에서 완전히 사라질 때까지 무한 루프로 체크
        # 파이썬 3.14의 임시 폴더 락이 완전히 해제될 때까지 이름 변경(ren)을 시도하며 대기합니다.
        f.write(":wait_process\n")
        f.write("timeout /t 1 /nobreak > nul\n")
        
        # 이름 변경을 시도해봅니다. 성공하면 프로세스가 죽어서 파일 락이 풀린 것입니다.
        f.write(f"if exist \"{target_filename}\" (\n")
        f.write(f"    ren \"{target_filename}\" \"{old_filename}\" > nul 2>&1\n")
        # 만약 이름 변경에 실패해서 여전히 원본 파일명이 존재한다면 다시 대기 루프로 이동
        f.write(f"    if exist \"{target_filename}\" goto wait_process\n")
        f.write(")\n")
        
        # 락이 완벽히 풀린 안전한 상태에서 새 버전 파일 이동(덮어쓰기)
        f.write(f"move /y \"{downloaded_file_str}\" \"{target_exe_str}\" > nul\n")
        
        # 새 버전 프로그램 실행
        f.write(f"start \"\" \"{target_exe_str}\"\n")
        
        # 구버전 파일 삭제 및 배치 파일 자폭
        f.write("timeout /t 2 /nobreak > nul\n")
        f.write(f"del /f /q \"{old_filename}\" > nul 2>&1\n")
        f.write(f"start /b cmd /c del /f /q \"{str(updater_path)}\" & exit\n")

    # 2. 윈도우 API를 이용해 독립된 프로세스로 배치 파일 호출 (runas로 최고 권한 승계)
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
        
    # 3. 배치를 실행하자마자 부모인 파이썬 프로세스를 즉시 강제 종료하여 락 해제를 도와줌
    os._exit(0)


def download_and_install():
    """
    GUI의 start_update에서 호출하는 핵심 함수입니다.
    최신 파일을 다운로드하고 교체 프로세스(start_updater)를 시작합니다.
    """
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        assets = data.get("assets", [])
        if not assets:
            print("다운로드할 에셋이 없습니다.")
            return False

        # 첫 번째 에셋(업로드한 exe)을 대상으로 타겟팅
        asset = assets[0]
        download_url = asset.get("browser_download_url")
        file_name = asset.get("name", "update.exe")

        if not download_url:
            print("다운로드 URL이 없습니다.")
            return False

        # 윈도우 임시 폴더 내 안전구역 생성
        temp_dir = Path(tempfile.gettempdir()) / "ntea_update"
        temp_dir.mkdir(parents=True, exist_ok=True)

        downloaded_path = temp_dir / file_name
        
        # 다운로드 시작
        download_asset(download_url, downloaded_path)

        # 현재 실행 파일의 진짜 위치를 파악하여 교체 명령 하달
        target_exe = current_exe_path()
        start_updater(downloaded_path, target_exe)

        return True

    except Exception as e:
        print(f"업데이트 다운로드 중 오류 발생: {e}")
        return False