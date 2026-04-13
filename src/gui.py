import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from config import SortConfig
from detector import YoloDetector
from sorter import AlbumSorter


class PhotoSortGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Photo Sort - YOLO")
        self.root.geometry("700x420")

        self.source_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.model_var = tk.StringVar(value="yolo26n.pt")
        self.conf_var = tk.StringVar(value="0.35")
        self.mode_var = tk.StringVar(value="copy")
        self.unknown_var = tk.StringVar(value="unknown")

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="源目录").grid(row=0, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.source_var, width=70).grid(row=1, column=0, sticky="we", padx=(0, 8))
        ttk.Button(container, text="选择", command=self._pick_source).grid(row=1, column=1)

        ttk.Label(container, text="目标目录").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(container, textvariable=self.output_var, width=70).grid(row=3, column=0, sticky="we", padx=(0, 8))
        ttk.Button(container, text="选择", command=self._pick_output).grid(row=3, column=1)

        ttk.Label(container, text="模型文件名（会缓存到项目根目录）").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(container, textvariable=self.model_var, width=40).grid(row=5, column=0, sticky="w")

        options = ttk.Frame(container)
        options.grid(row=6, column=0, sticky="w", pady=(10, 0))
        ttk.Label(options, text="置信度").pack(side=tk.LEFT)
        ttk.Entry(options, textvariable=self.conf_var, width=8).pack(side=tk.LEFT, padx=(8, 16))
        ttk.Label(options, text="未识别目录名").pack(side=tk.LEFT)
        ttk.Entry(options, textvariable=self.unknown_var, width=14).pack(side=tk.LEFT, padx=(8, 16))
        ttk.Radiobutton(options, text="复制", variable=self.mode_var, value="copy").pack(side=tk.LEFT)
        ttk.Radiobutton(options, text="移动", variable=self.mode_var, value="move").pack(side=tk.LEFT, padx=(8, 0))

        self.run_button = ttk.Button(container, text="开始整理", command=self._run_sort)
        self.run_button.grid(row=7, column=0, sticky="w", pady=(14, 0))

        self.log = tk.Text(container, height=10)
        self.log.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=(12, 0))

        container.columnconfigure(0, weight=1)
        container.rowconfigure(8, weight=1)

    def _pick_source(self) -> None:
        selected = filedialog.askdirectory(title="选择源目录")
        if selected:
            self.source_var.set(selected)

    def _pick_output(self) -> None:
        selected = filedialog.askdirectory(title="选择目标目录")
        if selected:
            self.output_var.set(selected)

    def _run_sort(self) -> None:
        source_dir = Path(self.source_var.get().strip())
        output_dir = Path(self.output_var.get().strip())

        if not source_dir.exists() or not source_dir.is_dir():
            messagebox.showerror("错误", "请先选择有效的源目录")
            return
        if not output_dir.exists() or not output_dir.is_dir():
            messagebox.showerror("错误", "请先选择有效的目标目录")
            return

        try:
            confidence = float(self.conf_var.get().strip())
        except ValueError:
            messagebox.showerror("错误", "置信度必须是数字")
            return

        self.run_button.configure(state=tk.DISABLED)
        self._append_log("正在加载模型并整理图片，请稍候...\n")

        try:
            config = SortConfig(
                source_dir=source_dir,
                output_dir=output_dir,
                model_name=self.model_var.get().strip() or "yolo26n.pt",
                confidence=confidence,
                copy_mode=self.mode_var.get() == "copy",
                unknown_bucket=self.unknown_var.get().strip() or "unknown",
            )
            summary, model_path = self._sort_once(config)
            self._append_log(f"模型路径: {model_path}\n")
            self._append_summary(summary)
        except FileNotFoundError as exc:
            self._append_log(f"自动下载失败: {exc}\n")
            if not messagebox.askyesno("模型下载失败", "自动下载失败，是否手动选择本地 .pt 模型文件？"):
                messagebox.showerror("整理失败", str(exc))
                return

            selected_model = filedialog.askopenfilename(
                title="选择本地YOLO模型",
                filetypes=[("PyTorch Model", "*.pt")],
            )
            if not selected_model:
                messagebox.showwarning("已取消", "未选择模型文件，操作已取消")
                return

            self.model_var.set(selected_model)
            retry_config = SortConfig(
                source_dir=source_dir,
                output_dir=output_dir,
                model_name=selected_model,
                confidence=confidence,
                copy_mode=self.mode_var.get() == "copy",
                unknown_bucket=self.unknown_var.get().strip() or "unknown",
            )
            summary, model_path = self._sort_once(retry_config)
            self._append_log(f"模型路径: {model_path}\n")
            self._append_summary(summary)
        except Exception as exc:
            messagebox.showerror("整理失败", str(exc))
            self._append_log(f"失败: {exc}\n")
        finally:
            self.run_button.configure(state=tk.NORMAL)

    def _sort_once(self, config: SortConfig) -> tuple[dict[str, int], Path]:
        detector = YoloDetector(model_name=config.model_name, confidence=config.confidence)
        sorter = AlbumSorter(config=config, detector=detector)
        summary = sorter.sort()
        return summary, detector.model_path

    def _append_summary(self, summary: dict[str, int]) -> None:
        if summary:
            self._append_log("整理完成：\n")
            for category, count in sorted(summary.items()):
                self._append_log(f"  - {category}: {count}\n")
            return
        self._append_log("未发现支持的图片文件。\n")

    def _append_log(self, text: str) -> None:
        self.log.insert(tk.END, text)
        self.log.see(tk.END)

    def run(self) -> None:
        self.root.mainloop()


def launch_gui() -> None:
    app = PhotoSortGUI()
    app.run()
