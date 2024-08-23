import os
import io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class GraphCalib:
    def __init__(self, base_path, ref_file_path, channel, wavelength):
        self.base_path = base_path
        self.ref_file_path = ref_file_path
        self.channel = channel
        self.wavelength = wavelength

        self.figures_df = pd.DataFrame(columns=['Name', 'Figure'])

    def get_csv_files(self, folder_path):
        """Get list of CSV files in the folder"""
        return [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    def extract_number_from_folder(self, folder_name):
        """Extract the differentiating bond number from the folder name"""
        parts = folder_name.split('_')
        return parts[-2]  # Assuming the number is the second last element

    def read_csv(self, file_path):
        """Read the CSV file and transpose it"""
        try:
            data = pd.read_csv(file_path, comment='#', header=None)
            data = data.transpose()
            data.columns = data.iloc[0]  # Set the first row as the header
            data = data.drop(data.index[0])
            return data
        except Exception as e:
            print(f"Error reading and transposing file {file_path}: {e}")
            return None

    def save_plot_to_buffer(self, name):
        """Save the current plot to a BytesIO buffer and append to figures_df"""
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        df_figures = pd.DataFrame([{'Name': name, 'Figure': img_buffer}])
        self.figures_df = pd.concat([self.figures_df, df_figures], ignore_index=True)
        plt.close()  # Close the plot to avoid display overlap
        # print(f"Added figure: {name}")  # Debugging statement
        # print(self.figures_df)  # Debugging statement

    def plot_raw_calibration_data(self, data_dict, ref_data):
        plt.figure(figsize=(10, 6))

        # Plot reference data
        ref_wavelength = ref_data['wavelength'].astype(float)
        ref_channel = ref_data[self.channel].astype(float)
        plt.plot(ref_wavelength, ref_channel, label='Reference', color='black')

        # Generate a colormap
        colormap = plt.get_cmap('tab10')
        colors = colormap.colors

        # Sort the data by differentiating number and plot
        for i, differentiating_number in enumerate(sorted(data_dict.keys(), key=lambda x: int(x))):
            color = colors[i % len(colors)]  # Cycle through colors if there are more than 10 bonds
            for data in data_dict[differentiating_number]:
                dataset_wavelength = data['wavelength'].astype(float)
                dataset_channel = data[self.channel].astype(float)
                plt.plot(dataset_wavelength, dataset_channel, label=f'Bond_{differentiating_number}', color=color)

        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Power (dBm)')
        plt.title('Raw PWB Calibration Data')
        plt.legend()
        self.save_plot_to_buffer(f'{self.wavelength}_calibRaw')

    def plot_difference_data(self, data_dict, ref_wavelength, ref_channel):
        plt.figure(figsize=(10, 6))

        # Generate a colormap
        colormap = plt.get_cmap('tab10')
        colors = colormap.colors

        # Sort the data by bond number and plot the differences with unique colors
        for i, differentiating_number in enumerate(sorted(data_dict.keys(), key=lambda x: int(x))):
            color = colors[i % len(colors)]  # Cycle through colors if there are more than 10 bonds
            for data in data_dict[differentiating_number]:
                dataset_wavelength = data['wavelength'].astype(float)
                dataset_channel = data[self.channel].astype(float)

                # Interpolate reference data to match dataset wavelengths
                ref_channel_interpolated = np.interp(dataset_wavelength, ref_wavelength, ref_channel)

                # Calculate the difference
                difference = -(dataset_channel - ref_channel_interpolated)

                plt.plot(dataset_wavelength, difference, label=f'Bond_{differentiating_number}', color=color)

        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Insertion Loss (dB)')
        plt.title('PWB Calibration Data Insertion Loss')
        plt.legend()
        self.save_plot_to_buffer(f'{self.wavelength}_calibLoss')

    def fitted_loss(self, data_dict, ref_wavelength, ref_channel):
        # Second plot: All fitted data with average and standard deviation shaded area
        plt.figure(figsize=(10, 6))

        # Generate a colormap
        colormap = plt.get_cmap('tab10')
        colors = colormap.colors

        # Initialize lists to store all polynomial fits for calculating average and standard deviation
        poly_fits = []
        dataset_wavelength = None

        # Plot each fitted data in different colors with legend labels for bond numbers
        for i, differentiating_number in enumerate(sorted(data_dict.keys(), key=lambda x: int(x))):
            color = colors[i % len(colors)]  # Cycle through colors if there are more than 10 bonds
            for data in data_dict[differentiating_number]:
                dataset_wavelength = data['wavelength'].astype(float)
                dataset_channel = data[self.channel].astype(float)

                # Interpolate reference data to match dataset wavelengths
                ref_channel_interpolated = np.interp(dataset_wavelength, ref_wavelength, ref_channel)

                # Calculate the difference
                difference = -(dataset_channel - ref_channel_interpolated)

                # Fit the difference to a 4th degree polynomial
                poly_coeff = np.polyfit(dataset_wavelength, difference, 4)
                poly_fit = np.polyval(poly_coeff, dataset_wavelength)

                # Append the polynomial fit for later analysis
                poly_fits.append(poly_fit)

                # Plot the fitted data
                plt.plot(dataset_wavelength, poly_fit, label=f'Bond_{differentiating_number}', color=color,
                         linestyle='-', alpha=0.5)

        # Calculate the average and standard deviation of the polynomial fits
        if poly_fits:
            poly_fits = np.array(poly_fits)
            avg_fit = np.mean(poly_fits, axis=0)
            std_fit = np.std(poly_fits, axis=0)

            # Plot average line
            plt.plot(dataset_wavelength, avg_fit, label='Average Fitted Difference', color='black', linestyle='-')

            # Shade the area representing the standard deviation
            plt.fill_between(dataset_wavelength, avg_fit - std_fit, avg_fit + std_fit, color='gray', alpha=0.2,
                             label='±1 Std Dev')

        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Insertion Loss (dB)')
        plt.title('Fitted PWB Calibration Data Insertion Loss with Average and Std Dev')
        plt.legend()
        self.save_plot_to_buffer(f'{self.wavelength}_fittedLoss')
        plt.show()

    def plot_difference_at_wavl(self, data_dict, ref_wavelength, ref_channel):
        plt.figure(figsize=(10, 6))

        # Generate a colormap
        colormap = plt.get_cmap('tab10')
        colors = colormap.colors

        differences_at_wavl = []
        loss_data = []

        # Sort the data by differentiating number and plot the differences with unique colors
        for i, differentiating_number in enumerate(sorted(data_dict.keys(), key=lambda x: int(x))):
            color = colors[i % len(colors)]  # Cycle through colors if there are more than 10 bonds
            for data in data_dict[differentiating_number]:
                dataset_wavelength = data['wavelength'].astype(float)
                dataset_channel = data[self.channel].astype(float)

                # Interpolate reference data to match dataset wavelengths
                ref_channel_interpolated = np.interp(dataset_wavelength, ref_wavelength, ref_channel)

                # Calculate the difference
                difference = -(dataset_channel - ref_channel_interpolated)

                # Fit the difference to a 4th degree polynomial
                poly_coeff = np.polyfit(dataset_wavelength, difference, 4)
                poly_fit = np.polyval(poly_coeff, dataset_wavelength)

                # Calculate the average difference at the target wavelength using the polynomial fit
                wavl_range_mask = (dataset_wavelength >= (self.wavelength - 5)) & (
                        dataset_wavelength <= (self.wavelength + 5))
                if np.any(wavl_range_mask):
                    target_wavelength = self.wavelength
                    poly_diff_at_wavl = np.polyval(poly_coeff, target_wavelength)

                    # Calculate uncertainty of the fit
                    residuals = difference[wavl_range_mask] - poly_fit[wavl_range_mask]
                    residual_sum_of_squares = np.sum(residuals ** 2)
                    total_variance = residual_sum_of_squares / (len(residuals) - len(poly_coeff))
                    uncertainty_at_wavl = np.sqrt(total_variance)

                    differences_at_wavl.append(
                        (int(differentiating_number), poly_diff_at_wavl, color, f'Bond_{differentiating_number}',
                         uncertainty_at_wavl))
                    loss_data.append({
                        'Bond': int(differentiating_number),
                        'Loss (dB)': poly_diff_at_wavl,
                        'Uncertainty (dB)': uncertainty_at_wavl
                    })
                    print(
                        f"Bond {differentiating_number}: Difference at {target_wavelength} nm = {poly_diff_at_wavl:.2f} ± {uncertainty_at_wavl:.2f} dB")

        # Plot the differences at the target wavelength
        if differences_at_wavl:
            differences_at_wavl.sort(key=lambda x: x[0])  # Sort by bond number
            bonds, differences, colors, labels, uncertainties = zip(*differences_at_wavl)
            for bond, difference, color, label, uncertainty in zip(bonds, differences, colors, labels, uncertainties):
                plt.errorbar(bond, difference, yerr=uncertainty, fmt='o', color=color, label=label)

            # Calculate and plot the average difference and its uncertainty
            average_difference = np.mean(differences)
            std_deviation = np.std(differences)
            n = len(differences)
            sem = std_deviation / np.sqrt(n)  # Standard error of the mean

            # Total uncertainty is the combination of standard deviation and SEM
            total_uncertainty = np.sqrt(std_deviation ** 2 + sem ** 2)

            plt.axhline(y=average_difference, color='red', linestyle='--',
                        label=f'Average: {average_difference:.2f} ± {total_uncertainty:.2f} dB')

            print(
                f"Average difference at {self.wavelength} nm: {average_difference:.2f} +/- {total_uncertainty:.2f} dB")
            print(f"Standard deviation: {std_deviation:.2f} dB")
            print(f"Standard error of the mean: {sem:.2f} dB")

            plt.xlabel('Bond Number')
            plt.ylabel(f'Insertion Loss at {self.wavelength} nm (dB)')
            plt.title(f'PWB Calibration Data Insertion Loss at {self.wavelength} nm')
            plt.legend()
        else:
            print(f"No data available at {self.wavelength} nm")

        self.save_plot_to_buffer(f'{self.wavelength}_calibLossWAVL')

        loss_df = pd.DataFrame(loss_data)
        return self.figures_df, loss_df

    def fit_orig(self, data_dict, ref_wavelength, ref_channel):
        # Generate a colormap
        colormap = plt.get_cmap('tab10')
        colors = colormap.colors

        # Sort the data by bond number
        for i, differentiating_number in enumerate(sorted(data_dict.keys(), key=lambda x: int(x))):
            color = colors[i % len(colors)]  # Cycle through colors if there are more than 10 bonds
            for data in data_dict[differentiating_number]:
                dataset_wavelength = data['wavelength'].astype(float)
                dataset_channel = data[self.channel].astype(float)

                # Interpolate reference data to match dataset wavelengths
                ref_channel_interpolated = np.interp(dataset_wavelength, ref_wavelength, ref_channel)

                # Calculate the loss
                difference = -(dataset_channel - ref_channel_interpolated)

                # Fit the difference to a 4th degree polynomial
                poly_coeff = np.polyfit(dataset_wavelength, difference, 4)
                poly_fit = np.polyval(poly_coeff, dataset_wavelength)

                # Create a new plot for each bond number
                plt.figure(figsize=(10, 6))

                # Plot original data
                plt.plot(dataset_wavelength, difference, label=f'Original Bond_{differentiating_number}', color=color,
                         linestyle='-')

                # Plot fitted data
                plt.plot(dataset_wavelength, poly_fit, label=f'Fitted Bond_{differentiating_number}', color='black',
                         linestyle='--', linewidth=2)


                plt.xlabel('Wavelength (nm)')
                plt.ylabel('Insertion Loss (dB)')
                plt.title(f'Original and Fitted Data for Bond_{differentiating_number}')
                plt.legend()

                # Save the plot to buffer
                # self.save_plot_to_buffer(f'original_and_fitted_loss_bond_{differentiating_number}')
                plt.show()

    def analyze_data(self, verbose=False):
        """Plot data from folders and reference file"""
        # Read reference data
        ref_data = self.read_csv(self.ref_file_path)
        if ref_data is not None:
            ref_wavelength = ref_data['wavelength'].astype(float)
            ref_channel = ref_data[self.channel].astype(float)
        else:
            print("Error reading reference data.")
            return None, None

        # Collect all data
        data_dict = {}
        for folder_name in os.listdir(self.base_path):
            folder_path = os.path.join(self.base_path, folder_name)
            if os.path.isdir(folder_path) and 'calibration_ST2ST' in folder_name:
                csv_files = self.get_csv_files(folder_path)
                differentiating_number = self.extract_number_from_folder(folder_name)
                for csv_file in csv_files:
                    file_path = os.path.join(folder_path, csv_file)
                    data = self.read_csv(file_path)
                    if data is not None:
                        if differentiating_number not in data_dict:
                            data_dict[differentiating_number] = []
                        data_dict[differentiating_number].append(data)

        # Plot raw calibration data with reference data
        self.plot_raw_calibration_data(data_dict, ref_data)
        # Plot difference data
        self.plot_difference_data(data_dict, ref_wavelength, ref_channel)

        self.fitted_loss(data_dict,ref_wavelength,ref_channel)

        if verbose:
            self.fit_orig(data_dict, ref_wavelength, ref_channel)

        # Plot difference at wavelength and get loss dataframe
        df_figures, loss_df = self.plot_difference_at_wavl(data_dict, ref_wavelength, ref_channel)

        # Return the dataframes with the figures and loss data
        return self.figures_df, loss_df