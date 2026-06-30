import customtkinter as ctk
import core
import time
from PIL import Image
from config_manager import load_config, save_config
from macro_engine import MacroEngine
import keyboard
from pynput import mouse
import win32api
import win32con
import win32gui
import ctypes
import version

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class HotkeyManager:
    def __init__(self, start_callback, stop_callback=None):
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.mouse_listener = None
        self.keyboard_hook_ref = None
        self.is_active = False

    def start(self, target_key):
        tk_lower = str(target_key).lower()
        pure_key = tk_lower.replace("mouse_", "")
        mouse_buttons = ["left", "right", "middle", "x1", "x2", "button4", "button5"]

        if "mouse_" not in tk_lower and tk_lower not in mouse_buttons:
            def on_key_event(e):
                if e.name.lower() == tk_lower:
                    if e.event_type == keyboard.KEY_DOWN:
                        if not self.is_active:
                            self.is_active = True
                            self.start_callback()
                    elif e.event_type == keyboard.KEY_UP:
                        self.is_active = False
                        if self.stop_callback:
                            self.stop_callback()

            self.keyboard_hook_ref = on_key_event
            keyboard.hook(on_key_event)

        else:
            def on_click(x, y, button, pressed):
                btn_str = str(button).lower()
                btn_name = button.name.lower()
                
                if pure_key in btn_str or pure_key == btn_name:
                    if pressed:
                        if not self.is_active:
                            self.is_active = True
                            self.start_callback()
                    else:
                        self.is_active = False
                        if self.stop_callback:
                            self.stop_callback()

            self.mouse_listener = mouse.Listener(on_click=on_click)
            self.mouse_listener.start()

    def stop(self):
        if self.keyboard_hook_ref:
            try:
                keyboard.unhook(self.keyboard_hook_ref)
            except Exception:
                pass
        
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception:
                pass
            
        self.is_active = False

class cafe_earning:
    def __init__(self):
        self.name = "별미 카페 수익 받기"
        self.task_key = "run_cafe_earning"

    def build_settings_ui(self, parent_frame):
        return
    
class fishing:
    def __init__(self):
        self.name = "낚시"
        self.task_key = "run_fishing"

    def build_settings_ui(self, parent_frame):
        current_config = load_config()
        saved_count = current_config.get("fishing_settings", {}).get("max_count", "100")
        saved_option = current_config.get("fishing_settings", {}).get("bait", False)
        saved_option2 = current_config.get("fishing_settings", {}).get("sell", False)

        count_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        count_frame.pack(fill="x", padx=10, pady=(10, 5))

        lbl_count = ctk.CTkLabel(count_frame, text="최대 낚시 횟수 :", font=("맑은 고딕", 12))
        lbl_count.pack(side="left", padx=(0, 10))

        def validate_numeric(P):
            if P == "" or P.isdigit():
                return True
            return False
        
        vcmd = (parent_frame.register(validate_numeric), '%P')

        self.count_var = ctk.StringVar(value=str(saved_count))

        self.count_var.trace_add("write", lambda *args: self.save_settings_live())

        self.ent_count = ctk.CTkEntry(
            count_frame, 
            width=80, 
            textvariable=self.count_var, 
            justify="center",
            validate="key",            # 키보드가 눌릴 때마다 검사하겠다는 의미
            validatecommand=vcmd       # 검사할 때 위에서 만든 vcmd 함수를 실행
        )
        self.ent_count.pack(side="left")

        lbl_unit = ctk.CTkLabel(count_frame, text="회", font=("맑은 고딕", 12))
        lbl_unit.pack(side="left", padx=5)
        
        self.check_var = ctk.BooleanVar(value=saved_option)
        self.check_var2 = ctk.BooleanVar(value=saved_option2)
        
        self.chk_auto = ctk.CTkCheckBox(
            parent_frame, 
            text="미끼 자동 구매", 
            variable=self.check_var,
            command=self.save_settings_live
        )
        self.chk_auto2 = ctk.CTkCheckBox(
            parent_frame, 
            text="어획물 자동 판매", 
            variable=self.check_var2,
            command=self.save_settings_live
        )
        self.chk_auto.pack(fill="x", padx=10, pady=10)
        self.chk_auto2.pack(fill="x", padx=10, pady=0)

        usage_text = (
            "낚시 시작을 눌러 감정사가 낚싯대를 든 상태에서 시작\n"
            "만능 미끼 10개씩 자동 구매 가능\n"
            "낚시 10회마다 일괄 판매 가능"
        )
        ctk.CTkLabel(parent_frame, text=usage_text, justify="left", font=("맑은 고딕", 12)).pack(pady=10)

    def save_settings_live(self):
        config = load_config()
        if "fishing_settings" not in config:
            config["fishing_settings"] = {}
            
        config["fishing_settings"]["max_count"] = self.count_var.get()
        config["fishing_settings"]["bait"] = self.check_var.get()
        config["fishing_settings"]["sell"] = self.check_var2.get()

        save_config(config)

