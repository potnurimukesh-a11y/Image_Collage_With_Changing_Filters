from functools import reduce
from simpleimage import SimpleImage, clamp

def filter_original(path):
    img = SimpleImage(path)
    return img.pil_image.copy()

def single_gaussian_pass(src_img, w, h):
    out = SimpleImage.blank(w, h, 'white')
    kernel = [1, 2, 1, 2, 4, 2, 1, 2, 1]
    ksum = 16
    dx = [-1, 0, 1, -1, 0, 1, -1, 0, 1]
    dy = [-1,-1,-1,  0, 0, 0,  1, 1, 1]
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
    img  = SimpleImage(path)
    out1 = single_gaussian_pass(img,  img.width, img.height)
    out2 = single_gaussian_pass(out1, img.width, img.height)
    out3 = single_gaussian_pass(out2, img.width, img.height)
    return out3.pil_image.copy()

def filter_sharpen(path):
    img = SimpleImage(path)
    w, h = img.width, img.height
    out = SimpleImage.blank(w, h, 'white')
    kernel = [0, -2, 0, -2, 9, -2, 0, -2, 0]
    dx = [-1, 0, 1, -1, 0, 1, -1, 0, 1]
    dy = [-1,-1,-1,  0, 0, 0,  1, 1, 1]
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
    out2 = SimpleImage.blank(w, h, 'white')
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
    img = SimpleImage(path)
    for pixel in img:
        pixel.red   = 255 - pixel.red
        pixel.green = 255 - pixel.green
        pixel.blue  = 255 - pixel.blue
    return img.pil_image.copy()

def filter_grayscale(path):
    img = SimpleImage(path)
    for pixel in img:
        gray = int(0.299 * pixel.red + 0.587 * pixel.green + 0.114 * pixel.blue)
        pixel.red = gray
        pixel.green = gray
        pixel.blue = gray
    return img.pil_image.copy()

def filter_day(path):
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
        pixel.red = pixel.red   * 0.4
        pixel.green = pixel.green * 0.4
        pixel.blue = pixel.blue  * 0.7 + 30
    return img.pil_image.copy()

def filter_sepia(path):
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
filter_names = [name for name in filter_dict]

def get_pixel_stats(path):
    img = SimpleImage(path)
    all_pixels = [img.get_pixel(x, y) for x in range(img.width) for y in range(img.height)]
    lum_list  = list(map(lambda p: 0.299*p[0] + 0.587*p[1] + 0.114*p[2], all_pixels))
    total_lum = reduce(lambda a, b: a + b, lum_list)
    avg_lum   = round(total_lum / len(lum_list), 1)
    bright_px = list(filter(lambda p: p[0]+p[1]+p[2] > 382, all_pixels))
    dark_px   = list(filter(lambda p: p[0]+p[1]+p[2] < 128, all_pixels))
    red_list  = list(map(lambda p: p[0], all_pixels))
    avg_red   = round(reduce(lambda a, b: a + b, red_list) / len(red_list), 1)
    return {
        "total"  : len(all_pixels),
        "avg_lum": avg_lum,
        "bright" : len(bright_px),
        "dark"   : len(dark_px),
        "avg_red": avg_red,
    }