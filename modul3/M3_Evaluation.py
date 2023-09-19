"""
This script belongs to the PCCT
Writen by Eike Barnefske
External code is highlighted in the script and a permission to use the code was given.
"""
from tkinter import *
import pymysql as mariadb
import pandas as pd
import time

'''
The classification was done in the 2D space. This 2D information has to be transferred to the 3D space. This is done by
combining different tables of a database in this script.
'''


class ImageToPointCloud:

    def __init__(self, master):
        """
        Create a user interface for scan and classification data selection.
        """
        self.master = master
        master.title(" Create classified points.")

        self.close_button = Button(master, text="close", command=master.quit)
        self.close_button.grid(row=4, column=2)

        self.scan_text = StringVar()
        self.scan_text.set("Name of the scan")
        self.scan_labeltext = Label(master, textvariable=self.scan_text)
        self.scan_labeltext.grid(row=2, column=0)

        self.scan_textfeld = Text(master, height=1, width=40)
        self.scan_textfeld.grid(row=2, column=2, columnspan=2)

        self.daba_text = StringVar()
        self.daba_text.set("Database name")
        self.daba_labeltext = Label(master, textvariable=self.daba_text)
        self.daba_labeltext.grid(row=3, column=0)

        self.daba_textfeld = Text(master, height=1, width=40)
        self.daba_textfeld.grid(row=3, column=2, columnspan=2)

        self.csvToimage_button = Button(master, text="Classified points", command=self.execution_process)
        self.csvToimage_button.grid(row=4, column=1)

    def connection_database(self):
        """
        Connection to the database installed on a central (web) server. In this work, the open-source database MariaDB
         was used, which can be accessed with the most common SQL commands.
        :rtype: mariadb_connection: Connection objekt for database access (change here your parameter)
        """
        mariadb_connection = mariadb.connect(user='####', password='####', database='###', host='###.###.###.###',
                                             charset='utf8', use_unicode='FALSE', port='###')
        return mariadb_connection

    def get_textfield(self):
        """
        Transferring the inputs from the text fields of the user interface to the variables.
        :return: content_text: name of the chosen scan. daba: name of the database table.
        """
        content_text = self.scan_textfeld.get("1.0", "end-1c")
        daba = self.daba_textfeld.get("1.0", "end-1c")
        print('The data of scan', content_text, 'from table', daba, 'will be loaded.')
        return content_text, daba

    def get_max_class(self, scan, daba, mariadb_connection):
        """
       Load the classification results and determine the frequency for each scan object.
        :param scan: name of scan
        :param daba: name of database table
        :param mariadb_connection: connection object to database
        :return: df_class: df from database with all classification data of the current scan
        """
        ds = pd.read_sql_query("SELECT IdBild FROM image" + daba + " WHERE IdBild LIKE '_" + scan + "%';",
                               mariadb_connection)

        start = time.time()
        list_class = []
        list_image_id = []

        ds = ds.append({'IdBild': '1' + str(scan) + '9981'}, ignore_index=True)
        ds = ds.append({'IdBild': '1' + str(scan) + '9991'}, ignore_index=True)

        for IdBild in ds['IdBild']:
            df = pd.read_sql_query("SELECT * FROM ergebnisse" + daba + " WHERE IdBild=" + IdBild + ";",
                                   mariadb_connection)
            pd.to_numeric(df['klasse'], errors='coerce')
            items_counts = df['klasse'].value_counts().keys().max()
            # Set points without classification to '0'
            if str(items_counts) == 'nan':
                items_counts = '0'
            list_class.append(items_counts)
            list_image_id.append(IdBild)
        ende = time.time()
        # Save the current classification results for one scan as df
        df_class = pd.DataFrame({'IdBild': list_image_id, 'klasse': list_class})
        print('The scan consists of ' + str(len(df_class)) + '  subareas. Runtime:' + str(ende - start) + 's')
        return df_class

    def load_point_data(self, scan, daba, mariadb_connection):
        """
        Load 3D points with all features and IDs for the current scan.
        :param scan: name of scan
        :param daba: name of database table
        :param mariadb_connection: connection object
        :return: df_points: all points as df
        """
        print('Points of scan ' + str(scan) + ' will be loaded. This can take some minutes!')
        start = time.time()
        # Daten der Punkte aus Daba laden
        df_points = pd.read_sql_query("SELECT * FROM basisdaten" + daba + " WHERE IdBild LIKE '_" + scan + "%';",
                                      mariadb_connection)
        ende = time.time()
        print(str(df_points.shape[0]) + ' Alle points are loaded. Runtime: ' + str((ende - start) / 60) + 'min.')
        print(df_points.shape)
        return df_points

    def join_pandas(self, df_points, df_classification):
        """
        Combining df classification and point data.
        :param df_points: df with all point data
        :param df_classification: df with the classification results.
        :return: df_points_classes: combined df with classes and points
        """
        start = time.time()
        df_points_classes = pd.merge(df_points, df_classification, on=['IdBild'])
        ende = time.time()
        print('Point data and classifications are joined. Runtime: ' + str((ende - start)) + 'sec.')
        return df_points_classes

    def save_as_csv(self, scan, df_points_classes):
        """
        Save the point data with the class information as individual files and as a file with a label column.
        :param scan: name of scan
        :param df_points_classes: joined df with points and classification
        """
        tab_name_2 = scan + '_klassifiziert.pts'
        start = time.time()
        print('Started the export...Please wait')
        df_points_classes.to_csv(tab_name_2, mode='w', columns=['x', 'y', 'z', 'GT', 'klasse'], index=False)

        # single file export
        df_tisch = df_points_classes.loc[df_points_classes['klasse'] == '1']
        tab_name_tisch = 'Tabel_3D_' + scan + '.csv'
        df_tisch.to_csv(tab_name_tisch, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_wand = df_points_classes.loc[df_points_classes['klasse'] == '2']
        tab_name_wand = 'Wall_3D_' + scan + '.csv'
        df_wand.to_csv(tab_name_wand, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_boden = df_points_classes.loc[df_points_classes['klasse'] == '3']
        tab_name_boden = 'floor_3D_' + scan + '.csv'
        df_boden.to_csv(tab_name_boden, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_decke = df_points_classes.loc[df_points_classes['klasse'] == '4']
        tab_name_decke = 'ceiling_3D_' + scan + '.csv'
        df_decke.to_csv(tab_name_decke, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_stuhl = df_points_classes.loc[df_points_classes['klasse'] == '5']
        tab_name_stuhl = 'chair_3D_' + scan + '.csv'
        df_stuhl.to_csv(tab_name_stuhl, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_fenster = df_points_classes.loc[df_points_classes['klasse'] == '6']
        tab_name_fenster = 'window_3D_' + scan + '.csv'
        df_fenster.to_csv(tab_name_fenster, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_lamelle = df_points_classes.loc[df_points_classes['klasse'] == '7']
        tab_name_lamellar = 'lamellar_3D_' + scan + '.csv'
        df_lamelle.to_csv(tab_name_lamellar, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_lampe = df_points_classes.loc[df_points_classes['klasse'] == '8']
        tab_name_lampe = 'lamp_3D_' + scan + '.csv'
        df_lampe.to_csv(tab_name_lampe, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_bin = df_points_classes.loc[df_points_classes['klasse'] == '9']
        tab_name_bin = 'bin_3D_' + scan + '.csv'
        df_bin.to_csv(tab_name_bin, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_door = df_points_classes.loc[df_points_classes['klasse'] == '10']
        tab_name_door = 'door_3D_' + scan + '.csv'
        df_door.to_csv(tab_name_door, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_wand_deko = df_points_classes.loc[df_points_classes['klasse'] == '11']
        tab_name_wand_deko = 'wall_deco_3D_' + scan + '.csv'
        df_wand_deko.to_csv(tab_name_wand_deko, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_baum = df_points_classes.loc[df_points_classes['klasse'] == '12']
        tab_name_baum = 'tree_3D_' + scan + '.csv'

        df_baum.to_csv(tab_name_baum, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_schilder = df_points_classes.loc[df_points_classes['klasse'] == '13']
        tab_name_schilder = 'sign_3D_' + scan + '.csv'
        df_schilder.to_csv(tab_name_schilder, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_bauwerk = df_points_classes.loc[df_points_classes['klasse'] == '14']
        tab_name_bauwerk = 'building_3D_' + scan + '.csv'
        df_bauwerk.to_csv(tab_name_bauwerk, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_boden_veg = df_points_classes.loc[df_points_classes['klasse'] == '15']
        tab_name_boden_veg = 'floor_veg_3D_' + scan + '.csv'
        df_boden_veg.to_csv(tab_name_boden_veg, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_auto = df_points_classes.loc[df_points_classes['klasse'] == '16']
        tab_name_auto = 'car_3D_' + scan + '.csv'
        df_auto.to_csv(tab_name_auto, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_gehweg = df_points_classes.loc[df_points_classes['klasse'] == '17']
        tab_name_gehweg = 'pathway_3D_' + scan + '.csv'
        df_gehweg.to_csv(tab_name_gehweg, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_strasse = df_points_classes.loc[df_points_classes['klasse'] == '18']
        tab_name_strasse = 'street_3D_' + scan + '.csv'
        df_strasse.to_csv(tab_name_strasse, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_noise = df_points_classes.loc[df_points_classes['klasse'] == '19']
        tab_name_noise = 'noise_3D_' + scan + '.csv'
        df_noise.to_csv(tab_name_noise, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        df_small_class = df_points_classes.loc[df_points_classes['klasse'] == '20']
        tab_name_small_class = 'small_class_3D_' + scan + '.csv'
        df_small_class.to_csv(tab_name_small_class, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        # one all classes in one file
        tab_final_name = 'KlassifizierterScan_3D_' + scan + '.csv'
        df_points_classes.to_csv(tab_final_name, mode='w', columns=['x', 'y', 'z', 'klasse'], index=False)

        ende = time.time()
        print('CSV file saved. Runtime:' + str(ende - start) + 's\n Close the application')

    def check_classification(self, df, scan):
        """
        Evaluation of the classification against previous classifications.
        :param df: df with two classification one is done with PCCT. Save results as confusion matrix
        :param scan: name of the scan
        """
        df1 = df[['x', 'y', 'z', 'GT', 'klasse']]
        df1.loc[df1['GT'] == 'Stoerungen'] = 19
        df1["klasse"] = pd.to_numeric(df1["klasse"])
        df1["GT"] = pd.to_numeric(df1["GT"])
        dt_true = pd.DataFrame()
        df_false = pd.DataFrame()

        class_list = ['Tisch', 'Wand', 'Boden', 'Decke', 'Stuhl', 'Fenster', 'Lamelle', 'Lampe', 'Mülleimer', 'Tür',
                      'Wandbehang', 'Bäume', 'Street-furniture', 'Bauwerk', 'Veg', 'Auto', 'Gehweg', 'Strasse',
                      'Störungen', 'Sonstiges']

        with open(scan + 'confusionMatrix.csv', 'a') as fd:
            fd.write(
                ' ; Tisch; Wand; Boden; Decke; Stuhl; Fenster; Lamelle; Lampe; Mülleimer; Tür; Wandbehang; Bäume; '
                'Street-furniture; Bauwerke; Veg; Auto; Gehweg; Strasse; Störungen; Sonstiges \n')
            fd.close()

        with open(scan + 'confusionMatrix_anz.csv', 'a') as fd:
            fd.write(
                ' ; Tisch; Wand; Boden; Decke; Stuhl; Fenster; Lamelle; Lampe; Mülleimer; Tür; Wandbehang; Bäume; '
                'Street-furniture; Bauwerke; Veg; Auto; Gehweg; Strasse; Störungen; Sonstiges \n')
            fd.close()

        for i in range(1, 21):
            df_temp = df1.loc[df1['GT'] == i]

            df_temp_true = df_temp.query("GT == klasse")
            dt_true = dt_true.append(df_temp_true, ignore_index=True)

            df_temp_false = df_temp.query("GT != klasse")
            df_false = df_false.append(df_temp_false, ignore_index=True)

            if df_temp.shape[0] != 0:

                with open(scan + 'confusionMatrix.csv', 'a') as fd:
                    fd.write(class_list[i - 1] + ';')
                    fd.close()

                with open(scan + 'confusionMatrix_anz.csv', 'a') as fd:
                    fd.write(class_list[i - 1] + '; ')
                    fd.close()

                for j in range(1, 21):
                    df_temp_fp = df_temp.query("klasse == " + str(j))
                    prozent_fp = (df_temp_fp.shape[0] * 100) / df_temp.shape[0]

                    with open(scan + 'confusion_matrix_anz.csv', 'a') as fd:
                        fd.write(str(df_temp_fp.shape[0]) + '; ')
                        fd.close()

                    with open(scan + 'confusion_matrix.csv', 'a') as fd:
                        fd.write('{:04.2f}'.format(prozent_fp) + '; ')
                        fd.close()

                with open(scan + 'confusion_matrix_anz.csv', 'a') as fd:
                    fd.write('\n ')
                    fd.close()

                with open(scan + 'confusion_matrix.csv', 'a') as fd:
                    fd.write('\n ')
                    fd.close()
            else:
                print('There is no data!')

        print('TP' + str(dt_true.shape[0]) + ' und False ' + str(df_false.shape[0]))
        print('Over all acc', str((dt_true.shape[0] * 100) / df1.shape[0]))
        dt_true.to_csv(scan + '_true.pts', mode='w', columns=['x', 'y', 'z', 'GT'], index=False)
        df_false.to_csv(scan + '_false.pts', mode='w', columns=['x', 'y', 'z', 'GT'], index=False)

    def execution_process(self):
        """
        Process for evaluation and connection.
        """
        scan, daba = ImageToPointCloud.get_textfield(self)
        mariadb_connection = ImageToPointCloud.connection_database(self)

        output = ImageToPointCloud.get_max_class(self, scan, daba, mariadb_connection)
        df_points = ImageToPointCloud.load_point_data(self, scan, daba, mariadb_connection)
        df_points_classes = ImageToPointCloud.join_pandas(self, df_points, output)

        ImageToPointCloud.save_as_csv(self, scan, df_points_classes)
        ImageToPointCloud.check_classification(self, df_points_classes, scan)


if __name__ == "__main__":
    root = Tk()
    my_gui = ImageToPointCloud(root)
    root.mainloop()
