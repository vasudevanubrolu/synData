import argparse
from PIL import Image
import numpy as np
import re
import math
import json
import sys
import utils 

# parse argument
parser = argparse.ArgumentParser(description='Generate PDF')
parser.add_argument('--prefix', type=str, default='template', help='prefix for output files')
parser.add_argument('--pathFig', type=str, default='./figures/',
                    help='path to figures')
parser.add_argument('--listFig', type=str, default='list.txt',
                    help='path to figures list')
parser.add_argument('--listChart', type=str, default='list_chart.txt',
                    help='path to chart list')
parser.add_argument('--pathTable', type=str, default='./tables/',
                    help='path to tables')
parser.add_argument('--listTable', type=str, default='list.txt',
                    help='path to tables list')
parser.add_argument('--pathText', type=str, default='./text/',
                    help='path to text')
parser.add_argument('--listText', type=str, default='list.txt',
                    help='path to text list')
parser.add_argument('--pathCaption', type=str, default='./figures/annotations/coco_raw.json',
                    help='path to caption')

parser.add_argument('--fontSizeMin', type=int, default=10, help='min font size')
parser.add_argument('--fontSizeMax', type=int, default=12, help='max font size')
parser.add_argument('--fontHorizonCoeff', type=float, default=0.5, help='actual font size horizontally (e.g. font_size*0.5)')
parser.add_argument('--fontVerticalCoeff', type=float, default=1.25, help='actual font size vertically (e.g. font_size*1.25)')
parser.add_argument('--marginMin', type=float, default=0.50, help='min margin (inches)')
parser.add_argument('--marginMax', type=float, default=1.25, help='max margin (inches)')
parser.add_argument('--paraSkipRatio', type=float, default=1.0, help='paragraph skipping ratio')

parser.add_argument('--textMaxLine', type=int, default=10, help='max number of lines of text')

parser.add_argument('--sectionMaxWord', type=int, default=7, help='max words in section')
parser.add_argument('--sectionType', default=['section', 'subsection', 'subsubsection'], help='section type')
parser.add_argument('--sectionFontSize', default={'10': {'section': 14.4, 'subsection': 12, 'subsubsection': 10},
                                                  '11': {'section': 14.4, 'subsection': 12, 'subsubsection': 10.95},
                                                  '12': {'section': 17.28, 'subsection': 14.4, 'subsubsection': 12}
                                                  }, help='section font size')
parser.add_argument('--sectionFont', default={'section': '\Large',
                                              'subsection': '\large',
                                              'subsubsection': ''}, help='section font size')

parser.add_argument('--listType', default=['itemize', 'enumerate'], help='list type')
parser.add_argument('--itemNumberMax', type=int, default=5, help='max number of items')
parser.add_argument('--itemLengthMin', type=int, default=10, help='min chars in item')
parser.add_argument('--itemLengthMax', type=int, default=200, help='max chars in item')
parser.add_argument('--itemVaryRatio', type=float, default=0.4, help='item length vary ratio')

parser.add_argument('--imgWidthMinRatio', type=float, default=0.6, help='min img width (ratio\\textwidth)')
parser.add_argument('--imgWidthMaxRatio', type=float, default=1.0, help='max img width (ratio\\textwidth)')
parser.add_argument('--imgHeightMaxRatio', type=float, default=0.5, help='max img height (ratio\\textwidth)')

parser.add_argument('--figChart', type=float, default=0.5, help='probability that a figure is a chart (or others)')
parser.add_argument('--figCaptionPrefix', default=['Fig. ', 'Figure ', 'figure ', 'fig. '], help='figure caption type')
parser.add_argument('--figNoCaption', type=float, default=0.1, help='probability that a figure has no caption')
parser.add_argument('--figCaptionSpace', type=float, default=2.0, help='space between figure and caption when horizontally (2.0em)')
parser.add_argument('--capLengthMin', type=int, default=20, help='min chars in caption')
parser.add_argument('--capLengthMax', type=int, default=300, help='min chars in caption')

