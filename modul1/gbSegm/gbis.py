"""
This script belongs to the PCCT
Writen by Eike Barnefske
External code is highlighted in the script and a permission to use the code was given.
"""

from gbSegm.graph import build_graph, segment_graph
from PIL import Image, ImageFilter
from skimage import io
import io
import numpy as np
import pandas as pd
import base64
import importexport as iae


from random import random

""" 
Larger parts of this code are taken from Luis Gabriel's contribution after permission. 
Source: https://github.com/luisgabriel/image-segmentation
"""


def diff(img, x1, y1, x2, y2):
    """
    Calculation of the distance between two pixel coordinates.
    :param img: Image
    :param x1: x for first point
    :param y1: y for frist point
    :param x2: x for second point
    :param y2: y for second point
    :return: distance
    """
    _out = np.sum((img[x1, y1] - img[x2, y2]) ** 2)
    return np.sqrt(_out)


def threshold(size, const):
    """
    Calculate the threshold for the gray value based segmentation.
    :param size: dynamic value (see parameter setting in gui.py)
    :param const: specific value (see parameter setting in gui.py)
    :return: threshold_value: threshold for segmentation
    """
    threshold_value = (const * 1 / size)
    return threshold_value


def generate_image(forest, width, height, scan, df, stack, step):
    """
    Top level process for the segment calculation in images based on feature values and geometric attributes.
    :param forest: segmentation methode
    :param width: width of image
    :param height: height of image
    :param scan: name of scann (number of scan)
    :param df: import df with previously calculated parameter
    :param stack:  Area of projection bowl
    :param step: part of the naming of output images
    :return: list_classes: list with for the new classes, data_segment_image: temporal images, df_out: temporal
    database where all point parameter are combined.
    """
    data_segment_image = np.zeros((width, height, 3), dtype=np.uint8)

    list_x = []
    list_y = []
    l_class = []
    list_classes = []
    classes = dict()
    cc = 1
    print('Segmentes are calculated ...')

    for y in range(height):
        for x in range(width):
            comp = forest.find(y * width + x)
            if not classes.get(comp):
                classes[comp] = cc
                cc += 1
            l_class.append(classes[comp])
            data_segment_image[x, y] = classes[comp]
            list_x.append(x)
            list_y.append(y)
            if data_segment_image[x, y][0] not in list_classes:
                list_classes.append(int(data_segment_image[x, y][0]))

    df2 = pd.DataFrame()
    del list_classes

    df2['x_pix'] = list_y
    df2['y_pix'] = list_x
    df2['classe'] = l_class

    # Connection basedata with image database
    df_out = pd.merge(df, df2)
    df_val_counts = pd.DataFrame(df2['classe'].value_counts())
    # rest index in temp data frame
    df_value_counts = df_val_counts.reset_index()
    df_value_counts.columns = ['unique_values', 'counts']
    # put the segment names in list.
    list_classes = df_value_counts['unique_values']
    print('There are ', df2['classe'].value_counts().shape[0], 'segments.')
    cols, rows = height, width
    data = np.zeros((rows, cols, 3), dtype=np.uint8)
    data[data == 0] = 255

    for i in range(0, len(list_classes)):
        # Organized the correct naming
        image_name = str(stack) + scan.zfill(3) + str(list_classes[i]).zfill(3) + str(step)
        condition = df_out['classe'] == list_classes[i]
        df_out.loc[condition, 'IdBild'] = image_name
    return list_classes, data_segment_image, df_out


def generate_i_image(forest, width, height):
    """
    Generate an I-image form the spectral and transformed scans
    :param forest: segmentation methode
    :param width: width of image
    :param height: height of image
    :return: I-image
    """
    random_color = lambda: (int(random() * 255), int(random() * 255), int(random() * 255))
    colors = [random_color() in range(width * height)]
    img = Image.new('RGB', (width, height))
    im = img.load()
    for y in range(height):
        for x in range(width):
            comp = forest.find(y * width + x)
            im[x, y] = colors[comp]
    return img.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)


