import numpy as np
import math


def gen_random(low, high):
    return np.random.random() * (high - low) + low


def gen_text_height(text, width, font_size, args):
    if width < 1.0:
        return 0.0
    line = math.ceil(len(text) / (width / (font_size * args.fontHorizonCoeff)))
    return line * font_size * args.fontVerticalCoeff


def update_groundtruth(groundtruth, groundtruth_element_count, typ, path, content, pos):
    groundtruth_element = {}
    groundtruth_element['id'] = typ + str(groundtruth_element_count[typ])
    groundtruth_element_count[typ] += 1
    groundtruth_element['type'] = typ
    groundtruth_element['rect'] = pos  # top bottom left right
    groundtruth_element['path'] = path
    groundtruth_element['content'] = content
    groundtruth['structure'].append(groundtruth_element)
    return True


def gen_str_config(font_size=12, margin=1.5, indent=True, section_counter=[0, 0, 0]):
    # default: margin=1.5in on 12pt doc, 1.75in on 11pt, 1.875in on 10pt
    str_indent = ""
    if indent:
        str_indent = """\setlength\parindent{{0pt}}"""

    str_config = """
    \\documentclass[{}pt]{{article}}
    \\usepackage[a4paper, margin={}in]{{geometry}}
    \\usepackage[absolute,overlay]{{textpos}}
    \\usepackage{{graphicx}}
    \\usepackage{{calc}}
    \\usepackage{{tikz}}
    \\usepackage{{enumerate}}
    \\usepackage{{color}}
    {}
    \setlength{{\TPHorizModule}}{{1pt}}
    \setlength{{\TPVertModule}}{{1pt}}
    \setcounter{{section}}{{{}}}
    \setcounter{{subsection}}{{{}}}
    \setcounter{{subsubsection}}{{{}}}
    """
    str_config = str_config.format(font_size, margin, str_indent,
               section_counter[0], section_counter[1], section_counter[2])
    return str_config


def gen_str_begin():
    str_begin = """
    \\begin{document}
    """
    return str_begin


def gen_str_end():
    str_end = """
    \end{document}
    """
    return str_end


def gen_str_openfile(filename):
    str_openfile = """
    \\newwrite\writeFH
    \immediate\openout\writeFH={}
    \\newlength{{ \myreusablelength }}
    """.format(filename)
    return str_openfile


def gen_str_closefile():
    str_closefile = """
    \immediate\closeout\writeFH
    """
    return str_closefile


def gen_str_fig(width_fake, offset_x, offset_y, width, height, img_path):
    str_fig = """
    \\begin{{textblock}}{{{}}}({}, {})
    \\noindent
    \includegraphics[width={}pt,height={}pt]{{{}}}
    \end{{textblock}}
    """.format(width_fake, offset_x, offset_y, width, height, img_path)
    return str_fig


def gen_str_table(width_fake, offset_x, offset_y, width, height, img_path):
    str_table = """
    \\begin{{textblock}}{{{}}}({}, {})
    \\noindent
    \includegraphics[width={}pt,height={}pt]{{{}}}
    \end{{textblock}}
    """.format(width_fake, offset_x, offset_y, width, height, img_path)
    return str_table


def gen_str_section(width, offset_x, offset_y, section_type, section_content, color='black'):
    str_section = """
    \\begin{{textblock}}{{{}}}({}, {})
    \color{{{}}}\{}{{{}}}
    \end{{textblock}}
    """.format(width, offset_x, offset_y, color, section_type, section_content)
    return str_section


def gen_str_section_size(width, section_font, section_content, section_number, Id):
    str_text = """
    \settowidth{{ \myreusablelength }} {{ {} \\textbf {{ {} \enspace {} }} }}
    \immediate\write\writeFH{{{}:width:\\the\myreusablelength}}
    """.format(section_font, section_number, section_content, Id)
    return str_text


def gen_str_item(item_content, color='black'):
    str_item = """\item {{\color{{{}}} {}}} """.format(color, item_content)
    return str_item


def gen_str_itemize(width, list_type, offset_x, offset_y, itemsep, str_items):
    if list_type == 'itemize':
        style = ''
    else:
        style = np.random.choice(['', '[I]', '[(a)]'])
    str_itemize = """
    \\begin{{textblock}}{{{}}}({}, {})
        \\begin{{{}}}{}
            \itemsep{}em
            {}
        \end{{{}}}
    \end{{textblock}}
    """.format(width, offset_x, offset_y, list_type, style, itemsep, str_items, list_type)
    return str_itemize


def gen_str_itemize_size(width, list_type, item_sep, str_items, Id):
    str_text = """
    \settototalheight{{ \myreusablelength }} {{ \parbox{{ {}pt }} {{
        \\begin{{{}}}
            \itemsep{}em
            {}
        \end{{{}}}
    }} }}
    \immediate\write\writeFH{{{}:height:\\the\myreusablelength}}
    """.format(width, list_type, item_sep, str_items, list_type, Id)

    str_items = str_items.split('\item ')
    item_longest_length = max(map(len, str_items))
    item_longest = filter(lambda x: len(x) == item_longest_length, str_items)
    item_longest = '1 ' + item_longest[0]

    str_text += """
    \settowidth{{ \myreusablelength }} {{ {} }}
    \immediate\write\writeFH{{{}:width:\\the\myreusablelength}}
    """.format(item_longest, Id)
    return str_text


def gen_str_text(width, offset_x, offset_y, text, color='black'):
    str_text = """
    \\begin{{textblock}}{{{}}}({}, {})
        \color{{{}}}
        {}
    \end{{textblock}}
    """.format(width, offset_x, offset_y, color, text)
    return str_text


def gen_str_text_size(width, text, Id):
    str_text = """
    \settototalheight{{ \myreusablelength }} {{ \parbox{{ {}pt }} {{ {} }} }}
    \immediate\write\writeFH{{{}:height:\\the\myreusablelength}}
    """.format(width, text, Id)
    return str_text


def gen_str_visual(offset_x, offset_y, width, height, color):
    str_visual = """
    \\begin{{textblock}}{{1000}}({}, {})
    \\begin{{tikzpicture}}
    \draw[{}] (0pt, 0pt) rectangle ({}pt, {}pt);
    \end{{tikzpicture}}
    \end{{textblock}}
    """.format(offset_x, offset_y, color, width, height)
    return str_visual


def gen_str_rectangle(offset_x, offset_y, width, height, color='black'):
    str_rectangle = """
    \\begin{{textblock}}{{1000}}({}, {})
    \\begin{{tikzpicture}}
    \draw[fill={},{}] (0pt, 0pt) rectangle ({}pt, {}pt);
    \end{{tikzpicture}}
    \end{{textblock}}
    """.format(offset_x, offset_y, color, color, width, height)
    return str_rectangle
