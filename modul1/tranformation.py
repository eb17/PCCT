"""
This script belongs to the PCCT
Writen by Eike Barnefske
External code is highlighted in the script and a permission to use the code was given.
"""
import math
import numpy as np
from PIL import Image, ImageDraw
import pandas as pd


def roh_():
    """
    Variable "roh" for transformations
    :return: roh
    """
    roh = 180 / math.pi
    return roh


def cartesian_to_polar(df):
    """
    Transformation cartesian coordinates to polar coordinates
    :param df: df with cartesian coordinates
    :return df: df with cartesian and polar coordinates
    """
    list_a = []
    list_b = []
    roh = roh_()

    for x, y, z in zip(df['x'], df['y'], df['z']):

        # horizontal
        if x >= 0 and y > 0:  # 1
            a = math.atan(x / y) * roh

        elif x >= 0 > y:  # 2
            a = math.atan(x / y) * roh + 180
            # print('Q2')

        elif x <= 0 and y <= 0:  # 3
            if y == 0:
                y = 0.00001
            a = math.atan(x / y) * roh + 180  # 400
            # print('Q3')

        elif x <= 0 < y:  # 3
            a = math.atan(x / y) * roh + 360  # + 360
            # print('Q4')

        list_a.append(a)

        # vertical
        if z >= 0 and x > 0:
            b = 90 + math.atan(z / x) * roh
            # print('Q1')
        elif z >= 0 > x:
            b = 270 + math.atan(z / x) * roh

        elif z <= 0 and x < 0:
            b = 270 + math.atan(z / x) * roh
            # print('Q3')

        elif z <= 0 < x:
            b = 90 + math.atan(z / x) * roh
            # print('Q4')
        list_b.append(b)

    # extent the df
    df['hz'] = list_a
    df['vz'] = list_b
    df['d'] = np.sqrt(np.power(df['x'], 2) + np.power(df['y'], 2) + np.power(df['z'], 2))
    return df


def xyz_ball_projection(df):
    """
    Transformation cartesian coordinates to ball coordinates
    :param df: df with cartesian coordinates
    :return df: df with cartesian and ball coordinates
    """

    list_om = []
    list_phi = []
    roh = roh_()

    # radius
    df['r'] = np.sqrt(np.power(df['x'], 2) + np.power(df['y'], 2) + np.power(df['z'], 2))

    # angle
    for x, y, z, r in zip(df['x'], df['y'], df['z'], df['r']):
        phi = (math.acos(z / r)) - 90 / roh

        list_phi.append(phi)

        om = math.atan(y / x)
        list_om.append(om)

    # Extend df
    df['om'] = list_om  # Hz
    df['phi'] = list_phi  # Vz
    return df


def cylinder_projection(df):
    """
    Transformation cartesian coordinates to cylinder coordinates
    :param df: df with cartesian coordinates
    :return df: df with cartesian and cylinder coordinates
    """
    list_om = []
    df['r'] = np.sqrt(np.power(df['x'], 2) + np.power(df['y'], 2))

    for x, r, y in zip(df['x'], df['r'], df['y']):
        o = math.acos(x / r)
        list_om.append(o)

    df['omcyl'] = list_om
    return df


def ball_plane_projection(df, scale):
    """
    Transformation ball to plan coordinates.
    :param df: df with all features and coordinates (incl. ball coordinates)
    :param scale: Image pixel x and y
    :return df: Previous df with plan coordinates
    """
    y_list_int = []
    x_list_int = []

    for om, phi in zip(df['om'], df['phi']):
        x = math.tan((om / 2)) + 1  # Proj.from -90 to 90° on angle of  -45 bis 45°
        x_pix = int(x * scale)  # resolution
        x_list_int.append(x_pix)

        y = (math.tan(phi / 2)) + 1
        y_pix = int(y * scale)
        y_list_int.append(y_pix)

    df['x_pix'] = x_list_int
    df['y_pix'] = y_list_int
    return df


# Create images / image operation --------------------------------------------------------------------------------------

