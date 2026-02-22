import tkinter as tk
from tkinter import scrolledtext, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import datetime
import multiprocessing
import threading
import os
import sys

try:
    from Windows import WindowsAgent, AgentConfig
    from phone_agent.model import ModelConfig
except ImportError as e:
    messagebox.showerror("导入失败", f"无法导入模块：{str(e)}")
    sys.exit(1)

COLOR_THEME = "flatly"
FONT_MAIN = ("微软雅黑", 11)
FONT_TITLE = ("微软雅黑", 14, "bold")
FONT_LOG = ("Consolas", 10)

COLOR_WHITE = "#ffffff"
COLOR_DARK = "#212529"
COLOR_PRIMARY = "#0d6efd"
COLOR_SUCCESS = "#28a745"
COLOR_WARNING = "#ffc107"
COLOR_ERROR = "#dc3545"


def execute_task_in_process(cmd, result_queue):
    """在独立进程中执行WindowsAgent.run()"""
    try:
        model_config = ModelConfig(
            base_url="https://api-inference.modelscope.cn/v1",
            model_name="Qwen/Qwen3.5-397B-A17B",
            api_key="",
        )
        agent_config = AgentConfig(max_steps=100, verbose=True)
        agent = WindowsAgent(model_config=model_config, agent_config=agent_config)
        result = agent.run(cmd)
        result_queue.put(("success", result))
    except Exception as e:
        result_queue.put(("error", str(e)))


class WindowsControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoGLM Windows 电脑控制助手")
        self.root.geometry("1200x650")
        self.root.resizable(True, True)

        self.task_process = None
        self.task_running = False
        self.result_queue = None

        self.style = ttk.Style(COLOR_THEME)
        self.style.configure("Main.TFrame", background="#f8f9fa")
        self.style.configure("Title.TLabel", font=FONT_TITLE, foreground=COLOR_PRIMARY)
        self.style.configure("Big.TButton", font=FONT_MAIN, padding=8)

        self.create_widgets()

        self.log("📌 界面初始化完成！", "info")
        self.log("✅ Windows Agent 已就绪", "success")
        self.log("✅ 等待执行指令...", "success")

    def create_widgets(self):
        title_frame = ttk.Frame(self.root, style="Main.TFrame", padding=(20, 15, 20, 10))
        title_frame.pack(fill=X, padx=0, pady=0)

        ttk.Label(
            title_frame,
            text="AutoGLM Windows 电脑智能控制助手",
            style="Title.TLabel"
        ).pack(anchor=W)

        card_frame = ttk.Labelframe(
            self.root,
            text=" 指令执行区 ",
            style="Primary.TLabelframe",
            padding=(20, 15),
            borderwidth=2
        )
        card_frame.pack(fill=X, padx=20, pady=15)

        input_frame = ttk.Frame(card_frame, style="Main.TFrame")
        input_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            input_frame,
            text="执行指令：",
            font=FONT_MAIN,
            width=8,
            anchor=E
        ).pack(side=LEFT, padx=(0, 10))

        self.cmd_entry = ttk.Entry(
            input_frame,
            font=FONT_MAIN,
            bootstyle=PRIMARY,
            width=50
        )
        self.cmd_entry.pack(side=LEFT, fill=X, expand=True)

        btn_frame = ttk.Frame(input_frame, style="Main.TFrame")
        btn_frame.pack(side=LEFT, padx=(15, 0))

        self.run_btn = ttk.Button(
            btn_frame,
            text="执行",
            bootstyle=SUCCESS,
            style="Big.TButton",
            command=self.run_real_task,
            width=10
        )
        self.run_btn.pack(side=LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(
            btn_frame,
            text="强行终止",
            bootstyle=DANGER,
            style="Big.TButton",
            command=self.force_stop_task,
            width=10,
            state=DISABLED
        )
        self.stop_btn.pack(side=LEFT, padx=(0, 10))

        clear_btn = ttk.Button(
            btn_frame,
            text="清空",
            bootstyle=SECONDARY,
            style="Big.TButton",
            command=self.clear_all,
            width=10
        )
        clear_btn.pack(side=LEFT)

        log_card = ttk.Labelframe(
            self.root,
            text=" 执行日志 ",
            style="Info.TLabelframe",
            padding=(15, 10),
            borderwidth=2
        )
        log_card.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

        self.log_text = scrolledtext.ScrolledText(
            log_card,
            font=FONT_LOG,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=COLOR_WHITE,
            fg=COLOR_DARK,
            bd=0,
            relief=tk.FLAT
        )
        self.log_text.tag_configure("info", foreground=COLOR_DARK)
        self.log_text.tag_configure("success", foreground=COLOR_SUCCESS)
        self.log_text.tag_configure("warning", foreground=COLOR_WARNING)
        self.log_text.tag_configure("error", foreground=COLOR_ERROR)
        self.log_text.pack(fill=BOTH, expand=True, padx=5, pady=5)

        status_frame = ttk.Frame(self.root, style="Secondary.TFrame")
        status_frame.pack(fill=X, side=BOTTOM, padx=0, pady=0)

        self.status_var = tk.StringVar(value=" 📭 就绪 - 输入指令后点击执行 ")
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=FONT_MAIN,
            padding=(15, 8)
        )
        status_label.pack(anchor=W)

    def log(self, msg, level="info"):
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S.%f]")[:-3]
        self.log_text.insert(tk.END, f"{timestamp} {msg}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def run_real_task(self):
        cmd = self.cmd_entry.get().strip()

        if not cmd:
            self.log("❌ 错误：执行指令不能为空！", "warning")
            return

        if self.task_running:
            self.log("⚠️ 警告：已有任务正在执行，请先终止", "warning")
            return

        self.task_running = True
        self.run_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.status_var.set(f" 🚀 执行中 - 指令：{cmd[:20]}... ")
        self.log(f"🚀 开始执行指令：{cmd}", "info")

        self.result_queue = multiprocessing.Queue()

        self.task_process = multiprocessing.Process(
            target=execute_task_in_process,
            args=(cmd, self.result_queue),
            daemon=True
        )
        self.task_process.start()

        monitor_thread = threading.Thread(
            target=self._monitor_process,
            daemon=True
        )
        monitor_thread.start()

    def _monitor_process(self):
        self.task_process.join()

        try:
            if not self.result_queue.empty():
                status, result = self.result_queue.get()
                if status == "success":
                    self.root.after(0, lambda: self.log(f"✅ 执行成功！结果：{result}", "success"))
                    self.root.after(0, lambda: self.status_var.set(" ✅ 执行完成 - 等待新指令 "))
                else:
                    self.root.after(0, lambda: self.log(f"❌ 执行失败：{result}", "error"))
                    self.root.after(0, lambda: self.status_var.set(" ❌ 执行失败 - 请检查指令 "))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"⚠️ 获取结果出错：{str(e)}", "warning"))
        finally:
            self.root.after(0, self._cleanup_process)

    def force_stop_task(self):
        if not self.task_running or not self.task_process:
            self.log("⚠️ 没有正在执行的任务", "warning")
            return

        self.log("⏹️ 正在强制终止任务...", "warning")
        self.status_var.set(" ⏹️ 正在强制终止任务... ")
        self.stop_btn.config(state=DISABLED)

        try:
            self.task_process.terminate()
            self.task_process.join(timeout=2)

            if self.task_process.is_alive():
                self.task_process.kill()
                self.task_process.join()
                self.log("💥 任务已被强制杀死", "info")
            else:
                self.log("🛑 任务已终止", "info")

            self.status_var.set(" 🛑 任务已终止 - 等待新指令 ")

        except Exception as e:
            self.log(f"❌ 终止任务时出错：{str(e)}", "error")
        finally:
            self.root.after(0, self._cleanup_process)

    def _cleanup_process(self):
        if self.task_process:
            if self.task_process.is_alive():
                try:
                    self.task_process.terminate()
                    self.task_process.join(timeout=1)
                except:
                    pass

            self.task_process.close()
            self.task_process = None

        self.task_running = False
        self.run_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)

    def clear_all(self):
        self.cmd_entry.delete(0, tk.END)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.status_var.set(" 📌 已清空 - 等待新指令 ")
        self.log("📌 已清空输入框和执行日志", "info")


if __name__ == "__main__":
    multiprocessing.freeze_support()

    root = ttk.Window(themename=COLOR_THEME)
    app = WindowsControlGUI(root)
    root.mainloop()