def create_segmentimages(class_list, data_segment_image, image_file, m_conn, c, scan, stack, step, database):
    """
    Final creating and storage of the image file, that will be used in modul 2.
    :param class_list: list with all segment names
    :param data_segment_image: pixel sored by segment name
    :param image_file: curred image as base
    :param m_conn: scan no.
    :param c: database courser
    :param scan: scan number
    :param stack: left or right part of the bowl
    :param step: part of the naming of output images
    :param database: database object to write the data in the global database
    """
    bildlist = []
    for n in class_list:
        # Source: https: // stackoverflow.com / questions / 19666626 / replace - all - elements - of - python - numpy -
        # array - that - are - greater - than - some - value
        test = np.copy(data_segment_image)
        # Source: https: // stackoverflow.com / questions / 1616767 / pil - best - way - to - replace - color
        orig_color = [n, n, n]
        replacement_color = [200, 0, 0]
        replacement_color_non = [255, 255, 255]
        test[(data_segment_image != orig_color).all(axis=-1)] = replacement_color_non
        test[(data_segment_image == orig_color).all(axis=-1)] = replacement_color
        # Segment image
        f_image = Image.fromarray(test)
        f_image = f_image.convert('RGBA')
        # Panorama image
        b_image = image_file
        b_image = b_image.convert('RGBA')
        blended_img = Image.blend(b_image, f_image, alpha=0.4)
        buffered = io.BytesIO()
        blended_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue())
        bildlist.append(img_str)
        image_id = str(stack) + scan.zfill(3) + str(n).zfill(3) + str(step)

        # Save in global database
        c.execute('INSERT INTO image' + database + ' VALUES (%s, %s)', (image_id, img_str))
    m_conn.commit()


def get_segmented_image(sigma, neighbor, k_value, min_comp_size, image_file, scan, df, stack, step, database):
    """
    Finale segmentation on RGB-images.
    :param sigma: for graph base segmentation
    :param neighbor: considered neighbor pixel choose: 4 or 8 (see gui.py)
    :param k_value: user specific value to control the segmentation process (see gui.py)
    :param min_comp_size: min pixel to build a component
    :param image_file: input image (base for the calculations)
    :param scan: scan number
    :param df: base data
    :param stack: left or right part of the bowl
    :param step: part of the naming of output images
    :param database: database object to write the data in the global database
    :return: df: extend database with segments
    """
    w_image, h_image = image_file.size

    smooth = image_file.filter(ImageFilter.GaussianBlur(1))
    max_f = smooth.filter(ImageFilter.MaxFilter(sigma))
    aa = np.array(max_f)
    print('Graph will be calculate ... Please waite')
    graph_edges = build_graph(aa, h_image, w_image, diff, neighbor == 8)
    forest = segment_graph(graph_edges, w_image * h_image, k_value, min_comp_size, threshold)
    # Generate image with all segments and save class pixel relation
    class_list, data_segment_image, df = generate_image(forest, h_image, w_image, scan, df, stack, step)
    # Create access to database
    m_conn, c = iae.createimagetable(database)
    # Create images withe marked segments and add to database images
    create_segmentimages(class_list, data_segment_image, image_file, m_conn, c, scan, stack, step, database)
    return df


def get_segmented_i_image(sigma, neighbor, k_value, min_comp_size, image_file):
    """
     Finale segmentation on I-images.
    :param sigma: for graph base segmentation
    :param neighbor: considered neighbor pixel choose: 4 or 8 (see gui.py)
    :param k_value: user specific value to control the segmentation process (see gui.py)
    :param min_comp_size: min pixel to build a component
    :param image_file: input image (base for the calculations)
    """

    w_image, h_image = image_file.size
    smooth = image_file.filter(ImageFilter.GaussianBlur(1))
    max_f = smooth.filter(ImageFilter.MaxFilter(sigma))
    aa = np.array(max_f)
    print('Graph is calculated ... Please waite')
    graph_edges = build_graph(aa, h_image, w_image, diff, neighbor == 8)
    forest = segment_graph(graph_edges, w_image * h_image, k_value, min_comp_size, threshold)
    # Generate image with all segments and save class pixel relation
    image = generate_i_image(forest, h_image, w_image)
    image.save('test.png')