def create_rgb_image(df_temp):
    """
    Create an RGB-image form the transformed coordinates.
    :param df_temp: df with coordinates and spectral values
    :return: df extended with pixel information for any point (pixel value can be considered as feature)
    """
    df_temp['y_pix'] = df_temp['y_pix'] - df_temp['y_pix'].min()
    df_temp['x_pix'] = df_temp['x_pix'] - df_temp['x_pix'].min()
    cols, rows = df_temp['x_pix'].max() + 1, 1 + df_temp['y_pix'].max()
    data = np.zeros((rows, cols, 3), dtype=np.uint8)  # Array (mit 0) erstellen
    data[data == 0] = 255
    # Source: https://stackoverflow.com/questions/33338202/filling-matrix-with-array-of-coordinates-in-python
    data[df_temp['y_pix'], df_temp['x_pix']] = df_temp.loc[:, ['R', 'G', 'B']]
    data[data == 0] = 200
    # (only for process documentation and evaluation)
    image_file = Image.fromarray(data)
    image_file.save("rgb_image.jpg", "JPEG")
    return image_file, df_temp


def create_i_image(df_temp):
    """
    Create an I-image form the transformed coordinates.
    :param df_temp: df with coordinates and spectral values
    :return: df extended with pixel information for any point (pixel value can be considered as feature) and the
    image_file for manual use.
    """
    df_temp['y_pix'] = df_temp['y_pix'] - df_temp['y_pix'].min()
    df_temp['x_pix'] = df_temp['x_pix'] - df_temp['x_pix'].min()
    cols, rows = 1 + df_temp['x_pix'].max(), 1 + df_temp['y_pix'].max()
    data = np.zeros((rows, cols, 3), dtype=np.uint8)
    data[data == 0] = 255
    data[df_temp['y_pix'], df_temp['x_pix']] = df_temp.loc[:, ['I', 'I', 'I']]
    image_file = Image.fromarray(data, 'RGB')
    image_file = image_file.convert(mode="RGB")
    image_file.save("i_image.jpg", "JPEG")
    return image_file, df_temp


def create_rgb_image_s(df_temp, di_min, di, inout, n1):
    """
    Create an RGB image, from a cutting slice in the point cloud. Boundaries for the slices and the distances between
     them are defined by the function parameter.
    :param df_temp: df with coordinates and spectral values
    :param di_min: Height of the lowest slice
    :param di: Height of the highest slice
    :param inout: Distinction between the surrounding of the room and its contents.
    :param n1: Use of normal parameters: yes or no
    :return: df with pixel and slice information (parameters describing a 2D slice projection of a 3D point cloud).
    """
    nz = 0.8
    x_list_int = []
    y_list_int = []

    df_temp = df_temp[['y', 'x', 'z', 'R', 'G', 'B', 'nz', 'area', 'GT']].query(
        "z >=" + str(di_min) + " & z <" + str(di) + " & area ==" + str(inout))

    min_x = float(df_temp['x'].min() * -1)
    min_y = float(df_temp['y'].min() * -1)

    df_temp['y'] = df_temp['y'] + min_y
    df_temp['x'] = df_temp['x'] + min_x

    max_x = float(df_temp['x'].max())
    max_y = float(df_temp['y'].max())

    if n1:
        df_temp = df_temp[['x', 'y', 'z', 'R', 'G', 'B', 'nz', 'GT']].query(
            " nz <" + str(nz) + " and nz > " + str(nz * -1))
    else:
        df_temp = df_temp[['x', 'y', 'z', 'R', 'G', 'B', 'nz', 'GT']].query(
            " nz >=" + str(nz) + "or nz <=" + str(nz * -1))

    for x, y in zip(df_temp['x'], df_temp['y']):
        x_pix = int(((x * 520) / max_x))  # Resolution: 520
        x_list_int.append(x_pix)

        y_pix = int(((y * 520) / max_y))
        y_list_int.append(y_pix)

    df_temp['x_pix'] = x_list_int
    df_temp['y_pix'] = y_list_int

    cols, rows = 521, 521
    data = np.zeros((rows, cols, 3), dtype=np.uint8)
    data[df_temp['y_pix'], df_temp['x_pix']] = df_temp.loc[:, ['R', 'G', 'B']]

    data[data == 0] = 255
    image_file = Image.fromarray(data)
    image_file.save("rgb_image" + str(di) + ".jpg", "JPEG")

    df_temp['y'] = df_temp['y'] - min_y
    df_temp['x'] = df_temp['x'] - min_x
    return image_file, df_temp


