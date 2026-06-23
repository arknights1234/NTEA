import threading
from config_manager import load_config
import core
import time

class MacroEngine:
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.macro_thread = None
        self.stop_event = threading.Event()

        self.last_execution_time = 0
        self.cooldown_duration = 1.0

    def execute_task_by_hotkey(self, task, log_widget):
        """[핵심] 단축키 입력 시 엔진 내부 함수를 즉시 호출"""
        self.stop_event.clear()

        current_time = time.time()
        if current_time - self.last_execution_time < self.cooldown_duration:
            return  
        
        self.last_execution_time = current_time

        def log_messenger(msg):
            tmsg = f"[{time.ctime().split()[3]}] " + msg
            self.gui.append_log(log_widget, tmsg)
        if hasattr(task, 'task_key'):
            task_func = getattr(self, task.task_key, None)
            if task_func:
                task_func(self.stop_event, log_messenger)

    def start_macro(self, selected_tasks, log_widget, tab_id, button, selectors, gear_buttons, setting_content):
        self.stop_event.clear()
        self.macro_thread = threading.Thread(
            target=self.macro_pipeline,
            args=(selected_tasks, log_widget, tab_id, button, selectors, gear_buttons, setting_content),
            daemon=True
        )
        self.macro_thread.start()

    def stop_macro(self):
        self.stop_event.set()

    def macro_pipeline(self, selected_tasks, log_widget, tab_id, button, selectors, gear_buttons, setting_content):
        """[서브 스레드] 선택된 task들을 순차적으로 실행"""
        def log_messenger(msg):
            tmsg = f"[{time.ctime().split()[3]}] " + msg
            self.gui.append_log(log_widget, tmsg)

        try:
            for task in selected_tasks:
                if self.stop_event.is_set():
                    log_messenger("작업 중단되었습니다.")
                    return

                log_messenger(f"{task.name} 작업 시작")
                
                if hasattr(task, 'task_key'):
                    task_func = getattr(self, task.task_key, None)
                    
                    if task_func is not None:
                        task_func(self.stop_event, log_messenger)
                    else:
                        log_messenger(f"에러: {task.task_key} 함수를 엔진에서 찾을 수 없습니다.")
                else:
                    log_messenger("에러: 해당 작업 클래스에 task_key가 정의되지 않았습니다.")
                
                if self.stop_event.wait(0.5): return
                
            log_messenger("작업 완료")

        except Exception as e:
            log_messenger(f"매크로 실행 중 오류 발생: {e}")
        finally:
            self.gui.after(0, lambda: self.gui.reset_ui_after_macro(
                tab_id, button, selectors, gear_buttons, setting_content
            ))

    # =====================================================================
    # 작업별 매크로 함수들
    # =====================================================================
    
    def run_cafe_earning(self, stop_event, log_func):
        """별미 카페 수익 받기 매크로 로직"""
        if stop_event.wait(1.0): return
        core.active_window()
        for i in range(3):
            if stop_event.wait(1.0): return
            core.capture_game_window()
            coords, err = core.find_image_in_cropped_zone(template_path="images/별미카페/도시타이쿤.png", 
                                                            x1=1600, y1=400, x2=1730, y2=555, 
                                                            threshold=0.8)
            if coords:
                x, y = coords
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)
                break
            else: core.press_game_key("esc")

        if stop_event.wait(0.5): return
        for i in range(3):
            if stop_event.wait(1.0): return
            core.capture_game_window()
            coords, err = core.find_image_in_cropped_zone(template_path="images/별미카페/별미카페.png", 
                                                          x1=720, y1=625, x2=880, y2=780, 
                                                          threshold=0.8)
            if coords:
                x, y = coords
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)
                break

            if i == 2:
                return
            
        for i in range(3):
            if stop_event.wait(1.0): return
            core.capture_game_window()
            coords, err = core.find_image_in_cropped_zone(template_path="images/별미카페/수익인출.png", 
                                                          x1=290, y1=900, x2=430, y2=980, 
                                                          threshold=0.8)
            if coords:
                x, y = coords
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)
                break

            if i == 2:
                return
        
        for i in range(3):
            if stop_event.wait(1.0): return
            core.capture_game_window()
            coords, err = core.find_image_in_cropped_zone(template_path="images/별미카페/수익확인.png", 
                                                          x1=916, y1=874, x2=1009, y2=956, 
                                                          threshold=0.8)
            if coords:
                x, y = coords
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)
                break

            if i == 2:
                return
            
        for i in range(3):
            if stop_event.wait(1.0): return
            core.capture_game_window()
            coords, err = core.find_image_in_cropped_zone(template_path="images/별미카페/터치해.png", 
                                                          x1=936, y1=936, x2=1020, y2=974, 
                                                          threshold=0.8)
            if coords:
                x, y = coords
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)
                break

            if i == 2:
                return
            
        if stop_event.wait(1.0): return
        core.press_game_key("esc")
        
        if stop_event.wait(1.0): return
        core.press_game_key("esc")
            
        log_func("별미 카페 수익 받기 작업 종료")

    def run_fishing(self, stop_event, log_func):
        """낚시 매크로 로직"""
        config = load_config()
        settings = config.get("fishing_settings", {})
        is_bait = settings.get("bait", False)
        is_sell = settings.get("sell", False)
        
        if stop_event.wait(1.0): return
        core.active_window()
        fc = 0
        while(1):
            if stop_event.wait(1.0): return
            core.active_window()

            if fc != 0 and fc % 10 == 0 and is_sell:
                core.press_game_key("q")
                if stop_event.wait(1.0): return

                core.capture_game_window()
                coords, err = core.find_image_in_cropped_zone(template_path="images/낚시/신선저장고.png", 
                                                            x1=114, y1=381, x2=175, y2=440, 
                                                            threshold=0.8)
                if coords:
                    x, y = coords
                    if stop_event.wait(1.0): return
                    core.click_game_window2(x, y)
                    if stop_event.wait(1.0): return

                core.capture_game_window()
                coords2, err = core.find_image_in_cropped_zone(template_path="images/낚시/일괄판매.png", 
                                                            x1=1012, y1=950, x2=1115, y2=984, 
                                                            threshold=0.8)
                if coords2:
                    x, y = coords2
                    if stop_event.wait(1.0): return
                    core.click_game_window2(x, y)
                    if stop_event.wait(1.0): return
                
                core.capture_game_window()
                coords3, err = core.find_image_in_cropped_zone(template_path="images/낚시/판매확인.png", 
                                                            x1=1140, y1=689, x2=1200, y2=723, 
                                                            threshold=0.8)

                if coords3:
                    x, y = coords3
                    if stop_event.wait(1.0): return
                    core.click_game_window2(x, y)
                    if stop_event.wait(1.0): return

                log_func("어획물 일괄 판매")

                core.capture_game_window()
                coords4, err = core.find_image_in_cropped_zone(template_path="images/낚시/터치해.png", 
                                                            x1=934, y1=937, x2=1020, y2=974, 
                                                            threshold=0.8)
                if coords4:
                    x, y = coords4
                    if stop_event.wait(1.0): return
                    core.click_game_window2(x, y)
                    if stop_event.wait(1.0): return
                    core.press_game_key("esc")
                    if stop_event.wait(1.0): return

            fc = fc + 1

            core.press_game_key("f")
            
            for i in range(5):
                if stop_event.wait(0.2): return
                core.capture_game_window()
                coords3, err = core.find_image_in_cropped_zone(template_path="images/낚시/장착.png", 
                                                            x1=819, y1=522, x2=880, y2=555, 
                                                            threshold=0.8)
                if coords3:
                        if is_bait:
                            if stop_event.wait(1.0): return
                            core.press_game_key("r")
                            if stop_event.wait(1.0): return
                            core.capture_game_window()
                            coords4, err = core.find_image_in_cropped_zone(template_path="images/낚시/만능미끼.png", 
                                                                        x1=46, y1=118, x2=663, y2=609, 
                                                                        threshold=0.9)
                            if coords4:
                                x, y = coords4
                                if stop_event.wait(1.0): return
                                core.click_game_window2(x, y)

                            if stop_event.wait(1.0): return    
                            coords5, err = core.find_image_in_cropped_zone(template_path="images/낚시/플러스.png", 
                                                                        x1=1755, y1=931, x2=1790, y2=970, 
                                                                        threshold=0.8)
                            if coords5:
                                x, y = coords5
                                for i in range(9):
                                    if stop_event.wait(0.1): return
                                    core.click_game_window2(x, y)

                            if stop_event.wait(1.0): return
                            coords6, err = core.find_image_in_cropped_zone(template_path="images/낚시/구매.png", 
                                                                        x1=1576, y1=1004, x2=1649, y2=1060, 
                                                                        threshold=0.8)
                            if coords6:
                                x, y = coords6
                                if stop_event.wait(0.1): return
                                core.click_game_window2(x, y)
                                
                                log_func("미끼 구매")

                                if stop_event.wait(3.0): return
                                core.press_game_key("esc")
                                
                                if stop_event.wait(3.0): return
                                core.press_game_key("esc")

                                if stop_event.wait(1.0): return
                                core.press_game_key("e")

                            if stop_event.wait(1.0): return
                            core.capture_game_window()
                            coords9, err = core.find_image_in_cropped_zone(template_path="images/낚시/교체.png", 
                                                                        x1=1140, y1=688, x2=1200, y2=727, 
                                                                        threshold=0.8)
                            if coords9:
                                x, y = coords9
                                if stop_event.wait(0.1): return
                                core.click_game_window2(x, y)
                            if stop_event.wait(1.0): return
                            core.press_game_key("f")
                            break
                        else: return

            for i in range(30):
                if stop_event.wait(0.2): return
                core.capture_game_window()
                coords10, err = core.find_image_in_cropped_zone(template_path="images/낚시/입질.png", 
                                                            x1=654, y1=243, x2=714, y2=280, 
                                                            threshold=0.8)
                if coords10:
                        if stop_event.wait(1.0): return
                        core.press_game_key("f")
                        break
            c = 0
            while(1):
                if stop_event.wait(0.01): return
                coords1, err = core.find_object_fast(template_path="images/낚시/낚시1.png", 
                                                            x1=608, y1=60, x2=1321, y2=88, 
                                                            threshold=0.5)
                coords2, err = core.find_object_fast(template_path="images/낚시/낚시2.png", 
                                                            x1=608, y1=60, x2=1321, y2=88, 
                                                            threshold=0.7)
                
                if coords1 and coords2:
                    x1, y1 = coords1
                    x2, y2 = coords2
                    if abs(x2-x1) <= 20:
                        pt = 0
                    elif abs(x2-x1) <= 20:
                        pt = abs(x2-x1)/600
                    elif abs(x2-x1) <= 40:
                        pt = abs(x2-x1)/500
                    else: pt = abs(x2-x1)/400
                    if x1 <= x2:
                        core.press_game_key("a",press_time=pt)
                    else:
                        core.press_game_key("d",press_time=pt)
                else:
                    core.capture_game_window()
                    if stop_event.wait(1.0): return
                    coords, err = core.find_image_in_cropped_zone(template_path="images/낚시/터치해.png", 
                                                                x1=940, y1=961, x2=1020, y2=993, 
                                                                threshold=0.8)
                    if coords:
                        x, y = coords
                        if stop_event.wait(1.0): return
                        #core.click_game_window2(x, y)
                        core.press_game_key("esc")
                        log_func(f"낚시 {fc}번 완료")
                        if stop_event.wait(1.0): return
                        break
                    else:
                        c = c + 1
                        if c > 15:
                            break
        
        
        
        log_func("낚시 종료")

    def run_event_racing(self, stop_event, log_func):
        """무법 레이싱 매크로 로직"""
        config = load_config()
        settings = config.get("event_racing_setting", {})
        is_time = settings.get("time", True)

        if stop_event.wait(1.0): return
        core.active_window()
        while(1):
            while(1):
                if stop_event.wait(1.0): return
                core.capture_game_window()
                coords, err = core.find_image_in_cropped_zone(template_path="images/무법레이싱/이벤트.png", 
                                                                x1=1521, y1=437, x2=1583, y2=490, 
                                                                threshold=0.8)
                if coords:
                    x, y = coords
                    if stop_event.wait(1.0): return
                    core.click_game_window2(x, y)
                    break
                else: core.press_game_key("esc")


            if stop_event.wait(3.0): return
            core.capture_game_window()
            coords2, err = core.find_image_in_cropped_zone(template_path="images/무법레이싱/기간제.png", 
                                                            x1=204, y1=880, x2=246, y2=930, 
                                                            threshold=0.8)
            if coords2:
                x, y = coords2
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)


            if stop_event.wait(1.0): return
            core.capture_game_window()
            coords3, err = core.find_image_in_cropped_zone(template_path="images/무법레이싱/무법레이싱.png", 
                                                            x1=103, y1=618, x2=239, y2=652, 
                                                            threshold=0.8)
            if coords3:
                x, y = coords3
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)


            if stop_event.wait(1.0): return
            core.capture_game_window()
            coords4, err = core.find_image_in_cropped_zone(template_path="images/무법레이싱/레이스시작.png", 
                                                            x1=1620, y1=995, x2=1765, y2=1040, 
                                                            threshold=0.8)
            if coords4:
                x, y = coords4
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)


            if stop_event.wait(60.0): return
            core.press_game_key("w",press_time=5)
            if stop_event.wait(60.0): return
            core.press_game_key("w",press_time=5)
            if is_time:
                timer = 120
            while(1):
                if stop_event.wait(10.0): return
                core.capture_game_window()
                coords5, err = core.find_image_in_cropped_zone(template_path="images/무법레이싱/결과.png", 
                                                                x1=909, y1=26, x2=1016, y2=85, 
                                                                threshold=0.8)
                if coords5:
                    if stop_event.wait(3.0): return
                    coords6, err = core.find_image_in_cropped_zone(template_path="images/무법레이싱/나가기.png", 
                                                                x1=1561, y1=995, x2=1710, y2=1040, 
                                                                threshold=0.8)
                    if coords6:
                        x, y = coords6
                        if stop_event.wait(1.0): return
                        core.click_game_window2(x, y)
                        break
                timer = timer + 10
                if timer >= 600:
                    print(600)
                    if stop_event.wait(1.0): return
                    core.press_game_key("esc")
                    if stop_event.wait(2.0): return
                    core.capture_game_window()
                    coords7, err = core.find_image_in_cropped_zone(template_path="images/무법레이싱/종료하기.png", 
                                                                x1=1559, y1=559, x2=1716, y2=607, 
                                                                threshold=0.8)
                    if coords7:
                        x, y = coords7
                        if stop_event.wait(1.0): return
                        core.click_game_window2(x, y)
                        if stop_event.wait(5.0): return

        log_func("무법 레이싱 종료")

    def run_nanally_superjump(self, stop_event, log_func):
        """나나리 슈퍼 점프 매크로 로직"""
        config = load_config()
        delay = float(config.get("nanally_superjump_setting", {}).get("delay", 0.00))

        if stop_event.wait(0.01): return
        core.active_window()
        if stop_event.wait(0.1): return
        core.click_game_active_window()
        if stop_event.wait(0.3): return
        core.click_game_active_window()
        if stop_event.wait(0.3): return
        core.click_game_active_window()
        if stop_event.wait(0.490 + delay): return
        core.press_game_key("space")

        log_func("나나리 슈퍼 점프")