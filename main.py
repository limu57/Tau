"""
Tau 1.0 — Minecraft 自动钓鱼脚本 
by limu57 with deepseek
"""
import tkinter as tk
from tkinter import ttk
import threading, queue, time, random, math, json, os, sys, re, ctypes
import numpy as np
import pyautogui
from pynput import mouse
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key, Listener as KeyboardListener
from PIL import ImageGrab, Image, ImageTk
import io, base64, winsound, pyperclip, win32gui
from collections import deque

# ================= 默认配置 =================
DEFAULT_CONFIG = {
    'max_lines':8,'polling_rate':250,'px_color':'#fcfcfc','px_height':200,'px_width':325,'crosshair_x_ratio':0.5,'crosshair_y_ratio':0.5,'detect_center_offset_x_ratio':0.0,'detect_center_offset_y_ratio':-0.1111,'color_tolerance':20,'detection_tolerance':5,'detection_timeout':30.0,'no_fish_timeout':60.0,'confirmation_time':0.5,'reel_wait_min':4.0,'reel_wait_max':6.0,'cast_delay_min':0.1,'cast_delay_max':0.4,'dpi':1321,'sensitivity':95,'arrival_dist':1.5,'angle_tolerance':1.0,'obstacle_time':3,'polling_jitter':50,'mouse_jitter':2,'auto_throw_enabled':True,'fish_depleted_alert_enabled':True,'auto_relocate_enabled':True,'multiple_cast':True,'water_jump_threshold':63.0,'fn_lock_enabled':False,'per_check':1.0,'player_speed':5.625,'i_loop_max_iter':10,'i_loop_adaptive_max_walk':2.0,'i_loop_adaptive_ratio':0.6,'verbose_navigation':False,'log_level':'INFO','deg_per_pixel_override':None,'window_title_keyword':'布吉岛','min_distance_to_cast':5.0,'detection_poll_interval':0.2,'max_coord_retries':5,'t_loop_restart_interval':10.0,'t_loop_loose_dist':30.0,'t_loop_angle_tolerance':5.0,'walk_time_factor':0.9,'water_float_timeout':2.0,'max_water_fails':3,'pitch_down_after_arrival':0.0,'stuck_threshold':0.15,'manual_cast_timeout':31.0,'auto_cast_wait':2.0,'initial_catch_cast_delay':5.0,'copy_coord_delay':0.5,'coord_retry_delay_1':0.3,'coord_retry_delay_2':0.2,'mouse_move_step':20,'mouse_move_delay':0.005,'mouse_move_multiplier':1.0,'eye_height':1.62,'deg_per_pixel_factor':0.15,'max_rotation_attempts':5,'rotation_retry_delay':0.05,'t_to_i_distance':15.0,'water_turn_tolerance':5.0,'stuck_trigger_count':3,'i_loop_min_walk_time':0.05,'i_loop_max_walk_time':1.0,'i_loop_post_walk_delay':0.2,'align_water_max_iter':6,'align_water_delay':0.3,'shore_climb_time':0.3,'float_pitch_angle':45.0,'float_check_interval':0.3,'evasion_back_time':1.0,'evasion_short_max':3.0,'evasion_long_min':3.0,'evasion_long_max':5.0,'evasion_short_probability':0.8,'evasion_cycle_interval':3,'forbidden_max_depth':5,'forbidden_max_steps':50,'forbidden_step_duration':0.2,'forbidden_step_pause':0.1,'forbidden_approach_dist':5.0,'forbidden_exit_extra_time':0.3,'relocate_coord_retries':6,'exclude_spot_distance':5.0,'relocate_finish_delay':0.5,'multi_cast_delay_1':0.5,'multi_cast_delay_2':0.3,'via_spot_threshold':0.5,'click_pre_delay':0.02,'click_post_delay':0.05,'ray_align_min_step':2.0,'ui_window_width':360,'ui_window_height':900,'ui_minsize_width':360,'ui_minsize_height':700,'current_map':'map1','input_mode':'window','key_stop_navigation':'m','key_toggle_fishing':'n'
}

# ================= 默认地图数据 =================
DEFAULT_MAP_DATA = {
    "maps": {
        "map1": {
            "name": "图1",
            "water_jump_threshold": 63.0,
            "forbidden_zones":[
                {"x_min":105,"x_max":126,"z_min":219,"z_max":241}
            ],
            "via_stations":[
                {"id":"A1","x":148.0,"y":65.0,"z":373.0,"yaw":0.0,"pitch":0.0,
                 "water_x":148.0,"water_y":65.0,"water_z":373.0},
                {"id":"A2","x":129.0,"y":68.0,"z":361.0,"yaw":0.0,"pitch":0.0,
                 "water_x":129.0,"water_y":68.0,"water_z":361.0}
            ],
            "special_spots":[
                [133.63,65.00,377.07],[138.95,65.00,379.48],[147.39,65.00,382.04]
            ],
            "via_rule":{
                "mode":"conditional",
                "condition":{"x_max":124,"z_min":350},
                "path_when_true":["A2","A1"],
                "path_when_false":["A1"]
            },
            "fishing_spots": [
                {"x":84.18,"y":63.00,"z":223.51,"yaw":-270.24,"pitch":20.28},
                {"x":89.35,"y":63.00,"z":169.46,"yaw":-260.24,"pitch":16.25},
                {"x":104.31,"y":63.00,"z":159.00,"yaw":-209.97,"pitch":12.36},
                {"x":111.24,"y":63.00,"z":297.21,"yaw":-2.76,"pitch":22.08},
                {"x":116.60,"y":64.00,"z":363.64,"yaw":91.26,"pitch":24.03},
                {"x":122.68,"y":63.00,"z":272.16,"yaw":-87.48,"pitch":15.42},
                {"x":125.44,"y":65.00,"z":317.48,"yaw":135.70,"pitch":33.61},
                {"x":127.35,"y":63.00,"z":291.30,"yaw":-127.34,"pitch":11.53},
                {"x":133.63,"y":65.00,"z":377.07,"yaw":30.01,"pitch":32.64},
                {"x":133.94,"y":63.00,"z":178.32,"yaw":-88.03,"pitch":17.22},
                {"x":133.94,"y":64.00,"z":245.91,"yaw":-16.24,"pitch":26.80},
                {"x":138.95,"y":65.00,"z":379.48,"yaw":3.76,"pitch":29.72},
                {"x":144.71,"y":63.00,"z":301.16,"yaw":-152.89,"pitch":14.44},
                {"x":147.39,"y":65.00,"z":382.04,"yaw":-0.40,"pitch":32.91},
                {"x":154.43,"y":63.00,"z":253.87,"yaw":56.40,"pitch":20.83},
                {"x":158.31,"y":63.00,"z":170.10,"yaw":-214.14,"pitch":12.36},
                {"x":159.74,"y":63.00,"z":305.48,"yaw":-173.72,"pitch":12.08},
                {"x":161.79,"y":63.00,"z":270.36,"yaw":18.76,"pitch":9.58},
                {"x":175.66,"y":63.00,"z":312.11,"yaw":-128.31,"pitch":11.80},
                {"x":191.81,"y":63.00,"z":160.24,"yaw":-155.53,"pitch":23.89},
                {"x":193.40,"y":63.00,"z":321.02,"yaw":-144.84,"pitch":17.92},
                {"x":208.61,"y":64.00,"z":305.34,"yaw":36.40,"pitch":31.66},
                {"x":216.92,"y":63.00,"z":316.11,"yaw":22.51,"pitch":28.05},
                {"x":233.58,"y":63.00,"z":333.92,"yaw":178.61,"pitch":22.64},
                {"x":234.75,"y":63.00,"z":361.42,"yaw":-42.90,"pitch":17.92},
                {"x":243.29,"y":63.00,"z":351.00,"yaw":-130.67,"pitch":12.78},
                {"x":265.60,"y":63.00,"z":300.63,"yaw":-44.57,"pitch":24.17},
                {"x":278.04,"y":63.00,"z":263.34,"yaw":-70.81,"pitch":-13.33},
                {"x":279.42,"y":63.00,"z":227.52,"yaw":-63.59,"pitch":20.14}
            ],
            "water_candidates": [
                {"water_x":147.48,"water_y":63.0,"water_z":388.28},
                {"water_x":138.70,"water_y":63.0,"water_z":386.64},
                {"water_x":130.66,"water_y":63.0,"water_z":382.34},
                {"water_x":110.61,"water_y":63.0,"water_z":363.42},
                {"water_x":83.58,"water_y":63.0,"water_z":168.50},
                {"water_x":121.70,"water_y":63.0,"water_z":313.50},
                {"water_x":111.69,"water_y":63.0,"water_z":301.56},
                {"water_x":79.63,"water_y":63.0,"water_z":223.55},
                {"water_x":100.40,"water_y":63.0,"water_z":152.50},
                {"water_x":139.53,"water_y":63.0,"water_z":178.66},
                {"water_x":154.72,"water_y":63.0,"water_z":164.56},
                {"water_x":193.31,"water_y":63.0,"water_z":156.61},
                {"water_x":283.12,"water_y":63.0,"water_z":229.67},
                {"water_x":290.24,"water_y":63.0,"water_z":267.37},
                {"water_x":286.30,"water_y":63.0,"water_z":285.60},
                {"water_x":268.52,"water_y":63.0,"water_z":303.47},
                {"water_x":248.50,"water_y":63.0,"water_z":346.50},
                {"water_x":238.56,"water_y":63.0,"water_z":365.52},
                {"water_x":233.40,"water_y":63.0,"water_z":329.35},
                {"water_x":215.61,"water_y":63.0,"water_z":319.58},
                {"water_x":196.49,"water_y":63.0,"water_z":316.40},
                {"water_x":181.40,"water_y":63.0,"water_z":307.53},
                {"water_x":160.35,"water_y":63.0,"water_z":298.44},
                {"water_x":147.58,"water_y":63.0,"water_z":295.69},
                {"water_x":133.52,"water_y":63.0,"water_z":286.31},
                {"water_x":128.45,"water_y":63.0,"water_z":272.53},
                {"water_x":135.75,"water_y":63.0,"water_z":251.31},
                {"water_x":150.33,"water_y":63.0,"water_z":256.47},
                {"water_x":159.36,"water_y":63.0,"water_z":277.58},
                {"water_x":205.70,"water_y":63.0,"water_z":309.36},
                {"water_x":215.63,"water_y":63.0,"water_z":319.30}
            ]
        },
        "map2": {
            "name": "图2",
            "water_jump_threshold": 120.0,
            "forbidden_zones":[],
            "via_stations":[
                {"id":"A1","x":282.0,"y":122.0,"z":283.0,"yaw":0.0,"pitch":0.0,
                 "water_x":282.0,"water_y":122.0,"water_z":283.0},
                {"id":"A2","x":260.0,"y":122.0,"z":261.0,"yaw":0.0,"pitch":0.0,
                 "water_x":260.0,"water_y":122.0,"water_z":261.0}
            ],
            "special_spots":[
                [275.38,122.00,289.07],[281.37,122.00,301.03],
                [247.76,122.00,274.14],[258.40,122.00,282.92]
            ],
            "via_rule":{
                "mode":"decision",
                "decision_spots":[
                    {"id":"am3","station":"A1","x":275.38,"y":122.0,"z":289.07},
                    {"id":"am4","station":"A2","x":281.37,"y":122.0,"z":301.03}
                ],
                "fallback_path":[]
            },
            "fishing_spots":[
                {"x":181.32,"y":122.00,"z":166.24,"yaw":109.17,"pitch":24.02},
                {"x":206.92,"y":120.00,"z":122.97,"yaw":118.89,"pitch":19.85},
                {"x":213.92,"y":122.00,"z":173.91,"yaw":23.90,"pitch":31.24},
                {"x":228.95,"y":120.00,"z":252.50,"yaw":-325.10,"pitch":15.83},
                {"x":234.08,"y":120.00,"z":188.89,"yaw":-60.12,"pitch":12.77},
                {"x":235.22,"y":120.00,"z":217.69,"yaw":-237.89,"pitch":12.08},
                {"x":247.50,"y":120.00,"z":167.08,"yaw":317.90,"pitch":15.96},
                {"x":247.76,"y":122.00,"z":274.14,"yaw":-310.80,"pitch":24.17},
                {"x":247.79,"y":120.00,"z":141.19,"yaw":238.60,"pitch":9.71},
                {"x":258.40,"y":122.00,"z":282.92,"yaw":-258.45,"pitch":27.64},
                {"x":269.90,"y":120.00,"z":198.11,"yaw":495.81,"pitch":10.69},
                {"x":275.38,"y":122.00,"z":289.07,"yaw":-255.81,"pitch":29.17},
                {"x":281.37,"y":122.00,"z":301.03,"yaw":-352.46,"pitch":31.95},
                {"x":291.27,"y":120.00,"z":185.90,"yaw":477.06,"pitch":10.41},
                {"x":298.85,"y":120.00,"z":177.21,"yaw":514.42,"pitch":11.38},
                {"x":317.39,"y":120.00,"z":325.74,"yaw":-337.33,"pitch":13.05},
                {"x":331.84,"y":120.00,"z":145.96,"yaw":512.75,"pitch":11.94},
                {"x":333.94,"y":120.00,"z":328.94,"yaw":-375.52,"pitch":16.52},
                {"x":358.30,"y":120.00,"z":153.13,"yaw":249.99,"pitch":10.69},
                {"x":364.15,"y":120.00,"z":172.41,"yaw":289.43,"pitch":12.35},
                {"x":365.84,"y":120.50,"z":190.28,"yaw":-15.13,"pitch":19.16},
                {"x":376.00,"y":120.00,"z":234.82,"yaw":-75.96,"pitch":13.19}
            ],
            "water_candidates":[
                {"water_x":173.44,"water_y":120.00,"water_z":163.51},
                {"water_x":202.75,"water_y":120.00,"water_z":120.31},
                {"water_x":211.56,"water_y":120.00,"water_z":179.70},
                {"water_x":225.89,"water_y":120.00,"water_z":257.31},
                {"water_x":228.49,"water_y":120.00,"water_z":213.38},
                {"water_x":240.43,"water_y":120.00,"water_z":192.46},
                {"water_x":241.65,"water_y":120.00,"water_z":279.61},
                {"water_x":251.56,"water_y":120.00,"water_z":171.63},
                {"water_x":251.62,"water_y":120.00,"water_z":281.35},
                {"water_x":255.46,"water_y":120.00,"water_z":136.46},
                {"water_x":264.68,"water_y":120.00,"water_z":192.36},
                {"water_x":268.70,"water_y":120.00,"water_z":287.38},
                {"water_x":280.43,"water_y":120.00,"water_z":307.37},
                {"water_x":284.26,"water_y":120.00,"water_z":182.63},
                {"water_x":295.55,"water_y":120.00,"water_z":170.18},
                {"water_x":314.70,"water_y":120.00,"water_z":332.30},
                {"water_x":328.70,"water_y":120.00,"water_z":139.53},
                {"water_x":335.45,"water_y":120.00,"water_z":334.44},
                {"water_x":365.46,"water_y":120.00,"water_z":150.76},
                {"water_x":367.60,"water_y":120.00,"water_z":196.40},
                {"water_x":370.30,"water_y":120.00,"water_z":174.39},
                {"water_x":382.71,"water_y":120.00,"water_z":236.70}
            ]
        }
    }
}