class event_racing:
    def __init__(self):
        self.name = "무법 레이싱"
        self.task_key = "run_event_racing"

    def build_settings_ui(self, parent_frame):
        current_config = load_config()
        saved_option = current_config.get("event_racing_setting", {}).get("time", True)
        
        self.check_var = ctk.BooleanVar(value=saved_option)
        
        self.chk_auto = ctk.CTkCheckBox(
            parent_frame, 
            text="최대 대기 시간 10분", 
            variable=self.check_var,
            command=self.save_settings_live
        )
        self.chk_auto.pack(fill="x", padx=10, pady=20)

    def save_settings_live(self):
        current_state = self.check_var.get()
        
        config = load_config()
        if "event_racing_setting" not in config:
            config["event_racing_setting"] = {}
            
        config["event_racing_setting"]["time"] = current_state
        save_config(config)

class nanally_superjump:
    def __init__(self):
        self.name = "나나리 슈퍼점프"
        self.task_key = "run_nanally_superjump"
        self.is_listening = False

    def build_settings_ui(self, parent_frame):
        config = load_config()
        settings = config.get("nanally_superjump_setting", {})
        saved_key = settings.get("key", "caps lock")
        saved_delay = float(settings.get("delay", 0.00))

        self.key_label = ctk.CTkLabel(parent_frame, text=f"현재 단축키: [{saved_key}]", font=("맑은 고딕", 13))
        self.key_label.pack(pady=(10, 5))
        ctk.CTkButton(parent_frame, text="단축키 변경", command=self.start_listening).pack()

        self.delay_var = ctk.DoubleVar(value=saved_delay)
        
        delay_frame = ctk.CTkFrame(parent_frame)
        delay_frame.pack(pady=15, fill="x", padx=10)
        
        ctk.CTkLabel(delay_frame, text="점프 딜레이(s):").pack(side="left", padx=5)
        
        ctk.CTkButton(delay_frame, text="-", width=30, 
                      command=lambda: self.update_delay(-0.01)).pack(side="left")
        
        self.delay_entry = ctk.CTkLabel(delay_frame, textvariable=self.delay_var, width=50)
        self.delay_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(delay_frame, text="+", width=30, 
                      command=lambda: self.update_delay(0.01)).pack(side="left")
        
        ctk.CTkButton(delay_frame, text="기본값", width=40, fg_color="gray",
                      command=self.reset_delay).pack(side="left", padx=10)

        usage_text = (
            "점프 타이밍 조절 가능 (기본값 0.00)\n"
            "단축키는 마우스 버튼도 가능\n"
            "매크로 실행 후 게임 화면에서 단축키를 눌러서 사용"
        )
        ctk.CTkLabel(parent_frame, text=usage_text, justify="left", font=("맑은 고딕", 12)).pack(pady=10)

    def update_delay(self, delta):
        new_val = round(self.delay_var.get() + delta, 2)
        self.delay_var.set(new_val)
        self.save_delay_to_config(new_val)

    def reset_delay(self):
        self.delay_var.set(0.00)
        self.save_delay_to_config(0.00)

    def save_delay_to_config(self, value):
        config = load_config()
        if "nanally_superjump_setting" not in config:
            config["nanally_superjump_setting"] = {}
        config["nanally_superjump_setting"]["delay"] = value
        save_config(config)

    def start_listening(self):
        self.is_listening = True
        self.key_label.configure(text="키보드나 마우스 버튼을 누르세요...", text_color="#f1c40f")

        def on_key(event):
            if self.is_listening:
                self.save_key(event.name)
                self.is_listening = False
                keyboard.unhook(on_key)
        keyboard.hook(on_key)

        def on_click(x, y, button, pressed):
            if pressed and self.is_listening:
                self.save_key(f"mouse_{button.name}") 
                self.is_listening = False
                m_listener.stop()
                keyboard.unhook(on_key)

        m_listener = mouse.Listener(on_click=on_click)
        m_listener.start()

    def save_key(self, key):
        config = load_config()
        if "nanally_superjump_setting" not in config:
            config["nanally_superjump_setting"] = {}
        config["nanally_superjump_setting"]["key"] = key
        save_config(config)
        
        self.key_label.configure(text=f"현재 단축키: [{key}]", text_color="#2ecc71")

