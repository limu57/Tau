"""
Tau 1.3.2 — Minecraft 自动钓鱼脚本 
by limu57 with deepseek
"""
import tkinter as tk
from tkinter import ttk, filedialog
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
    'max_lines':8,'polling_rate':250,'px_color':'#fcfcfc','px_height':200,'px_width':325,'crosshair_x_ratio':0.5,'crosshair_y_ratio':0.5,'detect_center_offset_x_ratio':0.0,'detect_center_offset_y_ratio':-0.1111,'color_tolerance':20,'detection_tolerance':5,'detection_timeout':30.0,'no_fish_timeout':40.0,'base_no_fish_timeout':40.0,'total_catches':0,'confirmation_time':0.5,'reel_wait_min':4.0,'reel_wait_max':6.0,'cast_delay_min':0.1,'cast_delay_max':0.4,'dpi':1321,'sensitivity':95,'arrival_dist':1.5,'angle_tolerance':1.0,'obstacle_time':3,'polling_jitter':50,'mouse_jitter':2,'auto_throw_enabled':True,'fish_depleted_alert_enabled':True,'auto_relocate_enabled':True,'multiple_cast':True,'water_jump_threshold':124.0,'fn_lock_enabled':False,'per_check':1.0,'player_speed':5.625,'i_loop_max_iter':10,'i_loop_adaptive_max_walk':2.0,'i_loop_adaptive_ratio':0.6,'verbose_navigation':False,'log_level':'INFO','deg_per_pixel_override':None,'grab_from_window':False,'detect_start_delay':5.0,'relocate_timeout_enabled':True,'relocate_timeout':300.0,'window_title_keyword':'布吉岛','log_watch_enabled':True,'log_watch_path':'','log_watch_interval':0.3,'log_relocate_enabled':True,'log_watch_rules':[{'text':'[CHAT] 您取得了 通行证-沉船遗迹 !','action':'pass_card'},{'text':'[CHAT] 不行! 这个钓点已经枯竭','action':'relocate'}],'pass_bg_enabled':True,'pass_bg_color':'#8b5cf6','min_distance_to_cast':5.0,'detection_poll_interval':0.2,'max_coord_retries':5,'t_loop_restart_interval':10.0,'t_loop_loose_dist':30.0,'t_loop_angle_tolerance':5.0,'walk_time_factor':0.9,'water_float_timeout':2.0,'max_water_fails':3,'pitch_down_after_arrival':0.0,'stuck_threshold':0.15,'manual_cast_timeout':31.0,'auto_cast_wait':2.0,'initial_catch_cast_delay':5.0,'copy_coord_delay':0.5,'coord_retry_delay_1':0.3,'coord_retry_delay_2':0.2,'mouse_move_step':20,'mouse_move_delay':0.005,'mouse_move_multiplier':1.0,'eye_height':1.62,'deg_per_pixel_factor':0.15,'max_rotation_attempts':5,'rotation_retry_delay':0.05,'t_to_i_distance':15.0,'water_turn_tolerance':5.0,'stuck_trigger_count':2,'i_loop_min_walk_time':0.05,'i_loop_max_walk_time':1.0,'i_loop_post_walk_delay':0.2,'align_water_max_iter':6,'align_water_delay':0.3,'cast_aim_lift':0.15,'cast_aim_lift_start':6.0,'cast_aim_lift_height':0.1,'shore_climb_time':0.3,'float_pitch_angle':45.0,'float_check_interval':0.3,'evasion_back_time':1.0,'evasion_short_max':3.0,'evasion_long_min':3.0,'evasion_long_max':5.0,'evasion_short_probability':0.8,'evasion_cycle_interval':3,'forbidden_max_depth':5,'forbidden_max_steps':50,'forbidden_step_duration':0.2,'forbidden_step_pause':0.1,'forbidden_approach_dist':5.0,'forbidden_exit_extra_time':0.3,'relocate_coord_retries':6,'exclude_spot_distance':5.0,'relocate_finish_delay':0.5,'multi_cast_delay_1':0.5,'multi_cast_delay_2':0.3,'via_spot_threshold':0.5,'click_pre_delay':0.02,'click_post_delay':0.05,'ray_align_min_step':2.0,'ui_window_width':360,'ui_window_height':900,'ui_minsize_width':360,'ui_minsize_height':700,'current_map':'map1','input_mode':'window','key_stop_navigation':'b+m','key_toggle_fishing':'b+n','grab_sample_radius':2,'grab_fail_wait':0.5,'confirm_check_interval':0.1,'prepare_cast_delay':0.1,'auto_cast_post_wait':2.0,'poll_min_interval':0.05,'post_click_interval':0.03,'combo_key_interval':0.02,'coord_abs_limit':100000,'tasklist_timeout':5,'window_activate_delay':0.05,'align_success_angle':0.5,'forbidden_poll_wait':0.3,'coord_fail_wait':0.5,'coord_fail_wait_i':0.3,'log_retention_seconds':600,'log_clean_interval_ms':300000,'hourly_check_interval':60,'pixel_err_log_interval':5.0,'manual_cast_poll_wait':1.0,'chain_near_threshold':2.0
}

