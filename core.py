import os
import sys
import time
import ctypes
import cv2
import numpy as np
from ctypes import wintypes
from PIL import Image
import mss

# Windows API
User32 = ctypes.windll.user32
Gdi32 = ctypes.windll.gdi32

# Win32 메시지 관련 상수 선언
WM_LBUTTONDOWN = 0x0201 # 마우스 왼쪽 버튼 누름
WM_LBUTTONUP   = 0x0202 # 마우스 왼쪽 버튼 떼기
WM_MOUSEMOVE   = 0x0200
WM_ACTIVATE    = 0x0006
WM_SETCURSOR   = 0x0020
MK_LBUTTON     = 0x0001

# Win32 키보드 메시지 관련 상수 선언
WM_KEYDOWN    = 0x0100 # 키 누름
WM_KEYUP      = 0x0101 # 키 떼기
WM_CHAR       = 0x0102 # 문자 입력 (채팅창 등 텍스트 타이핑용)

# 자주 쓰는 가상 키코드 (Virtual Key Codes) 매핑
KEY_MAP = {
    'enter': 0x0D, 'esc': 0x1B, 'space': 0x20,
    'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
    'alt':0xA4, 'f1':0x70, 'f2':0x71, 'f3':0x72, 'f4':0x73, 'f5':0x74,
}

# Win32 마우스 휠 관련 상수 선언
WM_MOUSEWHEEL = 0x020A
WHEEL_DELTA   = 120 # 윈도우 표준 1칸 스크롤 값

LONG = ctypes.c_long
DWORD = ctypes.c_ulong
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

# 가상 마우스 하드웨어 상수
INPUT_MOUSE   = 0
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE     = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP   = 0x0004

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", LONG), ("dy", LONG), ("mouseData", DWORD),
        ("dwFlags", DWORD), ("time", DWORD), ("dwExtraInfo", ULONG_PTR)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", DWORD), ("u", INPUT_UNION)]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [('biSize', wintypes.DWORD), ('biWidth', wintypes.LONG), ('biHeight', wintypes.LONG),
                ('biPlanes', wintypes.WORD), ('biBitCount', wintypes.WORD), ('biCompression', wintypes.DWORD),
                ('biSizeImage', wintypes.DWORD), ('biXPelsPerMeter', wintypes.LONG), ('biYPelsPerMeter', wintypes.LONG),
                ('biClrUsed', wintypes.DWORD), ('biClrImportant', wintypes.DWORD)]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [('bmiHeader', BITMAPINFOHEADER), ('bmiColors', wintypes.DWORD * 3)]

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def imread_korean(file_path):
    clean_path = os.path.normpath(file_path)

    if os.path.isabs(clean_path):
        try:
            clean_path = os.path.relpath(clean_path, os.getcwd())
        except Exception:
            pass

    real_path = resource_path(clean_path)

    if not os.path.exists(real_path):
        real_path = os.path.normpath(os.path.join(os.getcwd(), clean_path))

    # 5. 최종 검증 후 이미지 로드
    if not os.path.exists(real_path):
        print(f"파일이 존재하지 않습니다: {real_path}")
        return None, "파일 없음"
    
    try:
        with open(real_path, "rb") as f:
            chunk = np.frombuffer(f.read(), np.uint8)
            img = cv2.imdecode(chunk, cv2.IMREAD_COLOR) 
        return img, None
    except Exception as e:
        return None, f"디코딩 실패: {str(e)}"

def _get_game_hwnd(window_title="NTE"):
    target_hwnd = None
    def callback(hwnd, extra):
        nonlocal target_hwnd
        length = User32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            User32.GetWindowTextW(hwnd, buff, length + 1)
            if buff.value.replace(" ", "") == window_title:
                target_hwnd = hwnd
                return False
        return True
    User32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(callback), 0)
    return target_hwnd

