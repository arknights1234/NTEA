import os
import sys
import json
import urllib.request
import subprocess

# 💡 본인의 GitHub 닉네임과 레포지토리 이름으로 변경하세요.
OWNER = "arknights1234"
REPO = "NTEA"

# GitHub Latest Release API 주소
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"

def check_for_update(current_version: str):
    """
    현재 버전과 GitHub의 최신 버전을 비교합니다.
    return: (업데이트 가능 여부(Bool), 최신 버전 문자열(str))
    """
    try:
        # GitHub API는 User-Agent 헤더가 필수입니다.
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            
            # GitHub에 등록된 최신 태그명 (예: "v1.1.0" 또는 "1.1.0")
            latest_version = data.get("tag_name", "v0.0.0")
            
            # 간단한 버전 비교 로직 (v 제거 후 숫자 비교)
            curr_clean = current_version.lower().replace("v", "").strip()
            late_clean = latest_version.lower().replace("v", "").strip()
            
            curr_parsed = [int(x) for x in curr_clean.split(".") if x.isdigit()]
            late_parsed = [int(x) for x in late_clean.split(".") if x.isdigit()]
            
            # 최신 버전이 더 높다면 True 반환
            if late_parsed > curr_parsed:
                return True, latest_version
            return False, latest_version
            
    except Exception as e:
        print(f"업데이트 확인 실패: {e}")
        return False, "확인 실패"

def download_and_install():
    """
    GitHub Release의 첫 번째 Asset(배포 파일)을 다운로드하고
    프로그램을 종료한 뒤 배치 파일로 덮어쓰기를 수행합니다.
    """
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            assets = data.get("assets", [])
            
            if not assets:
                print("다운로드할 에셋(파일)이 없습니다.")
                return False
                
            # 첫 번째 배포 자산의 다운로드 URL 및 파일명 가져오기
            download_url = assets[0].get("browser_download_url")
            file_name = assets[0].get("name") # 예: ntea_update.exe 또는 script.py
            
            # 1. 임시 파일로 다운로드
            temp_file = "update_temp_" + file_name
            print(f"다운로드 시작: {download_url}")
            
            urllib.request.urlretrieve(download_url, temp_file)
            print("다운로드 완료. 교체 스크립트를 생성합니다.")
            
            # 2. 실행 중인 현재 파일 정보 확보
            if getattr(sys, 'frozen', False):
                # PyInstaller로 빌드된 .exe 환경일 때 진짜 .exe 경로를 가져옵니다.
                current_exe = sys.executable 
            else:
                # 일반 .py 파일 실행 환경일 때
                current_exe = sys.argv[0]

            current_filename = os.path.basename(current_exe)
            
            # 3. 자체 덮어쓰기용 Windows 배치 파일(.bat) 생성
            # 프로그램이 켜져 있으면 exe 파일이 잠겨서 안 바뀌므로, 종료 후 바꿀 bat 파일이 필요합니다.
            bat_filename = "update_handler.bat"
            with open(bat_filename, "w", encoding="cp949") as f:
                f.write("@echo off\n")
                f.write("timeout /t 1 /nobreak > rcl\n") # 1초 대기 (프로그램이 완전히 꺼질 시간)
                f.write(f"move /y \"{temp_file}\" \"{current_filename}\"\n") # 파일 덮어쓰기
                f.write(f"start \"\" \"{current_filename}\"\n") # 프로그램 재시작
                f.write(f"del \"{bat_filename}\"\n") # 본인(bat) 삭제
                f.write("exit\n")
            
            # 4. 배치 파일 실행 후 메인 GUI 프로그램 강제 종료
            subprocess.Popen([bat_filename], shell=True)
            os._exit(0)
            
    except Exception as e:
        print(f"업데이트 다운로드 중 오류 발생: {e}")
        return False