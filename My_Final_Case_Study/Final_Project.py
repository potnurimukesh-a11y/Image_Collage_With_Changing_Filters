
#!/usr/bin/env python3

# ─── imports ──────────────────────────────────────────────────────────────────
import os
import sys
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from functools import reduce
from PIL import Image, ImageTk, ImageDraw, ImageFont

from simpleimage import SimpleImage, clamp   # ← exactly as sir used it

# ─────────────────────────────────────────────────────────────────────────────
# getch — as given by sir
# ─────────────────────────────────────────────────────────────────────────────
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import tty, termios
    def getch():
        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch


# ─────────────────────────────────────────────────────────────────────────────
# FILTER FUNCTIONS — all pixel-by-pixel via SimpleImage (exactly like sir's case studies)
# ─────────────────────────────────────────────────────────────────────────────

def filter_original(path):
    # like sir's Filter-CaseStudy — just load and return
    img = SimpleImage(path)
    return img.pil_image.copy()


def single_gaussian_pass(src_img, w, h):
    """One pass of 3x3 Gaussian blur using SimpleImage._get_pix_ / _set_pix_"""
    out    = SimpleImage.blank(w, h, 'white')
    kernel = [1, 2, 1,
              2, 4, 2,
              1, 2, 1]
    ksum   = 16
    dx     = [-1, 0, 1, -1, 0, 1, -1, 0, 1]
    dy     = [-1,-1,-1,  0, 0, 0,  1, 1, 1]
    for x in range(w):
        for y in range(h):
            rs = gs = bs = 0
            for i in range(9):
                nx = max(0, min(w - 1, x + dx[i]))
                ny = max(0, min(h - 1, y + dy[i]))
                r, g, b = src_img._get_pix_(nx, ny)
                rs += r * kernel[i]
                gs += g * kernel[i]
                bs += b * kernel[i]
            out._set_pix_(x, y, (rs // ksum, gs // ksum, bs // ksum))
    return out


def filter_blur(path):
    # like sir's Blurring-TheImage case study — recursive Gaussian passes
    img  = SimpleImage(path)
    out1 = single_gaussian_pass(img,  img.width, img.height)
    out2 = single_gaussian_pass(out1, img.width, img.height)
    out3 = single_gaussian_pass(out2, img.width, img.height)
    return out3.pil_image.copy()


def filter_sharpen(path):
    img    = SimpleImage(path)
    w, h   = img.width, img.height
    out    = SimpleImage.blank(w, h, 'white')
    kernel = [0, -2, 0, -2, 9, -2, 0, -2, 0]
    dx     = [-1, 0, 1, -1, 0, 1, -1, 0, 1]
    dy     = [-1,-1,-1,  0, 0, 0,  1, 1, 1]
    for x in range(w):
        for y in range(h):
            rs = gs = bs = 0
            for i in range(9):
                nx = max(0, min(w - 1, x + dx[i]))
                ny = max(0, min(h - 1, y + dy[i]))
                r, g, b = img._get_pix_(nx, ny)
                rs += r * kernel[i]
                gs += g * kernel[i]
                bs += b * kernel[i]
            out._set_pix_(x, y, (clamp(rs), clamp(gs), clamp(bs)))
    # second sharpen pass
    out2    = SimpleImage.blank(w, h, 'white')
    kernel2 = [0, -1, 0, -1, 7, -1, 0, -1, 0]
    for x in range(w):
        for y in range(h):
            rs = gs = bs = 0
            for i in range(9):
                nx = max(0, min(w - 1, x + dx[i]))
                ny = max(0, min(h - 1, y + dy[i]))
                r, g, b = out._get_pix_(nx, ny)
                rs += r * kernel2[i]
                gs += g * kernel2[i]
                bs += b * kernel2[i]
            out2._set_pix_(x, y, (clamp(rs), clamp(gs), clamp(bs)))
    return out2.pil_image.copy()


def filter_invert(path):
    # like sir's Filter-CaseStudy pattern — for pixel in image: modify channels
    img = SimpleImage(path)
    for pixel in img:
        pixel.red   = 255 - pixel.red
        pixel.green = 255 - pixel.green
        pixel.blue  = 255 - pixel.blue
    return img.pil_image.copy()


def filter_grayscale(path):
    # same pattern as sir's case studies
    img = SimpleImage(path)
    for pixel in img:
        gray        = int(0.299 * pixel.red + 0.587 * pixel.green + 0.114 * pixel.blue)
        pixel.red   = gray
        pixel.green = gray
        pixel.blue  = gray
    return img.pil_image.copy()


def filter_day(path):
    # like sir's Filter-CaseStudy: pixel.red = pixel.red * factor
    img = SimpleImage(path)
    for pixel in img:
        pixel.red   = pixel.red   * 1.2 + 20
        pixel.green = pixel.green * 1.1 + 10
        pixel.blue  = pixel.blue  * 0.9
    return img.pil_image.copy()


def filter_evening(path):
    img = SimpleImage(path)
    for pixel in img:
        pixel.red   = pixel.red   * 1.3
        pixel.green = pixel.green * 0.85
        pixel.blue  = pixel.blue  * 0.5
    return img.pil_image.copy()


def filter_night(path):
    img = SimpleImage(path)
    for pixel in img:
        pixel.red   = pixel.red   * 0.4
        pixel.green = pixel.green * 0.4
        pixel.blue  = pixel.blue  * 0.7 + 30
    return img.pil_image.copy()


def filter_sepia(path):
    # same pattern as sir's Skin-Colour_Change case study
    img = SimpleImage(path)
    for pixel in img:
        r = pixel.red
        g = pixel.green
        b = pixel.blue
        pixel.red   = r * 0.393 + g * 0.769 + b * 0.189
        pixel.green = r * 0.349 + g * 0.686 + b * 0.168
        pixel.blue  = r * 0.272 + g * 0.534 + b * 0.131
    return img.pil_image.copy()


def filter_cool(path):
    img = SimpleImage(path)
    for pixel in img:
        pixel.red   = pixel.red   * 0.7
        pixel.green = pixel.green * 0.9
        pixel.blue  = pixel.blue  * 1.4
    return img.pil_image.copy()


# dictionary: filter name → function  (like sir used dicts in case studies)
filter_dict = {
    "Original" : filter_original,
    "Blur"     : filter_blur,
    "Sharpen"  : filter_sharpen,
    "Invert"   : filter_invert,
    "Grayscale": filter_grayscale,
    "Day"      : filter_day,
    "Evening"  : filter_evening,
    "Night"    : filter_night,
    "Sepia"    : filter_sepia,
    "Cool"     : filter_cool,
}

# list comprehension — list of filter names
filter_names = [name for name in filter_dict]


# ─────────────────────────────────────────────────────────────────────────────
# PIXEL STATS — using SimpleImage just like sir: for pixel in image
# ─────────────────────────────────────────────────────────────────────────────

def get_pixel_stats(path):
    img = SimpleImage(path)

    # list comprehension — collect all (r,g,b) tuples using sir's get_pixel
    all_pixels = [img.get_pixel(x, y)
                  for x in range(img.width)
                  for y in range(img.height)]

    # map + lambda — luminance for each pixel
    lum_list  = list(map(lambda p: 0.299*p[0] + 0.587*p[1] + 0.114*p[2], all_pixels))

    # reduce + lambda — average luminance
    total_lum = reduce(lambda a, b: a + b, lum_list)
    avg_lum   = round(total_lum / len(lum_list), 1)

    # filter + lambda — bright pixels (R+G+B > 382)
    bright_px = list(filter(lambda p: p[0]+p[1]+p[2] > 382, all_pixels))

    # filter + lambda — dark pixels (R+G+B < 128)
    dark_px   = list(filter(lambda p: p[0]+p[1]+p[2] < 128, all_pixels))

    # map + lambda — red channel average
    red_list  = list(map(lambda p: p[0], all_pixels))
    avg_red   = round(reduce(lambda a, b: a + b, red_list) / len(red_list), 1)

    return {
        "total"  : len(all_pixels),
        "avg_lum": avg_lum,
        "bright" : len(bright_px),
        "dark"   : len(dark_px),
        "avg_red": avg_red
    }


# ─────────────────────────────────────────────────────────────────────────────
# SMART LAYOUT ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def get_layout(n, canvas_w, canvas_h):
    positions = []
    if n == 1:
        positions = [(0, 0, canvas_w, canvas_h)]
    elif n == 2:
        hw = canvas_w // 2
        positions = [(0, 0, hw, canvas_h), (hw, 0, canvas_w - hw, canvas_h)]
    elif n == 3:
        lw = canvas_w // 2
        rw = canvas_w - lw
        hh = canvas_h // 2
        positions = [
            (0,  0,  lw, canvas_h),
            (lw, 0,  rw, hh),
            (lw, hh, rw, canvas_h - hh),
        ]
    elif n == 4:
        hw = canvas_w // 2
        hh = canvas_h // 2
        positions = [
            (0,  0,  hw,          hh),
            (hw, 0,  canvas_w-hw, hh),
            (0,  hh, hw,          canvas_h-hh),
            (hw, hh, canvas_w-hw, canvas_h-hh),
        ]
    elif n == 5:
        lw = canvas_w // 2
        rw = canvas_w - lw
        hh = canvas_h // 2
        positions = [
            (0,  0,  lw,    canvas_h),
            (lw, 0,  rw//2, hh),
            (lw + rw//2, 0, rw - rw//2, hh),
            (lw, hh, rw//2, canvas_h-hh),
            (lw + rw//2, hh, rw - rw//2, canvas_h-hh),
        ]
    else:
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        tw   = canvas_w // cols
        th   = canvas_h // rows
        for i in range(n):
            row = i // cols
            col = i % cols
            x0  = col * tw
            y0  = row * th
            w   = canvas_w - x0 if col == cols - 1 else tw
            h   = canvas_h - y0 if row == rows - 1 else th
            positions.append((x0, y0, w, h))
    return positions


# ─────────────────────────────────────────────────────────────────────────────
# MAKE COLLAGE — uses SimpleImage.blank + _set_pix_ exactly like sir's Reflection case study
# ─────────────────────────────────────────────────────────────────────────────

def make_collage(*args, **kwargs):
    pil_images = args[0]
    caption    = kwargs.get('caption', '')
    mat        = kwargs.get('mat', 30)

    n        = len(pil_images)
    photo_w  = 600
    photo_h  = 420
    caption_h = 70 if caption.strip() != '' else 0
    total_w  = photo_w + mat * 2
    total_h  = photo_h + mat * 2 + caption_h

    # create white mat background — SimpleImage.blank like sir used in Image_Bars_CaseStudy
    canvas = SimpleImage.blank(total_w, total_h, 'white')

    positions = get_layout(n, photo_w, photo_h)

    # list comprehension — resize each PIL image to its slot
    resized = [pil_images[i].copy().resize(
                   (positions[i][2], positions[i][3]), Image.LANCZOS)
               for i in range(n)]

    # paste each image pixel by pixel using SimpleImage._set_pix_
    # exactly like sir did in Reflection-CaseStudy with _get_pix_ / set_rgb
    for i in range(n):
        x0, y0, w, h = positions[i]
        tpx = resized[i].load()
        for tx in range(w):
            for ty in range(h):
                cx = mat + x0 + tx
                cy = mat + y0 + ty
                canvas._set_pix_(cx, cy, tpx[tx, ty])

    # convert to PIL for drawing caption text
    canvas_pil = canvas.pil_image
    draw       = ImageDraw.Draw(canvas_pil)

    # thin border lines between image slots
    for i in range(n):
        x0, y0, w, h = positions[i]
        draw.rectangle(
            [mat+x0, mat+y0, mat+x0+w-1, mat+y0+h-1],
            outline=(200, 200, 200), width=1
        )

    # caption text at bottom centre
    if caption.strip() != '':
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
            except:
                font = ImageFont.load_default()
        bbox   = draw.textbbox((0, 0), caption, font=font)
        text_w = bbox[2] - bbox[0]
        text_x = (total_w - text_w) // 2
        text_y = photo_h + mat*2 + (caption_h - (bbox[3]-bbox[1])) // 2
        draw.text((text_x, text_y), caption, fill=(30, 30, 30), font=font)

    return canvas_pil


def make_preview_with_numbers(n, canvas_w, canvas_h):
    """Layout preview with numbered slots — shown before images are loaded."""
    mat  = 20
    pw   = canvas_w - mat * 2
    ph   = canvas_h - mat * 2
    img  = Image.new('RGB', (canvas_w, canvas_h), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, canvas_w-1, canvas_h-1], outline=(180, 180, 180), width=2)

    positions = get_layout(n, pw, ph)

    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_sm  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        font_big = font_sm = ImageFont.load_default()

    slot_colors = {0:(220,80,80), 1:(80,140,220), 2:(80,180,80),
                   3:(200,140,40), 4:(160,80,200), 5:(40,180,180)}

    for i in range(n):
        x0, y0, w, h = positions[i]
        rx0, ry0     = mat+x0, mat+y0
        draw.rectangle([rx0, ry0, rx0+w-1, ry0+h-1],
                       fill=(225,225,235), outline=(160,160,160), width=2)
        label  = str(i+1)
        badge_r = 22
        cx = rx0 + w // 2
        cy = ry0 + h // 2
        draw.ellipse([cx-badge_r, cy-badge_r, cx+badge_r, cy+badge_r],
                     fill=slot_colors.get(i%6,(100,100,200)),
                     outline=(255,255,255), width=2)
        bbox = draw.textbbox((0, 0), label, font=font_big)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text((cx-tw//2, cy-th//2-2), label, fill=(255,255,255), font=font_big)
        sub  = "Image " + label
        sbbox = draw.textbbox((0, 0), sub, font=font_sm)
        draw.text((cx-(sbbox[2]-sbbox[0])//2, cy+badge_r+5),
                  sub, fill=(80,80,80), font=font_sm)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL VARIABLES
# ─────────────────────────────────────────────────────────────────────────────

num_images    = 0
image_paths   = []
pil_images    = []
edited_images = []
current_path  = ""
current_pil   = None
collage_pil   = None
stats_dict    = {"loaded": 0, "total": 0, "done": False}
tk_img_ref    = None
tk_img_ref2   = None


# ─────────────────────────────────────────────────────────────────────────────
# TKINTER ROOT
# ─────────────────────────────────────────────────────────────────────────────

root = tk.Tk()
root.title("Image Collage Maker")
root.geometry("500x400")
root.resizable(False, False)

frame = tk.Frame(root, background="pink", width=500, height=400)
frame.pack()


def clear_frame():
    for widget in frame.winfo_children():
        widget.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# PROGRESS INDICATOR
# ─────────────────────────────────────────────────────────────────────────────

def draw_progress(parent, total, current):
    for w in parent.winfo_children():
        w.destroy()
    stages    = [i+1 for i in range(total)]
    color_map = {
        "active" : {"bg": "#e94560", "fg": "white"},
        "done"   : {"bg": "#4CAF50", "fg": "white"},
        "pending": {"bg": "#cccccc", "fg": "#777777"},
    }
    for stage in stages:
        style = color_map["active"] if stage == current else \
                color_map["done"]   if stage < current  else \
                color_map["pending"]
        box = tk.Frame(parent, bg=style["bg"], relief="raised", bd=2, width=40, height=40)
        box.pack(side="left", padx=3)
        box.pack_propagate(False)
        tk.Label(box, text=str(stage), font=("Arial",12,"bold"),
                 bg=style["bg"], fg=style["fg"]).place(relx=0.5, rely=0.5, anchor="center")
        if stage < total:
            tk.Label(parent, text="→", font=("Arial",11), bg="pink").pack(side="left")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — HOME
# ══════════════════════════════════════════════════════════════════════════════

def show_home():
    global num_images, image_paths, pil_images, edited_images, stats_dict
    num_images    = 0
    image_paths   = []
    pil_images    = []
    edited_images = []
    stats_dict    = {"loaded": 0, "total": 0, "done": False}
    clear_frame()
    root.geometry("500x300")
    frame.config(width=500, height=300)

    tk.Label(frame, text="Image Collage Maker",
             font=("Arial",15,"bold"), background="pink").place(x=140, y=25)
    tk.Label(frame, text="Enter number of images:",
             font=("Arial",11), background="pink").place(x=145, y=80)

    entry_num = tk.Entry(frame, width=20, font=("Arial",12))
    entry_num.place(x=160, y=115)
    entry_num.focus()

    lbl_err = tk.Label(frame, text="", font=("Arial",10),
                       background="pink", fg="red", wraplength=420)
    lbl_err.place(x=40, y=155)

    def click_start():
        global num_images, stats_dict
        raw = entry_num.get().strip()
        try:
            n = int(raw)
            if n < 1:
                raise ValueError
        except ValueError:
            lbl_err.config(text="Please enter a positive integer like 1, 2, 3 ...")
            return
        num_images = n
        stats_dict["total"] = n
        show_load_screen()

    btn_start = tk.Button(frame, text="Start", width=10, height=1, command=click_start)
    btn_start.place(x=195, y=200)
    entry_num.bind("<Return>", lambda e: click_start())


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — LOAD IMAGE
# ══════════════════════════════════════════════════════════════════════════════

def show_load_screen():
    clear_frame()
    root.geometry("760x520")
    frame.config(width=760, height=520)

    idx = len(image_paths) + 1

    tk.Label(frame, text="Progress:", font=("Arial",10,"bold"),
             background="pink").place(x=20, y=12)
    prog_f = tk.Frame(frame, background="pink")
    prog_f.place(x=20, y=34)
    draw_progress(prog_f, num_images, idx)
    tk.Frame(frame, bg="#aaaaaa", width=720, height=2).place(x=20, y=80)

    tk.Label(frame, text="Collage Layout  (where each image will go)",
             font=("Arial",10,"bold"), background="pink").place(x=20, y=90)
    layout_canvas = tk.Canvas(frame, width=340, height=260,
                              bg="white", relief="sunken", bd=2)
    layout_canvas.place(x=20, y=115)
    layout_img = make_preview_with_numbers(num_images, 340, 260)
    global tk_img_ref2
    tk_img_ref2 = ImageTk.PhotoImage(layout_img)
    layout_canvas.create_image(170, 130, anchor="center", image=tk_img_ref2)

    tk.Label(frame, text="Load Image " + str(idx) + " of " + str(num_images),
             font=("Arial",13,"bold"), background="pink").place(x=390, y=90)
    tk.Label(frame, text="Image path:", font=("Arial",10),
             background="pink").place(x=390, y=128)

    entry_path = tk.Entry(frame, width=36, font=("Arial",10))
    entry_path.place(x=390, y=152)
    entry_path.focus()

    lbl_err = tk.Label(frame, text="", font=("Arial",9),
                       background="pink", fg="red", wraplength=340)
    lbl_err.place(x=390, y=178)

    preview_canvas = tk.Canvas(frame, width=330, height=200,
                               bg="white", relief="sunken", bd=2)
    preview_canvas.place(x=390, y=200)

    lbl_info = tk.Label(frame, text="", font=("Arial",8),
                        background="pink", wraplength=340)
    lbl_info.place(x=390, y=408)

    def click_browse():
        path = filedialog.askopenfilename(
            filetypes=[("Image files","*.jpg *.jpeg *.png *.bmp *.gif"),
                       ("All files","*.*")])
        if path:
            entry_path.delete(0,'end')
            entry_path.insert(0, path)

    def click_load():
        global tk_img_ref
        path = entry_path.get().strip()
        try:
            # load via SimpleImage — exactly as sir did: img = SimpleImage(filename)
            img = SimpleImage(path)
            pil = img.pil_image.copy()

            prev = pil.copy()
            prev.thumbnail((326, 196), Image.LANCZOS)
            tk_img_ref = ImageTk.PhotoImage(prev)
            preview_canvas.delete("all")
            preview_canvas.create_image(165, 100, anchor="center", image=tk_img_ref)

            ps = get_pixel_stats(path)
            lbl_info.config(
                text="Size:" + str(pil.width) + "x" + str(pil.height) +
                     "  Pixels:" + str(ps["total"]) +
                     "  AvgLum:" + str(ps["avg_lum"]) +
                     "  Bright:" + str(ps["bright"]) +
                     "  Dark:"   + str(ps["dark"]))

            image_paths.append(path)
            pil_images.append(pil)
            stats_dict["loaded"] += 1

            root.after(700, lambda: show_edit_screen(path, pil))

        except FileNotFoundError:
            lbl_err.config(text="File not found: '" + path + "'")
        except Exception as ex:
            lbl_err.config(text="Cannot open image: " + str(ex))

    btn_browse = tk.Button(frame, text="Browse", width=8, command=click_browse)
    btn_browse.place(x=480, y=462)
    btn_load   = tk.Button(frame, text="Load",   width=8, command=click_load)
    btn_load.place(x=580, y=462)
    entry_path.bind("<Return>", lambda e: click_load())


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 3 — EDIT IMAGE
# ══════════════════════════════════════════════════════════════════════════════

def show_edit_screen(src_path, orig_pil):
    global current_path, current_pil, tk_img_ref
    current_path = src_path
    current_pil  = orig_pil.copy()

    clear_frame()
    root.geometry("720x620")
    frame.config(width=720, height=620)

    idx   = len(edited_images) + 1
    bname = os.path.basename(src_path)

    tk.Label(frame, text="Progress:", font=("Arial",10,"bold"),
             background="pink").place(x=20, y=12)
    prog_f = tk.Frame(frame, background="pink")
    prog_f.place(x=20, y=34)
    draw_progress(prog_f, num_images, idx)
    tk.Frame(frame, bg="#aaaaaa", width=680, height=2).place(x=20, y=80)

    tk.Label(frame, text="Edit Image " + str(idx) + " / " + str(num_images) + "   —   " + bname,
             font=("Arial",12,"bold"), background="pink").place(x=20, y=90)

    edit_canvas = tk.Canvas(frame, width=420, height=410,
                            bg="white", relief="sunken", bd=2)
    edit_canvas.place(x=15, y=118)

    def refresh_preview(pil_img):
        global tk_img_ref
        prev = pil_img.copy()
        prev.thumbnail((416, 406), Image.LANCZOS)
        tk_img_ref = ImageTk.PhotoImage(prev)
        edit_canvas.delete("all")
        edit_canvas.create_image(210, 205, anchor="center", image=tk_img_ref)

    refresh_preview(orig_pil)

    tk.Label(frame, text="Filters", font=("Arial",11,"bold"),
             background="pink").place(x=455, y=118)

    selected_filter = tk.StringVar()
    selected_filter.set("Original")

    def apply_filter():
        global current_pil
        fname      = selected_filter.get()
        result_pil = filter_dict[fname](current_path)   # dictionary lookup
        current_pil = result_pil
        refresh_preview(result_pil)

    y_pos = 144
    for name in filter_names:
        tk.Radiobutton(frame, text=name, variable=selected_filter, value=name,
                       font=("Arial",10), background="pink",
                       command=apply_filter).place(x=450, y=y_pos)
        y_pos += 28

    ps = get_pixel_stats(src_path)
    stats_text = ("Pixels: "  + str(ps["total"])   + "\n" +
                  "AvgLum: "  + str(ps["avg_lum"]) + "\n" +
                  "Bright: "  + str(ps["bright"])  + "\n" +
                  "Dark: "    + str(ps["dark"])     + "\n" +
                  "AvgRed: "  + str(ps["avg_red"]))
    tk.Label(frame, text=stats_text, font=("Arial",9),
             background="pink", justify="left").place(x=452, y=445)

    def click_accept():
        edited_images.append(current_pil.copy())
        if len(edited_images) < num_images:
            show_load_screen()
        else:
            show_caption_screen()

    tk.Button(frame, text="Accept & Next", width=14, height=1,
              command=click_accept).place(x=450, y=555)
    tk.Label(frame, text="(or press Enter)", font=("Arial",9),
             background="pink").place(x=458, y=585)
    root.bind("<Return>", lambda e: click_accept())


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 4 — CAPTION
# ══════════════════════════════════════════════════════════════════════════════

def show_caption_screen():
    root.unbind("<Return>")
    clear_frame()
    root.geometry("500x280")
    frame.config(width=500, height=280)

    tk.Label(frame, text="Add a Caption  (optional)",
             font=("Arial",13,"bold"), background="pink").place(x=120, y=30)
    tk.Label(frame, text="Type your caption below.",
             font=("Arial",11), background="pink").place(x=150, y=75)
    tk.Label(frame, text="Press Enter or click OK to skip / continue.",
             font=("Arial",10), background="pink", fg="#555555").place(x=95, y=100)

    entry_cap = tk.Entry(frame, width=36, font=("Arial",13))
    entry_cap.place(x=80, y=140)
    entry_cap.focus()

    def click_ok():
        show_collage_screen(entry_cap.get().strip())

    tk.Button(frame, text="OK", width=12, height=1,
              command=click_ok).place(x=190, y=200)
    entry_cap.bind("<Return>", lambda e: click_ok())


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 5 — COLLAGE RESULT
# ══════════════════════════════════════════════════════════════════════════════

def show_collage_screen(caption):
    global collage_pil, tk_img_ref
    clear_frame()
    root.geometry("760x660")
    frame.config(width=760, height=660)

    tk.Label(frame, text="Your Collage",
             font=("Arial",14,"bold"), background="pink").place(x=310, y=10)

    # map + lambda — sizes
    sizes      = list(map(lambda img: (img.width, img.height), edited_images))
    # filter + lambda — wide images
    wide_images = list(filter(lambda img: img.width > 200, edited_images))
    # reduce + lambda — total pixel count
    total_px   = reduce(lambda acc, s: acc + s[0]*s[1], sizes, 0)

    # make_collage with *args and **kwargs — same output as before
    collage_pil = make_collage(edited_images, caption=caption, mat=30)
    stats_dict["done"] = True

    prev = collage_pil.copy()
    prev.thumbnail((700, 520), Image.LANCZOS)
    tk_img_ref = ImageTk.PhotoImage(prev)

    result_canvas = tk.Canvas(frame, width=700, height=520,
                              bg="#dddddd", relief="sunken", bd=2)
    result_canvas.place(x=28, y=48)
    result_canvas.create_image(350, 260, anchor="center", image=tk_img_ref)

    info = ("Size: " + str(collage_pil.width) + "x" + str(collage_pil.height) +
            "  |  Images: " + str(len(edited_images)) +
            "  |  Wide: "   + str(len(wide_images)) +
            "  |  TotalPx: "+ str(total_px))
    tk.Label(frame, text=info, font=("Arial",9), background="pink").place(x=30, y=578)

    def click_save():
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image","*.png"),("JPEG image","*.jpg")])
        if path:
            collage_pil.save(path)
            messagebox.showinfo("Saved", "Collage saved:\n" + path)

    tk.Button(frame, text="Save",       width=10, height=1,
              command=click_save).place(x=270, y=610)
    tk.Button(frame, text="New Collage",width=14, height=1,
              command=show_home).place(x=390, y=610)


# ─────────────────────────────────────────────────────────────────────────────
# START
# ─────────────────────────────────────────────────────────────────────────────

show_home()
root.mainloop()