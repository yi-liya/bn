import logging
import threading
import tkinter as tk
import inspect
import os
import json
from tkinter import ttk, messagebox

import main_window
from project.general_function import db_function

current_filename = os.path.basename(__file__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# 用户登录类
class LoginWindow:
    """
    用户登录窗口类
    
    提供完整的用户登录功能，包括：
    - 用户名/密码验证
    - 记住我选项（UI层面，未实现持久化）
    - 跳转到注册界面
    - 跳转到忘记密码界面
    - 登录成功后启动主窗口（使用多线程）
    - 记录用户登录日志
    
    Attributes:
        __window (tk.Tk): 登录窗口根组件
        __user_info (db_function.UserInfo): 用户信息数据库操作对象
        __user_log (db_function.UserLog): 用户日志数据库操作对象
        username_entry (ttk.Entry): 用户名输入框
        password_entry (ttk.Entry): 密码输入框
        remember_var (tk.BooleanVar): "记住我"复选框状态变量
    """
    def __init__(self):
        """
        初始化登录窗口
        
        创建登录界面，包括：
        1. 初始化Tkinter窗口并设置属性
        2. 建立数据库连接
        3. 将窗口居中显示
        4. 创建所有UI组件
        5. 启动主事件循环
        """
        self.__window = tk.Tk()
        self.__window.title("用户登录")
        self.__window.geometry("400x300")
        self.__window.resizable(False, False)

        # 建立数据库连接
        self.__user_info = db_function.UserInfo()
        self.__user_log = db_function.UserLog()

        # 设置窗口居中
        self.__center_window()

        # 创建界面元素
        self.__create_widgets()

        # 加载已保存的凭据（账号+密码）
        self.__load_saved_login()

        #运行
        self.__run()

    def __center_window(self):
        """将窗口居中显示"""
        self.__window.update_idletasks()
        width = self.__window.winfo_width()
        height = self.__window.winfo_height()
        x = (self.__window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.__window.winfo_screenheight() // 2) - (height // 2)
        self.__window.geometry(f"{width}x{height}+{x}+{y}")

    def __create_widgets(self):
        """
        创建并布局所有界面元素
        
        创建登录窗口的所有UI组件，包括：
        - 标题标签
        - 用户名/密码输入框
        - 记住我复选框
        - 登录/取消按钮
        - 忘记密码和注册链接
        """
        # 主框架
        main_frame = ttk.Frame(self.__window, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 标题
        title_label = ttk.Label(main_frame, text="用户登录", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 用户名标签和输入框
        username_label = ttk.Label(main_frame, text="用户名:")
        username_label.grid(row=1, column=0, sticky="w", pady=5)

        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        self.username_entry.focus()

        # 密码标签和输入框
        password_label = ttk.Label(main_frame, text="密码:")
        password_label.grid(row=2, column=0, sticky="w", pady=5)

        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        # 记住我复选框
        self.remember_var = tk.BooleanVar()
        remember_check = ttk.Checkbutton(main_frame, text="记住密码", variable=self.remember_var)
        remember_check.grid(row=3, column=1, sticky="w", pady=5, padx=(10, 0))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        # 登录按钮
        login_button = ttk.Button(button_frame, text="登录", command=self.__login)
        login_button.pack(side="left", padx=(0, 10))

        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.__cancel)
        cancel_button.pack(side="left")

        # 忘记密码链接
        forgot_label = ttk.Label(main_frame, text="修改密码?", foreground="blue", cursor="hand2")
        forgot_label.grid(row=5, column=1, sticky="e", pady=5, padx=(0, 10))
        forgot_label.bind("<Button-1>", lambda e: self.__forgot_password())

        # 注册链接
        register_frame = ttk.Frame(main_frame)
        register_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Label(register_frame, text="还没有账户?").pack(side="left")
        register_label = ttk.Label(register_frame, text="立即注册", foreground="blue", cursor="hand2")
        register_label.pack(side="left", padx=(5, 0))
        register_label.bind("<Button-1>", lambda e: self.__register())

        # 配置网格权重
        self.__window.columnconfigure(0, weight=1)
        self.__window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 绑定回车键登录
        self.__window.bind("<Return>", lambda event: self.__login())

    def encrypt(self, data: str) -> str:
        """占位加密函数（实际未加密）"""
        return data 

    def decrypt(self, data: str) -> str:
        """占位解密函数（实际未解密）"""
        return data  

    def __save_login_info(self, username: str, password: str, remember: bool):
        """智能保存登录信息：如果加密函数有效则加密，否则明文"""
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, 'saved_login.json')

        if not remember:
            # 删除文件
            try:
                    if os.path.exists(config_file):
                        os.remove(config_file)
                        logging.info("已删除保存的登录信息")
            except Exception as e:
                logging.warning(f"删除登录信息失败: {e}")
            return

        # === 判断加密函数是否生效 ===
        test_plain = "TEST_123"
        test_encrypted = self.encrypt(test_plain)
        use_encryption = (test_encrypted != test_plain)

        try:
            if use_encryption:
                saved_password = self.encrypt(password)
                logging.debug("使用加密保存密码")
            else:
                saved_password = password  # 明文
                logging.debug("使用明文保存密码")

            login_data = {
                "username": username,
                "password": saved_password,
                "encrypted": use_encryption  # 标记是否加密（用于加载时判断）
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(login_data, f, ensure_ascii=False)
            logging.info("已保存登录信息")
        except Exception as e:
            logging.error(f"保存登录信息失败: {e}")
            messagebox.showwarning("警告", "无法保存登录信息。")

    def __load_saved_login(self):
        """智能加载：根据标记或内容判断是否需要解密"""
        config_file = os.path.join(os.path.dirname(__file__), 'config', 'saved_login.json')
        if not os.path.exists(config_file):
            return

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            username = data.get("username", "")
            saved_password = data.get("password", "")
            encrypted_flag = data.get("encrypted", False)  # 默认 False（兼容旧明文文件）

            if not username or not saved_password:
                return

            # === 尝试判断是否需要解密 ===
            need_decrypt = encrypted_flag

            # 兼容旧版：如果没有 encrypted 字段，再试探性判断
            if "encrypted" not in data:
                # 如果解密后和原串不同，可能是密文？但不可靠
                # 更安全做法：默认不解密（即当作明文）
                need_decrypt = False

            if need_decrypt:
                try:
                    password = self.decrypt(saved_password)
                except Exception:
                    # 解密失败，当作明文处理（降级）
                    password = saved_password
                    logging.warning("解密失败，回退到明文")
            else:
                password = saved_password  # 明文

            # 填充 UI
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, username)
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)
            self.remember_var.set(True)
            logging.info("已自动填充登录信息")

        except Exception as e:
            logging.warning(f"加载登录信息失败: {e}")        

    def __login(self):
        """
        处理用户登录验证
        
        登录流程：
        1. 获取用户名和密码输入
        2. 验证输入不为空
        3. 检查用户名是否存在
        4. 验证密码是否正确
        5. 记录登录日志
        6. 更新最后登录时间
        7. 在新线程中启动主窗口（避免阻塞UI）
        
        异常处理：
        - 使用try-except捕获数据库操作可能的异常
        - 记录详细的错误日志，包括文件名和函数名
        """

        # 获取用户名和密码（去除首尾空格）
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # 验证用户名不为空
        if not username:
            messagebox.showwarning("警告", "请输入用户名")
            return

        # 验证密码不为空
        if not password:
            messagebox.showwarning("警告", "请输入密码")
            return

        # 验证用户名是否存在
        if username in self.__user_info.user_info_select_account():
            try:
                # 验证密码是否正确
                if password in self.__user_info.user_info_select_password(username)[0]:
                    # 获取用户显示名称
                    name = self.__user_info.user_info_select_name(account=username)[0][0]

                    # 定义在主线程中启动主窗口的函数
                    def main_window_start(name, user_id):
                        self.__window.destroy()  # 关闭登录窗口
                        main_window.App(name, user_id)  # 创建主窗口

                    # 记录用户登录成功的日志
                    self.__user_log.user_log_insert(
                        user_id=self.__user_info.user_info_select_user_id(username)[0][0],
                        behavior='用户登录成功'
                    )

                    # ========== 新增：处理“记住密码”逻辑（使用 keyring 安全存储） ==========
                    self.__save_login_info(username, password, self.remember_var.get())

                    # 更新最后使用的账号（用于下次启动时尝试加载）
                    try:
                        config_dir = os.path.join(os.path.dirname(__file__), 'config')
                        os.makedirs(config_dir, exist_ok=True)
                        config_file = os.path.join(config_dir, 'last_account.json')
                        with open(config_file, 'w', encoding='utf-8') as f:
                            json.dump({"last_account": username}, f, ensure_ascii=False)
                    except Exception as e:
                        logging.warning(f"保存最后账号记录失败: {e}")

                    # 在新线程中启动主窗口（daemon=True表示主线程退出时子线程自动结束）
                    main_window_t1 = threading.Thread(
                        target=main_window_start(name, self.__user_info.user_info_select_user_id(username)[0][0]),
                        daemon=True
                    )
                    main_window_t1.start()

                    # 更新用户最后登录时间
                    self.__user_info.user_info_update_run_time(self.__user_info.user_info_select_user_id(username)[0][0])

                else:
                    # 密码错误处理
                    messagebox.showerror("错误", "密码错误")
                    self.password_entry.delete(0, tk.END)

            except Exception as e:
                # 记录详细的异常日志（文件名+函数名+异常信息）
                logging.error(f'文件{current_filename}---函数{inspect.currentframe().f_code.co_name}---异常{e}')

        else:
            # 用户名不存在处理
            messagebox.showerror("错误", "用户不存在")
            self.username_entry.delete(0, tk.END)

    def __cancel(self):
        """取消操作"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.remember_var.set(False)

    def __forgot_password(self):
        """忘记密码处理"""
        self.__window.destroy()
        ForgotPasswordWindow()

    def __register(self):
        """注册处理"""
        self.__window.destroy()
        UserRegistrationApp()

    def __run(self):
        """运行窗口"""
        self.__window.mainloop()

    def __del__(self):
        """析构函数，关闭数据库连接"""
        self.__user_info.user_info_stop()
        self.__user_log.user_log_stop()


class UserRegistrationApp:
    """
    用户注册窗口类
    
    提供新用户注册功能，包括：
    - 用户名、账号、密码输入
    - 密码确认验证
    - 账号唯一性检查
    - 注册成功后自动跳转到登录界面
    
    Attributes:
        __root (tk.Tk): 注册窗口根组件
        __user_info (db_function.UserInfo): 用户信息数据库操作对象
        __user_log (db_function.UserLog): 用户日志数据库操作对象
        name_entry (ttk.Entry): 用户名输入框
        account_entry (ttk.Entry): 账号输入框
        password_entry (ttk.Entry): 密码输入框
        confirm_entry (ttk.Entry): 确认密码输入框
    """
    def __init__(self):
        """
        初始化注册窗口
        
        创建注册界面，包括：
        1. 初始化Tkinter窗口并设置属性
        2. 建立数据库连接
        3. 创建并布局所有UI组件
        4. 窗口居中显示
        5. 启动主事件循环
        """
        self.__root = tk.Tk()
        self.__root.title("用户注册")
        self.__root.geometry("450x400")
        self.__root.resizable(False, False)

        #建立数据库连接
        self.__user_info = db_function.UserInfo()
        self.__user_log = db_function.UserLog()

        # 创建界面元素
        self.__create_widgets()

        #居中
        self.__center_window()

        self.__root.mainloop()

    def __center_window(self):
        """将窗口居中显示"""
        self.__root.update_idletasks()
        width = self.__root.winfo_width()
        height = self.__root.winfo_height()
        x = (self.__root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.__root.winfo_screenheight() // 2) - (height // 2)
        self.__root.geometry(f"{width}x{height}+{x}+{y}")

    def __create_widgets(self):
        """
        创建并布局注册窗口的所有界面元素
        
        创建注册表单，包括：
        - 标题
        - 用户名输入框
        - 账号输入框
        - 密码输入框
        - 确认密码输入框
        - 注册/重置按钮
        - 返回登录链接
        """
        # 主框架
        main_frame = ttk.Frame(self.__root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="用户注册", font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 25))

        # 表单框架
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X)

        # 用户名
        name_label = ttk.Label(form_frame, text="用户名:")
        name_label.grid(row=0, column=0, sticky="w", pady=8)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=8, padx=(10, 0))

        # 账号
        account_label = ttk.Label(form_frame, text="账号:")
        account_label.grid(row=1, column=0, sticky="w", pady=8)
        self.account_entry = ttk.Entry(form_frame, width=30)
        self.account_entry.grid(row=1, column=1, pady=8, padx=(10, 0))

        # 密码
        password_label = ttk.Label(form_frame, text="密码:")
        password_label.grid(row=2, column=0, sticky="w", pady=8)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=8, padx=(10, 0))

        # 确认密码
        confirm_label = ttk.Label(form_frame, text="确认密码:")
        confirm_label.grid(row=3, column=0, sticky="w", pady=8)
        self.confirm_entry = ttk.Entry(form_frame, width=30, show="*")
        self.confirm_entry.grid(row=3, column=1, pady=8, padx=(10, 0))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=25)

        # 注册按钮
        register_button = ttk.Button(button_frame, text="注册", command=self.__register_user)
        register_button.pack(side=tk.LEFT, padx=(0, 15))

        # 重置按钮
        reset_button = ttk.Button(button_frame, text="重置", command=self.__reset_form)
        reset_button.pack(side=tk.LEFT)

        # 返回登录链接
        login_frame = ttk.Frame(main_frame)
        login_frame.pack(pady=10)

        ttk.Label(login_frame, text="已有账户?").pack(side=tk.LEFT)
        login_label = ttk.Label(login_frame, text="立即登录", foreground="blue", cursor="hand2")
        login_label.pack(side=tk.LEFT, padx=(5, 0))
        login_label.bind("<Button-1>", lambda e: self.__show_login())

    def __register_user(self):
        """
        处理用户注册逻辑
        
        注册流程：
        1. 获取所有输入字段
        2. 验证输入不为空
        3. 验证两次输入的密码一致
        4. 检查账号是否已存在
        5. 插入新用户信息到数据库
        6. 记录注册日志
        7. 显示成功消息并跳转到登录界面
        """
        # 获取表单数据
        name = self.name_entry.get().strip()
        account = self.account_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_entry.get()

        # 验证表单数据
        if not name:
            messagebox.showwarning("警告", "请输入用户名")
            return

        if not account:
            messagebox.showwarning("警告", "请输入账号")
            return

        if not password:
            messagebox.showwarning("警告", "请输入密码")
            return

        if password != confirm_password:
            messagebox.showerror("错误", "两次输入的密码不一致")
            self.password_entry.delete(0, tk.END)
            self.confirm_entry.delete(0, tk.END)
            return

        # 检查账号是否已存在
        if account in self.__user_info.user_info_select_account():
            messagebox.showerror("错误", "该账号已存在，请使用其它的账号")
            return
        self.__user_info.user_info_insert(name=name, password=password, account=account)
        self.__user_log.user_log_insert(self.__user_info.user_info_select_user_id(account=account)[0],
                                        behavior='用户注册成功')
        messagebox.showinfo("成功", "注册成功,请登录！")
        self.__root.destroy()
        LoginWindow()

    def __reset_form(self):
        """重置表单"""
        self.name_entry.delete(0, tk.END)
        self.account_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_entry.delete(0, tk.END)

    def __show_login(self):
        """显示登录界面"""
        self.__root.destroy()
        LoginWindow()

    def __del__(self):
        """析构函数，关闭数据库连接"""
        self.__user_info.user_info_stop()
        pass


class ForgotPasswordWindow:
    """
    忘记密码/重置密码窗口类
    
    提供密码重置功能，包括：
    - 输入账号验证身份
    - 输入新密码
    - 确认新密码
    - 更新数据库中的密码
    - 记录密码修改日志
    
    Attributes:
        __root (tk.Tk): 密码重置窗口根组件
        __account_entry (ttk.Entry): 账号输入框
        __new_password_entry (ttk.Entry): 新密码输入框
        __confirm_entry (ttk.Entry): 确认密码输入框
        __user_info (db_function.UserInfo): 用户信息数据库操作对象
        __user_log (db_function.UserLog): 用户日志数据库操作对象
    """
    def __init__(self):
        """
        初始化密码重置窗口
        
        创建密码重置界面，包括：
        1. 初始化Tkinter窗口并设置属性
        2. 建立数据库连接
        3. 创建并布局所有UI组件
        4. 窗口居中显示
        5. 启动主事件循环
        """
        self.__root = tk.Tk()
        self.__root.title("修改密码")
        self.__root.geometry("400x350")
        self.__root.resizable(False, False)
        self.__root.grab_set()  # 模态窗口

        # 连接数据库
        self.__user_info = db_function.UserInfo()
        self.__user_log = db_function.UserLog()

        # 创建界面元素
        self.__create_widgets()

        # 居中显示
        self.__center_window()
        self.__root.mainloop()

    def __center_window(self):
        """将窗口居中显示"""
        self.__root.update_idletasks()
        width = self.__root.winfo_width()
        height = self.__root.winfo_height()
        x = (self.__root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.__root.winfo_screenheight() // 2) - (height // 2)
        self.__root.geometry(f"{width}x{height}+{x}+{y}")

    def __create_widgets(self):
        """
        创建并布局密码重置窗口的所有界面元素
        
        创建密码重置表单，包括：
        - 标题
        - 说明文本
        - 账号输入框
        - 新密码输入框
        - 确认密码输入框
        - 重置密码/取消按钮
        """
        # 主框架
        main_frame = ttk.Frame(self.__root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="修改密码", font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 25))

        # 说明文本
        desc_label = ttk.Label(main_frame, text="请输入您的账号和新的密码",
                               font=("Arial", 10))
        desc_label.pack(pady=(0, 20))

        # 表单框架
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X)

        # 账号
        account_label = ttk.Label(form_frame, text="账号:")
        account_label.grid(row=0, column=0, sticky="w", pady=8)
        self.__account_entry = ttk.Entry(form_frame, width=30)
        self.__account_entry.grid(row=0, column=1, pady=8, padx=(10, 0))
        self.__account_entry.focus()

        # 新密码
        new_password_label = ttk.Label(form_frame, text="新密码:")
        new_password_label.grid(row=1, column=0, sticky="w", pady=8)
        self.__new_password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.__new_password_entry.grid(row=1, column=1, pady=8, padx=(10, 0))

        # 确认新密码
        confirm_label = ttk.Label(form_frame, text="确认密码:")
        confirm_label.grid(row=2, column=0, sticky="w", pady=8)
        self.__confirm_entry = ttk.Entry(form_frame, width=30, show="*")
        self.__confirm_entry.grid(row=2, column=1, pady=8, padx=(10, 0))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        # 重置密码按钮
        reset_button = ttk.Button(button_frame, text="重置密码", command=self.__reset_password)
        reset_button.pack(side=tk.LEFT, padx=(0, 15))

        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=lambda: [self.__root.destroy(), LoginWindow()])
        cancel_button.pack(side=tk.LEFT)

    def __reset_password(self):
        """
        处理密码重置逻辑
        
        重置流程：
        1. 获取所有输入字段
        2. 验证输入不为空
        3. 验证两次输入的新密码一致
        4. 检查账号是否存在
        5. 更新数据库中的密码
        6. 记录密码修改日志
        7. 显示成功消息并返回登录界面
        """
        # 获取表单数据
        account = self.__account_entry.get().strip()
        new_password = self.__new_password_entry.get()
        confirm_password = self.__confirm_entry.get()

        # 验证表单数据
        if not account:
            messagebox.showwarning("警告", "请输入账号")
            return

        if not new_password:
            messagebox.showwarning("警告", "请输入新密码")
            return

        if new_password != confirm_password:
            messagebox.showerror("错误", "两次输入的密码不一致")
            self.__new_password_entry.delete(0, tk.END)
            self.__confirm_entry.delete(0, tk.END)
            return

        # 更新密码
        if account in self.__user_info.user_info_select_account():
            self.__user_info.user_info_update_password(account, new_password)
            self.__user_log.user_log_insert(user_id=self.__user_info.user_info_select_user_id(account=account)[0][0],
                                            behavior='重置账户的密码')

            messagebox.showinfo("成功", "密码重置成功！")

            self.__root.destroy()
            self.__user_info.user_info_stop()
            self.__user_log.user_log_stop()
            LoginWindow()
        else:
            messagebox.showerror("错误", "账号不存在")


if __name__ == "__main__":
    app = LoginWindow()

    # 查看所有日志
    # a=db_function.UserLog()
    # print(a.user_log_select())

    # 清空日志
    # a=db_function.UserLog()
    # a.user_log_delete_all()

    # 删除用户
    # a=db_function.UserInfo()
    # a.user_info_delete('11')
    # print(a.user_info_select())

    # 查看所有用户信息
    # a=db_function.UserInfo()
    # print(a.user_info_select())

    # a=db_function.FlyLudoInput()
    # print(a.fly_ludo_input_select_id())