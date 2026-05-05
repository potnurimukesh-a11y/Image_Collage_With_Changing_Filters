import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from functools import reduce
from PIL import Image, ImageTk, ImageDraw, ImageFont
from simpleimage import SimpleImage
from filters import filter_dict, filter_names, get_pixel_stats

CAPTION_FONT_SIZE = 36
CAPTION_COLOR = (157, 0, 0)
CAPTION_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc", # For Mac
    "/Library/Fonts/Arial Bold.ttf", # For Linux
    "C:/Windows/Fonts/arialbd.ttf", # For Windows
    "C:/Windows/Fonts/Arial Bold.ttf",
]

def _load_caption_font():
    for path in CAPTION_FONT_PATHS:
        try:
            return ImageFont.truetype(path, CAPTION_FONT_SIZE)
        except Exception:
            continue
    return ImageFont.load_default()

def get_downloads_folder():
    """Return the user's Downloads folder path, works on Windows, macOS, Linux."""
    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    if not os.path.exists(downloads):
        os.makedirs(downloads, exist_ok=True)
    return downloads

def get_layout(n, canvas_w, canvas_h):
    positions = []
    if n == 1:
        positions = [(0, 0, canvas_w, canvas_h)]
    elif n == 2:
        hw = canvas_w // 2
        positions = [(0, 0, hw, canvas_h), (hw, 0, canvas_w - hw, canvas_h)]
    elif n == 3:
        lw = canvas_w // 2
        rw = lw
        h_for_2_3 = canvas_h // 2
        positions = [
            (0, 0, lw, canvas_h),
            (lw, 0, rw, h_for_2_3),
            (lw, h_for_2_3, rw, canvas_h - h_for_2_3)
        ]
    elif n == 4:
        hw = canvas_w // 2
        h_for_others = canvas_h // 2
        positions = [
            (0, 0, hw, h_for_others),
            (hw, 0, canvas_w - hw, h_for_others),
            (0, h_for_others, hw, canvas_h - h_for_others),
            (hw, h_for_others, canvas_w - hw, canvas_h - h_for_others),
        ]
    elif n == 5:
        lw = canvas_w // 2
        rw = canvas_w - lw
        hh = canvas_h // 2
        positions = [
            (0, 0, lw, canvas_h),
            (lw, 0, rw // 2, hh),
            (lw + rw // 2, 0, rw - rw // 2, hh),
            (lw, hh, rw // 2, canvas_h - hh),
            (lw + rw // 2, hh, rw - rw // 2, canvas_h - hh),
        ]
    else:
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        tw = canvas_w // cols
        th = canvas_h // rows
        for i in range(n):
            row = i // cols
            col = i % cols
            x0  = col * tw
            y0  = row * th
            w   = canvas_w - x0 if col == cols - 1 else tw
            h   = canvas_h - y0 if row == rows - 1 else th
            positions.append((x0, y0, w, h))
    return positions

def make_collage(*args, **kwargs):
    pil_images = args[0]
    caption = kwargs.get('caption', '')
    mat = kwargs.get('mat', 30)
    n = len(pil_images)
    photo_w = 600
    photo_h = 420
    caption_h = (CAPTION_FONT_SIZE + 28) if caption.strip() != '' else 0
    total_w = photo_w + mat * 2
    total_h = photo_h + mat * 2 + caption_h
    canvas  = SimpleImage.blank(total_w, total_h, 'white')
    positions = get_layout(n, photo_w, photo_h)
    resized = [
        pil_images[i].copy().resize((positions[i][2], positions[i][3]), Image.LANCZOS)
        for i in range(n)
    ]
    for i in range(n):
        x0, y0, w, h = positions[i]
        tpx = resized[i].load()
        for tx in range(w):
            for ty in range(h):
                canvas._set_pix_(mat + x0 + tx, mat + y0 + ty, tpx[tx, ty])

    canvas_pil = canvas.pil_image
    draw = ImageDraw.Draw(canvas_pil)
    for i in range(n):
        x0, y0, w, h = positions[i]
        draw.rectangle(
            [mat + x0, mat + y0, mat + x0 + w - 1, mat + y0 + h - 1],
            outline=(200, 200, 200), width=1
        )
    if caption.strip() != '':
        font   = _load_caption_font()
        bbox   = draw.textbbox((0, 0), caption, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (total_w - text_w) // 2
        text_y = photo_h + mat * 2 + (caption_h - text_h) // 2
        draw.text((text_x + 2, text_y + 2), caption, fill=(220, 220, 220), font=font)
        draw.text((text_x, text_y), caption, fill=CAPTION_COLOR, font=font)
    return canvas_pil

def make_preview_with_numbers(n, canvas_w, canvas_h):
    mat = 20
    pw = canvas_w - mat * 2
    ph = canvas_h - mat * 2
    img = Image.new('RGB', (canvas_w, canvas_h), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, canvas_w - 1, canvas_h - 1], outline=(180, 180, 180), width=2)
    positions = get_layout(n, pw, ph)
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_sm  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font_big = font_sm = ImageFont.load_default()
    slot_colors = {
        0: (220,  80,  80), 1: ( 80, 140, 220), 2: ( 80, 180,  80),
        3: (200, 140,  40), 4: (160,  80, 200), 5: ( 40, 180, 180),
    }
    for i in range(n):
        x0, y0, w, h = positions[i]
        rx0, ry0 = mat + x0, mat + y0
        draw.rectangle(
            [rx0, ry0, rx0 + w - 1, ry0 + h - 1],
            fill=(225, 225, 235), outline=(160, 160, 160), width=2
        )
        label   = str(i + 1)
        badge_r = 22
        cx = rx0 + w // 2
        cy = ry0 + h // 2
        draw.ellipse(
            [cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r],
            fill=slot_colors.get(i % 6, (100, 100, 200)), outline=(255, 255, 255), width=2
        )
        bbox = draw.textbbox((0, 0), label, font=font_big)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx - tw // 2, cy - th // 2 - 2), label, fill=(255, 255, 255), font=font_big)
        sub   = "Image " + label
        sbbox = draw.textbbox((0, 0), sub, font=font_sm)
        draw.text(
            (cx - (sbbox[2] - sbbox[0]) // 2, cy + badge_r + 5),
            sub, fill=(80, 80, 80), font=font_sm
        )
    return img

def draw_progress(parent, total, current):
    for w in parent.winfo_children():
        w.destroy()
    stages = [i + 1 for i in range(total)]
    color_map = {
        "active" : {"bg": "#e94560", "fg": "white"},
        "done"   : {"bg": "#4CAF50", "fg": "white"},
        "pending": {"bg": "#cccccc", "fg": "#777777"},
    }
    for stage in stages:
        style = (
            color_map["active"]  if stage == current else
            color_map["done"]    if stage <  current else
            color_map["pending"]
        )
        box = tk.Frame(parent, bg=style["bg"], relief="raised", bd=2, width=40, height=40)
        box.pack(side="left", padx=3)
        box.pack_propagate(False)
        tk.Label(
            box, text=str(stage), font=("Arial", 12, "bold"),
            bg=style["bg"], fg=style["fg"]
        ).place(relx=0.5, rely=0.5, anchor="center")
        if stage < total:
            tk.Label(parent, text="→", font=("Arial", 11), bg="pink").pack(side="left")


class CollageApp:
    def __init__(self, root):
        self.root  = root
        self.root.title("Image Collage Maker")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.frame = tk.Frame(root, background="pink", width=500, height=400)
        self.frame.pack()
        self.num_images    = 0
        self.image_paths   = []
        self.pil_images    = []
        self.edited_images = []
        self.current_path  = ""
        self.current_pil   = None
        self.collage_pil   = None
        self.stats_dict    = {"loaded": 0, "total": 0, "done": False}
        self.tk_img_ref    = None
        self.tk_img_ref2   = None

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_home(self):
        self.num_images    = 0
        self.image_paths   = []
        self.pil_images    = []
        self.edited_images = []
        self.stats_dict    = {"loaded": 0, "total": 0, "done": False}
        self.clear_frame()
        self.root.geometry("500x300")
        self.frame.config(width=500, height=300)

        tk.Label(self.frame, text="Image Collage Maker", font=("Arial", 15, "bold"), background="pink").place(x=140, y=25)
        tk.Label(self.frame, text="Enter number of images:", font=("Arial", 11), background="pink").place(x=145, y=80)
        entry_num = tk.Entry(self.frame, width=20, font=("Arial", 12))
        entry_num.place(x=160, y=115)
        entry_num.focus()
        lbl_err = tk.Label(self.frame, text="", font=("Arial", 10), background="pink", fg="red", wraplength=420)
        lbl_err.place(x=40, y=155)

        def click_start():
            raw = entry_num.get().strip()
            try:
                n = int(raw)
                if n < 1:
                    raise ValueError
            except ValueError:
                lbl_err.config(text="Please enter a positive integer like 1, 2, 3 ...")
                return
            self.num_images          = n
            self.stats_dict["total"] = n
            self.show_load_screen()

        tk.Button(self.frame, text="Start", width=10, height=1, command=click_start).place(x=195, y=200)
        entry_num.bind("<Return>", lambda e: click_start())

    def show_load_screen(self):
        self.clear_frame()
        self.root.geometry("760x520")
        self.frame.config(width=760, height=520)
        idx = len(self.image_paths) + 1
        tk.Label(self.frame, text="Progress:", font=("Arial", 10, "bold"), background="pink").place(x=20, y=12)
        prog_f = tk.Frame(self.frame, background="pink")
        prog_f.place(x=20, y=34)
        draw_progress(prog_f, self.num_images, idx)
        tk.Frame(self.frame, bg="#aaaaaa", width=720, height=2).place(x=20, y=80)
        tk.Label(
            self.frame,
            text="Collage Layout  (where each image will go)",
            font=("Arial", 10, "bold"), background="pink"
        ).place(x=20, y=90)
        layout_canvas = tk.Canvas(self.frame, width=340, height=260, bg="white", relief="sunken", bd=2)
        layout_canvas.place(x=20, y=115)
        layout_img = make_preview_with_numbers(self.num_images, 340, 260)
        self.tk_img_ref2 = ImageTk.PhotoImage(layout_img)
        layout_canvas.create_image(170, 130, anchor="center", image=self.tk_img_ref2)

        tk.Label(
            self.frame,
            text="Load Image " + str(idx) + " of " + str(self.num_images),
            font=("Arial", 13, "bold"), background="pink"
        ).place(x=390, y=90)
        tk.Label(self.frame, text="Image path:", font=("Arial", 10), background="pink").place(x=390, y=128)

        entry_path = tk.Entry(self.frame, width=36, font=("Arial", 10))
        entry_path.place(x=390, y=152)
        entry_path.focus()
        lbl_err = tk.Label(self.frame, text="", font=("Arial", 9), background="pink", fg="red", wraplength=340)
        lbl_err.place(x=390, y=178)
        preview_canvas = tk.Canvas(self.frame, width=330, height=200, bg="white", relief="sunken", bd=2)
        preview_canvas.place(x=390, y=200)
        lbl_info = tk.Label(self.frame, text="", font=("Arial", 8), background="pink", wraplength=340)
        lbl_info.place(x=390, y=408)

        def click_browse():
            path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
            )
            if path:
                entry_path.delete(0, 'end')
                entry_path.insert(0, path)

        def click_load():
            path = entry_path.get().strip()
            try:
                img = SimpleImage(path)
                pil = img.pil_image.copy()
                prev = pil.copy()
                prev.thumbnail((326, 196), Image.LANCZOS)
                self.tk_img_ref = ImageTk.PhotoImage(prev)
                preview_canvas.delete("all")
                preview_canvas.create_image(165, 100, anchor="center", image=self.tk_img_ref)
                ps = get_pixel_stats(path)
                lbl_info.config(text=(
                    "Size:" + str(pil.width) + "x" + str(pil.height) +
                    "  Pixels:" + str(ps["total"]) +
                    "  AvgLum:" + str(ps["avg_lum"]) +
                    "  Bright:" + str(ps["bright"]) +
                    "  Dark:"   + str(ps["dark"])
                ))
                self.image_paths.append(path)
                self.pil_images.append(pil)
                self.stats_dict["loaded"] += 1
                self.root.after(700, lambda: self.show_edit_screen(path, pil))
            except FileNotFoundError:
                lbl_err.config(text="File not found: '" + path + "'")
            except Exception as ex:
                lbl_err.config(text="Cannot open image: " + str(ex))

        tk.Button(self.frame, text="Browse", width=8, command=click_browse).place(x=480, y=462)
        tk.Button(self.frame, text="Load",   width=8, command=click_load).place(x=580, y=462)
        entry_path.bind("<Return>", lambda e: click_load())

    def show_edit_screen(self, src_path, orig_pil):
        self.current_path = src_path
        self.current_pil  = orig_pil.copy()
        self.clear_frame()
        self.root.geometry("720x620")
        self.frame.config(width=720, height=620)
        idx   = len(self.edited_images) + 1
        bname = os.path.basename(src_path)
        tk.Label(self.frame, text="Progress:", font=("Arial", 10, "bold"), background="pink").place(x=20, y=12)
        prog_f = tk.Frame(self.frame, background="pink")
        prog_f.place(x=20, y=34)
        draw_progress(prog_f, self.num_images, idx)
        tk.Frame(self.frame, bg="#aaaaaa", width=680, height=2).place(x=20, y=80)
        tk.Label(
            self.frame,
            text=("Edit Image " + str(idx) + " / " + str(self.num_images) + "   —   " + bname),
            font=("Arial", 12, "bold"), background="pink"
        ).place(x=20, y=90)

        edit_canvas = tk.Canvas(self.frame, width=420, height=410, bg="white", relief="sunken", bd=2)
        edit_canvas.place(x=15, y=118)

        def refresh_preview(pil_img):
            prev = pil_img.copy()
            prev.thumbnail((416, 406), Image.LANCZOS)
            self.tk_img_ref = ImageTk.PhotoImage(prev)
            edit_canvas.delete("all")
            edit_canvas.create_image(210, 205, anchor="center", image=self.tk_img_ref)

        refresh_preview(orig_pil)
        tk.Label(self.frame, text="Filters", font=("Arial", 11, "bold"), background="pink").place(x=455, y=118)
        selected_filter = tk.StringVar()
        selected_filter.set("Original")

        def apply_filter():
            fname = selected_filter.get()
            result_pil = filter_dict[fname](self.current_path)
            self.current_pil = result_pil
            refresh_preview(result_pil)

        y_pos = 144
        for name in filter_names:
            tk.Radiobutton(
                self.frame, text=name, variable=selected_filter, value=name,
                font=("Arial", 10), background="pink", command=apply_filter
            ).place(x=450, y=y_pos)
            y_pos += 28

        ps = get_pixel_stats(src_path)
        stats_text = (
            "Pixels: " + str(ps["total"])   + "\n" +
            "AvgLum: " + str(ps["avg_lum"]) + "\n" +
            "Bright: " + str(ps["bright"])  + "\n" +
            "Dark: "   + str(ps["dark"])     + "\n" +
            "AvgRed: " + str(ps["avg_red"])
        )
        tk.Label(self.frame, text=stats_text, font=("Arial", 9), background="pink", justify="left").place(x=452, y=445)

        def click_accept():
            self.edited_images.append(self.current_pil.copy())
            if len(self.edited_images) < self.num_images:
                self.show_load_screen()
            else:
                self.show_caption_screen()

        tk.Button(self.frame, text="Accept & Next", width=14, height=1, command=click_accept).place(x=450, y=555)
        tk.Label(self.frame, text="(or press Enter)", font=("Arial", 9), background="pink").place(x=458, y=585)
        self.root.bind("<Return>", lambda e: click_accept())

    def show_caption_screen(self):
        self.root.unbind("<Return>")
        self.clear_frame()
        self.root.geometry("500x280")
        self.frame.config(width=500, height=280)
        tk.Label(self.frame, text="Add a Caption  (optional)", font=("Arial", 13, "bold"), background="pink").place(x=120, y=30)
        tk.Label(self.frame, text="Type your caption below.", font=("Arial", 11), background="pink").place(x=150, y=75)
        tk.Label(
            self.frame,
            text="Press Enter or click OK to skip / continue.",
            font=("Arial", 10), background="pink", fg="#555555"
        ).place(x=95, y=100)
        entry_cap = tk.Entry(self.frame, width=36, font=("Arial", 13))
        entry_cap.place(x=80, y=140)
        entry_cap.focus()

        def click_ok():
            self.show_collage_screen(entry_cap.get().strip())

        tk.Button(self.frame, text="OK", width=12, height=1, command=click_ok).place(x=190, y=200)
        entry_cap.bind("<Return>", lambda e: click_ok())

    def show_collage_screen(self, caption):
        self.clear_frame()
        self.root.geometry("760x700")
        self.frame.config(width=760, height=700)

        tk.Label(self.frame, text="Your Collage", font=("Arial", 14, "bold"), background="pink").place(x=310, y=10)

        sizes       = list(map(lambda img: (img.width, img.height), self.edited_images))
        wide_images = list(filter(lambda img: img.width > 200, self.edited_images))
        total_px    = reduce(lambda acc, s: acc + s[0] * s[1], sizes, 0)

        self.collage_pil = make_collage(self.edited_images, caption=caption, mat=30)
        self.stats_dict["done"] = True

        prev = self.collage_pil.copy()
        prev.thumbnail((700, 520), Image.LANCZOS)
        self.tk_img_ref = ImageTk.PhotoImage(prev)

        result_canvas = tk.Canvas(self.frame, width=700, height=520, bg="#dddddd", relief="sunken", bd=2)
        result_canvas.place(x=28, y=48)
        result_canvas.create_image(350, 260, anchor="center", image=self.tk_img_ref)

        # ── info bar ──────────────────────────────────────────────────────────
        info = (
            "Size: " + str(self.collage_pil.width) + "x" + str(self.collage_pil.height) +
            "  |  Images: "  + str(len(self.edited_images)) +
            "  |  Wide: "    + str(len(wide_images)) +
            "  |  TotalPx: " + str(total_px)
        )
        tk.Label(self.frame, text=info, font=("Arial", 9), background="pink").place(x=30, y=578)

        # ── Save to Downloads button ──────────────────────────────────────────
        def click_save_downloads():
            downloads = get_downloads_folder()
            # auto-generate a unique filename
            base_name = "collage"
            ext       = ".png"
            counter   = 1
            save_path = os.path.join(downloads, base_name + ext)
            while os.path.exists(save_path):
                save_path = os.path.join(downloads, base_name + "_" + str(counter) + ext)
                counter  += 1
            try:
                self.collage_pil.save(save_path)
                messagebox.showinfo(
                    "Saved to Downloads",
                    "Collage saved to your Downloads folder:\n" + save_path
                )
            except Exception as ex:
                messagebox.showerror("Save Error", "Could not save file:\n" + str(ex))

        # ── Save As (file dialog) button ──────────────────────────────────────
        def click_save_as():
            path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg")]
            )
            if path:
                try:
                    self.collage_pil.save(path)
                    messagebox.showinfo("Saved", "Collage saved:\n" + path)
                except Exception as ex:
                    messagebox.showerror("Save Error", "Could not save file:\n" + str(ex))

        # ── New Collage button ────────────────────────────────────────────────
        def click_new_collage():
            self.show_home()

        # Button row — centred under the canvas
        btn_y = 610

        tk.Button(
            self.frame,
            text="💾  Save to Downloads",
            width=20, height=2,
            bg="#4CAF50", fg="white",
            font=("Arial", 10, "bold"),
            relief="raised", bd=3,
            command=click_save_downloads
        ).place(x=90, y=btn_y)

        tk.Button(
            self.frame,
            text="📂  Save As…",
            width=14, height=2,
            bg="#2196F3", fg="white",
            font=("Arial", 10, "bold"),
            relief="raised", bd=3,
            command=click_save_as
        ).place(x=320, y=btn_y)

        tk.Button(
            self.frame,
            text="🔄  New Collage",
            width=14, height=2,
            bg="#e94560", fg="white",
            font=("Arial", 10, "bold"),
            relief="raised", bd=3,
            command=click_new_collage
        ).place(x=510, y=btn_y)