class mouse_auto_click:
    def __init__(self):
        self.name = "마우스 광클"
        self.task_key = "run_mouse_auto_click"
        self.is_listening = False

    def build_settings_ui(self, parent_frame):
        config = load_config()
        settings = config.get("mouse_auto_click_setting", {})
        saved_key = settings.get("key", "caps lock")

        self.key_label = ctk.CTkLabel(parent_frame, text=f"현재 단축키: [{saved_key}]", font=("맑은 고딕", 13))
        self.key_label.pack(pady=(10, 5))
        ctk.CTkButton(parent_frame, text="단축키 변경", command=self.start_listening).pack()
        
        usage_text = (
            "감옥 설거지용\n"
            "단축키는 마우스 버튼도 가능\n"
            "매크로 실행 후 게임 화면에서 단축키를 꾹 눌러서 사용"
        )
        ctk.CTkLabel(parent_frame, text=usage_text, justify="left", font=("맑은 고딕", 12)).pack(pady=10)

    def start_listening(self):
        self.is_listening = True
        self.key_label.configure(text="키보드나 마우스 버튼을 누르세요...", text_color="#f1c40f")

        def on_key(event):
            if self.is_listening:
                self.save_key(event.name)
                self.is_listening = False
                keyboard.unhook(on_key)
        keyboard.hook(on_key)

        def on_click(x, y, button, pressed):
            if pressed and self.is_listening:
                self.save_key(f"mouse_{button.name}") 
                self.is_listening = False
                m_listener.stop()
                keyboard.unhook(on_key)

        m_listener = mouse.Listener(on_click=on_click)
        m_listener.start()

    def save_key(self, key):
        config = load_config()
        if "mouse_auto_click_setting" not in config:
            config["mouse_auto_click_setting"] = {}
        config["mouse_auto_click_setting"]["key"] = key
        save_config(config)
        
        self.key_label.configure(text=f"현재 단축키: [{key}]", text_color="#2ecc71")

class owners_selection:
    def __init__(self):
        self.name = "점장 특제"
        self.task_key = "run_owners_selection"

    def build_settings_ui(self, parent_frame):
        usage_text = (
            "점장 특제 스테이지 선택 화면에서 실행\n"
            "1-1반복\n"
            "보조 직원 라크리모사, 다포딜 사용 시 더 빠름"
        )
        ctk.CTkLabel(parent_frame, text=usage_text, justify="left", font=("맑은 고딕", 12)).pack(pady=10)

WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int)
GWL_WNDPROC = -4

