import tkinter as tk
from tkinter import messagebox

import create_user
from project.general_function import db_function,data_clear
from project.fly_ludo import fly_ludo_window
from project.bingo import bingo_window
from project.schedule import schedule_window
from project.interactive import interactive_window
from project.bigscreen import bigscreen_window
from project.rpg import rpg_window_html
from project.rpg import rpg_window
from project.upgrade import upgrade_window

class App:
    def __init__(self,username:str,user_id:int):
        # 基本配置
        self.__window = tk.Tk()
        self.__window.title("用户操作界面")
        self.__window.geometry('1200x800')
        self.__window.configure(bg='#f0f0f0')
        self.__username = username
        self.__user_id=user_id

        #建立数据库连接
        self.__user_info=db_function.UserInfo()
        self.__user_log=db_function.UserLog()

        # 创建组件
        self.create_window()

        # 居中窗口
        self.center_window()

        #启动窗口
        self.__window.mainloop()

    # —— 以下 center_window / darken_color 完全不变 —— #
    def center_window(self):
        self.__window.update_idletasks()
        w, h = self.__window.winfo_width(), self.__window.winfo_height()
        sw, sh = self.__window.winfo_screenwidth(), self.__window.winfo_screenheight()
        self.__window.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')

    def darken_color(self, color: str) -> str:
        mapping = {
            '#3498db': '#2980b9', '#2ecc71': '#27ae60', '#f39c12': '#d35400',
            '#9b59b6': '#8e44ad', '#1abc9c': '#16a085', '#e67e22': '#d35400',
            '#34495e': '#2c3e50', '#e74c3c': '#c0392b', '#2c3e50': '#1a2530',
            '#f1c40f': '#f39c12', '#d35400': '#a04000', '#7f8c8d': '#6c7a89',
            '#16a085': '#13856f', '#8e44ad': '#703691', '#c0392b': '#922b21'
        }
        return mapping.get(color, color)

    # —— 真正的改动从这里开始 —— #
    def create_window(self):
        # 1. 顶部框架（完全不变）
        top_frame = tk.Frame(self.__window, height=60, bg='#2c3e50', relief='raised', bd=2)
        top_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        top_frame.grid_propagate(False)
        tk.Label(top_frame, text=f'用户: {self.__username}', font=('Arial', 14, 'bold'),
                 fg='white', bg='#2c3e50', padx=20, pady=10).grid(row=0, column=0, sticky='w')

        tk.Button(top_frame, text='退出登录', command=lambda :[self.__user_log.user_log_insert(user_id=self.__user_id, behavior='用户退出登录'),
                                                               self.__stop(),
                                                               create_user.LoginWindow()], font=('Arial', 12),
                  bg='#e74c3c', fg='white', padx=20, pady=5, relief='raised', bd=2,
                  activebackground='#c0392b', cursor='hand2') \
            .grid(row=0, column=1, sticky='e', padx=20, pady=10)

        tk.Button(top_frame, text='修改密码', command=lambda :[self.__window.destroy(),create_user.ForgotPasswordWindow(),
                                                               self.__user_log.user_log_insert(user_id=self.__user_id,behavior='用户正在修改密码')
                                                               ],
                  font=('Arial', 12),
                  bg='#e74c3c', fg='white', padx=20, pady=5, relief='raised', bd=2,
                  activebackground='#c0392b', cursor='hand2') \
            .grid(row=0, column=2, sticky='e', padx=20, pady=10)

        top_frame.grid_columnconfigure(0, weight=1)

        # 2. 中间模式按钮框架（滚动区也不变）
        mode_frame = tk.Frame(self.__window, bg='#ecf0f1', relief='groove', bd=2)
        mode_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        mode_frame.grid_propagate(False)
        tk.Label(mode_frame, text="请选择模式", font=('Arial', 18, 'bold'),
                 fg='#2c3e50', bg='#ecf0f1').pack(pady=10)

        canvas = tk.Canvas(mode_frame, bg='#ecf0f1', highlightthickness=0)
        scrollbar = tk.Scrollbar(mode_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ecf0f1')
        scrollable_frame.bind("<Configure>",
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 3. 按钮配置表（只保留颜色和文字，事件函数全部单独写）
        self.__modes = [
            ('飞行棋', '#3498db'),
            ('宾果游戏', '#2ecc71'),
            ('bn安排', '#f39c12'),
            ('随机bn指令', '#9b59b6'),
            ('bn者现状', '#1abc9c'),
            ('剧情游戏', '#e67e22'),
            ('剧情游戏网页版', '#34495e'),
            ('表格升级', '#e74c3c'),
            ('网络配置', '#2c3e50'),
            ('安全审计', '#f1c40f'),
            ('性能优化', '#d35400'),
            ('故障排查', '#7f8c8d'),
            ('版本升级', '#16a085'),
            ('数据导入', '#8e44ad'),
            ('数据导出', '#c0392b'),
            ('系统维护', '#3498db'),
            ('帮助文档', '#27ae60'),
            ('关于系统', '#f39c12')
        ]
        # 4. 单独创建 18 个按钮，并保存到实例属性
        #    为了演示，这里只写 3 个，其余 15 个同理复制即可
        self.fly_ludo_button = self.__make_single_button(scrollable_frame, 0, 0,
                                                             '飞行棋', '#3498db', self.on_fly_ludo_button)
        self.bingo_button = self.__make_single_button(scrollable_frame, 0, 1,
                                                        '宾果游戏', '#2ecc71', self.on_bingo_button)
        self.schedule_button = self.__make_single_button(scrollable_frame, 0, 2,
                                                         'bn安排', '#f39c12', self.on_schedule_button)
        self.interactive_button = self.__make_single_button(scrollable_frame, 0, 3,
                                                             '随机bn指令', '#3498db', self.on_interactive_button)
        self.bigscreen_button = self.__make_single_button(scrollable_frame, 0, 4,
                                                        '膀胱大屏', '#2ecc71', self.on_bigscreen_button)
        self.rpg_button = self.__make_single_button(scrollable_frame, 0, 5,
                                                        '剧情游戏', '#2ecc71', self.on_rpg_button)
        self.rpg_html_button = self.__make_single_button(scrollable_frame, 1, 0,
                                                        '剧情游戏网页版', '#2ecc71', self.on_rpg_html_button)
        self.rpg_html_button = self.__make_single_button(scrollable_frame, 1, 1,
                                                        '表格升级', '#2ecc71', self.on_upgrade_button)
        # …… 同理把剩下的 15 个按钮写完，row/col 按 6 列网格递增即可 ……

        # 5. 打包滚动组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 6. 底部说明框架（完全不变）
        bottom_frame = tk.Frame(self.__window, height=100, bg='#34495e')
        bottom_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        bottom_frame.grid_propagate(False)
        info = tk.Label(bottom_frame,
                        text='提示：请选择您需要的操作模式，系统将根据您的选择提供相应的功能界面\n',
                        font=('Arial', 12), fg='#ecf0f1', bg='#34495e',
                        wraplength=1000, justify='center')
        info.pack(expand=True)

        # 7. 行列权重 + 鼠标滚轮（不变）
        self.__window.grid_rowconfigure(1, weight=1)
        self.__window.grid_columnconfigure(0, weight=1)
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        scrollable_frame.bind("<MouseWheel>",
                              lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # —— 辅助：生成单个按钮 —— #
    def __make_single_button(self, parent, row, col, text, color, cmd):
        btn = tk.Button(parent, text=text, command=cmd,
                        font=('Arial', 12, 'bold'), bg=color, fg='white',
                        padx=20, pady=15, width=12, relief='raised', bd=3,
                        activebackground=self.darken_color(color), cursor='hand2')
        btn.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
        parent.grid_columnconfigure(col, weight=1)
        return btn

    # —— 每个按钮对应一个单独的实例方法 —— #
    # 飞行棋
    def on_fly_ludo_button(self):
        self.__user_log.user_log_insert(user_id=self.__user_id,
                                        behavior='用户在主界面点击飞行棋按钮')
        self.__stop()
        fly_ludo_window.FlyLudoApp(username=self.__username,user_id=self.__user_id)

    # 宾果游戏
    def on_bingo_button(self):
        self.__user_log.user_log_insert(user_id=self.__user_id,
                                        behavior='用户在主界面点击宾果游戏按钮')
        self.__stop()
        bingo_window.BingoApp(username=self.__username,user_id=self.__user_id)

    # bn安排
    def on_schedule_button(self):
        self.__user_log.user_log_insert(user_id=self.__user_id,
                                        behavior='用户在主界面点击bn安排按钮')
        self.__stop()
        schedule_window.ScheduleApp(username=self.__username,user_id=self.__user_id)

    # 随机bn指令
    def on_interactive_button(self):
        self.__user_log.user_log_insert(user_id=self.__user_id,
                                        behavior='用户在主界面点击随机bn指令按钮')
        self.__stop()
        interactive_window.InteractiveApp(username=self.__username,user_id=self.__user_id)

    # 膀胱大屏
    def on_bigscreen_button(self):
        self.__user_log.user_log_insert(user_id=self.__user_id,
                                        behavior='用户在主界面点击膀胱大屏按钮')
        self.__stop()
        bigscreen_window.BigscreenApp(username=self.__username,user_id=self.__user_id)

    def on_rpg_button(self):
        self.__user_log.user_log_insert(user_id=self.__user_id,
                                        behavior='用户在主界面点击剧情游戏按钮')
        self.__stop()
        rpg_window.RpgApp(username=self.__username,user_id=self.__user_id)

    def on_rpg_html_button(self):
        self.__user_log.user_log_insert(user_id=self.__user_id,
                                        behavior='用户在主界面点击剧情游戏网页版按钮')
        self.__stop()
        rpg_window_html.RpgHtmlApp(username=self.__username,user_id=self.__user_id)

    def on_upgrade_button(self):
        self.__user_log.user_log_insert(user_id=self.__user_id,
                                        behavior='用户在主界面点击表格升级按钮')
        self.__stop()
        upgrade_window.UpgradeWindow(username=self.__username,user_id=self.__user_id)
    # …… 同理写剩下的 15 个 on_xxx 方法 ……

    def __stop(self):
        self.__user_info.user_info_stop()
        self.__user_log.user_log_stop()
        self.__window.destroy()