def create_i_image_s(df_temp, di_min, di, inout, n1):
    """
    Create an I-image, from a cutting slice in the point cloud. Boundaries for the slices and the distances between
     them are defined by the function parameter.
    :param df_temp: df with coordinates and spectral values
    :param di_min: Height of the lowest slice
    :param di: Height of the highest slice
    :param inout: Distinction between the surrounding of the room and its contents.
    :param n1: Use of normal parameters: yes or no
    :return: df with pixel and slice information (parameters describing a 2D slice projection of a 3D point cloud).
    """
    nz = 0.8

    x_list_int = []
    y_list_int = []

    df_temp = df_temp[['y', 'x', 'z', 'I', 'nz', 'area', 'GT']].query(
        "z >=" + str(di_min) + " & z <" + str(di) + " & area ==" + str(inout))

    min_x = float(df_temp['x'].min() * -1)
    min_y = float(df_temp['y'].min() * -1)

    df_temp['y'] = df_temp['y'] + min_y
    df_temp['x'] = df_temp['x'] + min_x

    max_x = float(df_temp['x'].max())
    max_y = float(df_temp['y'].max())

    if n1:
        df_temp = df_temp[['x', 'y', 'z', 'I', 'nz', 'GT']].query(
            " nz <" + str(nz) + " and nz > " + str(nz * -1))
    else:
        df_temp = df_temp[['x', 'y', 'z', 'I', 'nz', 'GT']].query(
            " nz >=" + str(nz) + "or nz <=" + str(nz * -1))

    for x, y in zip(df_temp['x'], df_temp['y']):
        x_pix = int(((x * 520) / max_x))  # resolution: 520
        x_list_int.append(x_pix)

        y_pix = int(((y * 520) / max_y))
        y_list_int.append(y_pix)

    df_temp['II'] = 255
    df_temp['III'] = 200

    df_temp['x_pix'] = x_list_int
    df_temp['y_pix'] = y_list_int

    cols, rows = 521, 521
    data = np.zeros((rows, cols, 3), dtype=np.uint8)
    data[data == 0] = 255

    data[df_temp['y_pix'], df_temp['x_pix']] = df_temp.loc[:, ['I', 'II', 'III']]
    image_file = Image.fromarray(data, 'RGB')
    image_file = image_file.convert(mode="RGB")
    image_file.save("rgb_image" + str(di) + ".jpg", "JPEG")

    data[data == 0] = 255
    image_file = Image.fromarray(data)
    image_file.save("i_image" + str(di) + ".jpg", "JPEG")

    df_temp['y'] = df_temp['y'] - min_y
    df_temp['x'] = df_temp['x'] - min_x
    return image_file, df_temp


def create_rgb_mask(df, di_min, di):
    """
    Creating a mask for separating inside and outside room in RGB images.
    :param df: df with coordinates and spectral values
    :param di_min: Height of the lowest slice
    :param di: Height of the highest slice
    :return: df as into df, but with a new colum, that indicates if the point is inside or outside.
    :rtype: pandas dataframe
    """

    df_temp = cartesian_to_polar(df)
    x_list_int = []
    y_list_int = []

    min_x = float(df_temp['x'].min() * -1)
    min_y = float(df_temp['y'].min() * -1)

    df_temp['y'] = df_temp['y'] + min_y
    df_temp['x'] = df_temp['x'] + min_x

    max_x = float(df_temp['x'].max())
    max_y = float(df_temp['y'].max())

    for x, y in zip(df_temp['x'], df_temp['y']):
        x_pix = int(((x * 520) / max_x))  # Auflösung für ein 520 x 520 px Bild.
        x_list_int.append(x_pix)

        y_pix = int(((y * 520) / max_y))
        y_list_int.append(y_pix)

    df_temp['x_pix'] = x_list_int
    df_temp['y_pix'] = y_list_int

    df_temp_1 = df_temp[['y', 'x', 'z', 'R', 'G', 'B', 'x_pix', 'y_pix', 'nz', 'hz', 'd', 'GT']].query(
        "z >=" + str(di_min) + " & z <" + str(di))

    df_temp_2 = pd.DataFrame()
    for i in range(0, 360, 2):
        j = i + 1
        temp_100 = df_temp_1[['x', 'y', 'z', 'R', 'G', 'B', 'x_pix', 'y_pix', 'nz', 'hz', 'd', 'GT']].query(
            " hz >=" + str(i) + " & hz<" + str(j))
        if temp_100.size == 0:
            continue
        df_temp_200 = temp_100[['x', 'y', 'z', 'R', 'G', 'B', 'x_pix', 'y_pix', 'nz', 'hz', 'd', 'GT']].query(
            " d ==" + str(temp_100['d'].min()) + " & d < 10")
        if df_temp_200.size == 0:
            continue
        df_temp_2 = df_temp_2.append(df_temp_200, ignore_index=True)

    df_temp_2['hz'] = df_temp_2['hz']
    df_temp3 = df_temp_2.sort_values(by=['hz'])

    shape = list(zip(df_temp3.x_pix, df_temp3.y_pix))
    img = Image.new("RGB", (521, 521))
    img1 = ImageDraw.Draw(img)
    img1.polygon(shape, fill="green", outline="red")
    aa = np.array(img)  # convert image to numpy array

    mask = np.where(np.all(aa == [0, 128, 0], axis=-1))
    maske = pd.DataFrame(mask[0], columns=['y_pix'])
    maske['x_pix'] = mask[1]
    maske['area'] = 1

    df = pd.merge(df, maske, on=['x_pix', 'y_pix'], how='left')
    df['area'] = df['area'].fillna(0)
    return df