# ================= 默认地图数据 =================
DEFAULT_MAP_DATA = {'maps': {'map1': {'name': '一图(绿林浅滩)',
                   'water_jump_threshold': 124.0,
                   'sea_levels': [{'id': 'L0', 'y': 124.0, 'rects': []},
                                  {'id': 'L1',
                                   'y': 129.0,
                                   'rects': [[-263.3, -121.7, -39.7, -24.3],
                                             [-264.76, -26.55, -96.48, 184.7]]}],
                   'forbidden_zones': [],
                   'via_stations': [],
                   'special_spots': [[-13.94, 125.0, 161.77],
                                     [13.58, 124.0, 182.14],
                                     [31.97, 124.0, 188.03],
                                     [48.97, 124.0, 197.88],
                                     [54.03, 124.0, 213.39],
                                     [44.38, 124.0, 238.18],
                                     [27.99, 125.0, 247.48]],
                   'via_rule': {'mode': 'chain',
                                'chain': [{'id': 'A1', 'x': -13.94, 'y': 125.0, 'z': 161.77},
                                          {'id': 'A2', 'x': 13.58, 'y': 124.0, 'z': 182.14},
                                          {'id': 'A3', 'x': 31.97, 'y': 124.0, 'z': 188.03},
                                          {'id': 'A4', 'x': 48.97, 'y': 124.0, 'z': 197.88},
                                          {'id': 'A5', 'x': 54.03, 'y': 124.0, 'z': 213.39},
                                          {'id': 'A6', 'x': 44.38, 'y': 124.0, 'z': 238.18},
                                          {'id': 'A7', 'x': 27.99, 'y': 125.0, 'z': 247.48}],
                                'class': 'chain'},
                   'fishing_spots': [{'x': -59.81, 'y': 124.0, 'z': 10.27},
                                     {'x': -60.99, 'y': 124.0, 'z': 26.0},
                                     {'x': -61.21, 'y': 124.0, 'z': 44.77},
                                     {'x': -60.47, 'y': 124.0, 'z': 64.12},
                                     {'x': -59.13, 'y': 124.0, 'z': 98.61},
                                     {'x': -43.56, 'y': 124.0, 'z': 128.2},
                                     {'x': -23.24, 'y': 124.0, 'z': 152.08},
                                     {'x': -221.3, 'y': 129.0, 'z': 42.1},
                                     {'x': -207.46, 'y': 129.0, 'z': 48.01},
                                     {'x': -186.81, 'y': 129.0, 'z': 48.72},
                                     {'x': -171.16, 'y': 131.0, 'z': 53.74},
                                     {'x': -137.99, 'y': 129.0, 'z': 65.32},
                                     {'x': -121.05, 'y': 129.0, 'z': 67.67},
                                     {'x': -192.25, 'y': 131.0, 'z': 76.74},
                                     {'x': -218.22, 'y': 133.0, 'z': 95.94},
                                     {'x': -253.07, 'y': 133.0, 'z': 78.77},
                                     {'x': -251.09, 'y': 130.0, 'z': 46.04},
                                     {'x': -258.01, 'y': 131.0, 'z': 32.97},
                                     {'x': -230.07, 'y': 130.0, 'z': -54.16},
                                     {'x': -230.98, 'y': 130.0, 'z': -27.0},
                                     {'x': -227.77, 'y': 130.0, 'z': -17.18},
                                     {'x': -223.93, 'y': 131.0, 'z': -1.2},
                                     {'x': -201.97, 'y': 131.0, 'z': 13.3},
                                     {'x': -194.0, 'y': 131.0, 'z': 29.03},
                                     {'x': -221.93, 'y': 131.0, 'z': -71.17},
                                     {'x': -210.67, 'y': 129.0, 'z': -87.07},
                                     {'x': -190.73, 'y': 129.0, 'z': -104.83},
                                     {'x': -171.8, 'y': 130.0, 'z': -103.02},
                                     {'x': -157.97, 'y': 129.0, 'z': -90.92},
                                     {'x': -146.74, 'y': 129.0, 'z': -83.73},
                                     {'x': -151.94, 'y': 130.0, 'z': -62.3},
                                     {'x': -165.5, 'y': 129.0, 'z': -64.99},
                                     {'x': -191.14, 'y': 129.0, 'z': -63.87},
                                     {'x': -204.27, 'y': 131.0, 'z': -54.7},
                                     {'x': -7.05, 'y': 124.0, 'z': -96.3},
                                     {'x': -10.21, 'y': 124.0, 'z': -74.1},
                                     {'x': -29.76, 'y': 126.0, 'z': -55.32},
                                     {'x': -54.26, 'y': 128.0, 'z': -55.95},
                                     {'x': -65.79, 'y': 129.0, 'z': -62.14},
                                     {'x': -82.34, 'y': 130.0, 'z': -57.3},
                                     {'x': -104.63, 'y': 130.0, 'z': -56.26},
                                     {'x': -115.93, 'y': 132.0, 'z': -56.5},
                                     {'x': -128.05, 'y': 130.0, 'z': -77.01},
                                     {'x': -13.94, 'y': 125.0, 'z': 161.77},
                                     {'x': 13.58, 'y': 124.0, 'z': 182.14},
                                     {'x': 31.97, 'y': 124.0, 'z': 188.03},
                                     {'x': 48.97, 'y': 124.0, 'z': 197.88},
                                     {'x': 54.03, 'y': 124.0, 'z': 213.39},
                                     {'x': 44.38, 'y': 124.0, 'z': 238.18},
                                     {'x': 27.99, 'y': 125.0, 'z': 247.48}],
                   'water_candidates': [{'water_x': -54.46, 'water_y': 124.0, 'water_z': 23.99},
                                        {'water_x': -53.55, 'water_y': 124.0, 'water_z': 7.76},
                                        {'water_x': -54.71, 'water_y': 124.0, 'water_z': 41.63},
                                        {'water_x': -52.41, 'water_y': 124.0, 'water_z': 66.67},
                                        {'water_x': -51.45, 'water_y': 124.0, 'water_z': 98.3},
                                        {'water_x': -38.7, 'water_y': 124.0, 'water_z': 122.7},
                                        {'water_x': -18.7, 'water_y': 124.0, 'water_z': 147.56},
                                        {'water_x': -244.7, 'water_y': 129.0, 'water_z': 75.7},
                                        {'water_x': -221.69, 'water_y': 129.0, 'water_z': 87.63},
                                        {'water_x': -200.3, 'water_y': 129.0, 'water_z': 74.44},
                                        {'water_x': -209.3, 'water_y': 129.0, 'water_z': 53.3},
                                        {'water_x': -188.3, 'water_y': 129.0, 'water_z': 54.67},
                                        {'water_x': -173.41, 'water_y': 129.0, 'water_z': 60.58},
                                        {'water_x': -140.3, 'water_y': 129.0, 'water_z': 69.3},
                                        {'water_x': -122.48, 'water_y': 129.0, 'water_z': 75.48},
                                        {'water_x': -223.51, 'water_y': 129.0, 'water_z': -20.53},
                                        {'water_x': -218.45, 'water_y': 129.0, 'water_z': -4.67},
                                        {'water_x': -208.3, 'water_y': 129.0, 'water_z': 14.3},
                                        {'water_x': -199.61, 'water_y': 129.0, 'water_z': 33.54},
                                        {'water_x': -227.52, 'water_y': 129.0, 'water_z': 50.66},
                                        {'water_x': -250.41, 'water_y': 129.0, 'water_z': 29.36},
                                        {'water_x': -244.62, 'water_y': 129.0, 'water_z': 51.49},
                                        {'water_x': -227.37, 'water_y': 129.0, 'water_z': -32.73},
                                        {'water_x': -225.32, 'water_y': 129.0, 'water_z': -50.51},
                                        {'water_x': -213.62, 'water_y': 129.0, 'water_z': -70.82},
                                        {'water_x': -205.49, 'water_y': 129.0, 'water_z': -62.62},
                                        {'water_x': -192.65, 'water_y': 129.0, 'water_z': -70.53},
                                        {'water_x': -204.5, 'water_y': 129.0, 'water_z': -85.66},
                                        {'water_x': -191.61, 'water_y': 129.0, 'water_z': -97.62},
                                        {'water_x': -174.37, 'water_y': 129.0, 'water_z': -95.57},
                                        {'water_x': -165.69, 'water_y': 129.0, 'water_z': -70.38},
                                        {'water_x': -161.53, 'water_y': 129.0, 'water_z': -86.76},
                                        {'water_x': -149.41, 'water_y': 129.0, 'water_z': -78.58},
                                        {'water_x': -1.41, 'water_y': 124.0, 'water_z': -93.36},
                                        {'water_x': -3.46, 'water_y': 124.0, 'water_z': -71.58},
                                        {'water_x': -25.55, 'water_y': 124.0, 'water_z': -48.5},
                                        {'water_x': -54.41, 'water_y': 129.0, 'water_z': -51.43},
                                        {'water_x': -68.52, 'water_y': 129.0, 'water_z': -57.52},
                                        {'water_x': -82.66, 'water_y': 129.0, 'water_z': -61.4},
                                        {'water_x': -102.25, 'water_y': 129.0, 'water_z': -62.59},
                                        {'water_x': -117.5, 'water_y': 129.0, 'water_z': -64.59},
                                        {'water_x': -129.7, 'water_y': 129.0, 'water_z': -69.3},
                                        {'water_x': -147.57, 'water_y': 129.0, 'water_z': -67.53},
                                        {'water_x': 27.53, 'water_y': 124.0, 'water_z': 256.36},
                                        {'water_x': 48.3, 'water_y': 124.0, 'water_z': 241.3},
                                        {'water_x': 60.39, 'water_y': 124.0, 'water_z': 212.45},
                                        {'water_x': 53.53, 'water_y': 124.0, 'water_z': 192.5},
                                        {'water_x': 33.79, 'water_y': 124.0, 'water_z': 180.61},
                                        {'water_x': -5.09, 'water_y': 124.0, 'water_z': 158.19},
                                        {'water_x': 17.53, 'water_y': 124.0, 'water_z': 175.58}]},
          'map2': {'name': '二图(绿林溪湾)',
                   'water_jump_threshold': 120.0,
                   'sea_levels': [{'id': 'L0', 'y': 120.0, 'rects': []}],
                   'forbidden_zones': [],
                   'fishing_spots': [{'x': 181.32, 'y': 122.0, 'z': 166.24},
                                     {'x': 206.92, 'y': 120.0, 'z': 122.97},
                                     {'x': 213.92, 'y': 122.0, 'z': 173.91},
                                     {'x': 228.95, 'y': 120.0, 'z': 252.5},
                                     {'x': 234.08, 'y': 120.0, 'z': 188.89},
                                     {'x': 235.22, 'y': 120.0, 'z': 217.69},
                                     {'x': 247.5, 'y': 120.0, 'z': 167.08},
                                     {'x': 247.76, 'y': 122.0, 'z': 274.14},
                                     {'x': 247.79, 'y': 120.0, 'z': 141.19},
                                     {'x': 258.4, 'y': 122.0, 'z': 282.92},
                                     {'x': 269.9, 'y': 120.0, 'z': 198.11},
                                     {'x': 275.38, 'y': 122.0, 'z': 289.07},
                                     {'x': 281.37, 'y': 122.0, 'z': 301.03},
                                     {'x': 291.27, 'y': 120.0, 'z': 185.9},
                                     {'x': 298.85, 'y': 120.0, 'z': 177.21},
                                     {'x': 317.39, 'y': 120.0, 'z': 325.74},
                                     {'x': 331.84, 'y': 120.0, 'z': 145.96},
                                     {'x': 333.94, 'y': 120.0, 'z': 328.94},
                                     {'x': 358.3, 'y': 120.0, 'z': 153.13},
                                     {'x': 364.15, 'y': 120.0, 'z': 172.41},
                                     {'x': 365.84, 'y': 120.5, 'z': 190.28},
                                     {'x': 376.0, 'y': 120.0, 'z': 234.82}],
                   'water_candidates': [{'water_x': 173.44, 'water_y': 120.0, 'water_z': 163.51},
                                        {'water_x': 202.75, 'water_y': 120.0, 'water_z': 120.31},
                                        {'water_x': 211.56, 'water_y': 120.0, 'water_z': 179.7},
                                        {'water_x': 225.89, 'water_y': 120.0, 'water_z': 257.31},
                                        {'water_x': 228.49, 'water_y': 120.0, 'water_z': 213.38},
                                        {'water_x': 240.43, 'water_y': 120.0, 'water_z': 192.46},
                                        {'water_x': 241.65, 'water_y': 120.0, 'water_z': 279.61},
                                        {'water_x': 251.56, 'water_y': 120.0, 'water_z': 171.63},
                                        {'water_x': 251.62, 'water_y': 120.0, 'water_z': 281.35},
                                        {'water_x': 255.46, 'water_y': 120.0, 'water_z': 136.46},
                                        {'water_x': 264.68, 'water_y': 120.0, 'water_z': 192.36},
                                        {'water_x': 268.7, 'water_y': 120.0, 'water_z': 287.38},
                                        {'water_x': 280.43, 'water_y': 120.0, 'water_z': 307.37},
                                        {'water_x': 284.26, 'water_y': 120.0, 'water_z': 182.63},
                                        {'water_x': 295.55, 'water_y': 120.0, 'water_z': 170.18},
                                        {'water_x': 314.7, 'water_y': 120.0, 'water_z': 332.3},
                                        {'water_x': 328.7, 'water_y': 120.0, 'water_z': 139.53},
                                        {'water_x': 335.45, 'water_y': 120.0, 'water_z': 334.44},
                                        {'water_x': 365.46, 'water_y': 120.0, 'water_z': 150.76},
                                        {'water_x': 367.6, 'water_y': 120.0, 'water_z': 196.4},
                                        {'water_x': 370.3, 'water_y': 120.0, 'water_z': 174.39},
                                        {'water_x': 382.71, 'water_y': 120.0, 'water_z': 236.7}],
                   'sub_via_stations': [{'id': 'A1',
                                         'x': 282.0,
                                         'y': 122.0,
                                         'z': 283.0,
                                         'spots': [12, 13],
                                         'class': 'sub'},
                                        {'id': 'A2',
                                         'x': 260.0,
                                         'y': 122.0,
                                         'z': 261.0,
                                         'spots': [8, 10],
                                         'class': 'sub'},
                                        {'id': 'A3',
                                         'x': 224.23,
                                         'y': 123.0,
                                         'z': 163.88,
                                         'spots': [1, 2, 3],
                                         'class': 'sub'}]},
          'map3': {'name': '三图(绿林深潭)',
                   'sea_levels': [],
                   'forbidden_zones': [],
                   'via_stations': [],
                   'special_spots': [],
                   'fishing_spots': [],
                   'water_candidates': []},
          'map4': {'name': '四图(沉船遗迹)',
                   'sea_levels': [],
                   'forbidden_zones': [],
                   'via_stations': [],
                   'special_spots': [],
                   'fishing_spots': [],
                   'water_candidates': []}}}

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
            had_base = 'base_no_fish_timeout' in loaded   # 旧配置迁移：无该字段时以当前 no_fish_timeout 为准
            for key in DEFAULT_CONFIG:
                if key not in loaded:
                    loaded[key] = DEFAULT_CONFIG[key]
            if not had_base:
                loaded['base_no_fish_timeout'] = loaded.get('no_fish_timeout', DEFAULT_CONFIG['no_fish_timeout'])
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

def _first_map(maps):
    """返回 maps 中的第一个地图；空则返回空 dict。"""
    if maps:
        return maps[next(iter(maps))]
    return {}

def load_map_data(path, current_map):
    if not os.path.exists(path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_MAP_DATA, f, indent=4, ensure_ascii=False)
            print(f"[信息] 已生成默认地图配置文件: {path}")
        except Exception as e:
            print(f"[错误] 无法生成地图配置文件: {e}")
        default_maps = DEFAULT_MAP_DATA.get("maps", {})
        if current_map in default_maps:
            return default_maps[current_map]
        return _first_map(default_maps)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        maps = data.get("maps", {})
        if current_map not in maps:
            print(f"[警告] 未找到地图 '{current_map}'，使用第一个可用地图")
            return _first_map(maps)
        return maps[current_map]
    except Exception as e:
        print(f"[错误] 地图配置文件加载失败: {e}")
        return _first_map(DEFAULT_MAP_DATA.get("maps", {}))

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

class _BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_int32),
        ("biHeight", ctypes.c_int32),
        ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_int32),
        ("biYPelsPerMeter", ctypes.c_int32),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]

# ================= 圆角按钮 =================
ICON_BASE64 = "data:image/x-icon;base64,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"

