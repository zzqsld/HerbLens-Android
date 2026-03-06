from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "1772753925687.png"
DEFAULT_OUTPUT = ROOT / "app" / "src" / "main" / "res" / "drawable-nodpi" / "ic_launcher_source.png"
OUTPUT_SIZE = 1024


class IconCropperApp:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("Launcher Icon Cropper")
        self.master.geometry("1180x760")

        self.image_path: Path | None = None
        self.original: Image.Image | None = None
        self.display_image: Image.Image | None = None
        self.tk_image: ImageTk.PhotoImage | None = None

        self.canvas_w = 860
        self.canvas_h = 700
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.drag_start: tuple[float, float] | None = None
        self.selection: tuple[float, float, float, float] | None = None

        self._build_ui()
        if DEFAULT_INPUT.exists():
            self.load_image(DEFAULT_INPUT)

    def _build_ui(self) -> None:
        toolbar = tk.Frame(self.master)
        toolbar.pack(fill=tk.X, padx=8, pady=8)

        tk.Button(toolbar, text="Open Image", command=self.open_image).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Reset Selection", command=self.reset_selection).pack(side=tk.LEFT, padx=6)
        tk.Button(toolbar, text="Save Icon", command=self.save_icon).pack(side=tk.LEFT)

        self.path_label = tk.Label(toolbar, text="No image loaded", anchor="w")
        self.path_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        body = tk.Frame(self.master)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.canvas = tk.Canvas(body, width=self.canvas_w, height=self.canvas_h, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        right = tk.Frame(body)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(right, text="Preview (Square)", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.preview_square = tk.Label(right, bg="#f0f0f0", width=300, height=300)
        self.preview_square.pack(anchor="w", pady=(6, 16))

        tk.Label(right, text="Preview (Round)", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.preview_round = tk.Label(right, bg="#f0f0f0", width=300, height=300)
        self.preview_round.pack(anchor="w", pady=(6, 16))

        tk.Label(
            right,
            text="How to use:\n1) Drag on the image to select a square area.\n2) Adjust by dragging again.\n3) Click Save Icon.",
            justify=tk.LEFT,
            fg="#333333",
        ).pack(anchor="w")

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def open_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Choose icon image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp")],
            initialdir=str(ROOT),
        )
        if not file_path:
            return
        self.load_image(Path(file_path))

    def load_image(self, path: Path) -> None:
        try:
            image = Image.open(path).convert("RGBA")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load image:\n{exc}")
            return

        self.image_path = path
        self.original = image
        self.selection = None
        self.path_label.config(text=str(path))
        self._fit_image_to_canvas()
        self.redraw()

    def _fit_image_to_canvas(self) -> None:
        if self.original is None:
            return
        ow, oh = self.original.size
        self.scale = min(self.canvas_w / ow, self.canvas_h / oh)
        display_w = max(1, int(ow * self.scale))
        display_h = max(1, int(oh * self.scale))
        self.display_image = self.original.resize((display_w, display_h), Image.Resampling.LANCZOS)
        self.offset_x = (self.canvas_w - display_w) // 2
        self.offset_y = (self.canvas_h - display_h) // 2

    def redraw(self) -> None:
        self.canvas.delete("all")
        if self.display_image is None:
            self._clear_preview()
            return

        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas.create_image(self.offset_x, self.offset_y, image=self.tk_image, anchor=tk.NW)

        if self.selection is not None:
            x1, y1, x2, y2 = self.selection
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#00E5FF", width=2)
            self._update_preview()
        else:
            self._clear_preview()

    def on_press(self, event: tk.Event) -> None:
        if self.display_image is None:
            return
        self.drag_start = (event.x, event.y)
        self.selection = (event.x, event.y, event.x, event.y)
        self.redraw()

    def on_drag(self, event: tk.Event) -> None:
        if self.drag_start is None or self.display_image is None:
            return

        sx, sy = self.drag_start
        dx = event.x - sx
        dy = event.y - sy
        side = max(abs(dx), abs(dy))

        ex = sx + side if dx >= 0 else sx - side
        ey = sy + side if dy >= 0 else sy - side

        x1, x2 = sorted((sx, ex))
        y1, y2 = sorted((sy, ey))

        # Keep selection inside the displayed image bounds.
        min_x = self.offset_x
        min_y = self.offset_y
        max_x = self.offset_x + self.display_image.width
        max_y = self.offset_y + self.display_image.height

        x1 = max(min_x, min(x1, max_x))
        y1 = max(min_y, min(y1, max_y))
        x2 = max(min_x, min(x2, max_x))
        y2 = max(min_y, min(y2, max_y))

        current_side = min(x2 - x1, y2 - y1)
        x2 = x1 + current_side
        y2 = y1 + current_side

        self.selection = (x1, y1, x2, y2)
        self.redraw()

    def on_release(self, _event: tk.Event) -> None:
        self.drag_start = None

    def reset_selection(self) -> None:
        self.selection = None
        self.redraw()

    def _selection_to_original_box(self) -> tuple[int, int, int, int] | None:
        if self.original is None or self.display_image is None or self.selection is None:
            return None

        x1, y1, x2, y2 = self.selection
        x1 = (x1 - self.offset_x) / self.scale
        y1 = (y1 - self.offset_y) / self.scale
        x2 = (x2 - self.offset_x) / self.scale
        y2 = (y2 - self.offset_y) / self.scale

        ow, oh = self.original.size
        x1 = int(max(0, min(x1, ow)))
        y1 = int(max(0, min(y1, oh)))
        x2 = int(max(0, min(x2, ow)))
        y2 = int(max(0, min(y2, oh)))

        side = min(x2 - x1, y2 - y1)
        if side <= 1:
            return None
        return x1, y1, x1 + side, y1 + side

    def _crop_preview_image(self) -> Image.Image | None:
        if self.original is None:
            return None

        box = self._selection_to_original_box()
        if box is None:
            # Default center square when no selection is provided.
            ow, oh = self.original.size
            side = min(ow, oh)
            left = (ow - side) // 2
            top = (oh - side) // 2
            box = (left, top, left + side, top + side)

        cropped = self.original.crop(box)
        return cropped.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)

    def _update_preview(self) -> None:
        cropped = self._crop_preview_image()
        if cropped is None:
            self._clear_preview()
            return

        square = cropped.resize((280, 280), Image.Resampling.LANCZOS)
        square_tk = ImageTk.PhotoImage(square)
        self.preview_square.configure(image=square_tk)
        self.preview_square.image = square_tk

        round_img = square.copy()
        mask = Image.new("L", round_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, round_img.width, round_img.height), fill=255)
        round_img.putalpha(mask)
        round_tk = ImageTk.PhotoImage(round_img)
        self.preview_round.configure(image=round_tk)
        self.preview_round.image = round_tk

    def _clear_preview(self) -> None:
        self.preview_square.configure(image="")
        self.preview_round.configure(image="")
        self.preview_square.image = None
        self.preview_round.image = None

    def save_icon(self) -> None:
        cropped = self._crop_preview_image()
        if cropped is None:
            messagebox.showwarning("Warning", "Please load an image first.")
            return

        DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        try:
            cropped.save(DEFAULT_OUTPUT, format="PNG")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save icon:\n{exc}")
            return

        messagebox.showinfo("Saved", f"Icon saved to:\n{DEFAULT_OUTPUT}")


def main() -> None:
    root = tk.Tk()
    app = IconCropperApp(root)
    app.redraw()
    root.mainloop()


if __name__ == "__main__":
    main()
