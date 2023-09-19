"""
This script belongs to the PCCT
Writen by Eike Barnefske
External code is highlighted in the script and a permission to use the code was given.
"""

from tkinter import *
import pandas as pd
import importexport as iae
import tranformation as tap
import gbSegm.gbis as gbis


class GUI:

    def __init__(self, master):
        """
        Input mask for parameters to create the semantic images. Different methods can be controlled with this mask
        (see parameter description in the input mask).
        """
        self.master = master
        master.title("Build database for classification")

        self.close_button = Button(master, text="close", command=master.quit)
        self.close_button.grid(row=0, column=2)

        # Sigma
        self.load_text = StringVar()
        self.load_text.set("Sigma: ")
        self.load_labeltext = Label(master, textvariable=self.load_text)
        self.load_labeltext.grid(row=1, column=0)
        self.load_textfeld = Text(master, height=1, width=40)
        self.load_textfeld.grid(row=1, column=2, columnspan=2)

        # Minimum size of segment
        self.size_text = StringVar()
        self.size_text.set("Size:  ")
        self.size_labeltext = Label(master, textvariable=self.size_text)
        self.size_labeltext.grid(row=2, column=0)
        self.size_textfeld = Text(master, height=1, width=40)
        self.size_textfeld.grid(row=2, column=2, columnspan=2)

        # Name of scan
        self.scan_text = StringVar()
        self.scan_text.set("Name of scan: ")
        self.scan_labeltext = Label(master, textvariable=self.scan_text)
        self.scan_labeltext.grid(row=3, column=0)
        self.scan_textfeld = Text(master, height=1, width=40)
        self.scan_textfeld.grid(row=3, column=2, columnspan=2)

        # image or scan
        self.image_scan_text = StringVar()
        self.image_scan_text.set("Image or point cloud?")
        self.image_scan_labeltext = Label(master, textvariable=self.image_scan_text)
        self.image_scan_labeltext.grid(row=4, column=0)
        self.image_scan_in_radiobutton = Radiobutton(master, text="scan", variable=var4, indicatoron=True, value=1,
                                                     width=8)
        self.image_scan_in_radiobutton.grid(row=4, column=1, columnspan=2)
        self.image_scan_radio_button = Radiobutton(master, text="image", variable=var4, indicatoron=True, value=2,
                                                   width=8)
        self.image_scan_radio_button.grid(row=4, column=3, columnspan=2)

        # Maximum depth
        self.depth_text = StringVar()
        self.depth_text.set("Indoor or outdoor scan?")
        self.depth_labeltext = Label(master, textvariable=self.depth_text)
        self.depth_labeltext.grid(row=5, column=0)
        self.depth_in_radiobutton = Radiobutton(master, text="indoor", variable=var, indicatoron=True, value=1, width=8)
        self.depth_in_radiobutton.grid(row=5, column=1, columnspan=2)
        self.depth_out_radiobutton = Radiobutton(master, text="outdoor", variable=var, indicatoron=True, value=2,
                                                 width=8)
        self.depth_out_radiobutton.grid(row=5, column=3, columnspan=2)

        # Panorama or slice
        self.depth_in_radiobutton = Radiobutton(master, text="panorama", variable=var1, indicatoron=True, value=1,
                                                width=8)
        self.depth_in_radiobutton.grid(row=6, column=1, columnspan=2)
        self.depth_out_radiobutton = Radiobutton(master, text="point cloud", variable=var1, indicatoron=True, value=2,
                                                 width=8)
        self.depth_out_radiobutton.grid(row=6, column=3, columnspan=2)

        # Load file or folder
        self.depth_in_radiobutton = Radiobutton(master, text="folder", variable=var2, indicatoron=True, value=1,
                                                width=8)
        self.depth_in_radiobutton.grid(row=7, column=1, columnspan=2)
        self.depth_out_radiobutton = Radiobutton(master, text="file", variable=var2, indicatoron=True, value=2,
                                                 width=8)
        self.depth_out_radiobutton.grid(row=7, column=3, columnspan=2)

        # k-value
        self.k_text = StringVar()
        self.k_text.set("k value: ")
        self.k_labeltext = Label(master, textvariable=self.k_text)
        self.k_labeltext.grid(row=8, column=0)
        self.k_textfeld = Text(master, height=1, width=40)
        self.k_textfeld.grid(row=8, column=2, columnspan=2)

        # rgb or i
        self.depth_in_radiobutton = Radiobutton(master, text="rgb", variable=var3, indicatoron=True, value=1,
                                                width=8)
        self.depth_in_radiobutton.grid(row=9, column=1, columnspan=2)
        self.depth_out_radiobutton = Radiobutton(master, text="intensity", variable=var3, indicatoron=True, value=2,
                                                 width=8)
        self.depth_out_radiobutton.grid(row=9, column=3, columnspan=2)

        # database
        self.database_text = StringVar()
        self.database_text.set("Database: ")
        self.database_labeltext = Label(master, textvariable=self.database_text)
        self.database_labeltext.grid(row=10, column=0)
        self.database_textfeld = Text(master, height=1, width=40)
        self.database_textfeld.grid(row=10, column=2, columnspan=2)

        # Start button
        self.csvToimage_button = Button(master, text="database to image", command=self.execute)
        self.csvToimage_button.grid(row=11, column=2)

    def execute(self):
        """
        Connection of the individual methods for the execution of this modul.
        """

        if var4.get() == 1:
            scan_name, sigma, min_comp_size, k_value, database = GUI.read_parameter(self)
            df = GUI.load_file_folder(self, scan_name)

            if var1.get() == 1:
                print('panorama')

                if var.get() == 1:
                    print('indoor panorama')
                    # fix parameter. Evaluated in this work.
                    distance_step = [10, 15, 20]
                    distance_step_min = [0, 10, 15]
                    step = [1, 2, 3]
                    scale = [500, 500, 500]
                    nz = 0.8
                    df_3, df_4 = GUI.get_floor_roof(self, df, scan_name, database, nz)
                    df_rest = GUI.get_rest(self, df, df_3, df_4)
                    print('indoor panorama', distance_step_min)

                else:
                    distance_step = [5, 10, 20, 50]
                    distance_step_min = [0, 5, 10, 20]
                    step = [1, 2, 3, 4]
                    scale = [250, 250, 500, 500]
                    iae.empty_database(database)
                    df_rest = df
                    print('outdoor panorama', distance_step_min)

                if var3.get() == 1:
                    print('rgb image')
                    df_rest[df_rest.x == 0] = 0.001
                    for di, di_min, step, scale in zip(distance_step, distance_step_min, step, scale):
                        df_ball = tap.xyz_ball_projection(df_rest)
                        df_distance = df_ball[['x', 'y', 'z', 'R', 'G', 'B', 'r', 'nz', 'om', 'phi', 'GT']].query(
                            "r >=" + str(di_min) + " & r <" + str(di))
                        df_polar = tap.ball_plane_projection(df_distance, scale)
                        df_part1 = df_polar.query("x >= 0")
                        df_part2 = df_polar.query("x <= 0")
                        del df_ball, df_distance, df_polar
                        df_part1_1 = df_part1[
                            ['x', 'y', 'z', 'x_pix', 'y_pix', 'R', 'G', 'B', 'r', 'nz', 'om', 'phi', 'GT']].query(
                            " nz < 0.8 and nz > -0.8")
                        df_part1_2 = df_part1[
                            ['x', 'y', 'z', 'x_pix', 'y_pix', 'R', 'G', 'B', 'r', 'nz', 'om', 'phi', 'GT']].query(
                            " nz >= 0.8 or nz <=-0.8")
                        df_part2_1 = df_part2[
                            ['x', 'y', 'z', 'x_pix', 'y_pix', 'R', 'G', 'B', 'r', 'nz', 'om', 'phi', 'GT']].query(
                            " nz < 0.8 and nz > -0.8")
                        df_part2_2 = df_part2[
                            ['x', 'y', 'z', 'x_pix', 'y_pix', 'R', 'G', 'B', 'r', 'nz', 'om', 'phi', 'GT']].query(
                            " nz >= 0.8 or nz <=-0.8")

                        if df_part1_1.size != 0:
                            print('There are values for bowl segment 1-1')
                            df_part1_1.to_csv(scan_name + '-' + str(step) + '-1-1.pts', mode='w',
                                              columns=['x', 'y', 'z', 'GT'], index=False)
                            # Create the 2D image
                            input_image1, df_temp_1 = tap.create_rgb_image(df_part1_1)
                            # Automatic segmentation in the image
                            df_temp_1 = gbis.get_segmented_image(sigma, 4, k_value, min_comp_size, input_image1,
                                                                 scan_name, df_temp_1, 1, step, database)
                            # Save all image in the database
                            iae.df_to_daba(df_temp_1, database)
                            # clean workspace
                            del df_temp_1, input_image1, df_part1_1
                        else:
                            print('There are no values for bowl segment 1-1')

                        if df_part1_2.size != 0:
                            print('There are values for bowl segment 1-2')
                            df_part1_2.to_csv(scan_name + '-' + str(step) + '-1-2.pts', mode='w',
                                              columns=['x', 'y', 'z', 'GT'], index=False)
                            input_image1, df_temp_1 = tap.create_rgb_image(df_part1_2)
                            df_temp_1 = gbis.get_segmented_image(sigma, 4, k_value, min_comp_size, input_image1,
                                                                 scan_name, df_temp_1, 3, step, database)
                            iae.df_to_daba(df_temp_1, database)
                            del df_temp_1, input_image1, df_part1_2
                        else:
                            print('There are no values for bowl segment 1-2')

                        if df_part2_1.size != 0:
                            print('There are values for bowl segment 2-1')
                            df_part2_1.to_csv(scan_name + '-' + str(step) + '-2-1.pts', mode='w',
                                              columns=['x', 'y', 'z', 'GT'], index=False)

                            input_image2, df_temp_2 = tap.create_rgb_image(df_part2_1)
                            df_temp_2 = gbis.get_segmented_image(sigma, 4, k_value, min_comp_size, input_image2,
                                                                 scan_name, df_temp_2, 2, step, database)
                            iae.df_to_daba(df_temp_2, database)
                            del df_temp_2, input_image2, df_part2_1
                        else:
                            print('There are no values for bowl segment 2-1')

                        if df_part2_2.size != 0:
                            print('There are values for bowl segment 2-2')
                            df_part2_2.to_csv(scan_name + '-' + str(step) + '-2-2.pts', mode='w',
                                              columns=['x', 'y', 'z', 'GT'], index=False)
                            input_image2, df_temp_2 = tap.create_rgb_image(df_part2_2)
                            df_temp_2 = gbis.get_segmented_image(sigma, 4, k_value, min_comp_size, input_image2,
                                                                 scan_name, df_temp_2, 4, step, database)
                            iae.df_to_daba(df_temp_2, database)
                            del df_temp_2, input_image2, df_part2_2
                        else:
                            print('There are no values for bowl segment 2-1')

                        # End RGB-images ------------------------------------------------------------------------------
                else:
                    print('intensity image')
                    df_rest[df_rest.x == 0] = 0.001
                    for di, di_min, step, scale in zip(distance_step, distance_step_min, step, scale):
                        df_ball = tap.xyz_ball_projection(df_rest)
                        df_distance = df_ball[['x', 'y', 'z', 'I', 'r', 'nz', 'om', 'phi', 'GT']].query(
                            "r >=" + str(di_min) + " & r <" + str(di))
                        df_polar = tap.ball_plane_projection(df_distance, scale)
                        df_part1 = df_polar.query("x >= 0")
                        df_part2 = df_polar.query("x <= 0")
                        del df_ball, df_distance, df_polar
                        df_part1_1 = df_part1[
                            ['x', 'y', 'z', 'x_pix', 'y_pix', 'I', 'r', 'nz', 'om', 'phi', 'GT']].query(
                            " nz < 0.8 and nz > -0.8")
                        df_part1_2 = df_part1[
                            ['x', 'y', 'z', 'x_pix', 'y_pix', 'I', 'r', 'nz', 'om', 'phi', 'GT']].query(
                            " nz >= 0.8 or nz <=-0.8")
                        df_part2_1 = df_part2[
                            ['x', 'y', 'z', 'I', 'x_pix', 'y_pix', 'r', 'nz', 'om', 'phi', 'GT']].query(
                            " nz < 0.8 and nz > -0.8")
                        df_part2_2 = df_part2[
                            ['x', 'y', 'z', 'I', 'x_pix', 'y_pix', 'r', 'nz', 'om', 'phi', 'GT']].query(
                            " nz >= 0.8 or nz <=-0.8")

                        if df_part1_1.size != 0:
                            print('There are values for bowl segment 1-1')
                            # Speichern der Teilpunktwolke als pts
                            df_part1_1.to_csv(scan_name + '-' + str(step) + '-1-1.pts', mode='w',
                                              columns=['x', 'y', 'z', 'GT'], index=False)
                            input_image1, df_temp_1 = tap.create_i_image(df_part1_1)
                            df_temp_1 = gbis.get_segmented_image(sigma, 4, k_value, min_comp_size, input_image1,
                                                                 scan_name,
                                                                 df_temp_1, 1, step, database)
                            iae.df_to_daba(df_temp_1, database)
                            del df_temp_1, input_image1, df_part1_1
                        else:
                            print('There are no values for bowl segment 1-1')

                        if df_part1_2.size != 0:
                            print('There are values for bowl segment 1-2')
                            df_part1_2.to_csv(scan_name + '-' + str(step) + '-1-2.pts', mode='w',
                                              columns=['x', 'y', 'z', 'GT'], index=False)

                            input_image1, df_temp_1 = tap.create_i_image(df_part1_2)
                            df_temp_1 = gbis.get_segmented_image(sigma, 4, k_value, min_comp_size, input_image1,
                                                                 scan_name, df_temp_1, 3, step, database)
                            iae.df_to_daba(df_temp_1, database)
                            del df_temp_1, input_image1, df_part1_2
                        else:
                            print('There are no values for bowl segment 1-2')

                        if df_part2_1.size != 0:
                            print('There are values for bowl segment 2-1')
                            df_part2_1.to_csv(scan_name + '-' + str(step) + '-2-1.pts', mode='w',
                                              columns=['x', 'y', 'z', 'GT'], index=False)
                            input_image2, df_temp_2 = tap.create_i_image(df_part2_1)
                            df_temp_2 = gbis.get_segmented_image(sigma, 4, k_value, min_comp_size, input_image2,
                                                                 scan_name,
                                                                 df_temp_2, 2, step, database)
                            iae.df_to_daba(df_temp_2, database)
                            del df_temp_2, input_image2, df_part2_1
                        else:
                            print('There are no values for bowl segment 2-1')

                        if df_part2_2.size != 0:
                            print('There are values for bowl segment 2-2')
                            df_part2_2.to_csv(scan_name + '-' + str(step) + '-2-2.pts', mode='w',
                                              columns=['x', 'y', 'z', 'GT'], index=False)

                            input_image2, df_temp_2 = tap.create_i_image(df_part2_2)
                            df_temp_2 = gbis.get_segmented_image(sigma, 4, k_value, min_comp_size, input_image2,
                                                                 scan_name,
                                                                 df_temp_2, 4, step, database)
                            iae.df_to_daba(df_temp_2, database)
                            del df_temp_2, input_image2, df_part2_2
                        else:
                            print('There are no values for bowl segment 2-2')

                        # End of I-images ------------------------------------------------------------------------------
            # End of panorama ---------------------------------------------------------------------------------
            # slice-projection ---------------------------------------------------------------------------------
            else:
                print('Sliced point cloud')
                if var.get() == 1:
                    print('indoor')
                    mini = df['z'].min()  # 0.80
                    minmax = df['z'].nsmallest(1000).max()  # 0.85
                    distance_step_min = [mini, df['z'].min(), df['z'].nsmallest(1000).mean() + 0.2, 0.8501,
                                         df['z'].nlargest(100000).mean() - 0.3001]
                    distance_step = [minmax, df['z'].nsmallest(1000).mean() + 0.2, 0.85,
                                     df['z'].nlargest(100000).mean() - 0.3, df['z'].max()]
                    step = [0, 1, 2, 3, 4]
                    iae.empty_database(database)
                    df_rest = df

                else:
                    print('outdoor')
                    distance_step = [-1, 0, 1, df['z'].max()]
                    distance_step_min = [df['z'].min(), -1, 0, 1]
                    step = [1, 2, 3, 4]
                    iae.empty_database(database)
                    df_rest = df

                if var3.get() == 1:
                    print('rgb')
                    for di, di_min, step in zip(distance_step, distance_step_min, step):
                        if step == 0:
                            print('step', step)
                            df_rest = tap.create_rgb_mask(df_rest, di_min, di)
                        elif step == 1:
                            print('This is step:', step)
                            input_image1, df_temp_outside = tap.create_rgb_image_s(df_rest, di_min, di, 0, True)
                            print('Punkte in der Stufe', len(df_temp_outside))
                            if df_temp_outside.size != 0:
                                df1 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                               scan_name, df_temp_outside, 1, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df1[['x', 'y', 'z', 'GT', 'IdBild']])
                            else:
                                print('There are no values for this step')

                            input_image1, df_temp_outside = tap.create_rgb_image_s(df_rest, di_min, di, 0, False)
                            print('There are values for step ', len(df_temp_outside))

                            if df_temp_outside.size != 0:
                                df11 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                                scan_name,
                                                                df_temp_outside, 2, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df11[['x', 'y', 'z', 'GT', 'IdBild']])
                            else:
                                print('There are no values for this step')
                            input_image2, df_temp_inside = tap.create_rgb_image_s(df_rest, di_min, di, 1, False)
                            if df_temp_inside.size != 0:
                                df_temp_inside['klasse'] = str(3)
                                df_temp_inside['IdBild'] = '1' + str(scan_name) + '9991'
                                iae.df_to_daba(df_temp_inside, database)
                                iae.df_to_results(df_temp_inside, database)
                                del df_temp_inside

                            input_image2, df_temp_inside = tap.create_rgb_image_s(df_rest, di_min, di, 1, True)
                            if df_temp_inside.size != 0:
                                print('There are values for step', len(df_temp_inside))
                                df22 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image2,
                                                                scan_name,
                                                                df_temp_inside, 4, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df22[['x', 'y', 'z', 'GT', 'IdBild']])

                            else:
                                print('There are no values for this step')

                        elif step == 4:
                            # ceiling level
                            print('This is ', step)
                            input_image1, df_temp_outside = tap.create_rgb_image_s(df_rest, di_min, di, 0, True)
                            if df_temp_outside.size != 0:
                                print('There are values for step', len(df_temp_outside))
                                df1 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                               scan_name,
                                                               df_temp_outside, 1, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df1[['x', 'y', 'z', 'GT', 'IdBild']])
                            else:
                                print('There are no values for this step')

                            input_image1, df_temp_outside = tap.create_rgb_image_s(df_rest, di_min, di, 0, False)
                            if df_temp_outside.size != 0:
                                print('There are values for step', len(df_temp_outside))
                                df11 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                                scan_name,
                                                                df_temp_outside, 2, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df11[['x', 'y', 'z', 'GT', 'IdBild']])
                            else:
                                print('There are no values for this step')

                            input_image2, df_temp_inside = tap.create_rgb_image_s(df_rest, di_min, di, 1, False)
                            if df_temp_inside.size != 0:
                                df_temp_inside['klasse'] = str(4)  # Achtung muss 4 sein
                                df_temp_inside['IdBild'] = '1' + str(scan_name) + '9981'
                                iae.df_to_daba(df_temp_inside, database)
                                iae.df_to_results(df_temp_inside, database)
                                del df_temp_inside
                            else:
                                print('There are no values for this step')

                            input_image2, df_temp_inside = tap.create_rgb_image_s(df_rest, di_min, di, 1, True)
                            print('There are values for step', len(df_temp_inside))
                            if df_temp_inside.size != 0:
                                df22 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image2,
                                                                scan_name,
                                                                df_temp_inside, 4, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df22[['x', 'y', 'z', 'GT', 'IdBild']])
                            else:
                                print('There are no values for this step')
                        else:
                            print('Step', step)
                            input_image1, df_temp_outside = tap.create_rgb_image_s(df_rest, di_min, di, 0, True)
                            print('There are values for step', len(df_temp_outside))
                            if df_temp_outside.size != 0:
                                df1 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                               scan_name,
                                                               df_temp_outside, 1, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df1[['x', 'y', 'z', 'GT', 'IdBild']])
                            else:
                                print('There are no values for this step')

                            input_image1, df_temp_outside = tap.create_rgb_image_s(df_rest, di_min, di, 0, False)
                            print('Punkte in der Stufe', len(df_temp_outside))

                            if df_temp_outside.size != 0:
                                df11 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                                scan_name,
                                                                df_temp_outside, 2, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df11[['x', 'y', 'z', 'GT', 'IdBild']])
                            else:
                                print('There are no values for this step')

                            input_image2, df_temp_inside = tap.create_rgb_image_s(df_rest, di_min, di, 1, True)
                            print('There are values for step', len(df_temp_inside))
                            if df_temp_inside.size != 0:
                                df2 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image2,
                                                               scan_name,
                                                               df_temp_inside, 3, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df2[['x', 'y', 'z', 'GT', 'IdBild']])
                            else:
                                print('There are no values for this step')

                            input_image2, df_temp_inside = tap.create_rgb_image_s(df_rest, di_min, di, 1, False)
                            print('There are values for step', len(df_temp_inside))
                            if df_temp_inside.size != 0:
                                df22 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image2,
                                                                scan_name,
                                                                df_temp_inside, 4, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df22[['x', 'y', 'z', 'GT', 'IdBild']])
                            else:
                                print('There are no values for this step')
                else:
                    print('i Image')
                    for di, di_min, step in zip(distance_step, distance_step_min, step):

                        if step == 0:
                            print('step', step)
                            df_rest = tap.create_i_mask(df_rest, di_min, di)

                        elif step == 1:
                            print('Its step', step)
                            input_image1, df_temp_outside = tap.create_i_image_s(df_rest, di_min, di, 0, True)
                            print('There are values for step', len(df_temp_outside))
                            if df_temp_outside.size != 0:
                                df1 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                               scan_name,
                                                               df_temp_outside, 1, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df1[['x', 'y', 'z', 'GT', 'IdBild']])

                            input_image1, df_temp_outside = tap.create_i_image_s(df_rest, di_min, di, 0, False)
                            print('There are values for step', len(df_temp_outside))
                            if df_temp_outside.size != 0:
                                df11 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                                scan_name,
                                                                df_temp_outside, 2, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df11[['x', 'y', 'z', 'GT', 'IdBild']])

                            input_image2, df_temp_inside = tap.create_i_image_s(df_rest, di_min, di, 1, False)
                            if df_temp_inside.size != 0:
                                df_temp_inside['klasse'] = str(3)  # Achtung muss 3 sein
                                df_temp_inside['IdBild'] = '1' + str(scan_name) + '9991'
                                iae.df_to_daba(df_temp_inside, database)
                                iae.df_to_results(df_temp_inside, database)
                                del df_temp_inside

                            input_image2, df_temp_inside = tap.create_i_image_s(df_rest, di_min, di, 1, True)
                            print('There are values for step', len(df_temp_inside))
                            if df_temp_inside.size != 0:
                                df22 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image2,
                                                                scan_name,
                                                                df_temp_inside, 4, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df22[['x', 'y', 'z', 'GT', 'IdBild']])

                        elif step == 4:
                            print('It is', step)
                            input_image1, df_temp_outside = tap.create_i_image_s(df_rest, di_min, di, 0, True)
                            print('There are values for step', len(df_temp_outside))
                            if df_temp_outside.size != 0:
                                df1 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                               scan_name,
                                                               df_temp_outside, 1, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df1[['x', 'y', 'z', 'GT', 'IdBild']])

                            input_image1, df_temp_outside = tap.create_i_image_s(df_rest, di_min, di, 0, False)
                            print('There are values for step', len(df_temp_outside))
                            if df_temp_outside.size != 0:
                                df11 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                                scan_name,
                                                                df_temp_outside, 2, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df11[['x', 'y', 'z', 'GT', 'IdBild']])

                            input_image2, df_temp_inside = tap.create_i_image_s(df_rest, di_min, di, 1, False)
                            if df_temp_inside.size != 0:
                                df_temp_inside['klasse'] = str(4)  # Achtung muss 4 sein
                                df_temp_inside['IdBild'] = '1' + str(scan_name) + '9981'
                                iae.df_to_daba(df_temp_inside, database)
                                iae.df_to_results(df_temp_inside, database)
                                del df_temp_inside

                            input_image2, df_temp_inside = tap.create_i_image_s(df_rest, di_min, di, 1, True)
                            print('There are values for step', len(df_temp_inside))
                            if df_temp_inside.size != 0:
                                df22 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image2,
                                                                scan_name,
                                                                df_temp_inside, 4, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df22[['x', 'y', 'z', 'GT', 'IdBild']])

                        else:
                            print('Step', step)
                            input_image1, df_temp_outside = tap.create_i_image_s(df_rest, di_min, di, 0, True)
                            print('There are values for step', len(df_temp_outside))
                            if df_temp_outside.size != 0:
                                df1 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                               scan_name,
                                                               df_temp_outside, 1, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df1[['x', 'y', 'z', 'GT', 'IdBild']])

                            input_image1, df_temp_outside = tap.create_i_image_s(df_rest, di_min, di, 0, False)
                            print('There are values for step', len(df_temp_outside))
                            if df_temp_outside.size != 0:
                                df11 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image1,
                                                                scan_name,
                                                                df_temp_outside, 2, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df11[['x', 'y', 'z', 'GT', 'IdBild']])

                            input_image2, df_temp_inside = tap.create_i_image_s(df_rest, di_min, di, 1, True)
                            print('There are values for step', len(df_temp_inside))
                            if df_temp_inside.size != 0:
                                df2 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image2,
                                                               scan_name,
                                                               df_temp_inside, 3, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df2[['x', 'y', 'z', 'GT', 'IdBild']])

                            input_image2, df_temp_inside = tap.create_i_image_s(df_rest, di_min, di, 1, False)
                            print('There are values for step', len(df_temp_inside))
                            if df_temp_inside.size != 0:
                                df22 = gbis.get_segmented_image(sigma, 8, k_value, min_comp_size, input_image2,
                                                                scan_name,
                                                                df_temp_inside, 4, step, database)
                                iae.pandas_to_mariadb('basisdaten' + database, df22[['x', 'y', 'z', 'GT', 'IdBild']])

            # End slice ---------------------------------------------------------------------------------

        else:
            image_name, sigma, min_comp_size, k_value, database = GUI.read_parameter_image(self)
            print(image_name, sigma, min_comp_size, k_value, database)
            image_list = iae.load_folder_images(image_name)
            print(len(image_list))
            image_list[0].show()
            gbis.get_segmented_i_image(sigma, 4, k_value, min_comp_size, image_list[0])

    print('All calculations are finished! \n - End of program -')

    def read_parameter(self):
        """
        Reading the user parameters from the input mask and passing the parameter values to the variables in the
        execution loop. (Point Cloud)
        :return: Set of parameter values
        """
        pd.options.mode.chained_assignment = None
        scan_name = self.scan_textfeld.get("1.0", "end-1c")
        sigma = int(self.load_textfeld.get("1.0", "end-1c"))
        min_comp_size = int(self.size_textfeld.get("1.0", "end-1c"))
        k_value = int(self.k_textfeld.get("1.0", "end-1c"))
        database = self.database_textfeld.get("1.0", "end-1c")

        print(scan_name, sigma, min_comp_size, k_value, database)

        return scan_name, sigma, min_comp_size, k_value, database

    def read_parameter_image(self):
        """
        Reading the user parameters from the input mask and passing the parameter values to the variables in the
        execution loop. (image data)
        :return: Set of parameter values
        """
        pd.options.mode.chained_assignment = None
        image_name = self.scan_textfeld.get("1.0", "end-1c")
        sigma = int(self.load_textfeld.get("1.0", "end-1c"))
        min_comp_size = int(self.size_textfeld.get("1.0", "end-1c"))
        k_value = int(self.k_textfeld.get("1.0", "end-1c"))
        database = self.database_textfeld.get("1.0", "end-1c")
        return image_name, sigma, min_comp_size, k_value, database

    def load_file_folder(self, scan_name):
        """
        Loading the point clouds from one or more pts files.
        :param scan_name:File- or Folder name
        :return: df with all available point features
        """
        if var2.get() == 1:
            df = iae.load_folder_pts(scan_name)
            print('Folder')
        else:
            df = iae.load_pts(scan_name)
            print('File')
        return df

    def get_floor_roof(self, df, scan_name, database, nz):
        """
        Creating the floor and ceiling plane in the panoramic method.
        :param df: point cloud with all current features
        :param scan_name: name of scan
        :param database: database name
        :param nz: Threshold for normal direction
        :return: df_temp3, df_temp4 as inputted, but without the points that describe the ceiling and floor.
        """
        # Floor
        df_temp1 = df[['x', 'y', 'z', 'nz', 'R', 'G', 'B', 'I', 'GT']].query(
            "z <=" + str(df['z'].nsmallest(1000).mean() + 0.2))
        df_temp3 = df_temp1[['x', 'y', 'z', 'nz', 'R', 'G', 'B', 'I', 'GT']].query(
            " nz <" + str(nz) + " and nz > " + str(nz * -1))
        df_temp2 = df_temp1[['x', 'y', 'z', 'nz', 'R', 'G', 'B', 'I', 'GT']].query(
            " nz >=" + str(nz) + "or nz <=" + str(nz * -1))
        df_temp2['klasse'] = str(3)  # Achtung muss 3 sein
        df_temp2['IdBild'] = '1' + str(scan_name) + '9991'
        df_temp2.to_csv(scan_name + 'Boden.pts', mode='w', columns=['x', 'y', 'z', 'GT', 'klasse'], index=False)
        df_temp3.to_csv(scan_name + 'Boden2.pts', mode='w', columns=['x', 'y', 'z', 'GT'], index=False)
        iae.df_to_daba(df_temp2, database)
        iae.df_to_results(df_temp2, database)
        del df_temp1, df_temp2

        # Ceiling
        df_temp1 = df[['x', 'y', 'z', 'nz', 'R', 'G', 'B', 'I', 'GT']].query(
            "z >=" + str(df['z'].nlargest(10).mean()))
        df_temp4 = df_temp1[['x', 'y', 'z', 'nz', 'R', 'G', 'B', 'I', 'GT']].query(
            " nz < " + str(nz) + " and nz >" + str(nz * -1))
        df_temp2 = df_temp1[['x', 'y', 'z', 'nz', 'R', 'G', 'B', 'I', 'GT']].query(
            " nz >=" + str(nz) + " or nz <=" + str(nz * -1))

        df_temp2['klasse'] = str(19)
        df_temp2['IdBild'] = '1' + str(scan_name) + '9981'
        df_temp2.to_csv(scan_name + 'Decke.pts', mode='w', columns=['x', 'y', 'z', 'GT', 'klasse'],
                        index=False)
        df_temp4.to_csv(scan_name + 'Decke_vec.pts', mode='w', columns=['x', 'y', 'z', 'GT'],
                        index=False)
        iae.df_to_daba(df_temp2, database)
        iae.df_to_results(df_temp2, database)

        del df_temp1, df_temp2
        return df_temp3, df_temp4

    def get_rest(self, df, df_3, df_4):
        """
        Creating a point cloud without  the point of class floor and ceiling for the panoramic method.
        :param df: point cloud with all current features
        :param df_3: all point that not belong to floor
        :param df_4: all point that not belong to ceiling
        :return: df as input, but without the points that describe the ceiling and floor.
        """

        df_rest = df[['x', 'y', 'z', 'nz', 'R', 'G', 'B', 'I', 'GT']].query(
            " z >" + str(df['z'].nsmallest(1000).mean() + 0.2) + " & " + " z <" + str(df['z'].nlargest(10).mean()))
        df_rest = df_rest.append(df_3)
        df_rest = df_rest.append(df_4)

        del df_3, df_4
        return df_rest


if __name__ == "__main__":
    root = Tk()
    var = IntVar()
    var1 = IntVar()
    var2 = IntVar()
    var3 = IntVar()
    var4 = IntVar()
    GUI(root)
    root.mainloop()