def capture_game_window(window_title="NTE"):
    target_hwnd = _get_game_hwnd(window_title)

    if not target_hwnd:
        return None, f"'{window_title}' 창을 찾을 수 없습니다."

    rect = wintypes.RECT()
    User32.GetWindowRect(target_hwnd, ctypes.byref(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    hdc_screen = User32.GetDC(target_hwnd)
    hdc_mem = Gdi32.CreateCompatibleDC(hdc_screen)
    hbitmap = Gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
    old_bitmap = Gdi32.SelectObject(hdc_mem, hbitmap)

    User32.PrintWindow(target_hwnd, hdc_mem, 2)

    bmpinfo = BITMAPINFO()
    bmpinfo.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmpinfo.bmiHeader.biWidth = width
    bmpinfo.bmiHeader.biHeight = -height
    bmpinfo.bmiHeader.biPlanes = 1
    bmpinfo.bmiHeader.biBitCount = 32
    bmpinfo.bmiHeader.biCompression = 0

    buffer = ctypes.create_string_buffer(width * height * 4)
    Gdi32.GetDIBits(hdc_mem, hbitmap, 0, height, buffer, ctypes.byref(bmpinfo), 1)

    image = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", 0, 1).convert("RGB")
    
    Gdi32.SelectObject(hdc_mem, old_bitmap)
    Gdi32.DeleteObject(hbitmap)
    Gdi32.DeleteDC(hdc_mem)
    User32.ReleaseDC(target_hwnd, hdc_screen)

    return image, None

def click_game_active_window():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def click_game_window(x, y, window_title="NTE"):
    active_window(window_title)
    target_hwnd = _get_game_hwnd(window_title)

    if not target_hwnd:
        return False, f"'{window_title}' 창을 찾을 수 없습니다."
    
    lParam = (y << 16) | (x & 0xFFFF)

    try:

        User32.PostMessageW(target_hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lParam)
        time.sleep(0.05)
        User32.PostMessageW(target_hwnd, WM_LBUTTONUP, 0, lParam)
        
        return True, None
        
    except Exception as e:
        return False, f"클릭 메시지 주입 실패: {str(e)}"

def click_game_window2(x, y, window_title="NTE"):
    active_window(window_title)
    target_hwnd = _get_game_hwnd(window_title)

    if not target_hwnd:
        return False, f"'{window_title}' 창을 찾을 수 없습니다."
    
    if User32.IsIconic(target_hwnd):
        User32.ShowWindow(target_hwnd, 9)
    else:
        User32.ShowWindow(target_hwnd, 5)
        
    User32.SetForegroundWindow(target_hwnd)
    User32.SetActiveWindow(target_hwnd)
    
    time.sleep(0.1)


    orig_pos = wintypes.POINT()
    User32.GetCursorPos(ctypes.byref(orig_pos))


    rect = wintypes.RECT()
    User32.GetWindowRect(target_hwnd, ctypes.byref(rect))
    abs_x = rect.left + x
    abs_y = rect.top + y

    screen_width = User32.GetSystemMetrics(0)
    screen_height = User32.GetSystemMetrics(1)
    normalized_x = int((abs_x * 65536) / screen_width)
    normalized_y = int((abs_y * 65536) / screen_height)

    def send_mouse_input(flags, nx, ny):
        extra = ULONG_PTR(0)
        mi = MOUSEINPUT(nx, ny, 0, flags, 0, extra)
        inp = INPUT(INPUT_MOUSE, INPUT_UNION(mi=mi))
        User32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    try:

        User32.SetForegroundWindow(target_hwnd)

        send_mouse_input(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTDOWN, normalized_x, normalized_y)
        time.sleep(0.1)
        
        send_mouse_input(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTUP, normalized_x, normalized_y)
        time.sleep(0.1)

        orig_nx = int((orig_pos.x * 65536) / screen_width)
        orig_ny = int((orig_pos.y * 65536) / screen_height)
        send_mouse_input(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, orig_nx, orig_ny)
        
        return True, None
    except Exception as e:
        return False, str(e)
     
def active_window(window_title="NTE"):
    target_hwnd = _get_game_hwnd(window_title)
    if not target_hwnd:
        return False, f"'{window_title}' 창을 찾을 수 없습니다."
    
    if User32.IsIconic(target_hwnd):
        User32.ShowWindow(target_hwnd, 9)
    else:
        User32.ShowWindow(target_hwnd, 5)
        
    User32.SetForegroundWindow(target_hwnd)
    User32.SetActiveWindow(target_hwnd)
    time.sleep(0.05)

def press_game_key(key_name, press_time=0.05, window_title="NTE"):
    active_window(window_title)
    target_hwnd = _get_game_hwnd(window_title)
    if not target_hwnd:
        return False, f"'{window_title}' 창을 찾을 수 없습니다."

    key_code = KEY_MAP.get(key_name.lower())
    if not key_code:
        return False, f"지원하지 않는 키 이름입니다: {key_name}"

    try:
        User32.PostMessageW(target_hwnd, WM_KEYDOWN, key_code, 0)
        time.sleep(press_time)

        User32.PostMessageW(target_hwnd, WM_KEYUP, key_code, 0)
        return True, None
    except Exception as e:
        return False, f"키 입력 메시지 주입 실패: {str(e)}"
    
def press_game_key_down(key_name, window_title="NTE"):
    active_window(window_title)
    target_hwnd = _get_game_hwnd(window_title)
    if not target_hwnd:
        return False, f"'{window_title}' 창을 찾을 수 없습니다."

    key_code = KEY_MAP.get(key_name.lower())
    if not key_code:
        return False, f"지원하지 않는 키 이름입니다: {key_name}"

    try:
        User32.PostMessageW(target_hwnd, WM_KEYDOWN, key_code, 0)
        time.sleep(0.05) 
        return True, None
    except Exception as e:
        return False, f"키 입력 메시지 주입 실패: {str(e)}"

def press_game_key_up(key_name, window_title="NTE"):
    active_window(window_title)
    target_hwnd = _get_game_hwnd(window_title)
    if not target_hwnd:
        return False, f"'{window_title}' 창을 찾을 수 없습니다."


    key_code = KEY_MAP.get(key_name.lower())
    if not key_code:
        return False, f"지원하지 않는 키 이름입니다: {key_name}"

    try:
        User32.PostMessageW(target_hwnd, WM_KEYUP, key_code, 0)
        return True, None
    except Exception as e:
        return False, f"키 입력 메시지 주입 실패: {str(e)}"

def type_game_string(text, window_title="NTE"):
    active_window(window_title)
    target_hwnd = _get_game_hwnd(window_title)
    if not target_hwnd:
        return False, f"'{window_title}' 창을 찾을 수 없습니다."

    try:
        for char in text:
            User32.PostMessageW(target_hwnd, WM_CHAR, ord(char), 0)
            time.sleep(0.02)
        return True, None
    except Exception as e:
        return False, f"문자열 주입 실패: {str(e)}"
    
def scroll_game_window(x, y, direction="down", clicks=1, window_title="NTE"):
    active_window(window_title)
    target_hwnd = _get_game_hwnd(window_title)

    if not target_hwnd:
        return False, f"'{window_title}' 창을 찾을 수 없습니다."

    delta = WHEEL_DELTA if direction.lower() == "up" else -WHEEL_DELTA
    total_delta = delta * clicks

    wParam = (total_delta << 16) & 0xFFFF0000
    lParam = (y << 16) | (x & 0xFFFF)

    try:
        User32.PostMessageW(target_hwnd, WM_MOUSEWHEEL, wParam, lParam)
        return True, None
        
    except Exception as e:
        return False, f"휠 스크롤 메시지 주입 실패: {str(e)}"
    
def find_image_in_cropped_zone(template_path, x1, y1, x2, y2, threshold=0.8):
    img_cropped = capture_with_mss(x1, y1, x2, y2)
    if img_cropped is None or img_cropped.size == 0:
        return None, "화면 캡처 실패"

    template, err = imread_korean(template_path)
    if template is None:
        return None, f"템플릿 로드 실패: {err}"

    img_crop_gray = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    w, h = gray_template.shape[::-1]

    res = cv2.matchTemplate(img_crop_gray, gray_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        crop_center_x = max_loc[0] + int(w / 2)
        crop_center_y = max_loc[1] + int(h / 2)
        final_x = x1 + crop_center_x
        final_y = y1 + crop_center_y
        print(f"[{template_path} 매칭 성공] 유사도: {max_val:.2f} | 좌표: ({final_x}, {final_y})")
        return (final_x, final_y), None
    else:
        print(f"[{template_path} 매칭 실패] 최대 유사도: {max_val:.2f}")
        return None, "유사도 미달"

def rotate_camera(dx, dy, window_title="NTE"):
    active_window(window_title)
    target_hwnd = _get_game_hwnd(window_title)

    if not target_hwnd:
        return False, f"'{window_title}' 창을 찾을 수 없습니다."
    
    if User32.IsIconic(target_hwnd):
        User32.ShowWindow(target_hwnd, 9)
    else:
        User32.ShowWindow(target_hwnd, 5)
        
    User32.SetForegroundWindow(target_hwnd)
    User32.SetActiveWindow(target_hwnd)
    
    time.sleep(0.1)

    extra = ULONG_PTR(0)
    mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, extra)
    inp = INPUT(INPUT_MOUSE, INPUT_UNION(mi=mi))
    
    User32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

def capture_with_mss(x1, y1, x2, y2, window_title="NTE"):
    active_window(window_title)
    target_hwnd = _get_game_hwnd(window_title)

    if not target_hwnd:
        return False, f"'{window_title}' 창을 찾을 수 없습니다."

    rect = wintypes.RECT()
    User32.GetWindowRect(target_hwnd, ctypes.byref(rect))
    
    monitor_rect = {
        "top": rect.top + y1,
        "left": rect.left + x1,
        "width": x2 - x1,
        "height": y2 - y1
    }
    with mss.MSS() as sct:
        img = sct.grab(monitor_rect)
        
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        
        return frame

def find_object_fast(template_path, x1, y1, x2, y2, threshold=0.8):
    img_cropped = capture_with_mss(x1, y1, x2, y2)
    gray_crop = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2GRAY)
    
    template, _ = imread_korean(template_path)
    if template is None: 
        return None, "템플릿 로드 실패"
        
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    res = cv2.matchTemplate(gray_crop, gray_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        final_x = x1 + max_loc[0] + (gray_template.shape[1] // 2)
        final_y = y1 + max_loc[1] + (gray_template.shape[0] // 2)
        print(f"[{template_path} 매칭 성공] 유사도: {max_val:.2f} | 좌표: ({final_x}, {final_y})")
        return (final_x, final_y), None
    else:
        print(f"[{template_path} 매칭 실패] 최대 유사도: {max_val:.2f}")
    return None, "매칭 실패"