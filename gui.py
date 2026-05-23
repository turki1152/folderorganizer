"""Desktop GUI for folderorganizer."""

import threading
import tkinter.messagebox as messagebox
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from folderorganizer import apply_plan, build_plan, format_plan_preview

PREVIEW_MAX_LINES = 500
WINDOW_TITLE = "Folder Organizer"

# Accent palette (light mode, dark mode)
COLORS = {
    "hero": ("#4f46e5", "#6366f1"),
    "hero_text": ("#ffffff", "#ffffff"),
    "card_border": ("#c4b5fd", "#4338ca"),
    "card_fill": ("#f5f3ff", "#1e1b4b"),
    "preview_border": ("#5eead4", "#0d9488"),
    "preview_fill": ("#f0fdfa", "#042f2e"),
    "preview_btn": ("#7c3aed", "#a78bfa"),
    "preview_btn_hover": ("#6d28d9", "#8b5cf6"),
    "organize_btn": ("#059669", "#34d399"),
    "organize_btn_hover": ("#047857", "#10b981"),
    "browse_btn": ("#2563eb", "#60a5fa"),
    "browse_btn_hover": ("#1d4ed8", "#3b82f6"),
    "clear_border": ("#fb7185", "#f43f5e"),
    "clear_text": ("#e11d48", "#fb7185"),
    "progress": ("#f59e0b", "#fbbf24"),
    "title": ("#4f46e5", "#a5b4fc"),
    "subtitle": ("#6b7280", "#94a3b8"),
    "status_ok": ("#059669", "#34d399"),
    "status_warn": ("#d97706", "#fbbf24"),
    "badge_bg": ("#ddd6fe", "#312e81"),
    "badge_text": ("#5b21b6", "#c4b5fd"),
    "entry_border": ("#818cf8", "#6366f1"),
}

CATEGORY_CHIP_COLORS = {
    "Images": ("#fce7f3", "#831843"),
    "Videos": ("#ede9fe", "#4c1d95"),
    "Audio": ("#ffedd5", "#7c2d12"),
    "Documents": ("#dbeafe", "#1e3a8a"),
    "Code": ("#d1fae5", "#064e3b"),
    "Archives": ("#fef3c7", "#78350f"),
}


class FolderOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(WINDOW_TITLE)
        self.geometry("1000x800")
        self.minsize(880, 660)

        self.plan = []
        self.root_path = None
        self.busy = False

        self._build_ui()
        self._set_status("Choose a folder, then preview before organizing.")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        hero = ctk.CTkFrame(self, fg_color=COLORS["hero"], corner_radius=16)
        hero.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        hero.grid_columnconfigure(0, weight=1)

        hero_inner = ctk.CTkFrame(hero, fg_color="transparent")
        hero_inner.grid(row=0, column=0, sticky="ew", padx=24, pady=20)
        hero_inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hero_inner,
            text="Folder Organizer",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=COLORS["hero_text"],
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            hero_inner,
            text="Sort messy folders by type or date — preview every move first.",
            font=ctk.CTkFont(size=14),
            text_color=("#e0e7ff", "#e0e7ff"),
        ).grid(row=1, column=0, sticky="w", pady=(6, 14))

        chips_row = ctk.CTkFrame(hero_inner, fg_color="transparent")
        chips_row.grid(row=2, column=0, sticky="w")

        for name in ("Images", "Videos", "Documents", "Code", "Archives", "Audio"):
            fg, text = CATEGORY_CHIP_COLORS[name]
            ctk.CTkLabel(
                chips_row,
                text=name,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=fg,
                text_color=text,
                corner_radius=20,
                width=72,
                height=26,
            ).pack(side="left", padx=(0, 8))

        theme_frame = ctk.CTkFrame(hero_inner, fg_color="transparent")
        theme_frame.grid(row=0, column=1, rowspan=3, sticky="ne")

        ctk.CTkLabel(
            theme_frame,
            text="Theme",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#e0e7ff", "#e0e7ff"),
        ).pack(side="left", padx=(0, 8))

        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            width=110,
            fg_color=("#4338ca", "#312e81"),
            button_color=("#3730a3", "#1e1b4b"),
            button_hover_color=("#312e81", "#0f172a"),
            command=self._on_theme_change,
        )
        self.theme_menu.set("Dark")
        self.theme_menu.pack(side="left")

        controls = ctk.CTkFrame(
            self,
            fg_color=COLORS["card_fill"],
            border_color=COLORS["card_border"],
            border_width=2,
            corner_radius=14,
        )
        controls.grid(row=1, column=0, sticky="ew", padx=24, pady=10)
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            controls,
            text="Folder",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["title"],
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 6))

        folder_row = ctk.CTkFrame(controls, fg_color="transparent")
        folder_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 14))
        folder_row.grid_columnconfigure(0, weight=1)

        self.folder_entry = ctk.CTkEntry(
            folder_row,
            placeholder_text="C:\\Users\\you\\Downloads",
            height=42,
            font=ctk.CTkFont(size=13),
            border_color=COLORS["entry_border"],
            border_width=2,
        )
        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=(4, 10))

        self.browse_btn = ctk.CTkButton(
            folder_row,
            text="Browse",
            width=110,
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["browse_btn"],
            hover_color=COLORS["browse_btn_hover"],
            command=self._browse_folder,
        )
        self.browse_btn.grid(row=0, column=1)

        options = ctk.CTkFrame(controls, fg_color="transparent")
        options.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 14))
        options.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            options,
            text="Organize by",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["title"],
        ).grid(row=0, column=0, sticky="w", padx=4, pady=(0, 10))

        self.mode_var = ctk.StringVar(value="type")
        mode_frame = ctk.CTkFrame(
            options,
            fg_color=("white", "#0f172a"),
            corner_radius=10,
            border_color=COLORS["card_border"],
            border_width=1,
        )
        mode_frame.grid(row=1, column=0, sticky="w", padx=4)

        ctk.CTkRadioButton(
            mode_frame,
            text="File type — Images, Docs, Videos…",
            variable=self.mode_var,
            value="type",
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["preview_btn"],
            hover_color=COLORS["preview_btn_hover"],
            border_color=COLORS["card_border"],
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkRadioButton(
            mode_frame,
            text="Date modified — Year-Month folders",
            variable=self.mode_var,
            value="date",
            font=ctk.CTkFont(size=13),
            fg_color=("#0891b2", "#22d3ee"),
            hover_color=("#0e7490", "#06b6d4"),
            border_color=("#67e8f9", "#155e75"),
        ).pack(anchor="w", padx=14, pady=(4, 10))

        self.recursive_switch = ctk.CTkSwitch(
            options,
            text="Include files in subfolders",
            font=ctk.CTkFont(size=13),
            fg_color=("#94a3b8", "#475569"),
            progress_color=COLORS["organize_btn"],
            button_color=COLORS["organize_btn"],
            button_hover_color=COLORS["organize_btn_hover"],
        )
        self.recursive_switch.grid(row=1, column=1, sticky="e", padx=4)

        actions = ctk.CTkFrame(controls, fg_color="transparent")
        actions.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 14))

        self.preview_btn = ctk.CTkButton(
            actions,
            text="Preview moves",
            height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["preview_btn"],
            hover_color=COLORS["preview_btn_hover"],
            command=self._start_preview,
        )
        self.preview_btn.pack(side="left", padx=6)

        self.organize_btn = ctk.CTkButton(
            actions,
            text="Organize now",
            height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["organize_btn"],
            hover_color=COLORS["organize_btn_hover"],
            state="disabled",
            command=self._confirm_organize,
        )
        self.organize_btn.pack(side="left", padx=6)

        ctk.CTkButton(
            actions,
            text="Clear",
            height=44,
            width=96,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["clear_border"],
            text_color=COLORS["clear_text"],
            hover_color=("#fff1f2", "#4c0519"),
            command=self._clear_preview,
        ).pack(side="left", padx=6)

        preview_shell = ctk.CTkFrame(
            self,
            fg_color=COLORS["preview_fill"],
            border_color=COLORS["preview_border"],
            border_width=2,
            corner_radius=14,
        )
        preview_shell.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0, 10))
        preview_shell.grid_columnconfigure(0, weight=1)
        preview_shell.grid_rowconfigure(1, weight=1)

        preview_header = ctk.CTkFrame(preview_shell, fg_color="transparent")
        preview_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        preview_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            preview_header,
            text="Preview",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0f766e", "#5eead4"),
        ).grid(row=0, column=0, sticky="w")

        self.summary_label = ctk.CTkLabel(
            preview_header,
            text="No preview yet",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["badge_bg"],
            text_color=COLORS["badge_text"],
            corner_radius=16,
            width=120,
            height=28,
        )
        self.summary_label.grid(row=0, column=1, sticky="e")

        self.preview_box = ctk.CTkTextbox(
            preview_shell,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none",
            activate_scrollbars=True,
            border_color=COLORS["preview_border"],
            border_width=1,
            fg_color=("white", "#0f172a"),
        )
        self.preview_box.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.preview_box.configure(state="disabled")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 18))
        footer.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(
            footer,
            height=10,
            corner_radius=8,
            progress_color=COLORS["progress"],
            fg_color=("#fde68a", "#422006"),
        )
        self.progress.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.progress.set(0)
        self.progress.grid_remove()

        self.status_label = ctk.CTkLabel(
            footer,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["subtitle"],
            anchor="w",
        )
        self.status_label.grid(row=1, column=0, sticky="w")

    def _on_theme_change(self, choice):
        ctk.set_appearance_mode(choice.lower())

    def _set_status(self, text, tone="normal"):
        colors = {
            "normal": COLORS["subtitle"],
            "ok": COLORS["status_ok"],
            "warn": COLORS["status_warn"],
        }
        self.status_label.configure(text=text, text_color=colors.get(tone, COLORS["subtitle"]))

    def _update_summary_badge(self, text, tone="idle"):
        styles = {
            "idle": (COLORS["badge_bg"], COLORS["badge_text"]),
            "ready": (("#bbf7d0", "#14532d"), ("#166534", "#86efac")),
            "empty": (("#ffedd5", "#7c2d12"), ("#c2410c", "#fdba74")),
        }
        bg, fg = styles.get(tone, styles["idle"])
        self.summary_label.configure(text=text, fg_color=bg, text_color=fg)

    def _set_busy(self, busy):
        self.busy = busy
        state = "disabled" if busy else "normal"
        self.preview_btn.configure(state=state)
        self.organize_btn.configure(
            state="disabled" if busy or not self.plan else "normal"
        )
        self.folder_entry.configure(state=state)
        self.browse_btn.configure(state=state)
        self.theme_menu.configure(state=state)
        self.recursive_switch.configure(state=state)

    def _show_progress(self, show):
        if show:
            self.progress.grid()
            self.progress.set(0)
        else:
            self.progress.grid_remove()
            self.progress.set(0)

    def _browse_folder(self):
        path = filedialog.askdirectory(title="Select folder to organize")
        if path:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, path)
            self._set_status(f"Selected: {path}", tone="ok")

    def _resolve_folder(self):
        raw = self.folder_entry.get().strip().strip('"')
        if not raw:
            messagebox.showwarning(WINDOW_TITLE, "Please choose a folder first.")
            return None

        folder = Path(raw).expanduser()
        if not folder.exists() or not folder.is_dir():
            messagebox.showerror(
                WINDOW_TITLE,
                "That path is not a valid folder.\n\nCheck the path and try again.",
            )
            return None

        return folder.resolve()

    def _clear_preview(self):
        self.plan = []
        self.root_path = None
        self.preview_box.configure(state="normal")
        self.preview_box.delete("1.0", "end")
        self.preview_box.configure(state="disabled")
        self._update_summary_badge("No preview yet", tone="idle")
        self.organize_btn.configure(state="disabled")
        self._set_status("Preview cleared.")

    def _start_preview(self):
        if self.busy:
            return

        folder = self._resolve_folder()
        if folder is None:
            return

        self.root_path = folder
        mode = self.mode_var.get()
        recursive = bool(self.recursive_switch.get())

        self._set_busy(True)
        self._show_progress(True)
        self._set_status("Scanning folder…", tone="warn")

        def work():
            try:
                plan = build_plan(folder, mode, recursive)
                self.after(0, lambda: self._show_preview(plan, folder))
            except OSError as exc:
                self.after(0, lambda: self._on_error(f"Could not scan folder:\n{exc}"))
            finally:
                self.after(0, lambda: self._finish_task())

        threading.Thread(target=work, daemon=True).start()

    def _show_preview(self, plan, folder):
        self.plan = plan
        self.preview_box.configure(state="normal")
        self.preview_box.delete("1.0", "end")

        if not plan:
            self.preview_box.insert("1.0", "Nothing to organize — this folder is already tidy.")
            self._update_summary_badge("0 files", tone="empty")
            self.organize_btn.configure(state="disabled")
            self._set_status("No files need moving in this folder.", tone="warn")
        else:
            lines, truncated = format_plan_preview(plan, folder, max_lines=PREVIEW_MAX_LINES)
            body = "\n".join(lines)
            if truncated:
                remaining = len(plan) - PREVIEW_MAX_LINES
                body += f"\n\n… and {remaining} more file(s)"
            self.preview_box.insert("1.0", body)
            count = len(plan)
            self._update_summary_badge(
                f"{count} file{'s' if count != 1 else ''} ready",
                tone="ready",
            )
            self.organize_btn.configure(state="normal")
            self._set_status("Preview ready — review the list, then click Organize now.", tone="ok")

        self.preview_box.configure(state="disabled")

    def _confirm_organize(self):
        if self.busy or not self.plan:
            return

        count = len(self.plan)
        answer = messagebox.askyesno(
            WINDOW_TITLE,
            f"Move {count} file{'s' if count != 1 else ''} into organized folders?\n\n"
            "This cannot be undone automatically. Make sure the preview looks correct.",
            icon="warning",
        )
        if not answer:
            return

        self._set_busy(True)
        self._show_progress(True)
        self._set_status("Organizing files…", tone="warn")

        plan_copy = list(self.plan)

        def work():
            try:
                total = len(plan_copy)

                def on_progress(done, out_of):
                    progress = done / out_of
                    self.after(0, lambda p=progress: self.progress.set(p))

                apply_plan(plan_copy, on_progress=on_progress)
                self.after(0, lambda: self._on_organize_done(total))
            except OSError as exc:
                self.after(0, lambda: self._on_error(f"Organize stopped:\n{exc}"))
            finally:
                self.after(0, lambda: self._finish_task())

        threading.Thread(target=work, daemon=True).start()

    def _on_organize_done(self, count):
        self._clear_preview()
        messagebox.showinfo(
            WINDOW_TITLE,
            f"Done! Moved {count} file{'s' if count != 1 else ''}.",
        )
        self._set_status(f"Successfully moved {count} file(s).", tone="ok")

    def _on_error(self, message):
        messagebox.showerror(WINDOW_TITLE, message)
        self._set_status("Something went wrong. Try again.", tone="warn")

    def _finish_task(self):
        self._show_progress(False)
        self._set_busy(False)
        if self.plan:
            self.organize_btn.configure(state="normal")


def main():
    app = FolderOrganizerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