# ================= 路径与配置加载 =================
def _init_paths():
    global SCRIPT_DIR, CONFIG_PATH, MAP_DATA_PATH
    if getattr(sys, 'frozen', False):
        SCRIPT_DIR = os.path.dirname(sys.executable)
    else:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(SCRIPT_DIR, 'fisher_config.json')
    MAP_DATA_PATH = os.path.join(SCRIPT_DIR, 'map_data.json')

_init_paths()

# ================= DPI 感知（保证窗口坐标与截屏坐标系一致，避免检测区域错位） =================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

def _validate_config(config):
    """校验关键配置项，非法时回退默认值。"""
    px = config.get('px_color')
    if not (isinstance(px, str) and re.fullmatch(r'#[0-9a-fA-F]{6}', px or '')):
        print(f"[警告] px_color 无效: {px!r}，已回退默认 {DEFAULT_CONFIG['px_color']}")
        config['px_color'] = DEFAULT_CONFIG['px_color']
    for key in ('dpi', 'sensitivity', 'polling_rate'):
        try: config[key] = int(config[key])
        except (TypeError, ValueError): config[key] = DEFAULT_CONFIG[key]
    for key in ('no_fish_timeout', 'detection_timeout', 'reel_wait_min', 'reel_wait_max'):
        try: config[key] = float(config[key])
        except (TypeError, ValueError): config[key] = DEFAULT_CONFIG[key]
    return config

def load_config():
    config = DEFAULT_CONFIG.copy()
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            for key in DEFAULT_CONFIG:
                if key not in loaded:
                    loaded[key] = DEFAULT_CONFIG[key]
            config.update(loaded)
        else:
            save_config_internal(config, CONFIG_PATH)
    except Exception as e:
        print(f"[警告] 配置加载失败: {e}，使用默认配置")
    return _validate_config(config)

def save_config(config_dict):
    return save_config_internal(config_dict, CONFIG_PATH)

