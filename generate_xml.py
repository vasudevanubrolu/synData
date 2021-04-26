import json
import numpy as np
import cv2
import argparse
from lxml import etree, objectify


def meta_anno(folder, filename, width, height):
    E = objectify.ElementMaker(annotate=False)
    return E.annotation(
            E.folder(folder),
            E.filename(filename),
            E.source(
                E.database('synthetic'),
                E.annotation('synthetic'),
                E.image('synthetic'),
                ),
            E.size(
                E.width(width),
                E.height(height),
                E.depth(3),
                ),
            E.segmented(0)
            )


def elmt_anno(typ, rect, args, shape):
    E = objectify.ElementMaker(annotate=False)
    top = rect[0] / args.pageHeight * shape[0]
    bottom = rect[1] / args.pageHeight * shape[0]
    left = rect[2] / args.pageWidth * shape[1]
    right = rect[3] / args.pageWidth * shape[1]

    return E.object(
            E.name(typ),
            E.bndbox(
                E.xmin(int(left)),
                E.ymin(int(top)),
                E.xmax(int(right)),
                E.ymax(int(bottom)),
                ),
            )


# parse argument
parser = argparse.ArgumentParser(description='Generate PDF')
parser.add_argument('-I', '--input', nargs='+', help='input file')
parser.add_argument('--visualize', action='store_true', help='save img with bbox')
parser.add_argument('--pageWidth', type=float, default=599.841, help='pdf page width')
parser.add_argument('--pageHeight', type=float, default=845.559, help='pdf page height')
parser.add_argument('--colormap', help='color map', default={'caption': (0, 0, 255),
                                                             'text': (0, 255, 0),
                                                             'list': (255, 0, 0),
                                                             'section': (0, 0, 0),
                                                             'subsection': (0, 0, 0),
                                                             'subsubsection': (0, 0, 0),
                                                             'figure': (255, 255, 0),
                                                             'table': (255, 0, 255)})
args = parser.parse_args()

for ii, img_name in enumerate(args.input):
    print(ii)
    print(img_name)
    # read file
    img = cv2.imread(img_name)
    prefix = img_name.split('/')[-1].split('.')[0]
    with open('{}.tex.json'.format(prefix), 'r') as fin:
        img_gt = json.load(fin)

    # adjust
    try:
        img_out = [line.strip('\n') for line in open('{}.tex.out'.format(prefix))]
        for img_amend in img_out:
            img_amend = img_amend.split(':')
            img_amend_id = img_amend[0]
            img_amend_type = img_amend[1]
            img_amend_value = float(img_amend[2][:-2])

            # adjust
            for elmt in img_gt['structure']:
                if elmt['id'] == img_amend_id:
                    # top bottome left right
                    if img_amend_type == 'width':
                        elmt['rect'][3] = min(elmt['rect'][3], elmt['rect'][2] + img_amend_value)
                    else:
                        elmt['rect'][1] = elmt['rect'][0] + img_amend_value
                    break
    except IOError:
        print('no such file: {}'.format('{}.tex.out'.format(prefix)))

    # visualization
    if args.visualize:
        for elmt in img_gt['structure']:
            top = elmt['rect'][0] / args.pageHeight * img.shape[0]
            bottom = elmt['rect'][1] / args.pageHeight * img.shape[0]
            left = elmt['rect'][2] / args.pageWidth * img.shape[1]
            right = elmt['rect'][3] / args.pageWidth * img.shape[1]
            cv2.rectangle(img, (int(left), int(top)), (int(right), int(bottom)), args.colormap[elmt['type']], 2)
        cv2.imwrite('{}.pdf.jpg'.format(prefix), img)

    # save xml
    annotation = meta_anno('synthetic', '{}.jpg'.format(prefix), img.shape[1], img.shape[0])
    for elmt in img_gt['structure']:
        annotation.append(elmt_anno(elmt['type'], elmt['rect'], args, img.shape))
    x = etree.ElementTree(annotation)
    with open('{}.xml'.format(prefix), 'w') as fout:
        fout.write(etree.tostring(x, pretty_print=True))