class RoundedButton(tk.Canvas):
    def __init__(self, master=None, text="", command=None, radius=10,
                 bg='#3498db', fg='white', hover_bg='#2980b9', pressed_bg=None,
                 disabled_bg='#b0bec5', disabled_fg='#cfd8dc', font=('', 10, 'bold'), **kwargs):
        self.text = text
        self.command = command
        self.radius = radius
        self.bg = bg; self.fg = fg; self.hover_bg = hover_bg
        self.pressed_bg = pressed_bg or hover_bg
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
        if self.enabled:
            self.draw_round_rect(self.pressed_bg)
            self.after(90, self.draw_normal)
            if self.command: self.command()
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
        self.key_stop_nav = self.config.get('key_stop_navigation', 'b+m')
        self.key_toggle_fish = self.config.get('key_toggle_fishing', 'b+n')
        self._base_no_fish_timeout = float(self.config.get('base_no_fish_timeout',
                                                            self.config.get('no_fish_timeout', 40)))   # 配置设置里的无鱼超时原值（四图临时覆盖用，持久化保证重启后可恢复）
        self.total_catches = int(self.config.get('total_catches', 0))   # 累计上钩数（持久化，重启不消失）

        self.last_hour = time.localtime().tm_hour
        self.hourly_reset_thread = threading.Thread(target=self._hourly_reset_loop, daemon=True)
        self.hourly_reset_thread.start()

        self.root = tk.Tk()
        self.root.title("Tau 1.3.2")
        w = config.get('ui_window_width', 300); h = config.get('ui_window_height', 900)
        mw = config.get('ui_minsize_width', 300); mh = config.get('ui_minsize_height', 700)
        self.root.geometry(f"{w}x{h}"); self.root.minsize(mw, mh)
        self.root.configure(bg=self.BG)

        self.auto_throw_enabled = tk.BooleanVar(value=config.get('auto_throw_enabled', False))
        self.fish_depleted_alert_enabled = tk.BooleanVar(value=config.get('fish_depleted_alert_enabled', True))
        self.auto_relocate_enabled = tk.BooleanVar(value=config.get('auto_relocate_enabled', False))
        self.multiple_cast_enabled = tk.BooleanVar(value=config.get('multiple_cast', False))
        self.pass_bg_enabled_var = tk.BooleanVar(value=config.get('pass_bg_enabled', True))
        self.relocate_timeout_enabled_var = tk.BooleanVar(value=config.get('relocate_timeout_enabled', True))
        self.depleted_alerted = False
        self.relocating = False   # 日志触发换池进行中标志（防止重复触发）

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
        self.style.configure('TLabel', background=self.BG)
        self.style.configure('Title.TLabel', background=self.BG, font=('Microsoft YaHei UI', 14, 'bold'), foreground=self.TEXT)
        # 下拉框样式（白底 + 浅边框 + 蓝色箭头/聚焦边）
        self.style.configure('TCombobox', fieldbackground=self.CARD_BG, background=self.CARD_BG,
                             foreground=self.TEXT, bordercolor=self.CARD_BORDER,
                             lightcolor=self.CARD_BORDER, darkcolor=self.CARD_BORDER,
                             arrowcolor=self.PRIMARY, padding=4)
        self.style.map('TCombobox',
                       fieldbackground=[('readonly', self.CARD_BG)],
                       selectbackground=[('readonly', self.CARD_BG)],
                       selectforeground=[('readonly', self.TEXT)],
                       bordercolor=[('focus', self.PRIMARY)])
        # 滚动条样式
        self.style.configure('Vertical.TScrollbar', background='#cbd5e1',
                             troughcolor=self.BG, bordercolor=self.BG,
                             arrowcolor='#64748b')
        self.setup_ui()
        self.start_mouse_listener()
        self.start_keyboard_listener()
        self.start_log_watcher()
        self._log_queue = queue.Queue()   # 跨线程日志队列（主线程轮询刷新，避免后台线程直调 Tk）
        self._ui_queue = queue.Queue()    # 跨线程 UI 回调队列（主线程执行，如刷新累计上钩数）
        self.root.after(100, self._drain_log_queue)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.auto_throw_enabled.trace_add('write', lambda *a: self._on_checkbox_changed())
        self.fish_depleted_alert_enabled.trace_add('write', lambda *a: self._on_checkbox_changed())
        self.auto_relocate_enabled.trace_add('write', lambda *a: self._on_checkbox_changed())
        self.multiple_cast_enabled.trace_add('write', lambda *a: self._on_checkbox_changed())
        self.pass_bg_enabled_var.trace_add('write', lambda *a: self._on_pass_bg_changed())
        self.relocate_timeout_enabled_var.trace_add('write', lambda *a: self._on_relocate_timeout_toggle())
        self.fn_lock_on_var.trace_add('write', lambda *a: self._on_fn_lock_changed())
        self.fn_lock_off_var.trace_add('write', lambda *a: self._on_fn_lock_changed())
        self._update_status("就绪")
        self.log("欢迎使用Tau 1.3.2，作者:limu57，禁止倒卖，项目地址:https://github.com/limu57/Tau", "blue")
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

    # 地图选择选项: (配置键, 显示文本)
    MAP_OPTIONS = [
        ('map1', '一图(绿林浅滩)'),
        ('map2', '二图(绿林溪湾)'),
        ('map3', '三图(绿林深潭)'),
        ('map4', '四图(沉船遗迹)'),
    ]
    BG = '#f4f6fb'
    CARD_BG = '#ffffff'
    CARD_BORDER = '#e8ecf5'
    TEXT = '#2b3440'
    MUTED = '#94a3b8'          # 次要/占位文字
    PRIMARY = '#4f7cff'        # 主色（蓝）
    PRIMARY_HOVER = '#3b63e0'
    SUCCESS = '#10b981'        # 成功绿
    SUCCESS_HOVER = '#0d9668'
    ACCENT = '#8b5cf6'         # 强调紫
    HEADER_BG = '#1e293b'      # 顶部深色横幅
    HEADER_MUTED = '#cbd5e1'   # 横幅内次要文字
    WARN = '#f59e0b'           # 警告橙
    DANGER = '#ef4444'         # 危险红

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
        ('cast_aim_lift', '抛竿瞄准上抬(格/格)', float),
        ('cast_aim_lift_start', '抛竿补偿起始距离(格)', float),
        ('cast_aim_lift_height', '抛竿高差抵消系数(格/格)', float),
        ('px_color', '鱼漂像素颜色(#RRGGBB)', str),
        ('grab_from_window', '只读游戏窗口像素(后台用)', bool),
        ('window_title_keyword', '游戏窗口标题关键词', str),
        ('px_width', '检测区域宽(像素)', int),
        ('px_height', '检测区域高(像素)', int),
        ('detection_tolerance', '检测颜色容差', int),
        ('detect_start_delay', '检测延迟(秒)', float),
        ('relocate_timeout', '寻路超时(秒)', float),
        ('total_catches', '累计上钩数', int),
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
        """创建白色卡片容器（标题带圆角竖条），返回 (card, body)。"""
        card = tk.Frame(parent, bg=self.CARD_BG,
                        highlightbackground=self.CARD_BORDER, highlightthickness=1)
        card.pack(fill=tk.X, padx=12, pady=(0, 10))
        title_row = tk.Frame(card, bg=self.CARD_BG)
        title_row.pack(anchor='w', padx=14, pady=(12, 4))
        bar = tk.Canvas(title_row, width=4, height=16, bg=self.CARD_BG, highlightthickness=0)
        bar.pack(side='left')
        self._round_rect(bar, 0, 0, 4, 16, r=2, fill=self.PRIMARY)
        tk.Label(title_row, text=title, bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 10, 'bold')).pack(side='left', padx=(8, 0))
        body = tk.Frame(card, bg=self.CARD_BG)
        body.pack(fill=tk.X, padx=10, pady=(4, 10))
        return card, body

    def _make_badge(self, parent, text, bg):
        """创建小圆角徽章（Canvas 圆角矩形 + 居中白字）。"""
        font = (self.FONT, 8, 'bold')
        tmp = tk.Label(parent, text=text, font=font)
        w = tmp.winfo_reqwidth() + 14
        h = tmp.winfo_reqheight() + 4
        tmp.destroy()
        c = tk.Canvas(parent, width=w, height=h, bg=self.HEADER_BG, highlightthickness=0)
        self._round_rect(c, 1, 1, w - 1, h - 1, r=(h - 2) // 2, fill=bg)
        c.create_text(w // 2, h // 2, text=text, fill='#ffffff', font=font)
        return c

    def _make_entry(self, parent, textvariable, width=8, justify='center'):
        """创建统一风格输入框（扁平 + 浅边框 + 聚焦蓝色高亮）。"""
        return tk.Entry(parent, textvariable=textvariable, width=width,
                        justify=justify, font=(self.FONT, 9),
                        relief='flat', bd=0,
                        highlightthickness=1, highlightbackground=self.CARD_BORDER,
                        highlightcolor=self.PRIMARY, insertbackground=self.PRIMARY)

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

    def _draw_tabs(self, hover=None):
        """绘制顶部页面切换标签（主页面/设置），三态：选中/悬停/未选中。"""
        self.tab_canvas.delete('all')
        w = self.tab_canvas.winfo_width()
        if w < 10:
            w = 276
        gap = 10
        tab_w = (w - gap) / 2
        h = 34
        y = 2
        self._tab_rects = []
        for i, (name, key) in enumerate([('主页面', 'main'), ('设置', 'settings')]):
            x0 = i * (tab_w + gap)
            x1 = x0 + tab_w
            self._tab_rects.append((x0, x1))
            selected = self.page == key
            is_hover = (hover == i)
            if selected:
                fill, fg = self.PRIMARY, '#ffffff'
            elif is_hover:
                fill, fg = '#e2e8f0', self.TEXT
            else:
                fill, fg = self.CARD_BG, self.MUTED
            self._round_rect(self.tab_canvas, x0, y, x1, y + h, r=11, fill=fill,
                             outline=self.CARD_BORDER if not selected else fill)
            self.tab_canvas.create_text((x0 + x1) / 2, y + h / 2, text=name,
                                        fill=fg, font=(self.FONT, 10, 'bold'))

    def _on_tab_motion(self, event):
        hover = None
        for i, (x0, x1) in enumerate(getattr(self, '_tab_rects', [])):
            if x0 <= event.x <= x1:
                hover = i
                break
        self._draw_tabs(hover)

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
                elif ctype is bool:
                    low = raw.lower()
                    if low in ('true', '1', 'yes', 'on', '是', '开'):
                        val = True
                    elif low in ('false', '0', 'no', 'off', '否', '关'):
                        val = False
                    else:
                        val = None
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
            elif key == 'no_fish_timeout':
                self._base_no_fish_timeout = float(val)   # 更新配置设置原值（四图恢复时用）
                self.config['base_no_fish_timeout'] = float(val)   # 持久化原值，四图 70s 覆盖后重启仍可恢复
                self._refresh_throw_text()   # 主页面"XX秒无鱼自动抛竿"文案同步刷新
            elif key == 'relocate_timeout':
                self._refresh_relocate_timeout_text()   # 设置页勾选框文案同步时长
            elif key == 'total_catches':
                self.total_catches = int(float(val))   # 累计上钩数同步
                self._refresh_catch_count()
        self._save_config_async()
        self.log(f"配置 {key} → {val}", "grey")

    def _refresh_throw_text(self):
        """刷新主页面选项卡片里的无鱼抛竿文案（与 no_fish_timeout 同步）。"""
        try:
            timeout = int(self.config.get('no_fish_timeout', 60))
            self.auto_throw_chk.configure(text=f"{timeout}秒无鱼自动抛竿")
        except Exception:
            pass

    def _refresh_catch_count(self):
        """刷新主页面累计上钩数显示。"""
        try:
            self.catch_count_label.configure(text=f"累计上钩：{self.total_catches} 次")
        except Exception:
            pass

    def _on_catch(self):
        """一次成功上钩：累计数 +1 并持久化、刷新显示（线程安全）。"""
        self.total_catches += 1
        with self.config_lock:
            self.config['total_catches'] = self.total_catches
        self._schedule_ui(self._refresh_catch_count)
        self._save_config_async()

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
        header = tk.Frame(self.root, bg=self.HEADER_BG)
        header.pack(fill=tk.X)
        inner = tk.Frame(header, bg=self.HEADER_BG)
        inner.pack(fill=tk.X, padx=18, pady=(16, 12))

        top = tk.Frame(inner, bg=self.HEADER_BG)
        top.pack(fill=tk.X)

        # 状态圆点
        self.status_dot = tk.Canvas(top, width=14, height=14, bg=self.HEADER_BG, highlightthickness=0)
        self.status_dot.pack(side='left', padx=(0, 10), pady=(2, 0))
        self._dot_id = self.status_dot.create_oval(3, 3, 11, 11, fill=self.MUTED, outline='')

        # 标题 + 徽章
        title_box = tk.Frame(top, bg=self.HEADER_BG)
        title_box.pack(side='left')
        tk.Label(title_box, text="Tau", bg=self.HEADER_BG, fg='#ffffff',
                 font=(self.FONT, 18, 'bold')).pack(side='left')
        self._make_badge(title_box, "自动钓鱼", self.ACCENT).pack(side='left', padx=(8, 0), pady=(3, 0))
        tk.Label(top, text="v1.3.2", bg=self.HEADER_BG, fg=self.HEADER_MUTED,
                 font=(self.FONT, 9)).pack(side='right', pady=(5, 0))

        # 状态行
        status_row = tk.Frame(inner, bg=self.HEADER_BG)
        status_row.pack(fill=tk.X, pady=(8, 0))
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = tk.Label(status_row, textvariable=self.status_var, bg=self.HEADER_BG,
                                     fg=self.MUTED, font=(self.FONT, 9, 'bold'))
        self.status_label.pack(side='left')
        self.catch_count_label = tk.Label(status_row, text=f"累计上钩：{self.total_catches} 次",
                                          bg=self.HEADER_BG, fg=self.HEADER_MUTED,
                                          font=(self.FONT, 9, 'bold'))
        self.catch_count_label.pack(side='left', padx=(14, 0))

        # —— 页面切换标签 ——
        self.page = 'main'
        self.tab_canvas = tk.Canvas(self.root, height=36, bg=self.BG, highlightthickness=0)
        self.tab_canvas.pack(fill=tk.X, padx=12, pady=(0, 8))
        self.tab_canvas.bind('<Button-1>', self._on_tab_click)
        self.tab_canvas.bind('<Motion>', self._on_tab_motion)
        self.tab_canvas.bind('<Leave>', lambda e: self._draw_tabs(None))
        self.tab_canvas.bind('<Configure>', lambda e: self._draw_tabs())
        # 点击任意非输入控件时让输入框失焦（光标消失）
        self.root.bind('<Button-1>', self._on_global_click, add='+')

        # ================= 主页面 =================
        self.main_page = tk.Frame(self.root, bg=self.BG)
        self.main_page.pack(fill=tk.BOTH, expand=True)

        # —— 操作按钮 ——
        self.a_btn = RoundedButton(self.main_page, text="检测文字位置", command=self.start_detection,
                                   bg=self.PRIMARY, fg='white', hover_bg=self.PRIMARY_HOVER,
                                   pressed_bg='#3150c8',
                                   disabled_bg='#b0bec5', disabled_fg='#cfd8dc',
                                   font=(self.FONT, 10, 'bold'))
        self.a_btn.pack(pady=(0, 8))
        self.b_btn = RoundedButton(self.main_page, text="自动钓鱼开关", command=self.toggle_B,
                                   bg=self.SUCCESS, fg='white', hover_bg=self.SUCCESS_HOVER,
                                   pressed_bg='#0a7a55',
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
        self.pass_bg_chk = self._make_check(body, "钓上通行证后程序背景变色", self.pass_bg_enabled_var)

        # —— 地图选择卡片 ——
        _, body = self._make_card(self.main_page, "地图选择")
        self.map_vars = {}
        cur_map = self.config.get('current_map', 'map1')
        for mid, mtext in self.MAP_OPTIONS:
            var = tk.BooleanVar(value=(cur_map == mid))
            self.map_vars[mid] = var
            cb = tk.Checkbutton(body, text=mtext, variable=var,
                                bg=self.CARD_BG, fg=self.TEXT, activebackground=self.CARD_BG,
                                activeforeground=self.TEXT, selectcolor='white',
                                relief='flat', bd=0, highlightthickness=0,
                                font=(self.FONT, 9), anchor='w',
                                command=lambda m=mid: self._on_map_select(m))
            cb.pack(pady=2, padx=8, anchor='w')

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
                 bg=self.CARD_BG, fg=self.MUTED, font=(self.FONT, 8)).grid(row=4, column=0,
                 columnspan=2, padx=(10, 5), sticky='w')
        body.grid_columnconfigure(1, weight=1)

        # —— FnLock 卡片 ——
        _, body = self._make_card(self.settings_inner, "FnLock 状态")
        self.fn_lock_on_chk = self._make_check(body, "FnLock on", self.fn_lock_on_var,
                                               command=self._on_fn_lock_on_changed)
        self.fn_lock_off_chk = self._make_check(body, "FnLock off", self.fn_lock_off_var,
                                                command=self._on_fn_lock_off_changed)

        # —— 寻路超时卡片 ——
        _, body = self._make_card(self.settings_inner, "寻路超时")
        minutes = int(float(self.config.get('relocate_timeout', 300)) / 60)
        self.relocate_timeout_chk = tk.Checkbutton(body,
                                                   text=f"{minutes}分钟内未到钓点则放弃",
                                                   variable=self.relocate_timeout_enabled_var,
                                                   bg=self.CARD_BG, fg=self.TEXT,
                                                   activebackground=self.CARD_BG,
                                                   activeforeground=self.TEXT, selectcolor='white',
                                                   relief='flat', bd=0, highlightthickness=0,
                                                   font=(self.FONT, 9), anchor='w')
        self.relocate_timeout_chk.pack(pady=2, padx=8, anchor='w')
        tk.Label(body, text="时长在「配置设置」里修改（秒，默认300）",
                 bg=self.CARD_BG, fg=self.MUTED, font=(self.FONT, 8)).pack(pady=(0, 8), padx=8, anchor='w')

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

        # —— 日志监听卡片 ——
        _, body = self._make_card(self.settings_inner, "日志监听")
        # 行0：监听开关
        tk.Label(body, text="日志监听:", bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 9)).grid(row=0, column=0, padx=(10, 5), sticky='w')
        self.log_watch_combo = ttk.Combobox(body, values=['on', 'off'],
                                            state='readonly', width=5, font=(self.FONT, 9))
        self.log_watch_combo.set('on' if self.config.get('log_watch_enabled', True) else 'off')
        self.log_watch_combo.grid(row=0, column=1, sticky='w', pady=2)
        self.log_watch_combo.bind('<<ComboboxSelected>>', self._on_log_watch_toggle)
        # 行1：日志路径 + 浏览按钮（同一 Frame 内紧贴，避免 column weight 把按钮推到远处）
        tk.Label(body, text="日志路径:", bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 9)).grid(row=1, column=0, padx=(10, 5), sticky='w')
        self.log_path_var = tk.StringVar(value=str(self.config.get('log_watch_path', '') or ''))
        path_frame = tk.Frame(body, bg=self.CARD_BG)
        path_frame.grid(row=1, column=1, sticky='w', pady=2)
        path_entry = self._make_entry(path_frame, self.log_path_var, width=8, justify='left')   # 约 50px 宽
        path_entry.pack(side='left')
        path_entry.bind('<FocusOut>', self._on_log_path_changed)
        path_entry.bind('<Return>', self._on_log_path_changed)
        browse_btn = tk.Button(path_frame, text="浏览...", command=self._browse_log_path,
                               font=(self.FONT, 8), relief='flat', bg='#e2e8f0', fg=self.TEXT,
                               activebackground='#cbd5e1', cursor='hand2', padx=6)
        browse_btn.pack(side='left', padx=(6, 0))   # 紧贴输入框右侧
        # 行2：枯竭触发换池开关（类似输入模式切换）
        tk.Label(body, text="枯竭触发换池:", bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 9)).grid(row=2, column=0, padx=(10, 5), sticky='w')
        self.log_relocate_combo = ttk.Combobox(body, values=['on', 'off'],
                                               state='readonly', width=5, font=(self.FONT, 9))
        self.log_relocate_combo.set('on' if self.config.get('log_relocate_enabled', True) else 'off')
        self.log_relocate_combo.grid(row=2, column=1, sticky='w', pady=2)
        self.log_relocate_combo.bind('<<ComboboxSelected>>', self._on_log_relocate_toggle)
        # 行3：轮询间隔
        tk.Label(body, text="轮询间隔(秒):", bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 9)).grid(row=3, column=0, padx=(10, 5), sticky='w')
        interval_var = tk.StringVar(value=str(self.config.get('log_watch_interval', 0.3)))
        interval_entry = self._make_entry(body, interval_var, width=6)
        interval_entry.grid(row=3, column=1, sticky='w', pady=2)
        interval_entry.bind('<FocusOut>', lambda e, k='log_watch_interval', t=float, v=interval_var: self._on_config_changed(k, t, v))
        interval_entry.bind('<Return>', lambda e, k='log_watch_interval', t=float, v=interval_var: self._on_config_changed(k, t, v))
        # 行4：通行证背景颜色
        tk.Label(body, text="通行证背景色:", bg=self.CARD_BG, fg=self.TEXT,
                 font=(self.FONT, 9)).grid(row=4, column=0, padx=(10, 5), sticky='w')
        color_var = tk.StringVar(value=str(self.config.get('pass_bg_color', '#8b5cf6')))
        color_entry = self._make_entry(body, color_var, width=8)
        color_entry.grid(row=4, column=1, sticky='w', pady=2)
        color_entry.bind('<FocusOut>', lambda e, k='pass_bg_color', t=str, v=color_var: self._on_config_changed(k, t, v))
        color_entry.bind('<Return>', lambda e, k='pass_bg_color', t=str, v=color_var: self._on_config_changed(k, t, v))
        # 行5：规则说明
        tk.Label(body, text="匹配规则在 fisher_config.json 的 log_watch_rules 修改（action: pass_card / relocate）",
                 bg=self.CARD_BG, fg=self.MUTED, font=(self.FONT, 8)).grid(row=5, column=0,
                 columnspan=3, padx=(10, 5), sticky='w', pady=(2, 2))
        body.grid_columnconfigure(1, weight=1)

    def _on_log_watch_toggle(self, event=None):
        val = self.log_watch_combo.get() == 'on'
        with self.config_lock:
            self.config['log_watch_enabled'] = val
        self._save_config_async()
        self.log(f"日志监听: {'开' if val else '关'}", "blue")

    def _on_log_relocate_toggle(self, event=None):
        val = self.log_relocate_combo.get() == 'on'
        with self.config_lock:
            self.config['log_relocate_enabled'] = val
        self._save_config_async()
        self.log(f"日志触发换池: {'开' if val else '关'}", "blue")

    def _on_log_path_changed(self, event=None):
        val = self.log_path_var.get().strip()
        with self.config_lock:
            self.config['log_watch_path'] = val
        self._save_config_async()

    def _browse_log_path(self):
        """打开文件选择对话框选择 latest.log，并写入配置。"""
        path = filedialog.askopenfilename(
            title="选择游戏日志文件 (latest.log)",
            filetypes=[("日志文件", "*.log"), ("所有文件", "*.*")])
        if path:
            with self.config_lock:
                self.config['log_watch_path'] = path
            self.log_path_var.set(path)
            self._save_config_async()
            self.log(f"游戏日志路径已设置: {path}", "blue")

    def _draw_rounded_border(self, event=None):
        self.out_canvas.delete("all")
        w = self.out_canvas.winfo_width(); h = self.out_canvas.winfo_height()
        if w<5 or h<5: return
        r=12; o=self.CARD_BORDER; i='#ffffff'
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
                try:
                    self.status_dot.itemconfigure(self._dot_id, fill=self._status_dot_color(text))
                except Exception:
                    pass
            self.root.after(0, _apply)

    def _status_color(self, text):
        """根据状态文本返回横幅内状态文字的颜色。"""
        if '失败' in text or '异常' in text or '错误' in text: return '#fca5a5'
        if '换池' in text: return '#c4b5fd'
        if '检测' in text: return '#fcd34d'
        if '钓鱼' in text: return '#6ee7b7'
        return self.HEADER_MUTED

    def _status_dot_color(self, text):
        """状态圆点颜色（高饱和、醒目）。"""
        if '失败' in text or '异常' in text or '错误' in text: return self.DANGER
        if '换池' in text: return self.ACCENT
        if '检测' in text: return self.WARN
        if '钓鱼' in text: return self.SUCCESS
        return self.MUTED
    def log(self, message, color='black'):
        if not self._closing:
            try:
                self._log_queue.put((message, color))
            except Exception:
                pass   # 队列不可用时丢弃日志，不影响动作流程

    def _drain_log_queue(self):
        """主线程轮询：把各线程入队的日志与 UI 回调刷新到界面（避免后台线程直调 Tk 造成的阻塞/死锁）。"""
        if self._closing:
            return
        try:
            for _ in range(50):
                msg, color = self._log_queue.get_nowait()
                self._log_to_C(msg, color)
        except queue.Empty:
            pass
        except Exception:
            pass
        try:
            for _ in range(20):
                fn = self._ui_queue.get_nowait()
                try:
                    fn()
                except Exception:
                    pass
        except queue.Empty:
            pass
        except Exception:
            pass
        try:
            self.root.after(100, self._drain_log_queue)
        except Exception:
            pass

    def _schedule_ui(self, fn):
        """把 UI 刷新回调交给主线程执行（线程安全）。"""
        try:
            self._ui_queue.put(fn)
        except Exception:
            pass

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
        cutoff = time.time() - self.config.get('log_retention_seconds',600)
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
        self.root.after(self.config.get('log_clean_interval_ms',300000), self._clean_old_logs)

    # ================= 监听器 =================
    def start_mouse_listener(self):
        def on_click(x,y,button,pressed):
            if button==mouse.Button.right and pressed and not self.simulate_flag.is_set():
                self.click_queue.put('right')
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()

    def _key_ident(self, key):
        """返回按键统一标识：修饰键 ctrl/shift/alt，字母键小写字符；其他键返回 None。"""
        if key == Key.ctrl_l or key == Key.ctrl_r:
            return 'ctrl'
        if key == Key.shift_l or key == Key.shift_r:
            return 'shift'
        if key == Key.alt_l or key == Key.alt_r:
            return 'alt'
        if hasattr(key, 'char') and key.char and key.char.isalpha():
            return key.char.lower()
        try:
            if key.vk and 65 <= key.vk <= 90:
                return chr(key.vk).lower()
        except Exception:
            pass
        return None

    def _match_hotkey(self, key, pressed_keys, spec):
        """判断当前按键是否匹配快捷键配置 spec（支持组合键，如 'b+n' / 'ctrl+m'）。

        组合键语义：最后一段为主键（当前按下的键），其余段为必须同时按住的
        前缀键（B+M 表示按住 B 时按 M）。用 vk 匹配字母，规避 ctrl+字母 时
        char 变成控制字符的坑。
        """
        try:
            spec = str(spec).strip().lower()
            parts = [p.strip() for p in spec.split('+')]
            if not parts or not parts[0]:
                return False
            want_key = parts[-1]
            want_prefixes = set(p for p in parts[:-1] if p)
            char_ok = hasattr(key, 'char') and key.char and key.char.lower() == want_key
            vk_ok = False
            if len(want_key) == 1 and want_key.isalpha():
                try:
                    vk_ok = (key.vk == ord(want_key.upper()))
                except Exception:
                    pass
            if not (char_ok or vk_ok):
                return False
            return want_prefixes.issubset(pressed_keys)
        except Exception:
            return False

    def start_keyboard_listener(self):
        pressed_keys = set()
        def on_press(key):
            try:
                ident = self._key_ident(key)
                if ident is None:
                    return
                if self._match_hotkey(key, pressed_keys, self.key_stop_nav):
                    self.navigation_stop_event.set()
                    self.log(f"已按下 {str(self.key_stop_nav).upper()}，请求停止寻路", "purple")
                elif self._match_hotkey(key, pressed_keys, self.key_toggle_fish):
                    self.root.after(0, self.toggle_B)
                pressed_keys.add(ident)
            except Exception as e:
                self.log(f"键盘监听异常: {e}", "orange")
        def on_release(key):
            try:
                ident = self._key_ident(key)
                if ident is not None:
                    pressed_keys.discard(ident)
            except Exception:
                pass
        self.keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    # ===== 游戏日志监听（latest.log 增量 tail，匹配文字触发动作） =====
    def start_log_watcher(self):
        """启动 latest.log 监听线程：增量读取新增行，按规则匹配触发动作。"""
        self.log_watch_stop = threading.Event()
        self.log_watch_thread = threading.Thread(target=self._log_watcher_loop, daemon=True)
        self.log_watch_thread.start()

    def _decode_log_text(self, raw):
        """自动检测日志编码：优先 UTF-8，失败用 GB18030（中文 Windows 的 Minecraft 日志）。"""
        try:
            return raw.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return raw.decode('gb18030', errors='ignore')
            except Exception:
                return raw.decode('utf-8', errors='ignore')

    def _log_watcher_loop(self):
        """轮询日志文件：记录字节游标，只读新增内容；文件被重写时游标归零。
        二进制读取 + 自动编码检测（中文 Windows 日志为 GB18030，UTF-8 读会乱码）。"""
        if not self.config.get('log_watch_enabled', True):
            return
        path = str(self.config.get('log_watch_path', '') or '').strip()
        if not path:
            self.log("日志监听未启用：未设置日志路径（设置页点「浏览...」选择 latest.log）","orange")
            return
        rules = self.config.get('log_watch_rules', []) or []
        self.log(f"日志监听已启动: {path}（规则 {len(rules)} 条）","grey")
        # 启动时跳到文件末尾：只监听启动后新增的行，避免历史旧消息（如昨天的"枯竭"）误触发动作
        try:
            offset = os.path.getsize(path) if os.path.exists(path) else 0
        except Exception:
            offset = 0
        interval = float(self.config.get('log_watch_interval', 0.3))
        while not self._closing and not self.log_watch_stop.is_set():
            try:
                size = os.path.getsize(path)
                if size < offset:   # 日志被重写/滚动
                    offset = 0
                if size > offset:
                    with open(path, 'rb') as f:
                        f.seek(offset)
                        raw = f.read()
                        offset = f.tell()
                    self._check_log_lines(self._decode_log_text(raw))
            except FileNotFoundError:
                offset = 0
            except Exception:
                pass
            if self.log_watch_stop.wait(interval):
                break

    def _normalize_log_text(self, s):
        """归一化日志文本用于匹配：去 Minecraft 颜色代码(§x)、全角标点转半角、转小写。"""
        try:
            s = re.sub(r'\u00a7[0-9a-fk-or]', '', s, flags=re.IGNORECASE)
        except Exception:
            pass
        out = []
        for ch in s:
            o = ord(ch)
            if o == 0x3000:
                out.append(' ')
            elif 0xFF01 <= o <= 0xFF5E:
                out.append(chr(o - 0xFEE0))   # 全角 → 半角
            else:
                out.append(ch)
        return ''.join(out).lower()

    def _check_log_lines(self, data):
        """对新增日志逐行匹配规则（归一化后子串匹配，支持 '|' 多片段任一命中），
        命中则执行对应动作并输出命中行。"""
        if not data:
            return
        rules = self.config.get('log_watch_rules', []) or []
        if not rules:
            return
        for line in data.splitlines():
            line_norm = self._normalize_log_text(line)
            for rule in rules:
                text = ((rule or {}).get('text', '') or '').strip()
                if not text:
                    continue
                matched = False
                for frag in text.split('|'):
                    frag_norm = self._normalize_log_text(frag.strip())
                    if frag_norm and frag_norm in line_norm:
                        matched = True
                        break
                if matched:
                    self.log(f"日志命中: {line.strip()[:80]}","purple")
                    self._execute_log_action((rule or {}).get('action', ''), line)
                    break   # 一行只触发一条规则

    def _execute_log_action(self, action, line):
        """按动作类型分发：pass_card 主线程改背景；relocate 后台线程换池。"""
        if action == 'pass_card':
            self.root.after(0, self._log_action_pass_card)
        elif action == 'relocate':
            threading.Thread(target=self._log_action_relocate, daemon=True).start()
        else:
            self.log(f"未知日志动作: {action}", "orange")

    def _log_action_pass_card(self):
        """通行证日志：GUI 背景改为自定义颜色（默认紫），直到手动关闭自动钓鱼恢复。"""
        try:
            if not self.config.get('pass_bg_enabled', True):
                return
            color = str(self.config.get('pass_bg_color', '#8b5cf6') or '#8b5cf6')
            self._set_ui_bg(color)
            self.log(f"钓上通行证！程序背景变为 {color}（关闭自动钓鱼后恢复）","purple")
        except Exception as e:
            self.log(f"通行证背景动作失败: {e}", "orange")

    def _log_action_relocate(self):
        """钓点枯竭日志：触发自动换池（开关 log_relocate_enabled 控制）。"""
        if not self.config.get('log_relocate_enabled', True):
            return
        with self.lock:
            if self.relocating:
                return   # 已在换池中，跳过重复触发
            self.relocating = True
        try:
            self.log("日志检测：该钓点已枯竭，开始自动换池","orange")
            self.stop_fishing()
            self._relocate_and_restart()
        except Exception as e:
            self.log(f"日志换池错误: {e}", "red")
        finally:
            with self.lock:
                self.relocating = False

    def _set_ui_bg(self, color):
        """把程序背景（页面主体）设为指定颜色。"""
        try:
            widgets = [self.root, self.main_page, self.settings_page, self.tab_canvas,
                       self.settings_canvas, self.settings_inner, self.out_canvas]
            for w in widgets:
                try: w.configure(bg=color)
                except Exception: pass
            self._draw_tabs()
        except Exception:
            pass

    def _restore_ui_bg(self):
        """恢复默认背景色。"""
        try:
            self._set_ui_bg(self.BG)
        except Exception:
            pass

    def _on_pass_bg_changed(self):
        with self.config_lock:
            self.config['pass_bg_enabled'] = self.pass_bg_enabled_var.get()
        self._save_config_async()

    def _on_relocate_timeout_toggle(self):
        with self.config_lock:
            self.config['relocate_timeout_enabled'] = self.relocate_timeout_enabled_var.get()
        self._save_config_async()

    def _refresh_relocate_timeout_text(self):
        """设置页「寻路超时」勾选框文案同步时长（分钟）。"""
        try:
            minutes = int(float(self.config.get('relocate_timeout', 300)) / 60)
            self.relocate_timeout_chk.configure(text=f"{minutes}分钟内未到钓点则放弃")
        except Exception:
            pass

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
                time.sleep(self.config.get('post_click_interval',0.03))
                ctypes.windll.user32.PostMessageW(hwnd, self.WM_RBUTTONUP, 0, lParam)
            except Exception:
                self._fallback_global("窗口右键点击失败")
                pyautogui.click(button='right')
        else:
            pyautogui.click(button='right')
        time.sleep(self.config.get('click_post_delay',0.05))
        self.simulate_flag.clear()

    def _capture_game_window(self):
        """用 PrintWindow 抓取游戏窗口图像：后台/被遮挡时也取游戏自身内容，
        前台其他窗口不会干扰像素判定。注意 PW_RENDERFULLCONTENT(2) 渲染整个窗口
        （含边框），故位图用整窗尺寸、坐标映射用窗口原点。返回 PIL Image(RGB)；
        失败返回 None。带 80ms 缓存避免高频抓图开销。"""
        try:
            now = time.time()
            if getattr(self, '_win_cap', None) and now - self._win_cap[0] < 0.08:
                return self._win_cap[1]
            hwnd = self._find_game_window()
            if not hwnd:
                return None
            l, t, r, b = win32gui.GetWindowRect(hwnd)   # 整窗（含边框），与 flag=2 对应
            w, h = r - l, b - t
            if w <= 0 or h <= 0:
                return None
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            hwnd_dc = user32.GetDC(hwnd)
            if not hwnd_dc:
                return None
            try:
                mem_dc = gdi32.CreateCompatibleDC(hwnd_dc)
                if not mem_dc:
                    return None
                try:
                    bitmap = gdi32.CreateCompatibleBitmap(hwnd_dc, w, h)
                    if not bitmap:
                        return None
                    try:
                        old = gdi32.SelectObject(mem_dc, bitmap)
                        # PW_RENDERFULLCONTENT=2：走 DWM 合成内容，OpenGL/DirectX 后台也能抓
                        if user32.PrintWindow(hwnd, mem_dc, 2) == 0:
                            return None
                        bmi = _BITMAPINFOHEADER()
                        bmi.biSize = ctypes.sizeof(_BITMAPINFOHEADER)
                        bmi.biWidth = w
                        bmi.biHeight = -h   # 自顶向下
                        bmi.biPlanes = 1
                        bmi.biBitCount = 32
                        buf = ctypes.create_string_buffer(w * h * 4)
                        if gdi32.GetDIBits(mem_dc, bitmap, 0, h, buf, ctypes.byref(bmi), 0) == 0:
                            return None
                        img = Image.frombuffer('RGB', (w, h), buf, 'raw', 'BGRX', 0, 1)
                        if img.getbbox() is None:
                            return None   # 全黑视为抓取失败，回退屏幕截图
                        self._win_cap = (now, img)
                        return img
                    finally:
                        gdi32.SelectObject(mem_dc, old)
                        gdi32.DeleteObject(bitmap)
                finally:
                    gdi32.DeleteDC(mem_dc)
            finally:
                user32.ReleaseDC(hwnd, hwnd_dc)
        except Exception:
            return None

    def _get_window_origin(self):
        """返回游戏窗口左上角的屏幕坐标 (left, top)；失败返回 None。"""
        try:
            hwnd = self._find_game_window()
            if hwnd:
                l, t, r, b = win32gui.GetWindowRect(hwnd)
                return (l, t)
        except Exception:
            pass
        return None

    def _grab_pixel_rgb(self, x, y):
        """优先从游戏窗口（PrintWindow）取像素：后台挂机时只读游戏自身内容，
        前台其他窗口不会误触发上鱼。由 grab_from_window 配置控制（默认关，
        回退屏幕截图保证检测可靠）；PrintWindow 失败也会自动回退屏幕截图。"""
        if self.config.get('grab_from_window', False):
            try:
                img = self._capture_game_window()
                if img is not None:
                    origin = self._get_window_origin()
                    if origin is not None:
                        lx, ly = x - origin[0], y - origin[1]
                        if 0 <= lx < img.width and 0 <= ly < img.height:
                            return img.getpixel((lx, ly))
            except Exception:
                pass
        # 屏幕截图（默认方式）
        try:
            if not hasattr(self, '_screen_size'):
                self._screen_size = pyautogui.size()
            sw, sh = self._screen_size
            rad = int(self.config.get('grab_sample_radius', 2))
            left, top = max(0, x - rad), max(0, y - rad)
            right, bottom = min(sw - 1, x + rad + 1), min(sh - 1, y + rad + 1)
            if right <= left or bottom <= top:
                return None
            img2 = ImageGrab.grab(bbox=(left, top, right, bottom))
            arr = np.array(img2, dtype=np.int16)
            return tuple(int(v) for v in arr[y - top, x - left])
        except Exception as e:
            now = time.time()
            if now - getattr(self, '_last_px_err_log', 0.0) > self.config.get('pixel_err_log_interval', 5.0):
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
        # 检测延迟：点击「检测文字位置」后等待 n 秒再开始（默认5秒，留时间回游戏抛竿）
        delay = float(self.config.get('detect_start_delay', 5.0) or 0)
        if delay > 0:
            self.log(f"将在 {delay:.0f} 秒后开始检测，请回到游戏抛竿","orange")
            if self.detect_stop_event.wait(delay):
                return
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
        # 上钩文字由 title 变为 subtitle（显示位置下移），检测区域整体向下平移一个区域高度
        shift = int(self.config['px_height'])
        cx, cy = cx + ox, cy + oy + shift
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
            except Exception: time.sleep(self.config.get('grab_fail_wait',0.5)); continue
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
                    time.sleep(self.config.get('confirm_check_interval',0.1))
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
            with self.lock:
                self.auto_prepare_cast = True
            self.start_fishing()   # 统一走钓鱼线程：收竿→等待→抛竿→循环（start_fishing 内启用 b_btn）
        else:
            # 未获取到坐标：自动钓鱼开关保持灰色（仅当此前已成功获取过坐标时才可点）
            with self.m_lock:
                has_m = self.M is not None
            self.b_btn.set_enabled(has_m)
            self._update_status("就绪")

    def toggle_B(self):
        if self.B_status=='off': self.start_fishing()
        else:
            self.stop_fishing()
            self._restore_ui_bg()   # 手动关闭自动钓鱼：恢复通行证背景

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
            time.sleep(self.config.get('prepare_cast_delay',0.1)); self.simulate_right_click()
            self._on_catch()   # 第一次检测的上钩计入累计总数
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
                        if stop_event.wait(self.config.get('manual_cast_poll_wait',1.0)): return
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
                        if stop_event.wait(self.config.get('auto_cast_post_wait',2.0)): break
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
                        if stop_event.wait(self.config.get('confirm_check_interval',0.1)): return
                        pix = self._grab_pixel_rgb(mx, my)
                        if pix is None or sum(abs(a-b) for a,b in zip(pix, target_rgb)) > tol:
                            confirmed = False; break
                    if confirmed:
                        self.log("检测到上钩，收竿！","green")
                        self._on_catch()   # 累计上钩数 +1 并持久化
                        if stop_event.wait(self.config.get('confirm_check_interval',0.1)): break
                        self.simulate_right_click()
                        wait = random.uniform(rw_min, rw_max)
                        self.log(f"等待 {wait:.1f} 秒后重新抛竿...","blue")
                        if stop_event.wait(wait): break
                        self.simulate_right_click()
                        if stop_event.wait(random.uniform(cd_min, cd_max)): break
                        last_throw = time.time(); self.depleted_alerted = False
                        continue
                if stop_event.wait(max(self.config.get('poll_min_interval',0.05), poll_rate+random.uniform(-jitter,jitter))): break
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
                time.sleep(self.config.get('combo_key_interval',0.02))
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
                        if all(abs(v)<self.config.get('coord_abs_limit',100000) for v in (x,y,z)):
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
                    timeout=self.config.get('tasklist_timeout',5))
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
            if hwnd: win32gui.SetForegroundWindow(hwnd); time.sleep(self.config.get('window_activate_delay',0.05))
        except Exception as e: self.log(f"窗口激活异常: {e}","grey")

    def _mouse_move(self, dx, dy):
        mult = self.config.get('mouse_move_multiplier', 1.0)
        dx = int(dx * mult); dy = int(dy * mult)
        # 视角移动统一使用全局相对移动：Minecraft(GLFW) 依赖真实光标位置轮询计算视角，
        # PostMessage 的 WM_MOUSEMOVE 无法驱动视角（光标锁定模式下仍无效）。
        # 键盘/点击/F3+C 仍走输入模式隔离（PostMessage 仅影响游戏窗口）。
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

    def _get_sea_level_y(self, cx, cz):
        """返回 (cx,cz) 位置对应的海平面 Y 高度（水中上岸判定用）。

        sea_levels 格式: [{"id":"L0","y":63.0,"rects":[]},
                          {"id":"L1","y":66.0,"rects":[[xmin,zmin,xmax,zmax],...]}, ...]
        L0 为全图兜底层；非 L0 层按矩形区域匹配（只比较 x/z，忽略 y）。
        """
        sl = (self.current_map_data or {}).get('sea_levels')
        fallback = float(self.config.get('water_jump_threshold', 63.0))
        if not sl:
            return fallback
        l0_y = fallback
        for level in sl:
            y = level.get('y')
            if level.get('id') == 'L0':
                l0_y = float(y) if y is not None else fallback
                continue
            if y is None:
                continue
            for rect in (level.get('rects') or []):
                if len(rect) == 4 and rect[0] <= cx <= rect[2] and rect[1] <= cz <= rect[3]:
                    return float(y)
        return l0_y

    def _float_to_surface(self, last_ys, extra_yaw=None, target=None, timeout=None):
        if timeout is None: timeout = self.config.get('water_float_timeout',2.0)
        pitch_angle = self.config.get('float_pitch_angle',45.0)
        check_interval = self.config.get('float_check_interval',0.3)
        turn_tol = self.config.get('water_turn_tolerance', 5.0)
        stuck_threshold = self.config.get('stuck_threshold',0.15)
        stuck_trigger = self.config.get('stuck_trigger_count',2)
        coords = self._get_current_coords(2)
        if not coords: return False
        init_pitch = coords[4]; cyaw = coords[3]
        if extra_yaw is not None:
            self._rotate_to_angle(extra_yaw, init_pitch, cyaw, init_pitch, tolerance=turn_tol)
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
        stuck_count = 0; last_coord = None
        try:
            while not self.navigation_stop_event.is_set():
                if self._nav_timed_out():
                    self.log("寻路超时，放弃该目标","red"); return False
                coords = self._get_current_coords(2)
                if not coords:
                    if self._wait_or_stop(check_interval): break
                    continue
                cx, cy, cz = coords[0], coords[1], coords[2]
                last_ys.append(cy)
                water_th = self._get_sea_level_y(cx, cz)
                # 卡死检测：上浮时 xz 连续不变说明被障碍物卡住（如水面与半砖之间），触发避障
                if last_coord is not None:
                    d = math.hypot(cx - last_coord[0], cz - last_coord[1])
                    if d < stuck_threshold:
                        stuck_count += 1
                        self.log(f"上浮卡死计数: {stuck_count}/{stuck_trigger}","grey")
                        if stuck_count >= stuck_trigger:
                            self.log("上浮位置不变，触发避障","orange")
                            self._execute_stuck_evasion()
                            return False
                    else:
                        stuck_count = 0
                last_coord = (cx, cz)
                if cy >= water_th:
                    # 检测到上岸/浮出水面：立即停止移动（单次判定，不等二次确认，避免在岸上继续行进绕圈）
                    self.log("已浮出水面，停止上浮","green")
                    return True
                # 水中分段走：每段重新朝向目标方向（避免直游漂离、掠过钓点）
                if target:
                    tyaw, _ = self._calc_target_angles(coords[0], coords[1], coords[2],
                                                       target['x'], target['y'], target['z'])
                    self._rotate_to_angle(tyaw, coords[4], coords[3], coords[4], tolerance=turn_tol)
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
        if self._wait_or_stop(self.config.get('forbidden_poll_wait',0.3)): return
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
                if self._wait_or_stop(self.config.get('forbidden_poll_wait',0.3)): break
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
        # 抛竿下垂补偿：水域较远时抬高瞄准点；但若钓点比水域高，高差已提供射程，按高度差抵消补偿
        hor_dist = math.hypot(wx-cx, wz-cz)
        lift_start = float(self.config.get('cast_aim_lift_start', 6.0))
        lift_per = float(self.config.get('cast_aim_lift', 0.15))
        lift_height = float(self.config.get('cast_aim_lift_height', 1.0))
        delta_h = cy - wy   # 玩家脚底高度 - 水域高度，>0 表示玩家更高
        wy_aim = wy
        lifted = False
        if hor_dist > lift_start:
            dist_lift = (hor_dist - lift_start) * lift_per
            # 高差对抛竿下垂影响很小（下垂主要由水平飞行距离决定，
            # 2 格高差仅改变约 5%），只按小系数部分抵消，避免高处抛竿时
            # 完全取消上抬导致瞄不到水域
            lift = dist_lift - max(0.0, delta_h) * lift_height
            lift = max(0.0, lift)
            if lift > 0:
                wy_aim = wy + lift
                lifted = True
                self.log(f"水域距离 {hor_dist:.1f} 格，高差 {delta_h:.1f} 格，瞄准点上抬 {lift:.1f} 格补偿抛竿下垂", "grey")
            else:
                self.log(f"水域距离 {hor_dist:.1f} 格，高差 {delta_h:.1f} 格已足够，无需上抬补偿", "grey")
        # 近距离（无补偿）时视线穿过水域方块，可直接射线判定
        if not lifted and self._ray_hit_water_block(cx,cy,cz, cur_yaw,cur_pitch, wx,wy,wz):
            self.log("准心已对准水域方块","green"); return True
        # 闭环校正：每轮取真实坐标与视角，按真实偏差移动（避免 deg_per_pixel 线性近似误差累积导致偏瞄）
        for i in range(max_iter):
            if self.navigation_stop_event.is_set(): return False
            coords = self._get_current_coords(2)
            if not coords:
                if self._wait_or_stop(delay): return False
                continue
            cx, cy, cz = coords[0], coords[1], coords[2]
            cur_yaw, cur_pitch = coords[3], coords[4]
            tyaw, tpitch = self._calc_target_angles(cx, cy, cz, wx, wy_aim, wz)
            dyaw = ((tyaw - cur_yaw + 180) % 360) - 180
            dpitch = tpitch - cur_pitch
            angle_dist = math.hypot(dyaw, dpitch)
            if angle_dist < self.config.get('align_success_angle', 0.5):
                self.log("准心已对准水域方块","green"); return True
            if angle_dist < min_step:
                if angle_dist < 0.1:
                    move_yaw, move_pitch = (min_step if dyaw >= 0 else -min_step), (min_step if dpitch >= 0 else -min_step)
                else:
                    move_yaw, move_pitch = (dyaw / angle_dist) * min_step, (dpitch / angle_dist) * min_step
            else:
                move_yaw, move_pitch = dyaw, dpitch
            deg_px = self._get_deg_per_pixel()
            mdx = int(move_yaw / deg_px); mdy = int(move_pitch / deg_px)
            if mdx == 0 and mdy == 0: break
            self._mouse_move(mdx, mdy)
            if self._wait_or_stop(delay): return False
        # 末次验证：用真实坐标与视角确认
        coords = self._get_current_coords(2)
        if coords:
            if not lifted:
                if self._ray_hit_water_block(coords[0], coords[1], coords[2], coords[3], coords[4], wx, wy, wz):
                    self.log("准心已对准水域方块","green"); return True
            else:
                # 补偿模式下视线不再穿过水域方块，改用角度差验证
                tyaw, tpitch = self._calc_target_angles(coords[0], coords[1], coords[2], wx, wy_aim, wz)
                dyaw = ((tyaw - coords[3] + 180) % 360) - 180
                dpitch = tpitch - coords[4]
                if math.hypot(dyaw, dpitch) < self.config.get('align_success_angle', 0.5):
                    self.log("准心已对准水域方块（含抛竿补偿）","green"); return True
        self.log("对准水域方块失败","red"); return False

    # ===== T 循环 =====
    def _t_loop(self, target):
        tx,ty,tz = target['x'],target['y'],target['z']
        per_check = self.config.get('per_check',1.0)
        stuck_threshold = self.config.get('stuck_threshold',0.15); stuck_trigger = self.config.get('stuck_trigger_count',3)
        t_to_i = self.config.get('t_to_i_distance',15.0); water_tol = self.config.get('water_turn_tolerance',5.0)
        last_ys = deque(maxlen=2); w_down=False
        # 卡死状态用实例变量跨循环保留：水中反复上浮/撞墙位置不变也会累积并触发避障
        if getattr(self, '_stuck_count', None) is None: self._stuck_count = 0
        if getattr(self, '_last_stuck_coord', None) is None: self._last_stuck_coord = None
        try:
            while not self.navigation_stop_event.is_set():
                if self._nav_timed_out():
                    self.log("寻路超时，放弃该目标","red"); return 'timeout'
                coords = self._get_current_coords(2)
                if not coords:
                    if self._wait_or_stop(self.config.get('coord_fail_wait',0.5)): break
                    continue
                cx,cy,cz, cyaw,cpitch = coords; last_ys.append(cy)
                water_th = self._get_sea_level_y(cx, cz)
                if self._is_in_forbidden(cx,cz):
                    self.log("(T) 进入禁止区域，绕行","orange")
                    if w_down: self._key_up('w'); w_down=False
                    self._stuck_count=0; self._last_stuck_coord=None
                    if not self._exit_forbidden_zone(cx,cz): return False
                    else: return 'retry'
                # 卡死检测提前到落水前：无论是否在水中，位置不变都累积（修复水中撞墙不避障）
                if self._last_stuck_coord is not None:
                    d = math.hypot(cx-self._last_stuck_coord[0], cz-self._last_stuck_coord[1])
                    if d < stuck_threshold:
                        self._stuck_count+=1; self.log(f"T卡死计数: {self._stuck_count}/{stuck_trigger}","grey")
                    else:
                        self._stuck_count=0
                self._last_stuck_coord = (cx,cz)
                if self._stuck_count >= stuck_trigger:
                    self.log("连续坐标不变，触发避障","orange")
                    if w_down: self._key_up('w'); w_down=False
                    self._execute_stuck_evasion(); self._stuck_count=0; self._last_stuck_coord=None; return 'retry'
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
                    if not self._float_to_surface(last_ys, extra_yaw=tyaw, target=target):
                        self.log("上浮超时，重新T循环","orange"); return 'retry'
                    # 上岸后停止行进，重新开始新的 I/T 循环（重新评估距离决定走 I 还是 T，避免掠过目标绕圈）
                    self.log("已上岸，重新开始导航循环","blue")
                    return 'retry'
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
    def _i_loop(self, target, via_mode=False):
        tx,ty,tz = target['x'],target['y'],target['z']
        speed = self.config.get('player_speed',5.625); arrival_dist = self.config.get('arrival_dist',1.5)
        max_iter = self.config.get('i_loop_max_iter',10)
        walk_factor = self.config.get('walk_time_factor',0.9); stuck_threshold = self.config.get('stuck_threshold',0.15)
        stuck_trigger = self.config.get('stuck_trigger_count',3); min_walk = self.config.get('i_loop_min_walk_time',0.05)
        max_walk = self.config.get('i_loop_max_walk_time',1.0); post_walk = self.config.get('i_loop_post_walk_delay',0.2)
        iter_count=0; last_ys=deque(maxlen=2); water_fail_count=0
        # 卡死状态用实例变量跨循环保留（水中反复上浮/撞墙位置不变也会触发避障）
        if getattr(self, '_stuck_count', None) is None: self._stuck_count = 0
        if getattr(self, '_last_stuck_coord', None) is None: self._last_stuck_coord = None
        while not self.navigation_stop_event.is_set() and iter_count < max_iter:
            if self._nav_timed_out():
                self.log("寻路超时，放弃该目标","red"); return 'timeout'
            coords = self._get_current_coords(2)
            if not coords:
                if self._wait_or_stop(self.config.get('coord_fail_wait_i',0.3)): break
                continue
            cx,cy,cz, cyaw,cpitch = coords
            water_th = self._get_sea_level_y(cx, cz)
            if self._is_in_forbidden(cx,cz):
                self.log("(I) 进入禁止区域，绕行","orange")
                self._stuck_count=0; self._last_stuck_coord=None
                if not self._exit_forbidden_zone(cx,cz): return False
                else: return 'retry'
            # 卡死检测提前到落水前：水中撞墙位置不变也累积，避免反复上浮却不避障
            if self._last_stuck_coord is not None:
                d = math.hypot(cx-self._last_stuck_coord[0], cz-self._last_stuck_coord[1])
                if d < stuck_threshold:
                    self._stuck_count+=1; self.log(f"I卡死计数: {self._stuck_count}/{stuck_trigger}","grey")
                else:
                    self._stuck_count=0
            self._last_stuck_coord = (cx,cz)
            if self._stuck_count >= stuck_trigger:
                self.log("I循环卡死，触发避障重启","orange")
                self._execute_stuck_evasion(); self._stuck_count=0; self._last_stuck_coord=None; return 'retry'
            if cy < water_th:
                self.log("I循环落水，转向钓点上浮...")
                tyaw,_ = self._calc_target_angles(cx,cy,cz, tx,ty,tz)
                self._rotate_to_angle(tyaw,cpitch,cyaw,cpitch, tolerance=self.config.get('water_turn_tolerance',5.0))
                if not self._float_to_surface(last_ys, extra_yaw=tyaw, target=target):
                    water_fail_count+=1
                    if water_fail_count >= self.config.get('max_water_fails',3):
                        self.log("连续上浮失败超限，放弃该钓点","red"); return False
                    return 'retry'
                # 上岸后停止移动，重新开始新的 I/T 循环（避免继续行进绕过目标）
                self.log("已上岸，重新开始导航循环","blue")
                return 'retry'
            water_fail_count=0
            hor_dist = math.hypot(tx-cx, tz-cz)
            self.log(f"距钓点 {hor_dist:.1f} 格")
            if hor_dist <= arrival_dist and cy>=water_th: break
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
        is_via = via_mode
        if is_via:
            self.log("中转站无需对准水域，直接到达","blue")
            pitch_down = self.config.get('pitch_down_after_arrival',0.0)
            if pitch_down:
                self.log(f"额外下压俯仰角 {pitch_down:.1f}°")
                coords = self._get_current_coords(2)
                if coords:
                    cx,cy,cz,cyaw,cpitch = coords
                    new_pitch = max(-90.0, min(90.0, cpitch+pitch_down))
                    self._rotate_to_angle(cyaw,new_pitch,cyaw,cpitch, tolerance=self.config.get('align_success_angle',0.5))
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
                    self._rotate_to_angle(cyaw,new_pitch,cyaw,cpitch, tolerance=self.config.get('align_success_angle',0.5))
            return True

    def _navigate_to_target(self, target, via_mode=False):
        # —— 第一段：预判直行是否穿过未绕过的禁区，穿过则先执行绕角 ——
        while not self.navigation_stop_event.is_set():
            coords = self._get_current_coords(2)
            if not coords:
                if self._wait_or_stop(self.config.get('coord_fail_wait',0.5)): return False
                continue
            cx, cy, cz = coords[0], coords[1], coords[2]
            detour = self._check_forbidden_detour(cx, cz, target['x'], target['z'])
            if detour is None:
                break
            fz, pts = detour
            self.log("直行路径穿过禁区，执行绕角绕行","orange")
            for px, pz in pts:
                if self.navigation_stop_event.is_set(): return False
                if not self._navigate_to_target({'x': px, 'y': cy, 'z': pz}, via_mode=True):
                    return False
            self.bypassed_zones.append(fz)
            self.log("该禁区已绕过，继续寻路","green")
        # —— 第二段：原有 T/I 循环 ——
        self.obstacle_count = 0
        self._stuck_count = 0; self._last_stuck_coord = None   # 每次寻路重置卡死状态
        while not self.navigation_stop_event.is_set():
            t_result = self._t_loop(target)
            if t_result == True:
                self._update_status("导航中（I循环）")
                i_result = self._i_loop(target, via_mode)
                if i_result == 'retry': continue
                if i_result == 'timeout': return False
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

    # ===== 子中转（sub_via_stations：子中转点绑定一群钓点编号） =====
    def _find_spot_sub_via(self, spot, sub_stations):
        """返回钓点 spot 绑定的子中转站（按坐标匹配 fishing_spots 编号）；无则 None。"""
        if not spot:
            return None
        for i, s in enumerate(self.fishing_spots):
            if (s is spot or (abs(s['x']-spot['x'])<0.01 and abs(s['y']-spot['y'])<0.01
                              and abs(s['z']-spot['z'])<0.01)):
                num = i + 1
                for st in sub_stations:
                    if num in (st.get('spots') or []):
                        return st
                return None
        return None

    def _find_start_sub_via(self, cx, cz, sub_stations):
        """出发点最近的钓点绑定的子中转站；无则 None。"""
        best_sp, best_d = None, float('inf')
        for sp in self.fishing_spots:
            d = math.hypot(sp['x'] - cx, sp['z'] - cz)
            if d < best_d:
                best_d = d; best_sp = sp
        if best_sp is None:
            return None
        return self._find_spot_sub_via(best_sp, sub_stations)

    def _build_sub_via_path(self, cx, cz, target):
        """子中转路径规划：
        起点侧——出发点最近的钓点若绑定了子中转，先前往该子中转再继续；
        终点侧——目标钓点若绑定了子中转，先前往子中转再到目标（起点子中转与终点
        子中转相同时只去一次）。
        返回 [(name, point), ...]（不含最终目标）；无子中转配置时返回 []。"""
        sub_stations = (self.current_map_data or {}).get('sub_via_stations') or []
        if not sub_stations:
            return []
        start_sub = self._find_start_sub_via(cx, cz, sub_stations)
        end_sub = self._find_spot_sub_via(target, sub_stations)
        path = []
        if start_sub and (end_sub is None or start_sub.get('id') != end_sub.get('id')):
            path.append(('子中转', start_sub))
        if end_sub:
            path.append(('子中转', end_sub))
        return path

    def _is_via_point(self, target):
        threshold = self.config.get('via_spot_threshold', 0.5)
        for st in self.via_stations:
            if all(abs(target[k]-st[k]) < threshold for k in ('x','y','z')): return True
        return False

    def _build_via_path(self, cx, cz, target=None):
        """根据地图 via_rule 生成中转站 id 列表（chain 模式可能含目标）。

        chain 模式：A1-A7 链式中转。S/T 在链上则按链序行走；
        单侧在链上则走到较近链端（进/出链）。
        """
        rule = self.current_map_data.get('via_rule') if self.current_map_data else None
        if not rule:
            return []
        mode = rule.get('mode')
        if mode == 'chain':
            chain = rule.get('chain') or []
            chain_ids = [c['id'] for c in chain if isinstance(c, dict) and c.get('id')]
            chain_pts = {c['id']: c for c in chain if isinstance(c, dict)}
            near = self.config.get('chain_near_threshold', 2.0)
            s_idx = None
            for i, sid in enumerate(chain_ids):
                st = chain_pts.get(sid)
                if st and math.hypot(st['x']-cx, st['z']-cz) < near:
                    s_idx = i; break
            t_idx = None
            if target:
                for i, sid in enumerate(chain_ids):
                    st = chain_pts.get(sid)
                    if st and math.hypot(st['x']-target['x'], st['z']-target['z']) < near:
                        t_idx = i; break
            n = len(chain_ids)
            if s_idx is not None and t_idx is not None:
                step = 1 if t_idx >= s_idx else -1
                return [chain_ids[i] for i in range(s_idx, t_idx + step, step)]
            if s_idx is not None:
                # 出发点在链上、目标在链外：走到较近的链端后退出
                if s_idx <= (n - 1) - s_idx:
                    return [chain_ids[i] for i in range(s_idx, -1, -1)]
                return [chain_ids[i] for i in range(s_idx, n)]
            if t_idx is not None:
                # 目标在链上、出发点在链外：从较近的链端进入
                if t_idx <= (n - 1) - t_idx:
                    return [chain_ids[i] for i in range(0, t_idx + 1)]
                return [chain_ids[i] for i in range(n - 1, t_idx - 1, -1)]
            return []
        # 非 chain 模式：仅当目标是特殊钓点时才启用中转
        if target is None or not self._is_via_spot(target):
            return []
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

    def _nav_timed_out(self):
        """寻路超时判断（relocate_timeout_enabled 开启时，超过设定时长放弃该目标）。"""
        d = getattr(self, '_nav_deadline', None)
        return d is not None and time.time() > d

    def _navigate_to_spot_v2(self, target):
        if self.navigation_stop_event.is_set(): return False
        self._ensure_window_active(); self.navigation_stop_event.clear()
        self.bypassed_zones.clear()
        # 寻路超时：从开始导航本目标起计时，超时则放弃（T/I/上浮循环内检查 _nav_timed_out）
        self._nav_deadline = None
        if self.config.get('relocate_timeout_enabled', True):
            self._nav_deadline = time.time() + float(self.config.get('relocate_timeout', 300))
        self.log(f"目标钓点: ({target['x']:.2f}, {target['y']:.2f}, {target['z']:.2f})","grey")
        coords = self._get_current_coords(2)
        if not coords:
            self.log("无法获取当前坐标，直接导航","red"); return self._navigate_to_target(target)
        cx,cy,cz,_,_ = coords
        # —— 子中转路径（map 配置 sub_via_stations）：起点最近钓点子中转 → 目标子中转 → 目标 ——
        sub_points = self._build_sub_via_path(cx, cz, target)
        if sub_points:
            path_points = sub_points + [('目标', target)]
            path_str = " → ".join(f"{name}({pt['x']:.1f},{pt['y']:.1f},{pt['z']:.1f})" for name, pt in path_points)
            self.log(f"【子中转】路径规划: {path_str}","blue")
            for name, pt in path_points[:-1]:
                if self.navigation_stop_event.is_set(): return False
                if not self._navigate_to_target(pt, via_mode=True):
                    self.log(f"前往{name}失败","red"); return False
                self.log(f"已到达{name}","green")
            return self._navigate_to_target(target, via_mode=False)
        # —— 原有中转逻辑（chain/fixed/conditional/decision） ——
        path_ids = self._build_via_path(cx, cz, target)
        if not path_ids:
            return self._navigate_to_target(target)
        self.log("【特殊钓点】将启用中转路径")
        self.log(f"当前位置: ({cx:.1f}, {cy:.1f}, {cz:.1f})","grey")
        # 站坐标来源：via_stations + chain 数据
        stations = {st['id']: st for st in self.via_stations if st.get('id')}
        rule = (self.current_map_data or {}).get('via_rule') or {}
        if rule.get('mode') == 'chain':
            for item in (rule.get('chain') or []):
                if isinstance(item, dict) and item.get('id'):
                    stations[item['id']] = item
        path_points = []
        for sid in path_ids:
            st = stations.get(sid)
            if st is None:
                self.log(f"中转站 {sid} 未定义，跳过该段","orange")
                continue
            path_points.append((sid, st))
        if not path_points:
            return self._navigate_to_target(target)
        # 若链路径最后一个中转站就是目标本身（T 在链上），将其作为最终目标（需抛竿）
        last_st = path_points[-1][1]
        if math.hypot(last_st['x']-target['x'], last_st['z']-target['z']) < self.config.get('via_spot_threshold',0.5):
            path_points[-1] = ('目标', target)
        else:
            path_points.append(('目标', target))
        path_str = " → ".join(f"{name}({pt['x']:.1f},{pt['y']:.1f},{pt['z']:.1f})" for name,pt in path_points)
        self.log(f"路径规划: {path_str}","blue")
        for name,pt in path_points[:-1]:
            if self.navigation_stop_event.is_set(): return False
            if not self._navigate_to_target(pt, via_mode=True):
                self.log(f"前往{name}失败","red"); return False
            self.log(f"已到达中转站{name}","green")
        return self._navigate_to_target(target, via_mode=False)

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
            time.sleep(self.config.get('hourly_check_interval',60))
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
        # 地图未录入数据提示
        if not self.fishing_spots:
            self.log(f"警告：{new_map.get('name', map_name)} 还未录入数据，程序可能出现故障","red")
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
        for mid, var in self.map_vars.items():
            var.set(mid == map_name)
        with self.config_lock:
            cur_map = self.config.get('current_map')
        if cur_map == map_name: return
        self.log(f"切换地图至 {map_name}","blue")
        self.stop_fishing(); self.navigation_stop_event.set()
        with self.config_lock:
            self.config['current_map'] = map_name
            # 四图：无鱼超时强制 70 秒；切回其他图恢复配置设置里的原值
            if map_name == 'map4':
                self.config['no_fish_timeout'] = 70.0
            else:
                self.config['no_fish_timeout'] = float(self._base_no_fish_timeout)
            nft = self.config['no_fish_timeout']
        if map_name == 'map4':
            self.log(f"四图特殊规则：无鱼超时设为 {int(nft)} 秒","orange")
        else:
            self.log(f"已恢复无鱼超时到配置值 {int(nft)} 秒","grey")
        self._refresh_throw_text()
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
        if getattr(self, 'log_watch_stop', None):
            try: self.log_watch_stop.set()
            except Exception: pass
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
                cur_map = 'map1'
                for mid, var in self.map_vars.items():
                    if var.get():
                        cur_map = mid
                        break
                self.config['current_map'] = cur_map
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