def save_config_internal(config_dict, path):
    try:
        with open(path + '.tmp', 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
        os.replace(path + '.tmp', path)
        return True
    except Exception as e:
        print(f"[错误] 保存配置失败: {e}")
        return False

def load_map_data(path, current_map):
    if not os.path.exists(path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_MAP_DATA, f, indent=4, ensure_ascii=False)
            print(f"[信息] 已生成默认地图配置文件: {path}")
        except Exception as e:
            print(f"[错误] 无法生成地图配置文件: {e}")
        return DEFAULT_MAP_DATA["maps"].get(current_map, DEFAULT_MAP_DATA["maps"]["map1"])
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        maps = data.get("maps", {})
        if current_map not in maps:
            print(f"[警告] 未找到地图 '{current_map}'，使用 map1")
            return maps.get("map1", DEFAULT_MAP_DATA["maps"]["map1"])
        return maps[current_map]
    except Exception as e:
        print(f"[错误] 地图配置文件加载失败: {e}")
        return DEFAULT_MAP_DATA["maps"].get(current_map, DEFAULT_MAP_DATA["maps"]["map1"])

CONFIG = load_config()
CURRENT_MAP = CONFIG.get('current_map', 'map1')
MAP_DATA = load_map_data(MAP_DATA_PATH, CURRENT_MAP)

def enhance_fishing_spots(spots, waters):
    if not waters:
        for spot in spots:
            spot['water_x'] = spot['x']
            spot['water_y'] = spot['y']
            spot['water_z'] = spot['z']
        return
    for spot in spots:
        cx, cz = spot['x'], spot['z']
        best = min(waters, key=lambda w: (w['water_x']-cx)**2 + (w['water_z']-cz)**2)
        spot['water_x'] = best['water_x']
        spot['water_y'] = best['water_y']
        spot['water_z'] = best['water_z']

FISHING_SPOTS = MAP_DATA.get('fishing_spots', [])
WATER_CANDIDATES = MAP_DATA.get('water_candidates', [])
enhance_fishing_spots(FISHING_SPOTS, WATER_CANDIDATES)

FORBIDDEN_ZONES = MAP_DATA.get('forbidden_zones') or []
VIA_STATIONS = MAP_DATA.get('via_stations') or []
SPECIAL_SPOTS = [tuple(s) for s in (MAP_DATA.get('special_spots') or [])]
VIA_RULE = MAP_DATA.get('via_rule')
HAS_FORBIDDEN_ZONE = bool(FORBIDDEN_ZONES)

# ================= 圆角按钮 =================
ICON_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA7UlEQVQ4y2NgoBfYHaADwv9B+FaaFsP9SC7SNJ+MMwYb8LXLA2zI5TBRvDah4OMZLnDNIAy0/f8SJ6X/WDWfKQmGO/VshBKc/XpD//8v+QpwzTgNACl+v3chWCGIDdL0+8YhsBjIEJDGI0HKYLU4DQBpAGlExiDNmXqc/xdFmuDWfDJcE+4CkCEwm0EGgMRBBhQaceOPJmRbYYEGC3m8BpwuCoQHGC7NzZbCDPhcgOFsmN9h/sepGWYAkAJrQvY3zPaZMeYMBA1AtxWmudNGDL9mEAApBMU9LP5BfKI1g8BUey4GmCbkACNKMyUAAEa5EUQb0ge+AAAAAElFTkSuQmCC"

class RoundedButton(tk.Canvas):
    def __init__(self, master=None, text="", command=None, radius=10,
                 bg='#3498db', fg='white', hover_bg='#2980b9', disabled_bg='#b0bec5',
                 disabled_fg='#cfd8dc', font=('', 10, 'bold'), **kwargs):
        self.text = text
        self.command = command
        self.radius = radius
        self.bg = bg; self.fg = fg; self.hover_bg = hover_bg
        self.disabled_bg = disabled_bg; self.disabled_fg = disabled_fg
        self.font = font; self.enabled = True
        temp_label = tk.Label(master, text=text, font=font); temp_label.pack_forget()
        txt_width = temp_label.winfo_reqwidth(); txt_height = temp_label.winfo_reqheight()
        temp_label.destroy()
        pad_x, pad_y = 30, 10
        self.width = txt_width + 2 * pad_x; self.height = txt_height + 2 * pad_y
        super().__init__(master, width=self.width, height=self.height,
                         highlightthickness=0, bg=master['bg'], **kwargs)
        self.configure(cursor='hand2')
        self.bind("<Enter>", self.on_enter); self.bind("<Leave>", self.on_leave); self.bind("<Button-1>", self.on_click)
        self.draw_normal()

    def draw_round_rect(self, color):
        self.delete("all")
        x1, y1 = 2, 2; x2, y2 = self.width - 2, self.height - 2; r = self.radius
        self.create_arc((x1,y1,x1+2*r,y1+2*r), start=90, extent=90, fill=color, outline=color)
        self.create_arc((x2-2*r,y1,x2,y1+2*r), start=0, extent=90, fill=color, outline=color)
        self.create_arc((x1,y2-2*r,x1+2*r,y2), start=180, extent=90, fill=color, outline=color)
        self.create_arc((x2-2*r,y2-2*r,x2,y2), start=270, extent=90, fill=color, outline=color)
        self.create_rectangle((x1+r, y1, x2-r, y2), fill=color, outline=color)
        self.create_rectangle((x1, y1+r, x2, y2-r), fill=color, outline=color)
        self.create_text(self.width//2, self.height//2, text=self.text,
                         fill=self.fg if self.enabled else self.disabled_fg, font=self.font, justify='center')
    def draw_normal(self): self.draw_round_rect(self.bg if self.enabled else self.disabled_bg)
    def on_enter(self, event):
        if self.enabled: self.draw_round_rect(self.hover_bg)
    def on_leave(self, event):
        if self.enabled: self.draw_round_rect(self.bg)
    def on_click(self, event):
        if self.enabled and self.command: self.command()
    def set_enabled(self, enable: bool):
        self.enabled = enable
        self.configure(cursor='hand2' if enable else '')
        self.draw_normal()

# ================= 主应用 =================
class AutoFishingApp:
    def __init__(self, config):
        self.config = config
        self.config_lock = threading.Lock()
        self.M = None
        self.B_status = 'off'
        self.current_stop_event = None
        self.fishing_active = False
        self.simulate_flag = threading.Event()
        self.click_queue = queue.Queue()
        self.detect_stop_event = threading.Event()
        self.detect_thread = None
        self.skip_initial_throw = False
        self.auto_prepare_cast = False   # 检测完成后：在钓鱼线程内自动收竿→抛竿→循环
        self._save_lock = threading.Lock()   # 配置保存串行锁
        self.lock = threading.Lock()
        self.m_lock = threading.Lock()
        self.fishing_thread = None
        self.navigation_stop_event = threading.Event()
        self.log_entries = deque()
        self.mouse_listener = None
        self.keyboard_listener = None
        self._closing = False   # 关闭保护标志
        self._tag_configured = set()

        self.fishing_spots = FISHING_SPOTS
        self.water_candidates = WATER_CANDIDATES
        self.via_stations = VIA_STATIONS
        self.special_spots = SPECIAL_SPOTS
        self.via_rule = VIA_RULE
        self.forbidden_zones = FORBIDDEN_ZONES
        self.has_forbidden_zone = HAS_FORBIDDEN_ZONE
        self.bypassed_zones = []
        self.current_map_data = MAP_DATA

        self.available_spots = list(self.fishing_spots)
        self.exhausted_spots = []
        self.obstacle_count = 0
        self.last_strafe_key = None
        self.evasion_count = 0
        self.key_stop_nav = self.config.get('key_stop_navigation', 'm')
        self.key_toggle_fish = self.config.get('key_toggle_fishing', 'n')

        self.last_hour = time.localtime().tm_hour
        self.hourly_reset_thread = threading.Thread(target=self._hourly_reset_loop, daemon=True)
        self.hourly_reset_thread.start()

        self.root = tk.Tk()
        self.root.title("Tau 1.0")
        w = config.get('ui_window_width', 300); h = config.get('ui_window_height', 900)
        mw = config.get('ui_minsize_width', 300); mh = config.get('ui_minsize_height', 700)
        self.root.geometry(f"{w}x{h}"); self.root.minsize(mw, mh)
        self.root.configure(bg='#eef1f6')

        self.auto_throw_enabled = tk.BooleanVar(value=config.get('auto_throw_enabled', False))
        self.fish_depleted_alert_enabled = tk.BooleanVar(value=config.get('fish_depleted_alert_enabled', True))
        self.auto_relocate_enabled = tk.BooleanVar(value=config.get('auto_relocate_enabled', False))
        self.multiple_cast_enabled = tk.BooleanVar(value=config.get('multiple_cast', False))
        self.depleted_alerted = False

        fn_lock_enabled = config.get('fn_lock_enabled', True)
        self.fn_lock_on_var = tk.BooleanVar(value=fn_lock_enabled)
        self.fn_lock_off_var = tk.BooleanVar(value=not fn_lock_enabled)

        self.sens_var = tk.StringVar(value=str(config.get('sensitivity', 95)))
        self.multiplier_var = tk.StringVar(value=str(config.get('mouse_move_multiplier', 1.0)))
        ov = config.get('deg_per_pixel_override')
        self.deg_override_var = tk.StringVar(value='' if ov is None else str(ov))
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

        try:
            icon_photo = None
            ico_path = os.path.join(SCRIPT_DIR, 'tau.ico')
            if os.path.exists(ico_path):
                icon_image = Image.open(ico_path)
            else:
                b64_data = ICON_BASE64.split(',')[-1]
                icon_bytes = base64.b64decode(b64_data)
                icon_image = Image.open(io.BytesIO(icon_bytes))
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.root.iconphoto(True, icon_photo)
        except Exception as e:
            print(f"[警告] 窗口图标加载失败: {e}")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', background='#eef1f6')
        self.style.configure('Title.TLabel', background='#eef1f6', font=('Microsoft YaHei UI', 14, 'bold'), foreground='#334155')
        # 下拉框样式（白底 + 浅边框 + 蓝色箭头/聚焦边）
        self.style.configure('TCombobox', fieldbackground='#ffffff', background='#ffffff',
                             foreground='#334155', bordercolor='#e2e8f0',
                             lightcolor='#e2e8f0', darkcolor='#e2e8f0',
                             arrowcolor='#4f7cff', padding=4)
        self.style.map('TCombobox',
                       fieldbackground=[('readonly', '#ffffff')],
                       selectbackground=[('readonly', '#ffffff')],
                       selectforeground=[('readonly', '#334155')],
                       bordercolor=[('focus', '#4f7cff')])
        # 滚动条样式
        self.style.configure('Vertical.TScrollbar', background='#cbd5e1',
                             troughcolor='#eef1f6', bordercolor='#eef1f6',
                             arrowcolor='#64748b')
        self.setup_ui()
        self.start_mouse_listener()
        self.start_keyboard_listener()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.auto_throw_enabled.trace_add('write', lambda *a: self._on_checkbox_changed())
        self.fish_depleted_alert_enabled.trace_add('write', lambda *a: self._on_checkbox_changed())
        self.auto_relocate_enabled.trace_add('write', lambda *a: self._on_checkbox_changed())
        self.multiple_cast_enabled.trace_add('write', lambda *a: self._on_checkbox_changed())
        self.fn_lock_on_var.trace_add('write', lambda *a: self._on_fn_lock_changed())
        self.fn_lock_off_var.trace_add('write', lambda *a: self._on_fn_lock_changed())
        self._update_status("就绪")
        self.log(f"当前地图: {MAP_DATA.get('name', CURRENT_MAP)}", "grey")
        self.root.after(5 * 60 * 1000, self._clean_old_logs)

    # ================= UI 回调 =================
    def _on_checkbox_changed(self):
        with self.config_lock:
            self.config['auto_throw_enabled'] = self.auto_throw_enabled.get()
            self.config['fish_depleted_alert_enabled'] = self.fish_depleted_alert_enabled.get()
            self.config['auto_relocate_enabled'] = self.auto_relocate_enabled.get()
            self.config['multiple_cast'] = self.multiple_cast_enabled.get()
        self._save_config_async()

    def _on_fn_lock_changed(self):
        with self.config_lock:
            self.config['fn_lock_enabled'] = self.fn_lock_on_var.get()
        self._save_config_async()

    def _on_fn_lock_on_changed(self):
        if self.fn_lock_on_var.get():
            self.fn_lock_off_var.set(False)
        else:
            self.fn_lock_on_var.set(True)

    def _on_fn_lock_off_changed(self):
        if self.fn_lock_off_var.get():
            self.fn_lock_on_var.set(False)
        else:
            self.fn_lock_off_var.set(True)

    def _on_sens_multiplier_changed(self, event=None):
        with self.config_lock:
            try: self.config['sensitivity'] = int(self.sens_var.get())
            except (ValueError, TypeError): pass
            try: self.config['mouse_move_multiplier'] = float(self.multiplier_var.get())
            except (ValueError, TypeError): pass
        self._save_config_async()

    def _on_deg_override_changed(self, event=None):
        val = self.deg_override_var.get().strip()
        with self.config_lock:
            if val:
                try: self.config['deg_per_pixel_override'] = float(val)
                except: self.config['deg_per_pixel_override'] = None
            else:
                self.config['deg_per_pixel_override'] = None
        self._save_config_async()

    def _save_config_async(self):
        with self.config_lock:
            config_copy = self.config.copy()
        def _save():
            with self._save_lock:   # 串行化保存，避免并发写配置文件
                save_config_internal(config_copy, CONFIG_PATH)
        threading.Thread(target=_save, daemon=True).start()

    # ================= UI 布局 =================
    FONT = 'Microsoft YaHei UI'
    BG = '#eef1f6'
    CARD_BG = '#ffffff'
    CARD_BORDER = '#e2e8f0'
    TEXT = '#334155'

    # 「配置设置」栏显示的配置项: (键, 中文名, 类型)
    CONFIG_FIELDS = [
        ('detection_timeout', '检测超时 (秒)', float),
        ('no_fish_timeout', '无鱼判定超时 (秒)', float),
        ('manual_cast_timeout', '等待手动抛竿超时 (秒)', float),
        ('max_rotation_attempts', '最大转向尝试 (次)', int),
        ('angle_tolerance', '角度容差 (°)', float),
        ('mouse_move_multiplier', '鼠标移动倍率', float),
        ('mouse_jitter', '鼠标随机抖动 (像素)', int),
        ('water_float_timeout', '上浮超时 (秒)', float),
        ('pitch_down_after_arrival', '到达后下压俯仰角 (°)', float),
        ('max_water_fails', '连续上浮失败上限 (次)', int),
        ('water_jump_threshold', '落水判定Y高度', float),
        ('ray_align_min_step', '对准最小角度步进 (°)', float),
        ('align_water_max_iter', '对准水域最大迭代 (次)', int),
        ('px_color', '鱼漂像素颜色(#RRGGBB)', str),
        ('px_width', '检测区域宽(像素)', int),
        ('px_height', '检测区域高(像素)', int),
        ('detection_tolerance', '检测颜色容差', int),
        ('key_stop_navigation', '停止寻路快捷键', str),
        ('key_toggle_fishing', '钓鱼开关快捷键', str),
    ]

    def _on_global_click(self, event):
        """点击非输入控件时让输入框失焦（光标消失），日志框/输入控件保持焦点以便选择。"""
        w = event.widget
        if isinstance(w, (tk.Entry, ttk.Combobox, tk.Text)):
            return  # 输入控件与日志框保持焦点
        try:
            self.root.focus_set()
        except Exception:
            pass

    def _make_card(self, parent, title):
        """创建白色卡片容器（标题带蓝色竖条），返回 (card, body)。"""
        card = tk.Frame(parent, bg=self.CARD_BG,
                        highlightbackground=self.CARD_BORDER, highlightthickness=1)
        card.pack(fill=tk.X, padx=12, pady=(0, 10))
        title_row = tk.Frame(card, bg=self.CARD_BG)
        title_row.pack(anchor='w', padx=14, pady=(10, 2))
        tk.Frame(title_row, bg='#4f7cff', width=4, height=14).pack(side='left')
        tk.Label(title_row, text=title, bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 10, 'bold')).pack(side='left', padx=(6, 0))
        body = tk.Frame(card, bg=self.CARD_BG)
        body.pack(fill=tk.X, padx=10, pady=(0, 8))
        return card, body

    def _make_entry(self, parent, textvariable, width=8, justify='center'):
        """创建统一风格输入框（扁平 + 浅边框 + 聚焦蓝色高亮）。"""
        return tk.Entry(parent, textvariable=textvariable, width=width,
                        justify=justify, font=(self.FONT, 9),
                        relief='flat', bd=0,
                        highlightthickness=1, highlightbackground=self.CARD_BORDER,
                        highlightcolor='#4f7cff', insertbackground='#4f7cff')

    def _make_check(self, parent, text, var, command=None):
        """创建统一风格的复选框。"""
        chk = tk.Checkbutton(parent, text=text, variable=var, command=command,
                             bg=self.CARD_BG, fg=self.TEXT, activebackground=self.CARD_BG,
                             activeforeground=self.TEXT, selectcolor='white',
                             relief='flat', bd=0, highlightthickness=0,
                             font=(self.FONT, 9), anchor='w')
        chk.pack(pady=2, padx=8, anchor='w')
        return chk

    def _round_rect(self, canvas, x0, y0, x1, y1, r, fill, outline=''):
        """在 Canvas 上画圆角矩形。"""
        canvas.create_arc((x0, y0, x0+2*r, y0+2*r), start=90, extent=90, fill=fill, outline=outline)
        canvas.create_arc((x1-2*r, y0, x1, y0+2*r), start=0, extent=90, fill=fill, outline=outline)
        canvas.create_arc((x0, y1-2*r, x0+2*r, y1), start=180, extent=90, fill=fill, outline=outline)
        canvas.create_arc((x1-2*r, y1-2*r, x1, y1), start=270, extent=90, fill=fill, outline=outline)
        canvas.create_rectangle((x0+r, y0, x1-r, y1), fill=fill, outline=outline)
        canvas.create_rectangle((x0, y0+r, x1, y1-r), fill=fill, outline=outline)

    def _draw_tabs(self):
        """绘制顶部页面切换标签（主页面/设置），选中的显示蓝色。"""
        self.tab_canvas.delete('all')
        w = self.tab_canvas.winfo_width()
        if w < 10:
            w = 276
        gap = 10
        tab_w = (w - gap) / 2
        h = 32
        y = 1
        for i, (name, selected) in enumerate([('主页面', self.page == 'main'),
                                              ('设置', self.page == 'settings')]):
            x0 = i * (tab_w + gap)
            x1 = x0 + tab_w
            color = '#4f7cff' if selected else '#334155'
            self._round_rect(self.tab_canvas, x0, y, x1, y + h, r=10, fill=color)
            self.tab_canvas.create_text((x0 + x1) / 2, y + h / 2, text=name,
                                        fill='#ffffff', font=(self.FONT, 10, 'bold'))

    def _on_tab_click(self, event):
        w = self.tab_canvas.winfo_width()
        tab_w = (w - 10) / 2
        if event.x < tab_w + 5:
            self.show_page('main')
        else:
            self.show_page('settings')

    def show_page(self, page):
        """切换显示主页面或设置页。"""
        self.page = page
        if page == 'main':
            self.settings_page.pack_forget()
            self.main_page.pack(fill=tk.BOTH, expand=True)
        else:
            self.main_page.pack_forget()
            self.settings_page.pack(fill=tk.BOTH, expand=True)
        self.root.focus_set()   # 切换页面时让输入框失焦，光标消失
        self._draw_tabs()

    def _bind_settings_wheel(self, event):
        def _wheel(ev):
            self.settings_canvas.yview_scroll(int(-ev.delta / 120), 'units')
        self.settings_canvas.bind_all('<MouseWheel>', _wheel)

    def _on_config_changed(self, key, ctype, var):
        """配置设置栏数值变化：立即写入 config 并保存；非法输入恢复原值。"""
        raw = var.get().strip()
        with self.config_lock:
            try:
                if ctype is int:
                    val = int(float(raw)) if raw else None
                elif ctype is str:
                    val = raw.lower() if raw else None
                else:
                    val = float(raw) if raw else None
            except (ValueError, TypeError):
                val = None
            if val is None:
                var.set(str(self.config.get(key, '')))
                self.log(f"{key} 输入无效，已恢复原值", "orange")
                return
            self.config[key] = val
            # 快捷键即时生效
            if key == 'key_stop_navigation':
                self.key_stop_nav = val
            elif key == 'key_toggle_fishing':
                self.key_toggle_fish = val
        self._save_config_async()
        self.log(f"配置 {key} → {val}", "grey")

    def _on_input_mode_changed(self, event=None):
        """输入模式切换：global=全局注入 / window=窗口消息注入（不影响其他窗口）。"""
        val = self.input_mode_combo.get()
        with self.config_lock:
            self.config['input_mode'] = val
        self._save_config_async()
        tip = '窗口消息（不影响其他窗口）' if val == 'window' else '全局注入（会占用系统输入）'
        self.log(f"输入模式: {tip}", "blue")

    def setup_ui(self):
        # —— 顶部横幅 ——
        header = tk.Frame(self.root, bg='#1e293b')
        header.pack(fill=tk.X, pady=(0, 8))
        tk.Label(header, text="Tau 1.0", bg='#1e293b', fg='#ffffff',
                 font=(self.FONT, 16, 'bold')).pack(anchor='w', padx=18, pady=(12, 2))
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = tk.Label(header, textvariable=self.status_var, bg='#1e293b',
                                     fg='#cbd5e1', font=(self.FONT, 9))
        self.status_label.pack(anchor='w', padx=18, pady=(0, 10))

        # —— 页面切换标签 ——
        self.page = 'main'
        self.tab_canvas = tk.Canvas(self.root, height=36, bg=self.BG, highlightthickness=0)
        self.tab_canvas.pack(fill=tk.X, padx=12, pady=(0, 8))
        self.tab_canvas.bind('<Button-1>', self._on_tab_click)
        self.tab_canvas.bind('<Configure>', lambda e: self._draw_tabs())
        # 点击任意非输入控件时让输入框失焦（光标消失）
        self.root.bind('<Button-1>', self._on_global_click, add='+')

        # ================= 主页面 =================
        self.main_page = tk.Frame(self.root, bg=self.BG)
        self.main_page.pack(fill=tk.BOTH, expand=True)

        # —— 操作按钮 ——
        self.a_btn = RoundedButton(self.main_page, text="检测文字位置", command=self.start_detection,
                                   bg='#4f7cff', fg='white', hover_bg='#3b63e0',
                                   disabled_bg='#b0bec5', disabled_fg='#cfd8dc',
                                   font=(self.FONT, 10, 'bold'))
        self.a_btn.pack(pady=(0, 8))
        self.b_btn = RoundedButton(self.main_page, text="自动钓鱼开关", command=self.toggle_B,
                                   bg='#10b981', fg='white', hover_bg='#0d9668',
                                   disabled_bg='#b0bec5', disabled_fg='#cfd8dc',
                                   font=(self.FONT, 10, 'bold'))
        self.b_btn.pack(pady=(0, 10))
        self.b_btn.set_enabled(False)

        # —— 选项卡片 ——
        _, body = self._make_card(self.main_page, "选项")
        throw_text = f"{int(self.config.get('no_fish_timeout',60))}秒无鱼自动抛竿"
        self.auto_throw_chk = self._make_check(body, throw_text, self.auto_throw_enabled)
        self.fish_depleted_chk = self._make_check(body, "鱼群枯竭后发出提示音", self.fish_depleted_alert_enabled)
        self.auto_relocate_chk = self._make_check(body, "枯竭自动换池", self.auto_relocate_enabled)
        self.multiple_cast_chk = self._make_check(body, "换池后额外抛竿", self.multiple_cast_enabled)

        # —— 地图选择卡片 ——
        _, body = self._make_card(self.main_page, "地图选择")
        self.map1_var = tk.BooleanVar(value=(self.config.get('current_map','map1')=='map1'))
        self.map2_var = tk.BooleanVar(value=(self.config.get('current_map','map1')=='map2'))
        cb1 = tk.Checkbutton(body, text="1图", variable=self.map1_var,
                             bg=self.CARD_BG, fg=self.TEXT, activebackground=self.CARD_BG,
                             activeforeground=self.TEXT, selectcolor='white',
                             relief='flat', bd=0, highlightthickness=0,
                             font=(self.FONT, 9), anchor='w',
                             command=lambda: self._on_map_select('map1'))
        cb1.pack(pady=2, padx=8, anchor='w')
        cb2 = tk.Checkbutton(body, text="2图", variable=self.map2_var,
                             bg=self.CARD_BG, fg=self.TEXT, activebackground=self.CARD_BG,
                             activeforeground=self.TEXT, selectcolor='white',
                             relief='flat', bd=0, highlightthickness=0,
                             font=(self.FONT, 9), anchor='w',
                             command=lambda: self._on_map_select('map2'))
        cb2.pack(pady=2, padx=8, anchor='w')

        # —— 日志区 ——
        out_outer = tk.Frame(self.main_page, bg=self.BG)
        out_outer.pack(pady=(4, 12), padx=12, fill=tk.BOTH, expand=True)
        self.out_canvas = tk.Canvas(out_outer, bg=self.BG, highlightthickness=0)
        self.out_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.text_widget = tk.Text(out_outer, wrap=tk.WORD, bg='#ffffff', fg=self.TEXT,
                                   relief='flat', borderwidth=0, highlightthickness=0,
                                   padx=10, pady=10,
                                   font=(self.FONT, 9))
        self.text_widget.bind('<Key>', self._block_log_edit)
        self.text_widget.bind('<Control-c>', self._copy_log)
        scrollbar = ttk.Scrollbar(out_outer, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.out_canvas.bind('<Configure>', self._draw_rounded_border)
        self._draw_rounded_border()

        # ================= 设置页 =================
        self.settings_page = tk.Frame(self.root, bg=self.BG)
        self.settings_canvas = tk.Canvas(self.settings_page, bg=self.BG, highlightthickness=0)
        self.settings_scroll = ttk.Scrollbar(self.settings_page, orient=tk.VERTICAL,
                                             command=self.settings_canvas.yview)
        self.settings_inner = tk.Frame(self.settings_canvas, bg=self.BG)
        self.settings_inner.bind('<Configure>',
                                 lambda e: self.settings_canvas.configure(scrollregion=self.settings_canvas.bbox('all')))
        self.settings_canvas.create_window((0, 0), window=self.settings_inner, anchor='nw')
        self.settings_canvas.configure(yscrollcommand=self.settings_scroll.set)
        self.settings_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.settings_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.settings_canvas.bind('<Enter>', self._bind_settings_wheel)
        self.settings_canvas.bind('<Leave>', lambda e: self.settings_canvas.unbind_all('<MouseWheel>'))

        # —— 鼠标设置卡片 ——
        _, body = self._make_card(self.settings_inner, "鼠标设置")
        tk.Label(body, text="游戏灵敏度:", bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 9)).grid(row=0, column=0, padx=(10, 5), sticky='w')
        sens_entry = self._make_entry(body, self.sens_var, width=6)
        sens_entry.grid(row=0, column=1, sticky='w')
        sens_entry.bind('<FocusOut>', self._on_sens_multiplier_changed)
        tk.Label(body, text="鼠标移动倍率:", bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 9)).grid(row=1, column=0, padx=(10, 5), sticky='w')
        mult_entry = self._make_entry(body, self.multiplier_var, width=6)
        mult_entry.grid(row=1, column=1, sticky='w')
        mult_entry.bind('<FocusOut>', self._on_sens_multiplier_changed)
        tk.Label(body, text="转向覆写(°/像素):", bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 9)).grid(row=2, column=0, padx=(10, 5), sticky='w')
        deg_entry = self._make_entry(body, self.deg_override_var, width=8)
        deg_entry.grid(row=2, column=1, sticky='w')
        deg_entry.bind('<FocusOut>', self._on_deg_override_changed)
        tk.Label(body, text="输入模式:", bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 9)).grid(row=3, column=0, padx=(10, 5), sticky='w')
        self.input_mode_combo = ttk.Combobox(body, values=['global', 'window'],
                                             state='readonly', width=6, font=(self.FONT, 9))
        self.input_mode_combo.set(str(self.config.get('input_mode', 'global')))
        self.input_mode_combo.grid(row=3, column=1, sticky='w')
        self.input_mode_combo.bind('<<ComboboxSelected>>', self._on_input_mode_changed)
        tk.Label(body, text="global=全局 / window=只影响游戏窗口",
                 bg=self.CARD_BG, fg='#94a3b8', font=(self.FONT, 8)).grid(row=4, column=0,
                 columnspan=2, padx=(10, 5), sticky='w')
        body.grid_columnconfigure(1, weight=1)

        # —— FnLock 卡片 ——
        _, body = self._make_card(self.settings_inner, "FnLock 状态")
        self.fn_lock_on_chk = self._make_check(body, "FnLock on", self.fn_lock_on_var,
                                               command=self._on_fn_lock_on_changed)
        self.fn_lock_off_chk = self._make_check(body, "FnLock off", self.fn_lock_off_var,
                                                command=self._on_fn_lock_off_changed)

        # —— 配置设置卡片 ——
        _, body = self._make_card(self.settings_inner, "配置设置")
        self.config_entries = {}
        for i, (key, label, ctype) in enumerate(self.CONFIG_FIELDS):
            tk.Label(body, text=label, bg=self.CARD_BG, fg=self.TEXT,
                     font=(self.FONT, 9)).grid(row=i, column=0, padx=(10, 5), sticky='w')
            var = tk.StringVar(value=str(self.config.get(key, '')))
            entry = self._make_entry(body, var, width=8)
            entry.grid(row=i, column=1, sticky='w', pady=1)
            entry.bind('<FocusOut>', lambda e, k=key, t=ctype, v=var: self._on_config_changed(k, t, v))
            entry.bind('<Return>', lambda e, k=key, t=ctype, v=var: self._on_config_changed(k, t, v))
            self.config_entries[key] = var
        body.grid_columnconfigure(1, weight=1)

    def _draw_rounded_border(self, event=None):
        self.out_canvas.delete("all")
        w = self.out_canvas.winfo_width(); h = self.out_canvas.winfo_height()
        if w<5 or h<5: return
        r=12; o='#e2e8f0'; i='#ffffff'
        self.out_canvas.create_arc((2,2,2+2*r,2+2*r), start=90, extent=90, fill=o, outline=o)
        self.out_canvas.create_arc((w-2-2*r,2,w-2,2+2*r), start=0, extent=90, fill=o, outline=o)
        self.out_canvas.create_arc((2,h-2-2*r,2+2*r,h-2), start=180, extent=90, fill=o, outline=o)
        self.out_canvas.create_arc((w-2-2*r,h-2-2*r,w-2,h-2), start=270, extent=90, fill=o, outline=o)
        self.out_canvas.create_rectangle((2+r,2,w-2-r,h-2), fill=o, outline=o)
        self.out_canvas.create_rectangle((2,2+r,w-2,h-2-r), fill=o, outline=o)
        pad=3
        self.out_canvas.create_arc((2+pad,2+pad,2+2*r-pad,2+2*r-pad), start=90, extent=90, fill=i, outline=i)
        self.out_canvas.create_arc((w-2-2*r+pad,2+pad,w-2-pad,2+2*r-pad), start=0, extent=90, fill=i, outline=i)
        self.out_canvas.create_arc((2+pad,h-2-2*r+pad,2+2*r-pad,h-2-pad), start=180, extent=90, fill=i, outline=i)
        self.out_canvas.create_arc((w-2-2*r+pad,h-2-2*r+pad,w-2-pad,h-2-pad), start=270, extent=90, fill=i, outline=i)
        self.out_canvas.create_rectangle((2+r,2+pad,w-2-r,h-2-pad), fill=i, outline=i)
        self.out_canvas.create_rectangle((2+pad,2+r,w-2-pad,h-2-r), fill=i, outline=i)

    def _update_status(self, text):
        if not self._closing:
            def _apply():
                self.status_var.set(text)
                self.status_label.configure(fg=self._status_color(text))
            self.root.after(0, _apply)

    def _status_color(self, text):
        """根据状态文本返回横幅内状态文字的颜色。"""
        if '换池' in text: return '#a78bfa'
        if '检测' in text: return '#f59e0b'
        if '钓鱼' in text: return '#34d399'
        return '#cbd5e1'
    def log(self, message, color='black'):
        if not self._closing:
            self.root.after(0, self._log_to_C, message, color)

    def _block_log_edit(self, event):
        """日志框只读：禁止编辑，放行复制(Ctrl+C)与全选(Ctrl+A)。"""
        if (event.state & 0x0004) and event.keysym.lower() in ('c', 'a'):
            return None
        return 'break'

    def _copy_log(self, event=None):
        """复制日志：有选区复制选区，无选区复制全部（显式写剪贴板，可靠）。"""
        try:
            content = self.text_widget.get('sel.first', 'sel.last')
        except tk.TclError:
            content = self.text_widget.get('1.0', 'end-1c')
        if content:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
            except Exception:
                pass
        return 'break'

    def _log_to_C(self, message, color):
        widget = self.text_widget
        widget.insert(tk.END, message+'\n')
        if color!='black':
            tag=f"color_{color}"; linestart=widget.index("end-2c linestart"); lineend=widget.index("end-2c lineend")
            widget.tag_add(tag, linestart, lineend)
            if color not in self._tag_configured:
                self._tag_configured.add(color)
                widget.tag_config(tag, foreground=color)
        widget.see(tk.END)
        self.log_entries.append((time.time(), message, color))

    def _clean_old_logs(self):
        cutoff = time.time() - 10*60
        while self.log_entries and self.log_entries[0][0] < cutoff: self.log_entries.popleft()
        widget = self.text_widget
        widget.delete('1.0', tk.END)
        for ts, msg, color in self.log_entries:
            widget.insert(tk.END, msg+'\n')
            if color!='black':
                tag=f"color_{color}"; linestart=widget.index("end-2c linestart"); lineend=widget.index("end-2c lineend")
                widget.tag_add(tag, linestart, lineend)
                if color not in self._tag_configured:
                    self._tag_configured.add(color)
                    widget.tag_config(tag, foreground=color)
        widget.see(tk.END)
        self.root.after(5*60*1000, self._clean_old_logs)

    # ================= 监听器 =================
    def start_mouse_listener(self):
        def on_click(x,y,button,pressed):
            if button==mouse.Button.right and pressed and not self.simulate_flag.is_set():
                self.click_queue.put('right')
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()

    def start_keyboard_listener(self):
        def on_press(key):
            try:
                if hasattr(key, 'char'):
                    if key.char == self.key_stop_nav:
                        self.navigation_stop_event.set()
                        self.log(f"已按下 {self.key_stop_nav.upper()} 键，请求停止寻路", "purple")
                    elif key.char == self.key_toggle_fish:
                        self.root.after(0, self.toggle_B)
            except Exception as e:
                self.log(f"键盘监听异常: {e}", "orange")
        self.keyboard_listener = KeyboardListener(on_press=on_press)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    # ===== 输入后端（global=全局注入 / window=窗口消息注入，不影响用户操作） =====
    VK_MAP = {
        'w': 0x57, 'a': 0x41, 's': 0x53, 'd': 0x44,
        'space': 0x20, 'f3': 0x72, 'c': 0x43,
    }
    WM_KEYDOWN = 0x0100; WM_KEYUP = 0x0101
    WM_RBUTTONDOWN = 0x0204; WM_RBUTTONUP = 0x0205
    WM_MOUSEMOVE = 0x0200
    MK_RBUTTON = 0x0002
    KEYUP_LPARAM = 0xC0000000  # prev=1, transition=1

    def _get_input_hwnd(self):
        """window 输入模式下返回游戏窗口句柄；global 模式或找不到窗口返回 None。"""
        if self.config.get('input_mode', 'global') != 'window':
            return None
        return self._find_game_window()

    def _fallback_global(self, why):
        """窗口输入失败时回退全局模式，并提示用户。"""
        self.log(f"{why}，已回退全局输入", "orange")
        with self.config_lock:
            self.config['input_mode'] = 'global'

    def _key_down(self, key):
        key = str(key).lower()
        hwnd = self._get_input_hwnd()
        if hwnd is not None:
            try:
                vk = self.VK_MAP.get(key)
                if vk is None:
                    pyautogui.keyDown(key); return
                ctypes.windll.user32.PostMessageW(hwnd, self.WM_KEYDOWN, vk, 0)
                return
            except Exception:
                self._fallback_global("窗口键盘输入失败")
        pyautogui.keyDown(key)

    def _key_up(self, key):
        key = str(key).lower()
        hwnd = self._get_input_hwnd()
        if hwnd is not None:
            try:
                vk = self.VK_MAP.get(key)
                if vk is None:
                    pyautogui.keyUp(key); return
                ctypes.windll.user32.PostMessageW(hwnd, self.WM_KEYUP, vk, self.KEYUP_LPARAM)
                return
            except Exception:
                self._fallback_global("窗口键盘输入失败")
        pyautogui.keyUp(key)

    def simulate_right_click(self):
        self.simulate_flag.set()
        time.sleep(self.config.get('click_pre_delay',0.02))
        hwnd = self._get_input_hwnd()
        if hwnd is not None:
            try:
                l, t, r, b = win32gui.GetClientRect(hwnd)
                cx, cy = (r - l) // 2, (b - t) // 2
                lParam = (cy << 16) | (cx & 0xFFFF)
                ctypes.windll.user32.PostMessageW(hwnd, self.WM_RBUTTONDOWN, self.MK_RBUTTON, lParam)
                time.sleep(0.03)
                ctypes.windll.user32.PostMessageW(hwnd, self.WM_RBUTTONUP, 0, lParam)
            except Exception:
                self._fallback_global("窗口右键点击失败")
                pyautogui.click(button='right')
        else:
            pyautogui.click(button='right')
        time.sleep(self.config.get('click_post_delay',0.05))
        self.simulate_flag.clear()

    def _grab_pixel_rgb(self, x, y):
        """局部截屏取单像素 RGB（比 pyautogui.pixel 的全屏截图快）。失败返回 None。"""
        try:
            if not hasattr(self, '_screen_size'):
                self._screen_size = pyautogui.size()
            sw, sh = self._screen_size
            left, top = max(0, x - 2), max(0, y - 2)
            right, bottom = min(sw - 1, x + 3), min(sh - 1, y + 3)
            if right <= left or bottom <= top:
                return None
            img = ImageGrab.grab(bbox=(left, top, right, bottom))
            arr = np.array(img, dtype=np.int16)
            return tuple(int(v) for v in arr[y - top, x - left])
        except Exception as e:
            now = time.time()
            if now - getattr(self, '_last_px_err_log', 0.0) > 5.0:
                self._last_px_err_log = now
                self.log(f"截屏取色失败({x},{y}): {e}", "orange")
            return None

    # ================= 钓鱼逻辑 =================
    def start_detection(self):
        if self.B_status=='on': self.log("检测前自动停止钓鱼","orange"); self.stop_fishing()
        self.a_btn.set_enabled(False); self.b_btn.set_enabled(False)
        self.detect_stop_event.clear()
        self.detect_thread = threading.Thread(target=self._detection_thread, daemon=True)
        self.detect_thread.start(); self._update_status("检测中...")

    def _detection_thread(self):
        self.log("正在检测中，请抛竿","#2e317c")
        screen_w, screen_h = pyautogui.size()
        hwnd = self._find_game_window()
        if not hwnd:
            self.log("未找到游戏窗口，无法检测（请确认游戏窗口标题含关键词或已启动 javaw/java 进程）","red")
            self.root.after(0, self._finish_detection, False)
            return
        self.log("已定位游戏窗口，检测区域跟随窗口","grey")
        cx, cy, cw, ch = self._get_crosshair_screen_pos()
        # 检测区域中心 = 准心 + 比例偏移
        ox = round(float(self.config.get('detect_center_offset_x_ratio', 0.0)) * cw)
        oy = round(float(self.config.get('detect_center_offset_y_ratio', 0.0)) * ch)
        cx, cy = cx + ox, cy + oy
        half_w, half_h = self.config['px_width']//2, self.config['px_height']//2
        left, top = max(0, cx-half_w), max(0, cy-half_h)
        right, bottom = min(screen_w, cx+half_w), min(screen_h, cy+half_h)
        region_bbox = (left, top, right, bottom)
        self.log(f"检测区域(屏幕坐标): {region_bbox}", "grey")
        reg_cx, reg_cy = (right-left)//2, (bottom-top)//2
        target_rgb = self.hex_to_rgb(self.config['px_color'])
        tol = self.config.get('detection_tolerance',0); confirm_time = self.config['confirmation_time']
        start = time.time()
        while not self.detect_stop_event.is_set():
            if time.time()-start > self.config['detection_timeout']:
                self.log("检测超时，未找到稳定像素","red")
                self.root.after(0, self._finish_detection, False); return
            try:
                img = ImageGrab.grab(bbox=region_bbox)
                arr = np.array(img, dtype=np.int16)
            except Exception: time.sleep(0.5); continue
            diff = np.abs(arr - np.array(target_rgb, dtype=np.int16)).sum(axis=2)
            mask = diff <= tol
            if np.any(mask):
                ys, xs = np.where(mask)
                dists = (xs-reg_cx)**2 + (ys-reg_cy)**2
                idx = np.argmin(dists)
                cand_x = left+int(xs[idx]); cand_y = top+int(ys[idx])
                cand_x = max(0, min(screen_w-1, cand_x)); cand_y = max(0, min(screen_h-1, cand_y))
                cand_rgb = tuple(int(v) for v in arr[ys[idx], xs[idx]])
                self.log(f"发现候选像素 ({cand_x},{cand_y}) 颜色{cand_rgb}，持续监测中...")
                cstart = time.time(); confirmed = True
                while time.time()-cstart < confirm_time:
                    if self.detect_stop_event.is_set(): return
                    time.sleep(0.1)
                    pix = self._grab_pixel_rgb(cand_x, cand_y)
                    if pix is None or sum(abs(a-b) for a,b in zip(pix, target_rgb)) > tol:
                        confirmed = False; break
                if confirmed:
                    with self.m_lock:
                        self.M = [cand_x, cand_y]
                    self.root.after(0, self._finish_detection, True); return
                else: self.log("候选像素未稳定保留，重新扫描...")
            else: time.sleep(self.config.get('detection_poll_interval', 0.2))

    def _finish_detection(self, success):
        self.a_btn.set_enabled(True)
        if success:
            self.log(f"已获取关键像素位置{self.M}，正在自动收竿","#41b349")
            self.b_btn.set_enabled(False)
            with self.lock:
                self.auto_prepare_cast = True
            self.start_fishing()   # 统一走钓鱼线程：收竿→等待→抛竿→循环
        else:
            self.b_btn.set_enabled(True); self._update_status("就绪")

    def toggle_B(self):
        if self.B_status=='off': self.start_fishing()
        else: self.stop_fishing()

    def start_fishing(self):
        self.stop_fishing()
        if self.fishing_thread and self.fishing_thread.is_alive():
            if self.fishing_thread is not threading.current_thread():
                self.log("等待旧钓鱼线程退出...","grey"); self.fishing_thread.join(timeout=3.0)
        self.B_status='on'; self.log("钓鱼状态: on","blue"); self.b_btn.set_enabled(True)
        self.current_stop_event = threading.Event()
        self.fishing_thread = threading.Thread(target=self._fishing_logic, args=(self.current_stop_event,), daemon=True)
        self.fishing_thread.start(); self._update_status("钓鱼中")

    def stop_fishing(self):
        if self.B_status=='on': self.B_status='off'; self.log("钓鱼状态: off","blue")
        if self.current_stop_event: self.current_stop_event.set()
        self.navigation_stop_event.set()

    def _try_aim_nearest_water(self):
        coords = self._get_current_coords(2)
        if not coords or not self.water_candidates: return False
        cx, cy, cz = coords[0], coords[1], coords[2]
        best, best_dist = None, float('inf')
        for w in self.water_candidates:
            d = math.hypot(w['water_x']-cx, w['water_z']-cz)
            if d < best_dist: best_dist = d; best = w
        if best and best_dist <= 30:
            self.log(f"尝试对准最近水域 ({best['water_x']:.1f},{best['water_z']:.1f})","grey")
            temp_target = {'water_x':best['water_x'],'water_y':best['water_y'],'water_z':best['water_z'],
                           'x':cx,'y':cy,'z':cz}
            return self._align_to_water_block(temp_target)
        return False

    def _fishing_logic(self, stop_event):
        with self.m_lock:
            m_pos = self.M
        if m_pos is None: self.log("错误：未获取到钓鱼位置 M","red"); return
        mx, my = int(m_pos[0]), int(m_pos[1])
        poll_rate = self.config['polling_rate']/1000.0; jitter = self.config.get('polling_jitter',50)/1000.0
        target_rgb = self.hex_to_rgb(self.config['px_color']); tol = self.config['color_tolerance']
        timeout = self.config['no_fish_timeout']; confirm = self.config['confirmation_time']
        rw_min, rw_max = self.config.get('reel_wait_min',4.0), self.config.get('reel_wait_max',6.0)
        cd_min, cd_max = self.config.get('cast_delay_min',0.1), self.config.get('cast_delay_max',0.4)
        with self.lock:
            auto_prepare = self.auto_prepare_cast
            self.auto_prepare_cast = False
            skip_init = self.skip_initial_throw
            self.skip_initial_throw = False
        if auto_prepare:
            # 检测完成后统一在此线程完成：自动收竿 → 等待 → 自动抛竿 → 进入循环
            time.sleep(0.1); self.simulate_right_click()
            self.log("已自动收竿，请等待5秒","#41b349")
            if stop_event.wait(self.config.get('initial_catch_cast_delay',5.0)): return
            self.simulate_right_click()
            self.log("已自动抛竿，启动钓鱼循环","#41b349")
            last_throw = time.time(); self.depleted_alerted = False
            self.log("直接进入自动钓鱼循环","green")
        elif skip_init:
            last_throw = time.time(); self.depleted_alerted = False
            self.log("直接进入自动钓鱼循环","green")
        else:
            self.log("请先进行一次手动抛竿","blue")
            while not self.click_queue.empty():
                try: self.click_queue.get_nowait()
                except queue.Empty: break
            while True:
                try: self.click_queue.get(timeout=self.config.get('manual_cast_timeout',31.0)); break
                except queue.Empty:
                    if stop_event.is_set(): return
                    if self.auto_throw_enabled.get():
                        self.simulate_right_click()
                        if stop_event.wait(self.config.get('auto_cast_wait',2.0)): return
                        break
                    else:
                        self.log("长时间未检测到抛竿，请手动右键抛竿...","orange")
                        if stop_event.wait(1.0): return
                        continue
            last_throw = time.time(); self.depleted_alerted = False
        self.log("开始自动钓鱼循环","green"); self.fishing_active = True
        try:
            while not stop_event.is_set():
                if time.time()-last_throw > timeout:
                    if (self.fish_depleted_alert_enabled.get() or self.auto_relocate_enabled.get()) and not self.depleted_alerted:
                        try: winsound.MessageBeep()
                        except Exception: pass  # 蜂鸣失败可忽略
                        self.log("该地区鱼群枯竭，请换个地方","red"); self.depleted_alerted = True
                        if self.auto_relocate_enabled.get():
                            self.stop_fishing(); self.log("开始自动换池...","blue"); self._relocate_and_restart(); return
                    if self.auto_throw_enabled.get():
                        self._try_aim_nearest_water()
                        self.simulate_right_click()
                        last_throw = time.time(); self.depleted_alerted = False
                        if stop_event.wait(2.0): break
                        continue
                    else:
                        if stop_event.wait(poll_rate+random.uniform(-jitter,jitter)): break
                        continue
                match = False
                pixel = self._grab_pixel_rgb(mx, my)
                if pixel is not None and sum(abs(a-b) for a,b in zip(pixel, target_rgb)) <= tol:
                    match = True
                if match:
                    cstart = time.time(); confirmed = True
                    while time.time()-cstart < confirm:
                        if stop_event.wait(0.1): return
                        pix = self._grab_pixel_rgb(mx, my)
                        if pix is None or sum(abs(a-b) for a,b in zip(pix, target_rgb)) > tol:
                            confirmed = False; break
                    if confirmed:
                        self.log("检测到上钩，收竿！","green")
                        if stop_event.wait(0.1): break
                        self.simulate_right_click()
                        wait = random.uniform(rw_min, rw_max)
                        self.log(f"等待 {wait:.1f} 秒后重新抛竿...","blue")
                        if stop_event.wait(wait): break
                        self.simulate_right_click()
                        if stop_event.wait(random.uniform(cd_min, cd_max)): break
                        last_throw = time.time(); self.depleted_alerted = False
                        continue
                if stop_event.wait(max(0.05, poll_rate+random.uniform(-jitter,jitter))): break
        finally:
            self.fishing_active = False; self.log("钓鱼循环已停止","blue"); self.root.after(0, self._update_status, "就绪")

    # ================= 导航模块 =================
    def _send_copy_coordinates_sequence(self):
        hwnd = self._get_input_hwnd()
        if hwnd is not None:
            try:
                # F3+C 是组合键：F3 按住期间按下 C，再依次松开
                post = ctypes.windll.user32.PostMessageW
                post(hwnd, self.WM_KEYDOWN, self.VK_MAP['f3'], 0)
                post(hwnd, self.WM_KEYDOWN, self.VK_MAP['c'], 0)
                time.sleep(0.02)
                post(hwnd, self.WM_KEYUP, self.VK_MAP['c'], self.KEYUP_LPARAM)
                post(hwnd, self.WM_KEYUP, self.VK_MAP['f3'], self.KEYUP_LPARAM)
                time.sleep(self.config.get('copy_coord_delay', 0.5))
                return
            except Exception:
                self._fallback_global("窗口 F3+C 失败")
        pyautogui.hotkey('f3','c'); time.sleep(self.config.get('copy_coord_delay',0.5))

    def _parse_clipboard_coordinates(self):
        text = pyperclip.paste()
        patterns = [
            r'@s\s+([\d\.\-\s]+)', r'@p\s+([\d\.\-\s]+)',
            r'([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)'
        ]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                if len(match.groups())<=1: parts = match.group(1).strip().split()
                else: parts = [match.group(i) for i in range(1,6)]
                try:
                    if len(parts)>=5:
                        x,y,z,yaw,pitch = map(float, parts[:5])
                        if all(abs(v)<100000 for v in (x,y,z)):
                            yaw = ((yaw+180)%360)-180; return (x,y,z,yaw,pitch)
                except: continue
        return None

    def _get_current_coords(self, retries=None):
        if retries is None: retries = self.config.get('max_coord_retries',5)
        for _ in range(retries):
            self._send_copy_coordinates_sequence()
            time.sleep(self.config.get('coord_retry_delay_1',0.3))
            coords = self._parse_clipboard_coordinates()
            if coords: return coords
            time.sleep(self.config.get('coord_retry_delay_2',0.2))
        return None

    def _find_nearest_spot(self, current):
        if not self.available_spots or not current: return None
        cx,cy,cz,_,_ = current
        with self.lock:
            best,dist = None,float('inf')
            for sp in self.available_spots:
                d = math.hypot(sp['x']-cx, sp['y']-cy, sp['z']-cz)
                if d<dist: dist=d; best=sp
            return best

    def _calc_target_angles(self, cx,cy,cz, tx,ty,tz, eye_height=None):
        if eye_height is None: eye_height = self.config.get('eye_height',1.62)
        dx,dy,dz = tx-cx, ty-(cy+eye_height), tz-cz
        yaw = math.degrees(-math.atan2(dx,dz))%360.0
        yaw = ((yaw+180)%360)-180
        hor = math.hypot(dx,dz)
        pitch = math.degrees(-math.atan2(dy,hor)) if hor>0 else 0.0
        return yaw,pitch

    def _get_crosshair_screen_pos(self):
        """根据游戏窗口客户区坐标/大小按比例计算准心屏幕位置与客户区尺寸。
        返回 (cx, cy, cw, ch)；找不到窗口时回退屏幕中心。"""
        screen_w, screen_h = pyautogui.size()
        hwnd = self._find_game_window()
        if hwnd:
            try:
                l, t, r, b = win32gui.GetClientRect(hwnd)
                cw, ch = r - l, b - t
                if cw > 0 and ch > 0:
                    px, py = win32gui.ClientToScreen(hwnd, (0, 0))
                    rx = float(self.config.get('crosshair_x_ratio', 0.5))
                    ry = float(self.config.get('crosshair_y_ratio', 0.5))
                    cx = px + int(cw * rx)
                    cy = py + int(ch * ry)
                    return max(0, min(screen_w - 1, cx)), max(0, min(screen_h - 1, cy)), cw, ch
            except Exception:
                pass
        return screen_w // 2, screen_h // 2, screen_w, screen_h

    def _get_java_pids(self):
        """返回 Minecraft Java 进程的 PID 集合（javaw.exe / java.exe），用于标题匹配失败时的回退。"""
        import subprocess
        pids = set()
        for exe in ('javaw.exe', 'java.exe'):
            try:
                out = subprocess.check_output(
                    ['tasklist', '/FI', f'IMAGENAME eq {exe}', '/FO', 'CSV', '/NH'],
                    timeout=5)
                for line in out.decode(errors='ignore').splitlines():
                    parts = [p.strip().strip('"') for p in line.split(',')]
                    if len(parts) >= 2 and parts[1].isdigit():
                        pids.add(int(parts[1]))
            except Exception:
                continue
        return pids

    def _find_game_window(self):
        """查找游戏窗口：标题关键词匹配优先，失败则按 Minecraft Java 进程名回退。"""
        keyword = self.config.get('window_title_keyword', '布吉岛')
        exact, partial = None, None
        def cb(hwnd, _):
            nonlocal exact, partial
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and re.search(keyword, title, re.IGNORECASE):
                    if title.strip().lower() == keyword.lower():
                        exact = hwnd
                    elif partial is None:
                        partial = hwnd
            return True
        try:
            win32gui.EnumWindows(cb, None)
        except Exception:
            pass
        if exact or partial:
            return exact or partial
        # 标题匹配失败：按进程名（javaw.exe / java.exe）找第一个可见窗口
        pids = self._get_java_pids()
        if not pids:
            return None
        best = [None]
        def cb2(hwnd, _):
            if best[0] is not None:
                return True
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32gui.GetWindowThreadProcessId(hwnd)
                if pid in pids and win32gui.GetWindowText(hwnd):
                    best[0] = hwnd
            return True
        try:
            win32gui.EnumWindows(cb2, None)
        except Exception:
            pass
        return best[0]

    def _ensure_window_active(self):
        try:
            hwnd = self._find_game_window()
            if hwnd: win32gui.SetForegroundWindow(hwnd); time.sleep(0.05)
        except Exception as e: self.log(f"窗口激活异常: {e}","grey")

    def _mouse_move(self, dx, dy):
        mult = self.config.get('mouse_move_multiplier', 1.0)
        dx = int(dx * mult); dy = int(dy * mult)
        hwnd = self._get_input_hwnd()
        if hwnd is not None:
            # 窗口消息模式：一次性投递客户区绝对坐标（GLFW 禁用模式按消息差值计算视角）
            try:
                l, t, r, b = win32gui.GetClientRect(hwnd)
                cw, ch = r - l, b - t
                x = cw // 2 + dx
                y = ch // 2 + dy
                ctypes.windll.user32.PostMessageW(hwnd, self.WM_MOUSEMOVE, 0, (y << 16) | (x & 0xFFFF))
                return
            except Exception:
                self._fallback_global("窗口鼠标移动失败")
        step = self.config.get('mouse_move_step',20); delay = self.config.get('mouse_move_delay',0.005)
        rem_x = abs(dx); sign_x = 1 if dx>0 else -1
        while rem_x>0:
            if self.navigation_stop_event.is_set(): return
            cur = min(step, rem_x); ctypes.windll.user32.mouse_event(0x0001, int(cur*sign_x),0,0,0)
            rem_x-=cur; time.sleep(delay)
        rem_y = abs(dy); sign_y = 1 if dy>0 else -1
        while rem_y>0:
            if self.navigation_stop_event.is_set(): return
            cur = min(step, rem_y); ctypes.windll.user32.mouse_event(0x0001,0,int(cur*sign_y),0,0)
            rem_y-=cur; time.sleep(delay)

    def _get_deg_per_pixel(self):
        override = self.config.get('deg_per_pixel_override')
        if override is not None and override!='':
            try: return float(override)
            except (ValueError, TypeError): pass
        try: dpi = float(self.config.get('dpi',1320))
        except (ValueError, TypeError): dpi = 1320.0
        try: sens = float(self.sens_var.get())
        except (ValueError, TypeError): sens = self.config.get('sensitivity',95)
        factor = self.config.get('deg_per_pixel_factor',0.15)
        return factor*(dpi/800.0)*(sens/100.0)

    def _rotate_to_angle(self, target_yaw, target_pitch, cur_yaw, cur_pitch, tolerance=None):
        if tolerance is None: tolerance = self.config.get('angle_tolerance',1.0)
        max_attempts = self.config.get('max_rotation_attempts',3)
        retry_delay = self.config.get('rotation_retry_delay',0.05)
        total_dyaw = ((target_yaw - cur_yaw + 180) % 360) - 180
        total_dpitch = target_pitch - cur_pitch
        moved_yaw = 0.0; moved_pitch = 0.0
        moved = False
        for attempt in range(max_attempts):
            if self.navigation_stop_event.is_set(): return
            dyaw = total_dyaw - moved_yaw
            dpitch = total_dpitch - moved_pitch
            if abs(dyaw) <= tolerance and abs(dpitch) <= tolerance: break
            deg_px = self._get_deg_per_pixel()
            mdx = int(dyaw / deg_px); mdy = int(dpitch / deg_px)
            if mdx == 0 and mdy == 0: break
            moved = True
            self._mouse_move(mdx, mdy)
            moved_yaw += mdx * deg_px
            moved_pitch += mdy * deg_px
            if attempt < max_attempts - 1:
                time.sleep(retry_delay)
        if not moved:
            return  # 未发生移动（角度已到位），省去验证取坐标
        # 末次验证：真实角度仍有偏差则补一次，避免累计误差
        coords = self._get_current_coords(2)
        if coords:
            dyaw = ((target_yaw - coords[3] + 180) % 360) - 180
            dpitch = target_pitch - coords[4]
            if abs(dyaw) > tolerance or abs(dpitch) > tolerance:
                deg_px = self._get_deg_per_pixel()
                self._mouse_move(int(dyaw / deg_px), int(dpitch / deg_px))

    def _wait_or_stop(self, seconds): return self.navigation_stop_event.wait(seconds)

    def _float_to_surface(self, last_ys, extra_yaw=None, timeout=None):
        if timeout is None: timeout = self.config.get('water_float_timeout',2.0)
        water_th = self.config.get('water_jump_threshold',63.0)
        pitch_angle = self.config.get('float_pitch_angle',45.0)
        check_interval = self.config.get('float_check_interval',0.3)
        coords = self._get_current_coords(2)
        if not coords: return False
        init_pitch = coords[4]; cyaw = coords[3]
        if extra_yaw is not None:
            self._rotate_to_angle(extra_yaw, init_pitch, cyaw, init_pitch, tolerance=5.0)
            cyaw = extra_yaw
        target_pitch = max(-90, init_pitch-pitch_angle)
        dpitch = target_pitch - init_pitch
        deg_px = self._get_deg_per_pixel()
        dy_px = int(dpitch/deg_px)
        if dy_px!=0: self._mouse_move(0, dy_px); self.log(f"视角上抬 {pitch_angle:.0f}°")
        else: self.log("视角无需上抬")
        self._key_down('w'); self._key_down('space')
        t0 = time.time()   # 超时从按下空格起算（前置取坐标/转向不计入）
        last_warn = 0.0
        try:
            while not self.navigation_stop_event.is_set():
                coords = self._get_current_coords(2)
                if not coords:
                    if self._wait_or_stop(check_interval): break
                    continue
                cy = coords[1]; last_ys.append(cy)
                if len(last_ys)==2 and all(y>=water_th for y in last_ys): self.log("已浮出水面"); return True
                # 只要落水就一直按空格上浮：超时仅提示不退出，直到浮出水面或停止导航
                if time.time()-t0 > timeout and time.time()-last_warn > timeout:
                    last_warn = time.time()
                    self.log("上浮耗时较长，继续尝试...","orange")
                if self._wait_or_stop(check_interval): break
            return False
        finally:
            self._key_up('space'); self._key_up('w')
            cur_coords = self._get_current_coords(2)
            if cur_coords:
                cur_pitch = cur_coords[4]; restore_dp = init_pitch - cur_pitch
                restore_dy = int(restore_dp/deg_px)
                if restore_dy!=0: self._mouse_move(0, restore_dy)
                self.log("视角已恢复")

    def _is_in_forbidden(self, cx, cz):
        return any(fz['x_min'] <= cx <= fz['x_max'] and fz['z_min'] <= cz <= fz['z_max']
                   for fz in self.forbidden_zones)

    def _find_zone_at(self, cx, cz):
        """返回包含 (cx, cz) 的禁区；不在任何禁区时返回 None。"""
        for fz in self.forbidden_zones:
            if fz['x_min'] <= cx <= fz['x_max'] and fz['z_min'] <= cz <= fz['z_max']:
                return fz
        return None

    # ===== 禁区预判绕行（线段穿过禁区时的绕角路径） =====
    def _segment_intersects_rect(self, x1, z1, x2, z2, fz):
        """线段 (x1,z1)->(x2,z2) 与矩形是否相交；相交返回进入点 (px, pz)。"""
        xmin, xmax = fz['x_min'], fz['x_max']
        zmin, zmax = fz['z_min'], fz['z_max']
        dx, dz = x2 - x1, z2 - z1
        p = [-dx, dx, -dz, dz]
        q = [x1 - xmin, xmax - x1, z1 - zmin, zmax - z1]
        t0, t1 = 0.0, 1.0
        for i in range(4):
            if p[i] == 0:
                if q[i] < 0:
                    return None
            else:
                t = q[i] / p[i]
                if p[i] < 0:
                    if t > t1: return None
                    if t > t0: t0 = t
                else:
                    if t < t0: return None
                    if t < t1: t1 = t
        if t0 > t1:
            return None
        return (x1 + t0 * dx, z1 + t0 * dz)

    def _ray_intersection(self, o1x, o1z, d1x, d1z, o2x, o2z, d2x, d2z):
        """两条射线（原点+方向）的交点；平行或交点反向时返回 None。"""
        det = d1x * d2z - d1z * d2x
        if abs(det) < 1e-9:
            return None
        t = ((o2x - o1x) * d2z - (o2z - o1z) * d2x) / det
        s = ((o2x - o1x) * d1z - (o2z - o1z) * d1x) / det
        if t < 0 or s < 0:
            return None
        return (o1x + t * d1x, o1z + t * d1z)

    def _compute_detour_points(self, fz, blocked, sx, sz, tx, tz, enter):
        """计算绕行路径点 [A(直线上离禁区N格处), B(两条射线交点)]。"""
        px, pz = enter
        dx, dz = tx - sx, tz - sz
        dist = math.hypot(dx, dz)
        if dist < 1e-6:
            return None
        ux, uz = dx / dist, dz / dist
        approach = float(self.config.get('forbidden_approach_dist', 5.0))
        ax, az = px - ux * approach, pz - uz * approach
        xmin, xmax, zmin, zmax = fz['x_min'], fz['x_max'], fz['z_min'], fz['z_max']
        # —— 选择正方向：平行于最近边，且目标点在该方向的两个象限内 ——
        nearest_h = min(abs(az - zmin), abs(zmax - az))   # 水平边（东西向）
        nearest_v = min(abs(ax - xmin), abs(xmax - ax))   # 竖直边（南北向）
        candidates = ['east', 'west'] if nearest_h <= nearest_v else ['north', 'south']
        chosen = None
        for dname in candidates:
            if dname == 'east' and tx > ax: chosen = 'east'; break
            if dname == 'west' and tx < ax: chosen = 'west'; break
            if dname == 'north' and tz < az: chosen = 'north'; break
            if dname == 'south' and tz > az: chosen = 'south'; break
        if chosen is None:
            chosen = candidates[0]
        dirs = {'east': (1.0, 0.0), 'west': (-1.0, 0.0), 'north': (0.0, -1.0), 'south': (0.0, 1.0)}
        dvx, dvz = dirs[chosen]
        # —— 选角：方向两象限内所有待避开禁区的角，取离 A 最近的一个 ——
        corners = []
        for f in blocked:
            corners.extend([
                (f['x_min'], f['z_min']), (f['x_min'], f['z_max']),
                (f['x_max'], f['z_min']), (f['x_max'], f['z_max'])
            ])
        if chosen in ('east', 'west'):
            valid = [c for c in corners if (c[0] > ax) == (chosen == 'east')]
        else:
            valid = [c for c in corners if (c[1] < az) == (chosen == 'north')]
        if not valid:
            valid = corners
        corner = min(valid, key=lambda c: (c[0] - ax) ** 2 + (c[1] - az) ** 2)
        # —— B = 禁区中心→角 的射线 与 当前方向射线 的交点 ——
        ocx, ocz = (xmin + xmax) / 2.0, (zmin + zmax) / 2.0
        bx, bz = self._ray_intersection(ocx, ocz, corner[0] - ocx, corner[1] - ocz,
                                        ax, az, dvx, dvz)
        if bx is None:
            bx, bz = corner[0] + dvx * approach, corner[1] + dvz * approach
        return [(ax, az), (bx, bz)]

    def _check_forbidden_detour(self, cx, cz, tx, tz):
        """若从 (cx,cz) 直行到 (tx,tz) 会穿过未绕过的禁区，返回 (禁区, 绕行点列表)。"""
        blocked = []
        for fz in self.forbidden_zones:
            if fz in self.bypassed_zones:
                continue
            if fz['x_min'] <= cx <= fz['x_max'] and fz['z_min'] <= cz <= fz['z_max']:
                continue  # 已在禁区内，交给旧机制兜底
            enter = self._segment_intersects_rect(cx, cz, tx, tz, fz)
            if enter is not None:
                blocked.append((fz, enter))
        if not blocked:
            return None
        # 按进入点与出发点的距离排序，先处理线段最先穿过的禁区
        blocked.sort(key=lambda item: (item[1][0] - cx) ** 2 + (item[1][1] - cz) ** 2)
        fz, enter = blocked[0]
        pts = self._compute_detour_points(fz, [b[0] for b in blocked], cx, cz, tx, tz, enter)
        if not pts:
            return None
        return (fz, pts)

    def _execute_stuck_evasion(self):
        back_time = self.config.get('evasion_back_time',1.0)
        short_max = self.config.get('evasion_short_max',3.0)
        long_min = self.config.get('evasion_long_min',3.0); long_max = self.config.get('evasion_long_max',5.0)
        short_prob = self.config.get('evasion_short_probability',0.8)
        cycle = self.config.get('evasion_cycle_interval',3)
        self.log("卡点检测，执行避障：后退 + 随机侧移","orange")
        self._key_down('s')
        try:
            if self._wait_or_stop(back_time): return
        finally: self._key_up('s')
        if self._wait_or_stop(0.3): return
        choices = ['a','d']
        if self.last_strafe_key in choices: choices.remove(self.last_strafe_key)
        move_key = random.choice(choices)
        self.evasion_count += 1
        if self.evasion_count%cycle==0: strafe_time = random.uniform(long_min, long_max); self.log(f"强制长侧移 (每{cycle}次)","grey")
        else:
            if random.random()<short_prob: strafe_time = random.uniform(0.0, short_max)
            else: strafe_time = random.uniform(long_min, long_max)
        self.log(f"侧移方向: {move_key}，时长: {strafe_time:.2f}秒","grey")
        self._key_down(move_key)
        try:
            if self._wait_or_stop(strafe_time): return
        finally: self._key_up(move_key)
        self.last_strafe_key = move_key

    def _exit_forbidden_zone(self, cx, cz, depth=0):
        max_depth = self.config.get('forbidden_max_depth',5); max_steps = self.config.get('forbidden_max_steps',50)
        step_dur = self.config.get('forbidden_step_duration',0.2); step_pause = self.config.get('forbidden_step_pause',0.1)
        extra_time = self.config.get('forbidden_exit_extra_time',0.3)
        if depth > max_depth: self.log("绕行递归过深，放弃","red"); return False
        self._key_up('w')
        fz = self._find_zone_at(cx, cz)
        if not fz:
            self.log("当前位置不在任何禁区，无需绕行","orange"); return True
        distances = {'east':fz['x_max']-cx,'west':cx-fz['x_min'],'south':fz['z_max']-cz,'north':cz-fz['z_min']}
        dir_key = min(distances, key=lambda k: abs(distances[k]))
        self.log(f"离开禁区方向: {dir_key}","blue")
        if dir_key=='east': target_yaw=-90.0
        elif dir_key=='west': target_yaw=90.0
        elif dir_key=='south': target_yaw=0.0
        else: target_yaw=180.0
        coords = self._get_current_coords(2)
        if coords: cyaw,cpitch = coords[3],coords[4]; self._rotate_to_angle(target_yaw,cpitch,cyaw,cpitch, tolerance=1.0)
        last_pos=None; stuck_count=0
        for _ in range(max_steps):
            if self.navigation_stop_event.is_set(): return False
            coords = self._get_current_coords(2)
            if not coords:
                if self._wait_or_stop(0.3): break
                continue
            cx,cz = coords[0],coords[2]
            if not self._is_in_forbidden(cx,cz):
                self._key_down('w')
                try:
                    if self._wait_or_stop(extra_time): return False
                finally: self._key_up('w')
                self.log("已离开禁止区域"); return True
            if last_pos:
                if math.hypot(cx-last_pos[0],cz-last_pos[1]) < self.config.get('stuck_threshold',0.15): stuck_count+=1
                else: stuck_count=0
            last_pos = (cx,cz)
            if stuck_count >= self.config.get('stuck_trigger_count',3):
                self._execute_stuck_evasion(); stuck_count=0; return self._exit_forbidden_zone(cx,cz,depth+1)
            self._key_down('w')
            try:
                if self._wait_or_stop(step_dur): return False
            finally: self._key_up('w')
            if self._wait_or_stop(step_pause): return False
        self.log("离开禁区超时","red"); return False

    # ===== 射线检测 =====
    def _get_view_vector(self, yaw, pitch):
        rad_yaw = math.radians(yaw); rad_pitch = math.radians(pitch)
        cos_pitch = math.cos(rad_pitch)
        dx = -math.sin(rad_yaw)*cos_pitch; dy = math.sin(rad_pitch); dz = -math.cos(rad_yaw)*cos_pitch
        return dx,dy,dz

    def _ray_intersects_aabb(self, ox,oy,oz, dx,dy,dz, minx,miny,minz, maxx,maxy,maxz):
        epsilon=1e-7
        def check(lo,hi,orig,dir_val):
            if abs(dir_val)<epsilon: return (False,None,None) if orig<lo or orig>hi else (True,-float('inf'),float('inf'))
            t1=(lo-orig)/dir_val; t2=(hi-orig)/dir_val
            if t1>t2: t1,t2=t2,t1
            return True,t1,t2
        ok,t1,t2 = check(minx,maxx,ox,dx)
        if not ok: return False
        tmin,tmax = t1,t2
        ok,t1,t2 = check(miny,maxy,oy,dy)
        if not ok: return False
        tmin = max(tmin, t1); tmax = min(tmax, t2)
        ok,t1,t2 = check(minz,maxz,oz,dz)
        if not ok: return False
        tmin = max(tmin, t1); tmax = min(tmax, t2)
        return tmax >= max(0.0, tmin)

    def _ray_hit_water_block(self, cx,cy,cz, yaw,pitch, wx,wy,wz):
        eye_y = cy + self.config.get('eye_height',1.62)
        dx,dy,dz = self._get_view_vector(yaw,pitch)
        bx = math.floor(wx); by = math.floor(wy); bz = math.floor(wz)
        return self._ray_intersects_aabb(cx,eye_y,cz, dx,dy,dz, bx,by,bz, bx+1.0,by+1.0,bz+1.0)

    def _align_to_water_block(self, target):
        wx,wy,wz = target['water_x'], target['water_y'], target['water_z']
        max_iter = self.config.get('align_water_max_iter',6); min_step = self.config.get('ray_align_min_step',2.0)
        delay = self.config.get('align_water_delay',0.3)
        coords = self._get_current_coords(2)
        if not coords:
            self.log("对准水域方块失败","red"); return False
        cx,cy,cz, cur_yaw,cur_pitch = coords
        if self._ray_hit_water_block(cx,cy,cz, cur_yaw,cur_pitch, wx,wy,wz):
            self.log("准心已对准水域方块","green"); return True
        # 首次取坐标后，用像素累计推算视角微调（玩家静止，坐标不变），末次再验证
        for i in range(max_iter):
            if self.navigation_stop_event.is_set(): return False
            tyaw,tpitch = self._calc_target_angles(cx,cy,cz, wx,wy,wz)
            dyaw = ((tyaw-cur_yaw+180)%360)-180; dpitch = tpitch-cur_pitch
            angle_dist = math.hypot(dyaw,dpitch)
            if angle_dist < 0.5:
                self.log("准心已对准水域方块","green"); return True
            if angle_dist < min_step:
                if angle_dist<0.1: move_yaw, move_pitch = (min_step if dyaw>=0 else -min_step), (min_step if dpitch>=0 else -min_step)
                else: move_yaw, move_pitch = (dyaw/angle_dist)*min_step, (dpitch/angle_dist)*min_step
            else: move_yaw, move_pitch = dyaw, dpitch
            deg_px = self._get_deg_per_pixel()
            mdx = int(move_yaw/deg_px); mdy = int(move_pitch/deg_px)
            if mdx == 0 and mdy == 0: break
            self._mouse_move(mdx, mdy)
            cur_yaw += mdx * deg_px
            cur_pitch += mdy * deg_px
            if self._wait_or_stop(delay): return False
        # 末次验证：用真实坐标与视角确认
        coords = self._get_current_coords(2)
        if coords:
            if self._ray_hit_water_block(coords[0], coords[1], coords[2], coords[3], coords[4], wx,wy,wz):
                self.log("准心已对准水域方块","green"); return True
        self.log("对准水域方块失败","red"); return False

    # ===== T 循环 =====
    def _t_loop(self, target):
        tx,ty,tz = target['x'],target['y'],target['z']
        water_th = self.config.get('water_jump_threshold',63.0); per_check = self.config.get('per_check',1.0)
        stuck_threshold = self.config.get('stuck_threshold',0.15); stuck_trigger = self.config.get('stuck_trigger_count',3)
        t_to_i = self.config.get('t_to_i_distance',15.0); water_tol = self.config.get('water_turn_tolerance',5.0)
        last_ys = deque(maxlen=2); w_down=False; stuck_count=0; last_stuck_coord=None
        try:
            while not self.navigation_stop_event.is_set():
                coords = self._get_current_coords(2)
                if not coords:
                    if self._wait_or_stop(0.5): break
                    continue
                cx,cy,cz, cyaw,cpitch = coords; last_ys.append(cy)
                if self._is_in_forbidden(cx,cz):
                    self.log("(T) 进入禁止区域，绕行","orange")
                    if w_down: self._key_up('w'); w_down=False
                    if not self._exit_forbidden_zone(cx,cz): return False
                    else: return 'retry'
                hor_dist = math.hypot(tx-cx, tz-cz)
                self.log(f"距钓点 {hor_dist:.1f} 格")
                if hor_dist < t_to_i:
                    self.log("进入精确调整 (I 循环)")
                    if w_down: self._key_up('w')
                    return True
                if cy < water_th:
                    self.log("T循环落水，上浮")
                    if w_down: self._key_up('w'); w_down=False
                    tyaw,_ = self._calc_target_angles(cx,cy,cz, tx,ty,tz)
                    self._rotate_to_angle(tyaw,cpitch,cyaw,cpitch, tolerance=water_tol)
                    if not self._float_to_surface(last_ys, extra_yaw=tyaw):
                        self.log("上浮超时，重新T循环","orange"); return 'retry'
                    stuck_count=0; last_stuck_coord=None; continue
                if last_stuck_coord is not None:
                    d = math.hypot(cx-last_stuck_coord[0], cz-last_stuck_coord[1])
                    if d < stuck_threshold: stuck_count+=1; self.log(f"T卡死计数: {stuck_count}/{stuck_trigger}","grey")
                    else: stuck_count=0
                last_stuck_coord = (cx,cz)
                if stuck_count >= stuck_trigger:
                    self.log("连续坐标不变，触发避障","orange")
                    if w_down: self._key_up('w'); w_down=False
                    self._execute_stuck_evasion(); stuck_count=0; last_stuck_coord=None; return 'retry'
                tyaw,tpitch = self._calc_target_angles(cx,cy,cz, tx,ty,tz)
                if w_down: self._key_up('w'); w_down=False
                # 远距宽松容差：距离大时允许角度偏差，减少转向校正次数
                loose = self.config.get('t_loop_loose_dist', 30.0)
                tol = self.config.get('t_loop_angle_tolerance', 5.0) if hor_dist > loose else None
                self._rotate_to_angle(tyaw,tpitch,cyaw,cpitch, tolerance=tol)
                if not w_down: self._key_down('w'); w_down=True
                if self._wait_or_stop(per_check): break
            return False
        finally:
            if w_down: self._key_up('w')

    # ===== I 循环 =====
    def _i_loop(self, target):
        tx,ty,tz = target['x'],target['y'],target['z']
        speed = self.config.get('player_speed',5.625); arrival_dist = self.config.get('arrival_dist',1.5)
        water_th = self.config.get('water_jump_threshold',63.0); max_iter = self.config.get('i_loop_max_iter',10)
        walk_factor = self.config.get('walk_time_factor',0.9); stuck_threshold = self.config.get('stuck_threshold',0.15)
        stuck_trigger = self.config.get('stuck_trigger_count',3); min_walk = self.config.get('i_loop_min_walk_time',0.05)
        max_walk = self.config.get('i_loop_max_walk_time',1.0); post_walk = self.config.get('i_loop_post_walk_delay',0.2)
        iter_count=0; last_ys=deque(maxlen=2); water_fail_count=0; stuck_count=0; last_stuck_coord=None
        while not self.navigation_stop_event.is_set() and iter_count < max_iter:
            coords = self._get_current_coords(2)
            if not coords:
                if self._wait_or_stop(0.3): break
                continue
            cx,cy,cz, cyaw,cpitch = coords
            if self._is_in_forbidden(cx,cz):
                self.log("(I) 进入禁止区域，绕行","orange")
                if not self._exit_forbidden_zone(cx,cz): return False
                else: return 'retry'
            if cy < water_th:
                self.log("I循环落水，转向钓点上浮...")
                tyaw,_ = self._calc_target_angles(cx,cy,cz, tx,ty,tz)
                self._rotate_to_angle(tyaw,cpitch,cyaw,cpitch, tolerance=self.config.get('water_turn_tolerance',5.0))
                if not self._float_to_surface(last_ys, extra_yaw=tyaw):
                    water_fail_count+=1
                    if water_fail_count >= self.config.get('max_water_fails',3):
                        self.log("连续上浮失败超限，放弃该钓点","red"); return False
                    return 'retry'
                water_fail_count=0; stuck_count=0; last_stuck_coord=None; continue
            water_fail_count=0
            hor_dist = math.hypot(tx-cx, tz-cz)
            self.log(f"距钓点 {hor_dist:.1f} 格")
            if hor_dist <= arrival_dist and cy>=water_th: break
            if last_stuck_coord is not None:
                d = math.hypot(cx-last_stuck_coord[0], cz-last_stuck_coord[1])
                if d < stuck_threshold: stuck_count+=1; self.log(f"I卡死计数: {stuck_count}/{stuck_trigger}","grey")
                else: stuck_count=0
            last_stuck_coord = (cx,cz)
            if stuck_count >= stuck_trigger:
                self.log("I循环卡死，触发避障重启","orange")
                self._execute_stuck_evasion(); stuck_count=0; last_stuck_coord=None; return 'retry'
            tyaw,tpitch = self._calc_target_angles(cx,cy,cz, tx,ty,tz)
            self._rotate_to_angle(tyaw,tpitch,cyaw,cpitch)
            walk_time = (hor_dist/speed)*walk_factor
            # 步长自适应：距离远时允许更长单步行走，减少取坐标次数
            adaptive_max = max(max_walk, min(hor_dist/speed*self.config.get('i_loop_adaptive_ratio',0.6),
                                             self.config.get('i_loop_adaptive_max_walk',2.0)))
            walk_time = max(min_walk, min(walk_time, adaptive_max))
            self._key_down('w')
            try:
                if self._wait_or_stop(walk_time): return False
            finally: self._key_up('w')
            if self._wait_or_stop(post_walk): return False
            iter_count+=1
        is_via = self._is_via_point(target)
        if is_via:
            self.log("中转站无需对准水域，直接到达","blue")
            pitch_down = self.config.get('pitch_down_after_arrival',0.0)
            if pitch_down:
                self.log(f"额外下压俯仰角 {pitch_down:.1f}°")
                coords = self._get_current_coords(2)
                if coords:
                    cx,cy,cz,cyaw,cpitch = coords
                    new_pitch = max(-90.0, min(90.0, cpitch+pitch_down))
                    self._rotate_to_angle(cyaw,new_pitch,cyaw,cpitch, tolerance=0.5)
            return True
        else:
            if not self._align_to_water_block(target):
                self.log("对准水域失败，但将继续抛竿钓鱼","orange")
            pitch_down = self.config.get('pitch_down_after_arrival',0.0)
            if pitch_down:
                self.log(f"额外下压俯仰角 {pitch_down:.1f}°")
                coords = self._get_current_coords(2)
                if coords:
                    cx,cy,cz,cyaw,cpitch = coords
                    new_pitch = max(-90.0, min(90.0, cpitch+pitch_down))
                    self._rotate_to_angle(cyaw,new_pitch,cyaw,cpitch, tolerance=0.5)
            return True

    def _navigate_to_target(self, target):
        # —— 第一段：预判直行是否穿过未绕过的禁区，穿过则先执行绕角 ——
        while not self.navigation_stop_event.is_set():
            coords = self._get_current_coords(2)
            if not coords:
                if self._wait_or_stop(0.5): return False
                continue
            cx, cy, cz = coords[0], coords[1], coords[2]
            detour = self._check_forbidden_detour(cx, cz, target['x'], target['z'])
            if detour is None:
                break
            fz, pts = detour
            self.log("直行路径穿过禁区，执行绕角绕行","orange")
            for px, pz in pts:
                if self.navigation_stop_event.is_set(): return False
                if not self._navigate_to_target({'x': px, 'y': cy, 'z': pz}):
                    return False
            self.bypassed_zones.append(fz)
            self.log("该禁区已绕过，继续寻路","green")
        # —— 第二段：原有 T/I 循环 ——
        self.obstacle_count = 0
        while not self.navigation_stop_event.is_set():
            t_result = self._t_loop(target)
            if t_result == True:
                self._update_status("导航中（I循环）")
                i_result = self._i_loop(target)
                if i_result == 'retry': continue
                if i_result: return True
                else: return False
            elif t_result == 'retry': continue
            else: return False
        return False

    def _is_via_spot(self, target):
        threshold = self.config.get('via_spot_threshold',0.5)
        tx,ty,tz = target['x'],target['y'],target['z']
        for sx,sy,sz in self.special_spots:
            if math.hypot(tx-sx, ty-sy, tz-sz) < threshold: return True
        return False

    def _is_via_point(self, target):
        threshold = self.config.get('via_spot_threshold', 0.5)
        for st in self.via_stations:
            if all(abs(target[k]-st[k]) < threshold for k in ('x','y','z')): return True
        return False

    def _build_via_path(self, cx, cz):
        """根据地图 via_rule 生成中转站 id 列表（不包含目标）。"""
        rule = self.current_map_data.get('via_rule') if self.current_map_data else None
        if not rule:
            return []
        mode = rule.get('mode')
        if mode == 'fixed':
            return list(rule.get('path', []))
        if mode == 'conditional':
            cond = rule.get('condition') or {}
            ok = True
            if 'x_max' in cond and not (cx < cond['x_max']): ok = False
            if 'x_min' in cond and not (cx > cond['x_min']): ok = False
            if 'z_max' in cond and not (cz < cond['z_max']): ok = False
            if 'z_min' in cond and not (cz > cond['z_min']): ok = False
            return list(rule.get('path_when_true', []) if ok else rule.get('path_when_false', []))
        if mode == 'decision':
            spots = rule.get('decision_spots') or []
            best_id, best_d = None, float('inf')
            for sp in spots:
                d = math.hypot(cx - sp['x'], cz - sp['z'])
                if d < best_d:
                    best_d = d; best_id = sp.get('station')
            if best_id:
                return [best_id]
            return list(rule.get('fallback_path', []))
        return list(rule.get('fallback_path', []))

    def _navigate_to_spot_v2(self, target):
        if self.navigation_stop_event.is_set(): return False
        self._ensure_window_active(); self.navigation_stop_event.clear()
        self.bypassed_zones.clear()
        self.log(f"目标钓点: ({target['x']:.2f}, {target['y']:.2f}, {target['z']:.2f})","grey")
        if self._is_via_spot(target):
            self.log("【特殊钓点】将启用中转路径")
            coords = self._get_current_coords(2)
            if not coords:
                self.log("无法获取当前坐标，取消中转","red"); return self._navigate_to_target(target)
            cx,cy,cz,_,_ = coords
            self.log(f"当前位置: ({cx:.1f}, {cy:.1f}, {cz:.1f})","grey")
            stations = {st['id']: st for st in self.via_stations if st.get('id')}
            path_points = []
            for sid in self._build_via_path(cx, cz):
                st = stations.get(sid)
                if st is None:
                    self.log(f"中转站 {sid} 未定义，跳过该段","orange")
                    continue
                path_points.append((sid, st))
            path_points.append(('目标', target))
            path_str = " → ".join(f"{name}({pt['x']:.1f},{pt['y']:.1f},{pt['z']:.1f})" for name,pt in path_points)
            self.log(f"路径规划: {path_str}","blue")
            for name,pt in path_points[:-1]:
                if self.navigation_stop_event.is_set(): return False
                if not self._navigate_to_target(pt):
                    self.log(f"前往{name}失败","red"); return False
                self.log(f"已到达中转站{name}","green")
            return self._navigate_to_target(target)
        else:
            return self._navigate_to_target(target)

    def _relocate_and_restart(self):
        self.navigation_stop_event.clear(); self._update_status("换池中...")
        try:
            retries = self.config.get('relocate_coord_retries',6)
            coords = self._get_current_coords(retries)
            if not coords:
                self.log("无法获取坐标，放弃换池","red"); self._update_status("就绪"); return
            self.log(f"当前坐标: {coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f}","grey")
            excl_dist = self.config.get('exclude_spot_distance',5.0)
            with self.lock:
                nearest,min_d = None,float('inf')
                for sp in self.available_spots:
                    d = math.hypot(sp['x']-coords[0], sp['y']-coords[1], sp['z']-coords[2])
                    if d<min_d: min_d=d; nearest=sp
                if nearest and min_d<excl_dist:
                    self.available_spots.remove(nearest); self.exhausted_spots.append(nearest)
                    self.log(f"排除枯竭点 ({nearest['x']:.1f}, {nearest['y']:.1f}, {nearest['z']:.1f})","grey")
                if not self.available_spots:
                    self.log("重置钓点列表","green"); self.available_spots = list(self.fishing_spots); self.exhausted_spots.clear()
            while not self.navigation_stop_event.is_set():
                target = self._find_nearest_spot(coords)
                if not target: self.log("无可用钓点","red"); self._update_status("就绪"); return
                self.log(f"尝试前往: ({target['x']:.1f}, {target['y']:.1f}, {target['z']:.1f})","blue")
                if self.navigation_stop_event.is_set(): self.log("用户中断，停止换池","purple"); break
                success = self._navigate_to_spot_v2(target)
                if success:
                    with self.lock:
                        if target in self.available_spots:
                            self.available_spots.remove(target); self.log(f"标记完成，剩余: {len(self.available_spots)}","grey")
                    break
                else:
                    self.log("导航失败，移除该钓点","red")
                    with self.lock:
                        if target in self.available_spots: self.available_spots.remove(target); self.exhausted_spots.append(target)
            if self.navigation_stop_event.is_set(): self.log("换池已被用户终止","purple"); self._update_status("就绪"); return
            time.sleep(self.config.get('relocate_finish_delay',0.5))
            self.simulate_right_click()
            if self.multiple_cast_enabled.get():
                self.log("换池后额外抛竿：额外右键两次","grey")
                time.sleep(self.config.get('multi_cast_delay_1',0.5)); self.simulate_right_click()
                time.sleep(self.config.get('multi_cast_delay_2',0.3)); self.simulate_right_click()
            with self.lock:
                self.skip_initial_throw = True
            self.start_fishing(); self.log("换池完成，已重新开始钓鱼","green")
        except Exception as e:
            self.log(f"换池错误: {e}","red"); self._update_status("就绪")

    def hex_to_rgb(self, hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2],16) for i in (0,2,4))

    def _hourly_reset_loop(self):
        while True:
            time.sleep(60)
            try:
                now = time.localtime()
                if now.tm_hour != self.last_hour:
                    self.last_hour = now.tm_hour
                    self.log(f"整点 {now.tm_hour}:00 重置钓点状态","purple")
                    with self.lock:
                        self.available_spots = list(self.fishing_spots); self.exhausted_spots.clear()
                    self.depleted_alerted = False
            except Exception as e: self.log(f"整点重置异常: {e}","red")

    def _load_map(self, map_name):
        """加载地图数据并更新全部相关状态（地图切换与初始化共用）。"""
        new_map = load_map_data(MAP_DATA_PATH, map_name)
        self.current_map_data = new_map
        self.fishing_spots = new_map.get('fishing_spots', [])
        self.water_candidates = new_map.get('water_candidates', [])
        enhance_fishing_spots(self.fishing_spots, self.water_candidates)
        self.via_stations = new_map.get('via_stations') or []
        self.special_spots = [tuple(s) for s in (new_map.get('special_spots') or [])]
        self.via_rule = new_map.get('via_rule')
        self.forbidden_zones = new_map.get('forbidden_zones') or []
        self.has_forbidden_zone = bool(self.forbidden_zones)
        self.bypassed_zones = []
        with self.lock:
            self.available_spots = list(self.fishing_spots)
            self.exhausted_spots.clear()
        # 每张地图有自己的落水判定高度（图1=63.0，图2=120.0），切换地图时同步
        wjt = new_map.get('water_jump_threshold')
        if wjt is not None:
            with self.config_lock:
                self.config['water_jump_threshold'] = wjt
            var = getattr(self, 'config_entries', {}).get('water_jump_threshold')
            if var is not None:
                var.set(str(wjt))
            self.log(f"落水判定高度已更新为 {wjt}", "grey")
        self.depleted_alerted = False
        return new_map

    def _on_map_select(self, map_name):
        if map_name=='map1':
            self.map2_var.set(False)
        else:
            self.map1_var.set(False)
        with self.config_lock:
            cur_map = self.config.get('current_map')
        if cur_map == map_name: return
        self.log(f"切换地图至 {map_name}","blue")
        self.stop_fishing(); self.navigation_stop_event.set()
        with self.config_lock:
            self.config['current_map'] = map_name
        self._load_map(map_name)
        self.log("地图已切换，钓点列表已更新","green")
        with self.m_lock:
            has_m = self.M is not None
        if has_m:
            self.b_btn.set_enabled(True)
        self._save_config_async()

    def on_closing(self):
        self._closing = True
        if self.mouse_listener:
            try: self.mouse_listener.stop()
            except Exception: pass  # 关闭时忽略监听器停止异常
        if self.keyboard_listener:
            try: self.keyboard_listener.stop()
            except Exception: pass  # 关闭时忽略监听器停止异常
        self.stop_fishing()
        self.detect_stop_event.set()
        self.navigation_stop_event.set()
        try:
            with self.config_lock:
                self.config['auto_throw_enabled'] = self.auto_throw_enabled.get()
                self.config['fish_depleted_alert_enabled'] = self.fish_depleted_alert_enabled.get()
                self.config['auto_relocate_enabled'] = self.auto_relocate_enabled.get()
                self.config['multiple_cast'] = self.multiple_cast_enabled.get()
                self.config['fn_lock_enabled'] = self.fn_lock_on_var.get()
                try: self.config['sensitivity'] = int(self.sens_var.get())
                except (ValueError, TypeError): pass
                try: self.config['mouse_move_multiplier'] = float(self.multiplier_var.get())
                except (ValueError, TypeError): pass
                val = self.deg_override_var.get().strip()
                try:
                    self.config['deg_per_pixel_override'] = float(val) if val else None
                except (ValueError, TypeError):
                    self.config['deg_per_pixel_override'] = None
                self.config['current_map'] = 'map1' if self.map1_var.get() else 'map2'
            with self._save_lock:
                save_config_internal(self.config, CONFIG_PATH)
        except Exception as e:
            print(f"[关闭] 保存配置失败: {e}")
        try:
            self.root.destroy()
        except Exception:
            pass  # 窗口可能已销毁

    def run(self): self.root.mainloop()

if __name__ == "__main__":
    app = AutoFishingApp(CONFIG)
    app.run()