parser.add_argument('--inches2Pt', type=float, default=72.27, help='1 in = 72.27 pt')
parser.add_argument('--pageWidth', type=float, default=8.3, help='page width (inches)')
parser.add_argument('--pageHeight', type=float, default=11.7, help='page height (inches)')
parser.add_argument('--distribution',
                    default={'figure': 0.2, 'table': 0.4, 'section': 0.5, 'list': 0.6, 'text': 0.98, 'line': 1.00},
                    help='probability: fig | table | section | list | text')

parser.add_argument('--pageNum', type=int, default=100, help='number of pdf pages to generate')

parser.add_argument('--colors', default=['black', 'red', 'blue', 'green', 'cyan', 'magenta', 'yellow'], help='colors supported in latex')
parser.add_argument('--hasColors', type=float, default=0.2, help='probability to have color')

parser.add_argument('--hasHorizonBorder', type=float, default=0.5, help='prob of having border line')
parser.add_argument('--hasVerticalBorder', type=float, default=0.1, help='prob of having border line')
parser.add_argument('--borderLineMaxWidth', type=int, default=8, help='prob of having border line')

parser.add_argument('--maxColumns', type=int, default=3, help='prob of having border line')

parser.add_argument('--maxNumElements', type=int, default=100, help='prob of having border line')

args = parser.parse_args()

# lists
fig_list = np.genfromtxt(args.pathFig + args.listFig, delimiter='*', dtype=None)
chart_list = np.genfromtxt(args.pathFig + args.listChart, delimiter='*', dtype=None)
table_list = np.genfromtxt(args.pathTable + args.listTable, delimiter='*', dtype=None)
text_list = np.genfromtxt(args.pathText + args.listText, delimiter='*', dtype=None)
with open(args.pathCaption, 'r') as fin:
    caption_list = json.load(fin)

