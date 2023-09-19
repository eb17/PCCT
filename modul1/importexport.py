"""
This script belongs to the PCCT
Writen by Eike Barnefske
External code is highlighted in the script and a permission to use the code was given.
"""
import glob
import pandas as pd
from sqlalchemy import create_engine
import time
import pymysql as mariadb
import os
from PIL import Image


# Import of pts-files ------------------------------------------------------------------------------------------------
def load_pts(filename):
    """
    Load a single scanning station pts-file
    :param filename: name of the scan station
    :return df: Dataframe of all points with common features
      """
    filename = filename + '.pts'

    try:
        df = pd.read_csv(filename,
                         header=None,
                         skiprows=1,
                         delimiter=' ',
                         usecols=[0, 1, 2, 3, 4, 5, 6],
                         names=['x', 'y', 'z', 'I', 'R', 'G', 'B'])
        df['GT'] = str(21)
        print('all pts files in folder ' + filename + ' successfully loaded!')
        return df

    except FileNotFoundError:
        print(filename + '.pts was not loaded!')


def load_folder_pts(folder_name):
    """
    Load all files of one specific folder. E.g. if one room contains of multiple scan stations. Additionally, ground
    truth data can be loaded for evaluation of the tool.
    :param folder_name: Name of room oder scan collection
    :return df: Dataframe of all points with common features and ground truth
     """
    all_files = glob.glob(folder_name + "/*.pts")

    try:
        df = pd.concat([pd.read_csv(fp, header=None,
                                    skiprows=1,
                                    delimiter=' ',
                                    usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                                    names=['x', 'y', 'z', 'I', 'R', 'G', 'B', 'nx', 'ny', 'nz']).assign(
            GT=os.path.basename(fp).split('.')[0]) for fp in all_files])

        # encryption of semantic classes. Feel free to adapted for you needs (Multiple place of the script)
        df.loc[df['GT'] == 'Tisch', 'GT'] = 1
        df.loc[df['GT'] == 'Wand', 'GT'] = 2
        df.loc[df['GT'] == 'Boden', 'GT'] = 3
        df.loc[df['GT'] == 'Decke', 'GT'] = 4
        df.loc[df['GT'] == 'Stuhl', 'GT'] = 5
        df.loc[df['GT'] == 'Fenster', 'GT'] = 6
        df.loc[df['GT'] == 'Lamellen', 'GT'] = 7
        df.loc[df['GT'] == 'Lampen', 'GT'] = 8
        df.loc[df['GT'] == 'Mülleimer', 'GT'] = 9
        df.loc[df['GT'] == 'Tür', 'GT'] = 10
        df.loc[df['GT'] == 'Wandbehang', 'GT'] = 11
        df.loc[df['GT'] == 'Bäume', 'GT'] = 12
        df.loc[df['GT'] == 'Street_Furniture', 'GT'] = 13
        df.loc[df['GT'] == 'Bauwerke', 'GT'] = 14
        df.loc[df['GT'] == 'Bodenvegetation', 'GT'] = 15
        df.loc[df['GT'] == 'Auto', 'GT'] = 16
        df.loc[df['GT'] == 'Gehweg', 'GT'] = 17
        df.loc[df['GT'] == 'Strasse', 'GT'] = 18
        df.loc[df['GT'] == 'Störungen', 'GT'] = 19
        df.loc[df['GT'] == 'Sonstiges', 'GT'] = 20

        print('all pts files in folder ' + folder_name + ' successfully loaded!')
        return df
    except FileNotFoundError:
        print(folder_name + '.pts was not loaded!')


# Load images----------------------------------------------------------------------------------------------
def load_folder_images(folder_name):
    """
    Import all image of a specific folder (if preprocessed data is used)
    :param folder_name: Folder name
    :return images: List of images
    """
    images = []
    try:
        for filename in glob.glob(folder_name + "/*.jpg"):
            im = Image.open(filename)
            images.append(im)
        print('all images of folder ' + folder_name + ' successfully loaded!')
        return images

    except FileExistsError:
        print(folder_name + '.jpg was not loaded!')


# Export (intermediate) results as csv ---------------------------------------------------------------------------------
def save_as_csv(filename, data):
    """
    Export a pandas data frame as csv.
    :param filename: file name for export
    :param data: Name of the df to be exported
     """
    try:
        data.to_csv(filename, index=False)
        print('all pts files in folder ' + filename + ' successfully saved!')

    except:
        print(filename + '.pts was not saved!')


# Import variables into the MariaDB data base--------------------------------------------------------------------------
def pandas_to_mariadb(table_name, df):
    """
    Import df into database (MariaDB)
    Sources:
    DataFrames to SQL database.
    https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_sql.html
    https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.replace.html
    :param table_name: Table name of database
    :param df: Name of the df to be imported in the database
    """
    engine = create_engine('mysql+pymysql://####:###@###.###.###.###/database')

    t_start = time.time()
    print('Write' + str(df.shape[0]) + ' objects to ' + table_name + '\n please wait')

    df.to_sql(table_name, engine, if_exists='append', index=False)

    t_ende = time.time()
    print(f'... All Objects save in {t_ende - t_start:.3f} s \n -------------------------------- \n')


def createimagetable(database):
    """
    Create a new tabel for 2D Data in the database.
    :param database: Name of new table
    :return: connection object and cursor object
    """
    m_conn = mariadb.connect(user='###', password='###', database='###', host='###.###.###.###', charset='utf8',
                             use_unicode='FALSE', port=0000)
    c = m_conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS image" + database + "(IdBild TEXT, Bild LONGTEXT)")
    return m_conn, c


def df_to_daba(df_temp, database):
    """
    Import into an existing database
    :param df_temp: Name of df that should be added
    :param database: Name of database that should be extended
    """
    df_temp = df_temp[['x', 'y', 'z', 'GT', 'IdBild']]
    pandas_to_mariadb('basisdata' + database, df_temp)


def df_to_results(df_temp, database):
    """
    Import into an existing database (results)
    :param df_temp: Name of df that should be added
    :param database: Name of database that should be extended
    """
    df_temp = df_temp[['IdBild', 'klasse']].head(1)
    pandas_to_mariadb('results' + database, df_temp)


def empty_database(database):
    """
    Create empty database
    :param database: Name of new database.
    """
    m_conn = mariadb.connect(user='###', password='###', database='###', host='###.###.###.###', charset='utf8',
                             use_unicode='FALSE', port=0000)
    c = m_conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS ergebnisse" + database + "(IdBild TEXT, klasse TEXT)")