class MacroOverlay(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "#333333")
        self.configure(fg_color="#333333")

        target_hwnd = core._get_game_hwnd()
        if not target_hwnd:
            return None
        
        rect = win32gui.GetWindowRect(target_hwnd)
        x, y = rect[0], rect[1]+1080
        w, h = 200, 40
        x2 = x - w 
        y2 = y - h 
        self.geometry(f"{w}x{h}+{x}+{y2}")

        self.after(50, self.apply_overlay_mode)

    def apply_overlay_mode(self):
        self.hwnd = int(self.winfo_id())
        
        style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, 
                               style | win32con.WS_EX_TRANSPARENT | 
                               win32con.WS_EX_LAYERED | 
                               win32con.WS_EX_NOACTIVATE | 
                               win32con.WS_EX_TOOLWINDOW)

        win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 255, win32con.LWA_ALPHA)

        self.wndproc_ref = WNDPROC(self.pure_wndproc)
        self.old_wndproc = win32gui.SetWindowLong(self.hwnd, GWL_WNDPROC, self.wndproc_ref)

    def pure_wndproc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_SETCURSOR:
            return 1 
        
        if msg == 0x0084:
            return -1

        if msg == win32con.WM_PAINT:
            hdc, ps = win32gui.BeginPaint(hwnd)
            
            win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
            
            lf = win32gui.LOGFONT()
            lf.lfHeight = -15
            lf.lfWeight = 700
            lf.lfFaceName = "맑은 고딕"
            hfont = win32gui.CreateFontIndirect(lf)
            old_font = win32gui.SelectObject(hdc, hfont)

            win32gui.SetTextColor(hdc, win32api.RGB(0, 255, 255))
            win32gui.DrawText(hdc, " 매크로 실행 중", -1, (5, 8, 150, 40), win32con.DT_LEFT)
            
            win32gui.SetTextColor(hdc, win32api.RGB(207, 45, 45))
            win32gui.DrawText(hdc, "[F2] 중지", -1, (125, 8, 250, 40), win32con.DT_LEFT)
            
            win32gui.SelectObject(hdc, old_font)
            win32gui.DeleteObject(hfont)
            win32gui.EndPaint(hwnd, ps)
            return 0

        return win32gui.CallWindowProc(self.old_wndproc, hwnd, msg, wparam, lparam)
class MainGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NTEA")
        self.geometry("1100x600")
        self.resizable(False, False)

        self.engine = MacroEngine(self)

        self.checkbox_vars = {}

        self.active_listeners = []
        

        self.tab1_tasks = [cafe_earning()]
        self.tab2_tasks = [fishing(),
                           owners_selection(),
                           nanally_superjump(),
                           mouse_auto_click()]
        self.tab3_tasks = [event_racing()]

        self.running_tabs = set()

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=0, pady=0)
        
        space = " " * 25  
        self.tab_names = [f"{space}일일{space}", f"{space}상시{space}", f"{space}기타{space}", f"{space}정보{space}"]
        
        self.tab1 = self.tab_view.add(self.tab_names[0])
        self.tab2 = self.tab_view.add(self.tab_names[1])
        self.tab3 = self.tab_view.add(self.tab_names[2])
        self.tab4 = self.tab_view.add(self.tab_names[3])

        self.setup_tab_layout(self.tab1, is_radio=False, task_objects=self.tab1_tasks, tab_id=self.tab_names[0])
        self.setup_tab_layout(self.tab2, is_radio=True, task_objects=self.tab2_tasks, tab_id=self.tab_names[1])
        self.setup_tab_layout(self.tab3, is_radio=True, task_objects=self.tab3_tasks, tab_id=self.tab_names[2])

        self.setup_fourth_tab()

        keyboard.add_hotkey('f2', self.trigger_stop_by_hotkey)

        self.overlay = None

    def trigger_stop_by_hotkey(self):
        if not self.running_tabs:
            return
        
        def find_and_invoke():
            for tab_obj in [self.tab1, self.tab2, self.tab3]:
                for widget in tab_obj.winfo_children():
                    if isinstance(widget, ctk.CTkFrame):
                        for child in widget.winfo_children():
                            if isinstance(child, ctk.CTkButton) and child.cget("text") == "중지":
                                child.invoke()
                                return

        self.after(0, find_and_invoke)

    def setup_tab_layout(self, tab_object, is_radio, task_objects, tab_id):
        tab_object.grid_columnconfigure(0, weight=0)
        tab_object.grid_columnconfigure(1, weight=1)
        tab_object.grid_columnconfigure(2, weight=1)
        tab_object.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(tab_object, width=320)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_propagate(False) 
        
        middle_frame = ctk.CTkFrame(tab_object)
        middle_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        right_frame = ctk.CTkFrame(tab_object)
        right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        setting_title, setting_content = self.create_middle_section(middle_frame)
        log_text = self.create_right_section(right_frame)

        self.create_left_section(left_frame, is_radio, task_objects, setting_title, setting_content, log_text, tab_id)

    def on_checkbox_changed(self, task_name):
        current_state = self.checkbox_vars[task_name].get()
        
        self.config = load_config()
        
        if "daily_quest" not in self.config:
            self.config["daily_quest"] = {}
            
        self.config["daily_quest"][task_name] = current_state
        
        save_config(self.config)
    
    def create_left_section(self, left_frame, is_radio, task_objects, setting_title, setting_content, log_text, tab_id):
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=0)
        left_frame.grid_columnconfigure(0, weight=1)

        task_box = ctk.CTkScrollableFrame(left_frame, label_text="작업 목록", width=300)
        task_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        radio_var = ctk.StringVar(value="") if is_radio else None
        selectors, gear_buttons = [], []

        if not hasattr(self, 'checkbox_vars'):
            self.checkbox_vars = {}

        if not is_radio:
            self.config = load_config()
            daily_quest_config = self.config.get("daily_quest", {})

        for task in task_objects:
            task_item_frame = ctk.CTkFrame(task_box, fg_color="transparent")
            task_item_frame.pack(fill="x", padx=5, pady=5)
            
            if is_radio: 
                selector = ctk.CTkRadioButton(task_item_frame, text="", variable=radio_var, value=task.name, width=24)
            else:
                initial_value = daily_quest_config.get(task.name, False)
                var = ctk.BooleanVar(value=initial_value)
                self.checkbox_vars[task.name] = var
                
                selector = ctk.CTkCheckBox(
                    task_item_frame, 
                    text="", 
                    width=24, 
                    variable=var,
                    command=lambda t_name=task.name: self.on_checkbox_changed(t_name)
                )
                
            selector.task_reference = task 
            
            selector.pack(side="left", padx=(5, 5))
            selectors.append(selector)

            lbl = ctk.CTkLabel(task_item_frame, text=task.name, anchor="w")
            lbl.pack(side="left", padx=(0, 5))

            btn = ctk.CTkButton(task_item_frame, text="⚙", width=30, height=24, fg_color="#333333", hover_color="#555555",
                                command=lambda t=task, sc=setting_content, st=setting_title, lt=log_text: self.on_gear_clicked(t, sc, st, lt))
            btn.pack(side="right", padx=5)
            gear_buttons.append(btn)

        toggle_btn = ctk.CTkButton(left_frame, text="시작", fg_color="#1f538d")
        
        toggle_btn.configure(command=lambda b=toggle_btn, lt=log_text, tid=tab_id, sel=selectors, gb=gear_buttons, sc=setting_content, rv=radio_var: 
                             self.toggle_status(b, lt, tid, sel, gb, sc, rv))
        toggle_btn.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def on_gear_clicked(self, task, content_frame, title_label, log_widget):
        for widget in content_frame.winfo_children(): widget.destroy()
        title_label.configure(text=f"⚙ [{task.name}] 세부 설정")
        task.build_settings_ui(content_frame)

    def reset_ui_after_macro(self, tab_id, button, selectors, gear_buttons, setting_content):
        button.configure(text="시작", fg_color="#1f538d", hover_color="#14375e")
        
        self.running_tabs.discard(tab_id)
        
        for s in selectors: 
            s.configure(state="normal")
        for g in gear_buttons: 
            g.configure(state="normal")
            
        self.set_frame_widgets_state(setting_content, "normal")
        
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

        self.engine.stop_macro()

        self.update_tab_lock_state()
         

    def toggle_status(self, button, log_widget, tab_id, selectors, gear_buttons, setting_content, radio_var=None):
        
        if button.cget("text") == "시작":
            selected_tasks = []
            self.overlay = MacroOverlay(self)
            
            if radio_var is not None:
                chosen_task_name = radio_var.get()
                
                if not chosen_task_name:
                    self.append_log(log_widget, f"[{time.ctime().split()[3]}] 선택된 작업 없음")
                    return
                
                for selector in selectors:
                    if hasattr(selector, 'task_reference') and selector.task_reference.name == chosen_task_name:
                        selected_tasks.append(selector.task_reference)
                        break
                 
            else:
                for selector in selectors:
                    if selector.get() == 1:
                        if hasattr(selector, 'task_reference'):
                            selected_tasks.append(selector.task_reference)

            if not selected_tasks:
                self.append_log(log_widget, f"[{time.ctime().split()[3]}] 선택된 작업 없음")
                return

            button.configure(text="중지", fg_color="#d32f2f", hover_color="#b71c1c")
            self.append_log(log_widget, f"[{time.ctime().split()[3]}] 작업 시작")
            self.running_tabs.add(tab_id)
            for s in selectors: s.configure(state="disabled")
            for g in gear_buttons: g.configure(state="disabled")
            self.set_frame_widgets_state(setting_content, "disabled")

            is_hotkey_task_present = False
            for task in selected_tasks:
                config = load_config()
                
                if task.task_key == "run_nanally_superjump":
                    key = config.get("nanally_superjump_setting", {}).get("key", "caps lock")
                    is_hotkey_task_present = True
                    manager = HotkeyManager(lambda t=task: self.engine.execute_task_by_hotkey(t, log_widget))
                    manager.start(key)
                    self.active_listeners.append(manager)
                    
                elif task.task_key == "run_mouse_auto_click":
                    key = config.get("mouse_auto_click_setting", {}).get("key", "caps lock")
                    is_hotkey_task_present = True
                    manager = HotkeyManager(
                        start_callback=lambda t=task: self.engine.execute_task_by_hotkey(t, log_widget),
                        stop_callback=lambda: self.engine.stop_macro_by_hotkey(log_widget)
                    )
                    manager.start(key)
                    self.active_listeners.append(manager)

            if not is_hotkey_task_present:
                self.engine.start_macro(selected_tasks, log_widget, tab_id, button, selectors, gear_buttons, setting_content)
            
        else:
            button.configure(text="시작", fg_color="#1f538d", hover_color="#14375e")
            self.append_log(log_widget, f"[{time.ctime().split()[3]}] 작업 중지 요청 중...")
            self.running_tabs.discard(tab_id)
            
            for s in selectors: s.configure(state="normal")
            for g in gear_buttons: g.configure(state="normal")
            self.set_frame_widgets_state(setting_content, "normal")
            
            if self.overlay:
                self.overlay.destroy()
                self.overlay = None

            for listener in self.active_listeners:
                if listener is not None:
                    listener.stop()

            self.active_listeners = []
            self.engine.stop_macro()
            
        self.update_tab_lock_state()

    def set_frame_widgets_state(self, frame, state_string):
        for child in frame.winfo_children():
            try: child.configure(state=state_string)
            except Exception: pass

    def update_tab_lock_state(self):
        if len(self.running_tabs) > 0: self.tab_view._segmented_button.configure(state="disabled")
        else: self.tab_view._segmented_button.configure(state="normal")

    def create_middle_section(self, middle_frame):
        middle_frame.grid_columnconfigure(0, weight=1)
        setting_title = ctk.CTkLabel(middle_frame, text="세부 설정", font=("맑은 고딕", 16, "bold"))
        setting_title.pack(padx=10, pady=15)
        setting_content = ctk.CTkFrame(middle_frame, fg_color="transparent")
        setting_content.pack(fill="both", expand=True, padx=10, pady=5)
        no_selection_lbl = ctk.CTkLabel(setting_content, text="⚙ 아이콘을 누르면 세부 설정이 표시됩니다.")
        no_selection_lbl.pack(expand=True)
        return setting_title, setting_content

    def create_right_section(self, right_frame):
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        log_title = ctk.CTkLabel(right_frame, text="작업 로그", font=("맑은 고딕", 14, "bold"))
        log_title.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        log_text = ctk.CTkTextbox(right_frame, activate_scrollbars=True)
        log_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        log_text.insert("0.0", f"[{time.ctime().split()[3]}] NTEA 실행.\n")
        log_text.configure(state="disabled")
        return log_text

    def append_log(self, log_widget, message):
        log_widget.configure(state="normal")
        log_widget.insert("end", message + "\n")
        log_widget.see("end")
        log_widget.configure(state="disabled")

    def setup_fourth_tab(self):
        self.CURRENT_VERSION = version.VERSION

        self.tab4.grid_columnconfigure(0, weight=1)
        self.tab4.grid_rowconfigure(0, weight=1)

        center_frame = ctk.CTkFrame(self.tab4, fg_color="transparent")
        center_frame.grid(row=0, column=0, padx=20, pady=20)

        self.version_lbl = ctk.CTkLabel(center_frame, text=f"현재 버전: {self.CURRENT_VERSION}", font=("맑은 고딕", 16, "bold"))
        self.version_lbl.pack(pady=5)

        self.latest_version_lbl = ctk.CTkLabel(center_frame, text="최신 버전: 확인 필요", font=("맑은 고딕", 14), text_color="#aaaaaa")
        self.latest_version_lbl.pack(pady=5)

        self.update_btn = ctk.CTkButton(center_frame, text="업데이트 확인", width=200, height=40, command=self.check_update)
        self.update_btn.pack(pady=15)

        ctk.CTkFrame(center_frame, height=2, width=250, fg_color="#333333").pack(pady=20)

        self.screenshot_btn = ctk.CTkButton(center_frame, text="📸 스크린샷 테스트", width=200, height=40, 
                                             fg_color="#333333", hover_color="#555555", command=self.run_screenshot_test)
        self.screenshot_btn.pack(pady=10)

        self.status_lbl = ctk.CTkLabel(center_frame, text="", text_color="#ff4444", font=("맑은 고딕", 12))
        self.status_lbl.pack(pady=5)

    def check_update(self):
        import updater
        self.status_lbl.configure(text="서버와 동기화 중...", text_color="#4dabf7")
        self.update_btn.configure(state="disabled")
        
        self.update_idletasks()

        is_update_available, latest_v = updater.check_for_update(self.CURRENT_VERSION)

        self.latest_version_lbl.configure(text=f"최신 버전: {latest_v}", text_color="#2e7d32" if is_update_available else "#ffffff")

        if is_update_available:
            self.status_lbl.configure(text="새로운 업데이트 버전이 존재합니다.", text_color="#4dabf7")
            self.update_btn.configure(state="normal", text="업데이트 하기", fg_color="#2e7d32", hover_color="#1b5e20", command=self.start_update)
        else:
            self.status_lbl.configure(text="현재 최신 버전을 사용 중입니다.", text_color="#2e7d32")
            self.update_btn.configure(state="disabled", text="최신 버전 확인 완료", fg_color="#555555")

    def start_update(self):
        import threading
        import updater
        
        self.update_btn.configure(state="disabled", text="다운로드 중...")
        self.status_lbl.configure(text="GitHub에서 다운로드를 시작합니다", text_color="#ffffff")
        self.update_idletasks()
        
        t = threading.Thread(target=updater.download_and_install, args=(self.update_progress_callback,))
        t.daemon = True 
        t.start()

    def update_progress_callback(self, percent, current_mb, total_mb):
        def update_ui():
            self.status_lbl.configure(
                text=f"다운로드 중... {percent}% ({current_mb:.1f}MB / {total_mb:.1f}MB)", 
                text_color="#4dabf7"
            )
        self.after(0, update_ui)

    def run_screenshot_test(self):
        self.status_lbl.configure(text="")
        
        img_obj, err_msg = core.capture_game_window("NTE")
        
        if err_msg:
            self.status_lbl.configure(text=err_msg, text_color="#ff4444")
        else:
            self.status_lbl.configure(text="캡처 성공! 뷰어를 엽니다.", text_color="#2e7d32")
            self.open_screenshot_viewer(img_obj) 

    def open_screenshot_viewer(self, pil_img): 
        viewer = ctk.CTkToplevel(self)
        viewer.title("스크린샷 뷰어 (클릭하여 좌표 확인)")
        viewer.attributes("-topmost", True)

        img_w, img_h = pil_img.size
        
        viewer.geometry(f"{img_w}x{img_h + 50}")
        viewer.resizable(False, False)

        coord_lbl = ctk.CTkLabel(viewer, text="이미지를 클릭하면 해당 위치의 X, Y 좌표 표시", 
                                 font=("맑은 고딕", 13, "bold"), height=20)
        coord_lbl.pack(side="top", fill="x", pady=0)

        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(img_w, img_h))
        img_label = ctk.CTkLabel(viewer, image=ctk_img, text="")
        img_label.pack(side="top", fill="both", expand=True)

        def on_image_click(event):
            coord_lbl.configure(text=f"클릭한 좌표 X: {event.x} , Y: {event.y}", text_color="#4dabf7")

        img_label.bind("<Button-1>", on_image_click)