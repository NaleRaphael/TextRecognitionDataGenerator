import random as rnd

from PIL import Image, ImageColor, ImageFont, ImageDraw, ImageFilter


def generate(
    text,
    font,
    text_color,
    font_size,
    orientation,
    space_width,
    character_spacing,
    fit,
    word_split,
    stroke_width=0, 
    stroke_fill="#282828",
    random_spacing=False,
    max_num_text_for_random_spacing=None,
    random_font_size=False,
    min_font_size=None,
    random_number_char_spacing=False,
    random_y_pos=0,
):
    """
    Parameters
    ----------
    random_spacing : bool
    max_num_text_for_random_spacing : int or None
    random_font_size : bool
    min_font_size : int or None
    random_number_char_spacing : bool
    random_y_pos : int, list, tuple or None
    """
    if orientation == 0:
        return _generate_horizontal_text(
            text,
            font,
            text_color,
            font_size,
            space_width,
            character_spacing,
            fit,
            word_split,
            stroke_width,
            stroke_fill,
            random_spacing=random_spacing,
            max_num_text_for_random_spacing=max_num_text_for_random_spacing,
            random_font_size=random_font_size,
            min_font_size=min_font_size,
            random_number_char_spacing=random_number_char_spacing,
            random_y_pos=random_y_pos,
        )
    elif orientation == 1:
        return _generate_vertical_text(
            text, font, text_color, font_size, space_width, character_spacing, fit,
            stroke_width, stroke_fill, 
        )
    else:
        raise ValueError("Unknown orientation " + str(orientation))


