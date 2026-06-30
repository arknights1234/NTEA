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
        def async_wrapper():
            self.stop_event.clear()

            def log_messenger(msg):
                tmsg = f"[{time.ctime().split()[3]}] " + msg
                self.gui.append_log(log_widget, tmsg)

            if hasattr(task, 'task_key'):
                task_func = getattr(self, task.task_key, None)
                if task_func:
                    if task.task_key == "mouse_auto_click":
                        self.macro_thread = threading.Thread(
                            target=task_func, args=(self.stop_event, log_messenger), daemon=True
                        )
                        self.macro_thread.start()
                    else:
                        current_time = time.time()
                        if current_time - self.last_execution_time < self.cooldown_duration:
                            return  
                        self.last_execution_time = current_time
                        task_func(self.stop_event, log_messenger)

        launcher_thread = threading.Thread(target=async_wrapper, daemon=True)
        launcher_thread.start()

    def stop_macro_by_hotkey(self, log_widget):
        self.stop_event.set()

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
        for i in range(3):
            if stop_event.wait(1.0): return
            coords, err = core.find_image_in_cropped_zone(template_path="images/별미카페/도시타이쿤.png", 
                                                            x1=1600, y1=400, x2=1730, y2=555, 
                                                            threshold=0.8)
            if coords:
                x, y = coords
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)
                break
            else: core.press_game_key("esc")
            if i == 2:
                return
        if stop_event.wait(0.5): return
        for i in range(3):
            if stop_event.wait(1.0): return
            coords2, err = core.find_image_in_cropped_zone(template_path="images/별미카페/별미카페.png", 
                                                          x1=720, y1=625, x2=880, y2=780, 
                                                          threshold=0.8)
            if coords2:
                x, y = coords2
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)
                break

            if i == 2:
                return
            
        for i in range(3):
            if stop_event.wait(1.0): return
            coords3, err = core.find_image_in_cropped_zone(template_path="images/별미카페/수익인출.png", 
                                                          x1=290, y1=900, x2=430, y2=980, 
                                                          threshold=0.8)
            if coords3:
                x, y = coords3
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)
                break

            if i == 2:
                return
        
        for i in range(10):
            if stop_event.wait(0.1): return
            coords4, err = core.find_image_in_cropped_zone(template_path="images/별미카페/수익없음.png", 
                                                          x1=739, y1=513, x2=846, y2=564, 
                                                          threshold=0.8)
            
            coords5, err = core.find_image_in_cropped_zone(template_path="images/별미카페/수익정산.png", 
                                                          x1=635, y1=510, x2=788, y2=571, 
                                                          threshold=0.8)
            
            if coords4 or coords5:
                if stop_event.wait(1.0): return
                core.press_game_key("esc")
                
                if stop_event.wait(1.0): return
                core.press_game_key("esc")
                break
        
        for i in range(3):
            if stop_event.wait(1.0): return
            coords6, err = core.find_image_in_cropped_zone(template_path="images/별미카페/수익확인.png", 
                                                          x1=916, y1=874, x2=1009, y2=956, 
                                                          threshold=0.8)
            if coords6:
                x, y = coords6
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)
                break

            if i == 2:
                return
            
        for i in range(3):
            if stop_event.wait(1.0): return
            coords7, err = core.find_image_in_cropped_zone(template_path="images/별미카페/터치해.png", 
                                                          x1=936, y1=936, x2=1020, y2=974, 
                                                          threshold=0.8)
            if coords7:
                x, y = coords7
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
        max_count = int(settings.get("max_count", 100))
        if not max_count or max_count == 0:
            return
        if stop_event.wait(1.0): return
        fc = 0
        while(1):
            if stop_event.wait(1.0): return

            if fc != 0 and fc % 10 == 0 and is_sell:
                core.press_game_key("q")
                for i in range(3):
                    if stop_event.wait(1.0): return
                    coords, err = core.find_image_in_cropped_zone(template_path="images/낚시/신선저장고.png", 
                                                                x1=114, y1=381, x2=175, y2=440, 
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
                    coords2, err = core.find_image_in_cropped_zone(template_path="images/낚시/일괄판매.png", 
                                                                x1=1012, y1=950, x2=1115, y2=984, 
                                                                threshold=0.8)
                    if coords2:
                        x, y = coords2
                        if stop_event.wait(1.0): return
                        core.click_game_window2(x, y)
                        break
                    if i == 2:
                        return
                
                for i in range(3):
                    if stop_event.wait(1.0): return
                    coords3, err = core.find_image_in_cropped_zone(template_path="images/낚시/판매확인.png", 
                                                                x1=1140, y1=689, x2=1200, y2=723, 
                                                                threshold=0.8)
                    if coords3:
                        x, y = coords3
                        if stop_event.wait(1.0): return
                        core.click_game_window2(x, y)
                        break
                    if i == 2:
                        return

                log_func("어획물 일괄 판매")

                for i in range(3):
                    if stop_event.wait(1.0): return
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
                        break
                    if i == 2:
                        return

            fc = fc + 1

            core.press_game_key("f")
            
            for i in range(5):
                if stop_event.wait(0.2): return
                coords3, err = core.find_image_in_cropped_zone(template_path="images/낚시/장착.png", 
                                                            x1=819, y1=522, x2=880, y2=555, 
                                                            threshold=0.8)
                if coords3:
                        if is_bait:
                            if stop_event.wait(1.0): return
                            core.press_game_key("r")
                            for i in range(3):
                                if stop_event.wait(1.0): return
                                coords4, err = core.find_image_in_cropped_zone(template_path="images/낚시/만능미끼.png", 
                                                                            x1=46, y1=118, x2=663, y2=609, 
                                                                            threshold=0.9)
                                if coords4:
                                    x, y = coords4
                                    if stop_event.wait(1.0): return
                                    core.click_game_window2(x, y)
                                    break
                                if i == 2:
                                    return

                            for i in range(3):
                                if stop_event.wait(1.0): return    
                                coords5, err = core.find_image_in_cropped_zone(template_path="images/낚시/플러스.png", 
                                                                            x1=1755, y1=931, x2=1790, y2=970, 
                                                                            threshold=0.8)
                                if coords5:
                                    x, y = coords5
                                    for i in range(9):
                                        if stop_event.wait(0.1): return
                                        core.click_game_window2(x, y)
                                    break
                                if i == 2:
                                    return

                            for i in range(3):
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
                                    break
                                if i == 2:
                                    return

                            for i in range(3):
                                if stop_event.wait(1.0): return
                                coords9, err = core.find_image_in_cropped_zone(template_path="images/낚시/교체.png", 
                                                                            x1=1140, y1=688, x2=1200, y2=727, 
                                                                            threshold=0.8)
                                if coords9:
                                    x, y = coords9
                                    if stop_event.wait(0.1): return
                                    core.click_game_window2(x, y)
                                    break
                                if i == 2:
                                    return
                            if stop_event.wait(1.0): return
                            core.press_game_key("f")
                            break
                        else: return

            for i in range(50):
                if stop_event.wait(0.2): return
                coords10, err = core.find_image_in_cropped_zone(template_path="images/낚시/입질.png", 
                                                            x1=654, y1=243, x2=714, y2=280, 
                                                            threshold=0.8)
                if coords10:
                        if stop_event.wait(1.0): return
                        core.press_game_key("f")
                        break
            c = 0
            while(1):
                if stop_event.wait(0.0001): return
                coords1, err = core.find_object_fast(template_path="images/낚시/낚시1.png", 
                                                            x1=608, y1=60, x2=1321, y2=88, 
                                                            threshold=0.5)
                coords2, err = core.find_object_fast(template_path="images/낚시/낚시2.png", 
                                                            x1=608, y1=60, x2=1321, y2=88, 
                                                            threshold=0.7)
                
                if coords1 and coords2:
                    x1, y1 = coords1
                    x2, y2 = coords2
                    if abs(x2-x1) <= 10:
                        pt = 0
                    elif abs(x2-x1) <= 20:
                        pt = abs(x2-x1)/550
                    elif abs(x2-x1) <= 40:
                        pt = abs(x2-x1)/450
                    else: pt = abs(x2-x1)/350
                    if x1 <= x2:
                        core.press_game_key("a",press_time=pt)
                    else:
                        core.press_game_key("d",press_time=pt)
                else:
                    if stop_event.wait(0.2): return
                    coords, err = core.find_image_in_cropped_zone(template_path="images/낚시/터치해.png", 
                                                                x1=940, y1=961, x2=1020, y2=993, 
                                                                threshold=0.8)
                    if coords:
                        x, y = coords
                        if stop_event.wait(1.0): return
                        core.press_game_key("esc")
                        log_func(f"낚시 {fc}번 완료")
                        if max_count >= fc:
                            return
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
        erc=0
        if stop_event.wait(1.0): return
        while(1):
            while(1):
                if stop_event.wait(1.0): return
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
            coords2, err = core.find_image_in_cropped_zone(template_path="images/무법레이싱/기간제.png", 
                                                            x1=204, y1=880, x2=246, y2=930, 
                                                            threshold=0.8)
            if coords2:
                x, y = coords2
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)


            for i in range(3):
                if stop_event.wait(1.0): return
                coords3, err = core.find_image_in_cropped_zone(template_path="images/무법레이싱/무법레이싱.png", 
                                                                x1=91, y1=211, x2=252, y2=850, 
                                                                threshold=0.8)
                if coords3:
                    x, y = coords3
                    if stop_event.wait(1.0): return
                    core.click_game_window2(x, y)
                    break
                if i == 2:
                    return
                


            for i in range(3):
                if stop_event.wait(1.0): return
                coords4, err = core.find_image_in_cropped_zone(template_path="images/무법레이싱/레이스시작.png", 
                                                                x1=1620, y1=995, x2=1765, y2=1040, 
                                                                threshold=0.8)
                if coords4:
                    x, y = coords4
                    if stop_event.wait(1.0): return
                    core.click_game_window2(x, y)
                    break
                if i == 2:
                    return


            if stop_event.wait(60.0): return
            core.press_game_key("w",press_time=5)
            if stop_event.wait(60.0): return
            core.press_game_key("w",press_time=5)
            if is_time:
                timer = 120
            while(1):
                if stop_event.wait(10.0): return
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
                        erc = erc + 1
                        log_func(f"무법 레이싱 {erc}번 완료")
                        break
                timer = timer + 10
                if timer >= 600:
                    print(600)
                    if stop_event.wait(1.0): return
                    core.press_game_key("esc")
                    if stop_event.wait(2.0): return
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

        if stop_event.wait(0.1): return
        core.click_game_active_window()
        if stop_event.wait(0.3): return
        core.click_game_active_window()
        if stop_event.wait(0.3): return
        core.click_game_active_window()
        if stop_event.wait(0.43 + delay): return
        core.press_game_key("space")

        log_func("나나리 슈퍼 점프")

    def run_mouse_auto_click(self, stop_event, log_func):
        """마우스 광클 매크로 로직"""
        log_func("마우스 광클")
        while not stop_event.is_set():
            if stop_event.wait(0.1): return
            core.click_game_active_window()

    def run_owners_selection(self, stop_event, log_func):
        """점장 특제 매크로 로직"""
        if stop_event.wait(1.0): return
        c = 0
        for i in range(59):
            core.scroll_game_window(x=172, y=556, direction="up", clicks=100)
            for i in range(3):
                if stop_event.wait(0.5): return
                coords1, err = core.find_image_in_cropped_zone(template_path="images/점장특제/신제품시연.png", 
                                                                x1=21, y1=338, x2=322, y2=451, 
                                                                threshold=0.8)
                if coords1:
                    x, y = coords1
                    if stop_event.wait(0.5): return
                    core.click_game_window2(x, y)
                    break
                else: core.scroll_game_window(x=172, y=556, direction="up", clicks=100)
                if i == 2:
                    return
            
            for i in range(3):
                if stop_event.wait(1.0): return
                coords2, err = core.find_image_in_cropped_zone(template_path="images/점장특제/영업개시.png", 
                                                                x1=1655, y1=984, x2=1781, y2=1040, 
                                                                threshold=0.8)
                if coords2:
                    x, y = coords2
                    if stop_event.wait(1.0): return
                    core.click_game_window2(x, y)
                    break
                if i == 2:
                    return
            if stop_event.wait(3.0): return
            for i in range(5):
                if stop_event.wait(1.0): return
                coords3, err = core.find_image_in_cropped_zone(template_path="images/점장특제/1분.png", 
                                                                x1=878, y1=57, x2=967, y2=99, 
                                                                threshold=0.8)
                if coords3:
                    break
                if i == 4:
                    return

            for i in range(15):
                if stop_event.wait(0.2): return
                coords4, err = core.find_image_in_cropped_zone(template_path="images/점장특제/크루아상준비.png", 
                                                                x1=639, y1=909, x2=841, y2=1040, 
                                                                threshold=0.8)
                if coords4:
                    x, y = coords4
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    break
                if i == 15:
                    return
                
            for i in range(15):
                if stop_event.wait(0.2): return
                coords5, err = core.find_image_in_cropped_zone(template_path="images/점장특제/케이크준비.png", 
                                                                x1=878, y1=905, x2=1103, y2=1040, 
                                                                threshold=0.8)
                if coords5:
                    x, y = coords5
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    break
                if i == 14:
                    return
            if stop_event.wait(1.0): return
            for i in range(15):
                if stop_event.wait(0.2): return
                coords6, err = core.find_image_in_cropped_zone(template_path="images/점장특제/식빵준비.png", 
                                                                x1=20, y1=908, x2=248, y2=1040, 
                                                                threshold=0.8)
                if coords6:
                    x, y = coords6
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    break
                if i == 14:
                    return
            
            r = 0
            while(1):
                if stop_event.wait(0.1): return
                coords7, err = core.find_image_in_cropped_zone(template_path="images/점장특제/에그토마토크루아상.png", 
                                                                x1=581, y1=124, x2=1414, y2=424, 
                                                                threshold=0.8)
                coords72, err = core.find_image_in_cropped_zone(template_path="images/점장특제/에그토마토크루아상2.png", 
                                                                x1=581, y1=124, x2=1414, y2=424, 
                                                                threshold=0.8)
                if coords7 or coords72:
                    coords8, err = core.find_image_in_cropped_zone(template_path="images/점장특제/크루아상.png", 
                                                                x1=508, y1=736, x2=782, y2=869, 
                                                                threshold=0.8)
                    if coords8:
                        x, y = coords8
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                    if stop_event.wait(0.2): return
                    coords9, err = core.find_image_in_cropped_zone(template_path="images/점장특제/에그.png", 
                                                                x1=361, y1=639, x2=451, y2=717, 
                                                                threshold=0.8)
                    if coords9:
                        x, y = coords9
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                        r = r + 1
                    if stop_event.wait(1.0): return

                coords10, err = core.find_image_in_cropped_zone(template_path="images/점장특제/애플파이.png", 
                                                                x1=581, y1=124, x2=1414, y2=424,
                                                                threshold=0.8)
                if coords10:
                    coords11, err = core.find_image_in_cropped_zone(template_path="images/점장특제/케이크.png", 
                                                                x1=1142, y1=962, x2=1381, y2=1080, 
                                                                threshold=0.8)
                    if coords11:
                        x, y = coords11
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                    if stop_event.wait(0.2): return
                    coords12, err = core.find_image_in_cropped_zone(template_path="images/점장특제/애플.png", 
                                                                x1=967, y1=594, x2=1119, y2=711, 
                                                                threshold=0.8)
                    if coords12:
                        x, y = coords12
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                        r = r + 1
                    if stop_event.wait(1.0): return

                coords13, err = core.find_image_in_cropped_zone(template_path="images/점장특제/참치샌드위치.png", 
                                                                x1=581, y1=124, x2=1414, y2=424,
                                                                threshold=0.8)
                if coords13:
                    coords14, err = core.find_image_in_cropped_zone(template_path="images/점장특제/식빵.png", 
                                                                x1=3, y1=733, x2=246, y2=873, 
                                                                threshold=0.8)
                    if coords14:
                        x, y = coords14
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                        r = r + 1
                    if stop_event.wait(0.2): return
                    coords15, err = core.find_image_in_cropped_zone(template_path="images/점장특제/참치.png", 
                                                                x1=194, y1=643, x2=277, y2=720, 
                                                                threshold=0.8)
                    if coords15:
                        x, y = coords15
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                    if stop_event.wait(1.0): return

                coords16, err = core.find_image_in_cropped_zone(template_path="images/점장특제/특제토마토주스.png", 
                                                                x1=581, y1=124, x2=1414, y2=424,
                                                                threshold=0.8)
                coords162, err = core.find_image_in_cropped_zone(template_path="images/점장특제/특제토마토주스2.png", 
                                                                x1=581, y1=124, x2=1414, y2=424,
                                                                threshold=0.8)
                if coords16 or coords162:
                    coords17, err = core.find_image_in_cropped_zone(template_path="images/점장특제/컵.png", 
                                                                x1=1688, y1=698, x2=1893, y2=888, 
                                                                threshold=0.8)
                    if coords17:
                        x, y = coords17
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                    if stop_event.wait(0.2): return
                    coords18, err = core.find_image_in_cropped_zone(template_path="images/점장특제/토마토주스.png", 
                                                                x1=1634, y1=571, x2=1764, y2=697, 
                                                                threshold=0.8)
                    if coords18:
                        x, y = coords18
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                        r = r + 2
                    if stop_event.wait(1.0): return
                
                if r >= 3:
                    core.press_game_key("esc")
                    break

            for i in range(3):
                if stop_event.wait(1.0): return
                coords19, err = core.find_image_in_cropped_zone(template_path="images/점장특제/수령.png", 
                                                                x1=1127, y1=818, x2=1191, y2=852, 
                                                                threshold=0.8)
                if coords19:
                    x, y = coords19
                    if stop_event.wait(1.0): return
                    core.click_game_window2(x, y)
                    c = c + 1
                    log_func(f"점장 특제 {c}번 완료")
                    break
                if i == 2:
                    return
            for i in range(10):
                if stop_event.wait(0.1): return
                coords20, err = core.find_image_in_cropped_zone(template_path="images/점장특제/도시활력제.png", 
                                                                x1=581, y1=519, x2=744, y2=559, 
                                                                threshold=0.8)
                if coords20:
                    return
    
    def run_bagel(self, stop_event, log_func):
        """베이글 매크로 로직"""
        config = load_config()
        comment = config.get("bagel_settings", {}).get("comment_text", "great")
        if stop_event.wait(1.0): return
        for i in range(3):
            if stop_event.wait(1.0): return
            coords, err = core.find_image_in_cropped_zone(template_path="images/베이글/베이글.png", 
                                                            x1=1630, y1=575, x2=1704, y2=652, 
                                                            threshold=0.8)
            if coords:
                x, y = coords
                if stop_event.wait(1.0): return
                core.click_game_window2(x, y)
                break
            else: core.press_game_key("esc")
            if i == 2:
                return
            
        if stop_event.wait(3.0): return
        core.active_window()
        core.scroll_game_window(x=960,y=540,direction="down",clicks=16)
        
        like = 0

        #게시물1
        #==================================

        if stop_event.wait(1.0): return
        core.click_game_window2(520, 459)

        for i in range(5):
            if stop_event.wait(1.0): return
            coords2, err = core.find_image_in_cropped_zone(template_path="images/베이글/좋아요.png", 
                                                            x1=896, y1=892, x2=1060, y2=936, 
                                                            threshold=0.8)
            if coords2:
                x, y = coords2
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                like = like + 1
                break
        
        for i in range(5):
            if stop_event.wait(1.0): return
            coords3, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글.png", 
                                                            x1=1371, y1=955, x2=1491, y2=1010, 
                                                            threshold=0.8)
            if coords3:
                x, y = coords3
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
                    
        if stop_event.wait(1.0): return
        core.type_game_string(comment)

        for i in range(5):
            if stop_event.wait(1.0): return
            coords4, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글확인.png", 
                                                            x1=1717, y1=949, x2=1790, y2=986, 
                                                            threshold=0.8)
            if coords4:
                x, y = coords4
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
            
        for i in range(10):
            if stop_event.wait(0.2): return
            coords5, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글딜레이.png", 
                                                            x1=826, y1=514, x2=905, y2=564, 
                                                            threshold=0.8)
            if coords5:
                x, y = coords5
                if stop_event.wait(5.0): return
                for i in range(5):
                    if stop_event.wait(1.0): return
                    coords6, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글.png", 
                                                                    x1=1371, y1=955, x2=1491, y2=1010, 
                                                                    threshold=0.8)
                    if coords6:
                        x, y = coords6
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                        break
                    if i == 4:
                        return
                for i in range(5):
                    if stop_event.wait(1.0): return
                    coords7, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글확인.png", 
                                                                    x1=1717, y1=949, x2=1790, y2=986, 
                                                                    threshold=0.8)
                    if coords7:
                        x, y = coords7
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                        break
                    if i == 4:
                        return
                    
                break
                
        for i in range(5):
            if stop_event.wait(1.0): return
            coords8, err = core.find_image_in_cropped_zone(template_path="images/베이글/엑스.png", 
                                                            x1=1813, y1=39, x2=1852, y2=79, 
                                                            threshold=0.8)
            if coords8:
                x, y = coords8
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
        
        #게시물2
        #==================================

        if stop_event.wait(1.0): return
        core.click_game_window2(912, 447)

        for i in range(5):
            if stop_event.wait(1.0): return
            coords9, err = core.find_image_in_cropped_zone(template_path="images/베이글/좋아요.png", 
                                                            x1=896, y1=892, x2=1060, y2=936, 
                                                            threshold=0.8)
            if coords9:
                x, y = coords9
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                like = like + 1
                break
        
        for i in range(5):
            if stop_event.wait(1.0): return
            coords10, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글.png", 
                                                            x1=1371, y1=955, x2=1491, y2=1010, 
                                                            threshold=0.8)
            if coords10:
                x, y = coords10
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
                    
        if stop_event.wait(1.0): return
        core.type_game_string(comment)

        for i in range(5):
            if stop_event.wait(1.0): return
            coords11, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글확인.png", 
                                                            x1=1717, y1=949, x2=1790, y2=986, 
                                                            threshold=0.8)
            if coords11:
                x, y = coords11
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
            
        for i in range(10):
            if stop_event.wait(0.2): return
            coords12, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글딜레이.png", 
                                                            x1=826, y1=514, x2=905, y2=564, 
                                                            threshold=0.8)
            if coords12:
                x, y = coords12
                if stop_event.wait(5.0): return
                for i in range(5):
                    if stop_event.wait(1.0): return
                    coords13, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글.png", 
                                                                    x1=1371, y1=955, x2=1491, y2=1010, 
                                                                    threshold=0.8)
                    if coords13:
                        x, y = coords13
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                        break
                    if i == 4:
                        return
                for i in range(5):
                    if stop_event.wait(1.0): return
                    coords14, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글확인.png", 
                                                                    x1=1717, y1=949, x2=1790, y2=986, 
                                                                    threshold=0.8)
                    if coords14:
                        x, y = coords14
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                        break
                    if i == 4:
                        return
                    
                break
                
        for i in range(5):
            if stop_event.wait(1.0): return
            coords15, err = core.find_image_in_cropped_zone(template_path="images/베이글/엑스.png", 
                                                            x1=1813, y1=39, x2=1852, y2=79, 
                                                            threshold=0.8)
            if coords15:
                x, y = coords15
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
            

        #게시물3
        #==================================

        if stop_event.wait(1.0): return
        core.click_game_window2(1318, 543)

        for i in range(5):
            if stop_event.wait(1.0): return
            coords16, err = core.find_image_in_cropped_zone(template_path="images/베이글/좋아요.png", 
                                                            x1=896, y1=892, x2=1060, y2=936, 
                                                            threshold=0.8)
            if coords16:
                x, y = coords16
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                like = like + 1
                break
        
        for i in range(5):
            if stop_event.wait(1.0): return
            coords17, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글.png", 
                                                            x1=1371, y1=955, x2=1491, y2=1010, 
                                                            threshold=0.8)
            if coords17:
                x, y = coords17
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
                    
        if stop_event.wait(1.0): return
        core.type_game_string(comment)

        for i in range(5):
            if stop_event.wait(1.0): return
            coords18, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글확인.png", 
                                                            x1=1717, y1=949, x2=1790, y2=986, 
                                                            threshold=0.8)
            if coords18:
                x, y = coords18
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
            
        for i in range(10):
            if stop_event.wait(0.2): return
            coords19, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글딜레이.png", 
                                                            x1=826, y1=514, x2=905, y2=564, 
                                                            threshold=0.8)
            if coords19:
                x, y = coords19
                if stop_event.wait(5.0): return
                for i in range(5):
                    if stop_event.wait(1.0): return
                    coords20, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글.png", 
                                                                    x1=1371, y1=955, x2=1491, y2=1010, 
                                                                    threshold=0.8)
                    if coords20:
                        x, y = coords20
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                        break
                    if i == 4:
                        return
                for i in range(5):
                    if stop_event.wait(1.0): return
                    coords21, err = core.find_image_in_cropped_zone(template_path="images/베이글/댓글확인.png", 
                                                                    x1=1717, y1=949, x2=1790, y2=986, 
                                                                    threshold=0.8)
                    if coords21:
                        x, y = coords21
                        if stop_event.wait(0.1): return
                        core.click_game_window2(x, y)
                        break
                    if i == 4:
                        return
                    
                break
                
        for i in range(5):
            if stop_event.wait(1.0): return
            coords22, err = core.find_image_in_cropped_zone(template_path="images/베이글/엑스.png", 
                                                            x1=1813, y1=39, x2=1852, y2=79, 
                                                            threshold=0.8)
            if coords22:
                x, y = coords22
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
            
        #게시물4
        #==================================

        if stop_event.wait(1.0): return
        core.click_game_window2(1720, 543)

        if like < 3:
            for i in range(5):
                if stop_event.wait(1.0): return
                coords23, err = core.find_image_in_cropped_zone(template_path="images/베이글/좋아요.png", 
                                                                x1=896, y1=892, x2=1060, y2=936, 
                                                                threshold=0.8)
                if coords23:
                    x, y = coords23
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    like = like + 1
                    break
        
        for i in range(5):
            if stop_event.wait(1.0): return
            coords24, err = core.find_image_in_cropped_zone(template_path="images/베이글/엑스.png", 
                                                            x1=1813, y1=39, x2=1852, y2=79, 
                                                            threshold=0.8)
            if coords24:
                x, y = coords24
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
            

        #게시물5
        #==================================

        if stop_event.wait(1.0): return
        core.click_game_window2(526,964)

        if like < 3:
            for i in range(5):
                if stop_event.wait(1.0): return
                coords25, err = core.find_image_in_cropped_zone(template_path="images/베이글/좋아요.png", 
                                                                x1=896, y1=892, x2=1060, y2=936, 
                                                                threshold=0.8)
                if coords25:
                    x, y = coords25
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    like = like + 1
                    break
        
        for i in range(5):
            if stop_event.wait(1.0): return
            coords26, err = core.find_image_in_cropped_zone(template_path="images/베이글/엑스.png", 
                                                            x1=1813, y1=39, x2=1852, y2=79, 
                                                            threshold=0.8)
            if coords26:
                x, y = coords26
                if stop_event.wait(0.1): return
                core.click_game_window2(x, y)
                break
            if i == 4:
                return
            
        #게시물6
        #==================================

        if like < 3:
            if stop_event.wait(1.0): return
            core.click_game_window2(912,964)

        
            for i in range(5):
                if stop_event.wait(1.0): return
                coords27, err = core.find_image_in_cropped_zone(template_path="images/베이글/좋아요.png", 
                                                                x1=896, y1=892, x2=1060, y2=936, 
                                                                threshold=0.8)
                if coords27:
                    x, y = coords27
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    like = like + 1
                    break
        
            for i in range(5):
                if stop_event.wait(1.0): return
                coords28, err = core.find_image_in_cropped_zone(template_path="images/베이글/엑스.png", 
                                                                x1=1813, y1=39, x2=1852, y2=79, 
                                                                threshold=0.8)
                if coords28:
                    x, y = coords28
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    break
                if i == 4:
                    return
                
        #게시물7
        #==================================

        if like < 3:
            if stop_event.wait(1.0): return
            core.click_game_window2(1324,990)

        
            for i in range(5):
                if stop_event.wait(1.0): return
                coords28, err = core.find_image_in_cropped_zone(template_path="images/베이글/좋아요.png", 
                                                                x1=896, y1=892, x2=1060, y2=936, 
                                                                threshold=0.8)
                if coords28:
                    x, y = coords28
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    like = like + 1
                    break
        
            for i in range(5):
                if stop_event.wait(1.0): return
                coords29, err = core.find_image_in_cropped_zone(template_path="images/베이글/엑스.png", 
                                                                x1=1813, y1=39, x2=1852, y2=79, 
                                                                threshold=0.8)
                if coords29:
                    x, y = coords29
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    break
                if i == 4:
                    return
                
        #게시물8
        #==================================

        if like < 3:
            if stop_event.wait(1.0): return
            core.click_game_window2(1728,988)

        
            for i in range(5):
                if stop_event.wait(1.0): return
                coords29, err = core.find_image_in_cropped_zone(template_path="images/베이글/좋아요.png", 
                                                                x1=896, y1=892, x2=1060, y2=936, 
                                                                threshold=0.8)
                if coords29:
                    x, y = coords29
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    like = like + 1
                    break
        
            for i in range(5):
                if stop_event.wait(1.0): return
                coords30, err = core.find_image_in_cropped_zone(template_path="images/베이글/엑스.png", 
                                                                x1=1813, y1=39, x2=1852, y2=79, 
                                                                threshold=0.8)
                if coords30:
                    x, y = coords30
                    if stop_event.wait(0.1): return
                    core.click_game_window2(x, y)
                    break
                if i == 4:
                    return
            
        if stop_event.wait(1.0): return
        core.press_game_key("esc")
        return