def create_i_mask(df, di_min, di):
    """
    Creating a mask for separating inside and outside room in I-images.
    :param df: df with coordinates and spectral values
    :param di_min: Height of the lowest slice
    :param di: Height of the highest slice
    :return: df as into df, but with a new colum, that indicates if the point is inside or outside.
    :rtype: pandas dataframe
    """
    df_temp = cartesian_to_polar(df)
    x_list_int = []
    y_list_int = []

    min_x = float(df_temp['x'].min() * -1)
    min_y = float(df_temp['y'].min() * -1)

    df_temp['y'] = df_temp['y'] + min_y
    df_temp['x'] = df_temp['x'] + min_x

    max_x = float(df_temp['x'].max())
    max_y = float(df_temp['y'].max())

    for x, y in zip(df_temp['x'], df_temp['y']):
        x_pix = int(((x * 520) / max_x))  # Resolution
        x_list_int.append(x_pix)

        y_pix = int(((y * 520) / max_y))
        y_list_int.append(y_pix)

    df_temp['x_pix'] = x_list_int
    df_temp['y_pix'] = y_list_int

    df_temp_1 = df_temp[['y', 'x', 'z', 'I', 'x_pix', 'y_pix', 'nz', 'hz', 'd', 'GT']].query(
        "z >=" + str(di_min) + " & z <" + str(di))

    df_temp_2 = pd.DataFrame()
    for i in range(0, 360, 2):
        j = i + 1
        temp_100 = df_temp_1[['x', 'y', 'z', 'I', 'x_pix', 'y_pix', 'nz', 'hz', 'd', 'GT']].query(
            " hz >=" + str(i) + " & hz<" + str(j))
        if temp_100.size == 0:
            continue
        df_temp_200 = temp_100[['x', 'y', 'z', 'I', 'x_pix', 'y_pix', 'nz', 'hz', 'd', 'GT']].query(
            " d ==" + str(temp_100['d'].min()) + " & d < 10")
        if df_temp_200.size == 0:
            continue
        df_temp_2 = df_temp_2.append(df_temp_200, ignore_index=True)

    df_temp3 = df_temp_2.sort_values(by=['hz'])

    shape = list(zip(df_temp3.x_pix, df_temp3.y_pix))
    img = Image.new("RGB", (521, 521))
    img1 = ImageDraw.Draw(img)
    img1.polygon(shape, fill="green", outline="red")
    aa = np.array(img)

    mask = np.where(np.all(aa == [0, 128, 0], axis=-1))
    maske = pd.DataFrame(mask[0], columns=['y_pix'])
    maske['x_pix'] = mask[1]
    maske['area'] = 1

    df = pd.merge(df, maske, on=['x_pix', 'y_pix'], how='left')
    df['area'] = df['area'].fillna(0)
    return df


if __name__ == "__main__":
    test = roh_()
    print(test)