def _generate_horizontal_text(
    text, font, text_color, font_size, space_width, character_spacing, fit, word_split, 
    stroke_width=0, stroke_fill="#282828", random_spacing=False,
    max_num_text_for_random_spacing=None, random_font_size=False,
    min_font_size=None, random_number_char_spacing=False, random_y_pos=0,
):
    if random_spacing and max_num_text_for_random_spacing is None:
        raise ValueError('`max_num_text_for_random_spacing` should be specified when '
            '`random_spacing` is True.')
    if random_font_size and min_font_size is None:
        raise ValueError('`min_font_size` should be specified when `random_font_size` is True.')

    image_font = ImageFont.truetype(font=font, size=font_size)

    space_width = int(image_font.getsize(" ")[0] * space_width)

    if word_split:
        splitted_text = []
        for w in text.split(" "):
            splitted_text.append(w)
            splitted_text.append(" ")
        splitted_text.pop()
    else:
        splitted_text = text

    if random_spacing and len(splitted_text) < max_num_text_for_random_spacing:
        splitted_text = list(splitted_text)
        while len(splitted_text) < max_num_text_for_random_spacing:
            splitted_text.insert(rnd.randint(0, len(splitted_text)), " ")

    if random_font_size:
        font_size_list = [rnd.randint(min_font_size, font_size) for i in range(len(splitted_text))]
        font_list = [image_font.font_variant(size=v) for v in font_size_list]
        piece_widths = [
            font_list[i].getsize(p)[0] if p != " " else space_width for i, p in enumerate(splitted_text)
        ]
    else:
        font_size_list = [font_size]*len(splitted_text)
        font_list = None
        piece_widths = [
            image_font.getsize(p)[0] if p != " " else space_width for i, p in enumerate(splitted_text)
        ]

    if random_y_pos:
        if isinstance(random_y_pos, (list, tuple)):
            y_pos_list = [rnd.randint(*random_y_pos) for i in range(len(splitted_text))]
        else:
            y_pos_list = [rnd.randint(-random_y_pos, random_y_pos) for i in range(len(splitted_text))]
    else:
        y_pos_list = None

    text_width = sum(piece_widths)
    if not word_split:
        # NOTE: We should use `splitted_text` to calculate required width for
        # additional spaces here.
        text_width += character_spacing * (len(splitted_text) - 1)

    text_height = max([image_font.getsize(p)[1] for p in splitted_text])

    txt_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    txt_mask = Image.new("RGB", (text_width, text_height), (0, 0, 0))

    txt_img_draw = ImageDraw.Draw(txt_img)
    txt_mask_draw = ImageDraw.Draw(txt_mask, mode="RGB")
    txt_mask_draw.fontmode = "1"

    colors = [ImageColor.getrgb(c) for c in text_color.split(",")]
    c1, c2 = colors[0], colors[-1]

    fill = (
        rnd.randint(min(c1[0], c2[0]), max(c1[0], c2[0])),
        rnd.randint(min(c1[1], c2[1]), max(c1[1], c2[1])),
        rnd.randint(min(c1[2], c2[2]), max(c1[2], c2[2])),
    )

    stroke_colors = [ImageColor.getrgb(c) for c in stroke_fill.split(",")]
    stroke_c1, stroke_c2 = stroke_colors[0], stroke_colors[-1]

    stroke_fill = (
        rnd.randint(min(stroke_c1[0], stroke_c2[0]), max(stroke_c1[0], stroke_c2[0])),
        rnd.randint(min(stroke_c1[1], stroke_c2[1]), max(stroke_c1[1], stroke_c2[1])),
        rnd.randint(min(stroke_c1[2], stroke_c2[2]), max(stroke_c1[2], stroke_c2[2])),
    )

    current_font = image_font
    prev_number_size = current_font.getsize('0')[0]
    y = 0
    prev_text = ''
    x_offset = 0

    for i, p in enumerate(splitted_text):
        if random_number_char_spacing:
            if prev_text.isnumeric() and p.isnumeric() and rnd.randint(0, 1):
                x_offset += character_spacing

        y = y_pos_list[i] if random_y_pos else 0
        x = sum(piece_widths[0:i]) + i * character_spacing * int(not word_split)
        current_font = font_list[i] if random_font_size else image_font

        txt_img_draw.text(
            (x - x_offset, y),
            p,
            fill=fill,
            font=current_font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        txt_mask_draw.text(
            (x - x_offset, y),
            p,
            fill=((i + 1) // (255 * 255), (i + 1) // 255, (i + 1) % 255),
            font=current_font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        prev_text = p
        prev_number_size = current_font.getsize('0')[0]

    if fit:
        return txt_img.crop(txt_img.getbbox()), txt_mask.crop(txt_img.getbbox())
    else:
        return txt_img, txt_mask


def _generate_vertical_text(
    text, font, text_color, font_size, space_width, character_spacing, fit,
    stroke_width=0, stroke_fill="#282828"
):
    image_font = ImageFont.truetype(font=font, size=font_size)

    space_height = int(image_font.getsize(" ")[1] * space_width)

    char_heights = [
        image_font.getsize(c)[1] if c != " " else space_height for c in text
    ]
    text_width = max([image_font.getsize(c)[0] for c in text])
    text_height = sum(char_heights) + character_spacing * len(text)

    txt_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    txt_mask = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))

    txt_img_draw = ImageDraw.Draw(txt_img)
    txt_mask_draw = ImageDraw.Draw(txt_mask)

    colors = [ImageColor.getrgb(c) for c in text_color.split(",")]
    c1, c2 = colors[0], colors[-1]

    fill = (
        rnd.randint(c1[0], c2[0]),
        rnd.randint(c1[1], c2[1]),
        rnd.randint(c1[2], c2[2]),
    )

    stroke_colors = [ImageColor.getrgb(c) for c in stroke_fill.split(",")]
    stroke_c1, stroke_c2 = stroke_colors[0], stroke_colors[-1] 

    stroke_fill = (
        rnd.randint(stroke_c1[0], stroke_c2[0]),
        rnd.randint(stroke_c1[1], stroke_c2[1]),
        rnd.randint(stroke_c1[2], stroke_c2[2]),
    )

    for i, c in enumerate(text):
        txt_img_draw.text(
            (0, sum(char_heights[0:i]) + i * character_spacing),
            c,
            fill=fill,
            font=image_font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        txt_mask_draw.text(
            (0, sum(char_heights[0:i]) + i * character_spacing),
            c,
            fill=(i // (255 * 255), i // 255, i % 255),
            font=image_font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )

    if fit:
        return txt_img.crop(txt_img.getbbox()), txt_mask.crop(txt_img.getbbox())
    else:
        return txt_img, txt_mask