# main
args.pageWidth = args.pageWidth * args.inches2Pt
args.pageHeight = args.pageHeight * args.inches2Pt
for it_page in range(args.pageNum):
    print(it_page)
    try:
        fout_name = '{}{}.tex'.format(args.prefix, it_page)

        groundtruth = {}
        groundtruth['type'] = 'Doc'
        groundtruth['structure'] = []
        groundtruth_element_count = {'figure': 0, 'table': 0, 'caption': 0,
                                     'section': np.random.randint(1, 10), 'subsection': np.random.randint(1, 10),
                                     'subsubsection': np.random.randint(1, 10), 'list': 0, 'text': 0}
        output = ''

        font_size = np.random.randint(args.fontSizeMin, args.fontSizeMax+1)
        margin = np.random.random() * (args.marginMax - args.marginMin) + args.marginMin
        marginPt = margin * args.inches2Pt
        indent = np.random.choice([True, False])
        output += utils.gen_str_config(font_size, margin, indent,
                                       [groundtruth_element_count['section'],
                                        groundtruth_element_count['subsection'],
                                        groundtruth_element_count['subsubsection']])
        output += utils.gen_str_begin()
        output += utils.gen_str_openfile(fout_name + '.out')

        offset_x = marginPt
        offset_y = marginPt

        # border line
        if np.random.random() < args.hasColors:
            color = np.random.choice(args.colors)
        else:
            color = 'black'

        line_width = np.random.randint(1, args.borderLineMaxWidth)
        if np.random.random() < args.hasHorizonBorder:
            output += utils.gen_str_rectangle(offset_x, np.random.randint(1, offset_y-line_width), args.pageWidth - 2 * marginPt, line_width, color)
        if np.random.random() < args.hasHorizonBorder:
            output += utils.gen_str_rectangle(offset_x, np.random.randint(args.pageHeight-marginPt, args.pageHeight-line_width), args.pageWidth - 2 * marginPt, line_width, color)
        if np.random.random() < args.hasVerticalBorder:
            output += utils.gen_str_rectangle(np.random.randint(1, offset_y-line_width), offset_y, line_width, args.pageHeight - 2 * marginPt, color)
        if np.random.random() < args.hasVerticalBorder:
            output += utils.gen_str_rectangle(np.random.randint(args.pageWidth-marginPt, args.pageWidth-line_width), offset_y, line_width, args.pageHeight - 2 * marginPt, color)

        # main
        it_element = 0
        num_columns = np.random.randint(1, args.maxColumns + 1)
        margin_delta = np.random.random() * args.marginMin * args.inches2Pt
        column_width = (args.pageWidth - 2 * marginPt - num_columns * margin_delta) / num_columns
        for it_column in range(num_columns):
            offset_x = marginPt + it_column * column_width + it_column * margin_delta
            offset_y = marginPt
            column_right = marginPt + (it_column + 1) * column_width + it_column * margin_delta

            while offset_y < (args.pageHeight - marginPt):
                if it_element > args.maxNumElements:
                    break
                it_element += 1

                opt = np.random.random()
                if opt < args.distribution['figure']:
                    if np.random.random() > args.figChart:
                        # image caption
                        img_element = np.random.choice(caption_list)
                        img_caption = np.random.choice(args.figCaptionPrefix) + str(np.random.randint(1, 10)) + ' ' + \
                                                       np.random.choice(img_element['captions'])
                        if np.random.random() < args.figNoCaption:
                            img_caption = ''

                        # get image
                        img_path = args.pathFig + img_element['file_path']
                    else:
                        # image caption
                        img_caption = ''
                        textfile = np.random.choice(text_list)
                        with open(args.pathText + textfile) as f:
                            text = f.read()
                            text_length = np.random.randint(args.capLengthMin, args.capLengthMax)
                            text_starter = np.random.randint(len(text) - text_length)
                            text = text[text_starter:(text_starter + text_length)]
                            section = img_caption

                        # img path
                        img_path = args.pathFig + np.random.choice(chart_list)

                    img_width_ratio = utils.gen_random(args.imgWidthMinRatio, args.imgWidthMaxRatio)
                    img_width = int(img_width_ratio * column_width)

                    img = Image.open(img_path)
                    img_height = img_width * img.size[1] / img.size[0]
                    if img_height > args.imgHeightMaxRatio * column_width:
                        img_height = img_height * 0.5
                        img_width = img_width * 0.5
                    if img_height > args.pageHeight - offset_y - marginPt:
                        continue

                    # caption
                    if img_width_ratio > 0.8 or num_columns > 1:
                        caption_location = np.random.choice(['top', 'bottom'])
                    else:
                        caption_location = np.random.choice(['top', 'bottom', 'left', 'right'])

                    if caption_location in ['top', 'bottom']:
                        caption_width = min(column_width, len(img_caption) * args.fontHorizonCoeff * font_size)
                    else:
                        caption_width = min((1 - img_width_ratio) * column_width,
                                            1.0 * img_width, len(img_caption) * args.fontHorizonCoeff * font_size)
                    caption_height = utils.gen_text_height(img_caption, caption_width, font_size, args)

                    # add element to latex
                    if img_caption == '':
                        # add figure
                        offset_x = offset_x + (column_width - img_width) / 2
                        output += utils.gen_str_fig(img_width, offset_x, offset_y, img_width, img_height, img_path)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'figure', img_path, '', [offset_y, offset_y + img_height,
                                                                          offset_x, offset_x + img_width])
                        # adjust
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_y += img_height + font_size * args.paraSkipRatio
                    elif caption_location == 'top':
                        # add caption
                        offset_x = offset_x + (column_width - caption_width) / 2
                        output += utils.gen_str_text(caption_width, offset_x, offset_y, img_caption)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'caption', '', img_caption, [offset_y, offset_y + caption_height,
                                                                              offset_x, offset_x + caption_width])
                        offset_y += caption_height
                        # add figure
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_x = offset_x + (column_width - img_width) / 2
                        output += utils.gen_str_fig(img_width, offset_x, offset_y, img_width, img_height, img_path)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'figure', img_path, '', [offset_y, offset_y + img_height,
                                                                          offset_x, offset_x + img_width])
                        # adjust
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_y += img_height + font_size * args.paraSkipRatio
                    elif caption_location == 'bottom':
                        # add figure
                        offset_x = offset_x + (column_width - img_width) / 2
                        output += utils.gen_str_fig(img_width, offset_x, offset_y, img_width, img_height, img_path)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'figure', img_path, '', [offset_y, offset_y + img_height,
                                                                          offset_x, offset_x + img_width])
                        offset_y += img_height + font_size * args.paraSkipRatio
                        # add caption
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_x = offset_x + (column_width - caption_width) / 2
                        output += utils.gen_str_text(caption_width, offset_x, offset_y, img_caption)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'caption', '', img_caption, [offset_y, offset_y + caption_height,
                                                                              offset_x, offset_x + caption_width])
                        # adjust
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_y += caption_height
                    elif caption_location == 'left':
                        # add caption
                        offset_x = offset_x + (column_width - img_width - caption_width) / 2
                        offset_y_old = offset_y
                        if caption_height < img_height:
                            caption_align = np.random.choice(['top', 'center', 'bottom'])
                            if caption_align == 'center':
                                offset_y += (img_height - caption_height) / 2
                            elif caption_align == 'bottom':
                                offset_y += img_height - caption_height
                        output += utils.gen_str_text(caption_width, offset_x, offset_y, img_caption)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'caption', '', img_caption, [offset_y, offset_y + caption_height,
                                                                              offset_x, offset_x + caption_width])
                        offset_y = offset_y_old
                        # add figure
                        offset_x += caption_width + font_size * args.figCaptionSpace
                        output += utils.gen_str_fig(img_width, offset_x, offset_y, img_width, img_height, img_path)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'figure', img_path, '', [offset_y, offset_y + img_height,
                                                                          offset_x, offset_x + img_width])
                        # adjust
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_y += max(img_height, caption_height) + font_size * args.paraSkipRatio
                    else:  # right
                        # add figure
                        offset_x = offset_x + (column_width - img_width - caption_width) / 2
                        output += utils.gen_str_fig(img_width, offset_x, offset_y, img_width, img_height, img_path)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'figure', img_path, '', [offset_y, offset_y + img_height,
                                                                          offset_x, offset_x + img_width])
                        # add caption
                        offset_x += img_width + font_size * args.figCaptionSpace
                        offset_y_old = offset_y
                        if caption_height < img_height:
                            caption_align = np.random.choice(['top', 'center', 'bottom'])
                            if caption_align == 'center':
                                offset_y += (img_height - caption_height) / 2
                            elif caption_align == 'bottom':
                                offset_y += img_height - caption_height
                        output += utils.gen_str_text(caption_width, offset_x, offset_y, img_caption)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'caption', '', img_caption, [offset_y, offset_y + caption_height,
                                                                              offset_x, offset_x + caption_width])
                        # adjust
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_y = offset_y_old
                        offset_y += max(img_height, caption_height) + font_size * args.paraSkipRatio
                elif opt < args.distribution['table']:
                    # copied from above
                    # image caption
                    img_caption = ''
                    textfile = np.random.choice(text_list)
                    with open(args.pathText + textfile) as f:
                        text = f.read()
                        text_length = np.random.randint(args.capLengthMin, args.capLengthMax)
                        text_starter = np.random.randint(len(text) - text_length)
                        text = text[text_starter:(text_starter + text_length)]
                        section = img_caption

                    # img path
                    img_path = args.pathTable + np.random.choice(table_list)

                    img_width_ratio = utils.gen_random(args.imgWidthMinRatio, args.imgWidthMaxRatio)
                    img_width = int(img_width_ratio * column_width)

                    img = Image.open(img_path)
                    img_height = img_width * img.size[1] / img.size[0]
                    if img_height > args.imgHeightMaxRatio * column_width:
                        img_height = img_height * 0.5
                        img_width = img_width * 0.5
                    if img_height > args.pageHeight - offset_y - marginPt:
                        continue

                    # caption
                    if img_width_ratio > 0.8 or num_columns > 1:
                        caption_location = np.random.choice(['top', 'bottom'])
                    else:
                        caption_location = np.random.choice(['top', 'bottom', 'left', 'right'])

                    if caption_location in ['top', 'bottom']:
                        caption_width = min(column_width, len(img_caption) * args.fontHorizonCoeff * font_size)
                    else:
                        caption_width = min((1 - img_width_ratio) * column_width,
                                            1.0 * img_width, len(img_caption) * args.fontHorizonCoeff * font_size)
                    caption_height = utils.gen_text_height(img_caption, caption_width, font_size, args)

                    # add element to latex
                    if img_caption == '':
                        # add figure
                        offset_x = offset_x + (column_width - img_width) / 2
                        output += utils.gen_str_fig(img_width, offset_x, offset_y, img_width, img_height, img_path)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'table', img_path, '', [offset_y, offset_y + img_height,
                                                                          offset_x, offset_x + img_width])
                        # adjust
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_y += img_height + font_size * args.paraSkipRatio
                    elif caption_location == 'top':
                        # add caption
                        offset_x = offset_x + (column_width - caption_width) / 2
                        output += utils.gen_str_text(caption_width, offset_x, offset_y, img_caption)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'caption', '', img_caption, [offset_y, offset_y + caption_height,
                                                                              offset_x, offset_x + caption_width])
                        offset_y += caption_height
                        # add figure
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_x = offset_x + (column_width - img_width) / 2
                        output += utils.gen_str_fig(img_width, offset_x, offset_y, img_width, img_height, img_path)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'table', img_path, '', [offset_y, offset_y + img_height,
                                                                          offset_x, offset_x + img_width])
                        # adjust
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_y += img_height + font_size * args.paraSkipRatio
                    elif caption_location == 'bottom':
                        # add figure
                        offset_x = offset_x + (column_width - img_width) / 2
                        output += utils.gen_str_fig(img_width, offset_x, offset_y, img_width, img_height, img_path)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'table', img_path, '', [offset_y, offset_y + img_height,
                                                                          offset_x, offset_x + img_width])
                        offset_y += img_height + font_size * args.paraSkipRatio
                        # add caption
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_x = offset_x + (column_width - caption_width) / 2
                        output += utils.gen_str_text(caption_width, offset_x, offset_y, img_caption)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'caption', '', img_caption, [offset_y, offset_y + caption_height,
                                                                              offset_x, offset_x + caption_width])
                        # adjust
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_y += caption_height
                    elif caption_location == 'left':
                        # add caption
                        offset_x = offset_x + (column_width - img_width - caption_width) / 2
                        offset_y_old = offset_y
                        if caption_height < img_height:
                            caption_align = np.random.choice(['top', 'center', 'bottom'])
                            if caption_align == 'center':
                                offset_y += (img_height - caption_height) / 2
                            elif caption_align == 'bottom':
                                offset_y += img_height - caption_height
                        output += utils.gen_str_text(caption_width, offset_x, offset_y, img_caption)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'caption', '', img_caption, [offset_y, offset_y + caption_height,
                                                                              offset_x, offset_x + caption_width])
                        offset_y = offset_y_old
                        # add figure
                        offset_x += caption_width + font_size * args.figCaptionSpace
                        output += utils.gen_str_fig(img_width, offset_x, offset_y, img_width, img_height, img_path)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'table', img_path, '', [offset_y, offset_y + img_height,
                                                                          offset_x, offset_x + img_width])
                        # adjust
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_y += max(img_height, caption_height) + font_size * args.paraSkipRatio
                    else:  # right
                        # add figure
                        offset_x = offset_x + (column_width - img_width - caption_width) / 2
                        output += utils.gen_str_fig(img_width, offset_x, offset_y, img_width, img_height, img_path)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'table', img_path, '', [offset_y, offset_y + img_height,
                                                                          offset_x, offset_x + img_width])
                        # add caption
                        offset_x += img_width + font_size * args.figCaptionSpace
                        offset_y_old = offset_y
                        if caption_height < img_height:
                            caption_align = np.random.choice(['top', 'center', 'bottom'])
                            if caption_align == 'center':
                                offset_y += (img_height - caption_height) / 2
                            elif caption_align == 'bottom':
                                offset_y += img_height - caption_height
                        output += utils.gen_str_text(caption_width, offset_x, offset_y, img_caption)
                        # groundtruth
                        utils.update_groundtruth(groundtruth, groundtruth_element_count,
                                                 'caption', '', img_caption, [offset_y, offset_y + caption_height,
                                                                              offset_x, offset_x + caption_width])
                        # adjust
                        offset_x = marginPt + it_column * column_width + it_column * margin_delta
                        offset_y = offset_y_old
                        offset_y += max(img_height, caption_height) + font_size * args.paraSkipRatio

                elif opt < args.distribution['section']:
                    section = ''

                    textfile = np.random.choice(text_list)
                    with open(args.pathText + textfile) as f:
                        text = f.read()
                        text_length = 200
                        text_starter = np.random.randint(len(text) - 2*text_length)
                        text = text[text_starter:(text_starter + 2*text_length)]
                        text = re.sub('[^a-zA-Z0-9 ]', '', text)
                        section = text

                    section = section.split(' ')
                    section = ' '.join(section[:min(args.sectionMaxWord, len(section))])
                    section_type = np.random.choice(args.sectionType)
                    section_font_size = args.sectionFontSize[str(font_size)][section_type]

                    section_id = section_type + str(groundtruth_element_count[section_type])
                    section_number = '.'.join([str(groundtruth_element_count['section'] + 1),
                                               str(groundtruth_element_count['subsection'] + 1),
                                               str(groundtruth_element_count['subsubsection'] + 1)])

                    section_height = section_font_size * max(2.0, math.ceil(len(section) * section_font_size * args.fontHorizonCoeff / (column_width - (len(section_number) + 2) * section_font_size * args.fontHorizonCoeff)))

                    if offset_y + section_height > args.pageHeight - marginPt:
                        continue

                    # add element
                    if np.random.random() < args.hasColors:
                        color = np.random.choice(args.colors)
                    else:
                        color = 'black'

                    output += utils.gen_str_section(column_width, offset_x, offset_y, section_type, section, color)  # TODO

                    # add calculation
                    output += utils.gen_str_section_size(column_width,
                                                         args.sectionFont[section_type],
                                                         section,
                                                         section_number,
                                                         section_id)
                    # groundtruth
                    utils.update_groundtruth(groundtruth, groundtruth_element_count, section_type, '', section,
                                             [offset_y + font_size * 0.25, offset_y + font_size * 0.25 + section_height,
                                              offset_x, offset_x + column_width])
                    # adjust
                    offset_y += section_height + section_font_size * args.paraSkipRatio
                elif opt < args.distribution['list']:
                    text = ''
                    textfile = np.random.choice(text_list)
                    with open(args.pathText + textfile) as f:
                        text = f.read()
                        text_length = 500
                        text_starter = np.random.randint(len(text) - 2*text_length)
                        text = text[text_starter:(text_starter + 2*text_length)]
                        text = re.sub('[^a-zA-Z0-9 ]', '', text)

                    text_width = column_width
                    text_length = int(text_width / (font_size * 0.5))
                    text_line = 0

                    item_length = np.random.randint(args.itemLengthMin, args.itemLengthMax)
                    item_start = 0
                    content = ''
                    item_nb = np.random.randint(1, args.itemNumberMax + 1)

                    if np.random.random() < args.hasColors:
                        color = np.random.choice(args.colors)
                    else:
                        color = 'black'

                    for ii in range(item_nb):
                        item_length_current = item_length + np.random.randint(-int(item_length * args.itemVaryRatio),
                                                                              int(item_length * args.itemVaryRatio))
                        text_line += math.ceil(item_length_current * 1.0 / text_length)
                        content += utils.gen_str_item(text[item_start:(item_start + item_length_current)], color)
                        item_start += item_length_current

                    item_sep = 0
                    list_type = np.random.choice(args.listType)
                    list_height = font_size * (text_line * 1.5 - 0.5)
                    if offset_y + list_height > args.pageHeight - marginPt:
                        continue

                    # add element
                    str_itemize = utils.gen_str_itemize(column_width, list_type, offset_x, offset_y, item_sep, content)  # TODO
                    output += str_itemize

                    list_id = 'list' + str(groundtruth_element_count['list'])
                    # add calculation
                    output += utils.gen_str_itemize_size(column_width,
                                                         list_type,
                                                         item_sep,
                                                         content,
                                                         list_id)
                    # groundtruth
                    utils.update_groundtruth(groundtruth, groundtruth_element_count, 'list', '', content,
                                             [offset_y, offset_y + list_height, offset_x, offset_x + column_width])
                    # adjust
                    offset_y += list_height + font_size * (args.paraSkipRatio + 1)
                elif opt < args.distribution['text']:
                    text_width = column_width
                    try:
                        text_line = (args.pageHeight - offset_y - marginPt) / font_size
                        text_line_current = np.random.randint(1, min(text_line, args.textMaxLine))
                        text_height = text_line_current * font_size * args.fontVerticalCoeff
                    except ValueError:
                        break
                    text_length = int(text_width / (font_size * args.fontHorizonCoeff)) * text_line_current

                    text = ''
                    textfile = np.random.choice(text_list)
                    with open(args.pathText + textfile) as f:
                        text = f.read()
                        text_starter = np.random.randint(len(text) - 2*text_length)
                        text = text[text_starter:(text_starter + 2*text_length)]
                        text = re.sub('[^a-zA-Z0-9\.\?,;! ]', '', text)
                        text = text[:text_length]

                    # add element
                    if np.random.random() < args.hasColors:
                        color = np.random.choice(args.colors)
                    else:
                        color = 'black'
                    output += utils.gen_str_text(text_width, offset_x, offset_y, text, color=color)

                    # add calculation
                    text_id = 'text' + str(groundtruth_element_count['text'])
                    output += utils.gen_str_text_size(text_width, text, text_id)

                    # groundtruth
                    utils.update_groundtruth(groundtruth, groundtruth_element_count, 'text', '', text,
                                             [offset_y, offset_y + text_height, offset_x, offset_x + min(text_width, len(text) * font_size * args.fontHorizonCoeff)])
                    # adjust
                    offset_y += text_height + font_size * (args.paraSkipRatio - 1)
                else:  # line
                    if np.random.random() < args.hasColors:
                        color = np.random.choice(args.colors)
                    else:
                        color = 'black'

                    line_width = np.random.randint(1, args.borderLineMaxWidth / 2)
                    output += utils.gen_str_rectangle(offset_x, offset_y, column_width, line_width, color)
                    offset_y += line_width + font_size * args.paraSkipRatio


        # finalize output string
        output += utils.gen_str_closefile()
        output += utils.gen_str_end()

        # filename
        groundtruth['filename'] = fout_name

        # save tex file
        with open(fout_name, 'w') as fout:
            fout.write(output)

        # save groundtruth to json
        with open(fout_name + '.json', 'w') as fout:
            json.dump(groundtruth, fout, sort_keys=True, indent=4, ensure_ascii=False)
    except Exception as e:
        print(e)
