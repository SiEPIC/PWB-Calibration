import os
from PwbCalib.Execute import Execute

if __name__ == "__main__":
    # base_path = r"D:\Pycharm Projects\PWB_calib\Data\01_Becky\1550_TE"
    # ref_file_path = r"D:\Pycharm Projects\PWB_calib\Data\01_Becky\1550_TE\ref_long_2_1\03-Jul-2024 18.07.47.csv"

    # base_path = r"D:\Pycharm Projects\PWB_calib\Data\02_Edward\1550_TE"
    # ref_file_path = r'D:\Pycharm Projects\PWB_calib\Data\02_Edward\1550_TE\ref_long_1_1\10-Jul-2024 10.27.47.csv'

    # base_path = r"D:\Pycharm Projects\PWB_calib\Data\03_Matthew\1550_TE"
    # ref_file_path = r'D:\Pycharm Projects\PWB_calib\Data\03_Matthew\1550_TE\ref_long_1_1\11-Jul-2024 10.43.51.csv'

    # base_path = r"D:\Pycharm Projects\PWB_calib\Data\04_Tianye\1550_TE"
    # ref_file_path = r'D:\Pycharm Projects\PWB_calib\Data\04_Tianye\1550_TE\ref_short_1_1\23-Jul-2024 15.00.00.csv'

    base_path = os.path.join(os.getcwd(), '01_Becky', '1550_TE')
    ref_file_path = os.path.join(os.getcwd(), '01_Becky', '1550_TE','ref_long_2_1','03-Jul-2024 18.07.47.csv')

    chip_name = ' 20240626_Chip5_Becky'
    measure_date = '2024-07-03'  # YYYY-MM-DD
    process = 'PWB'

    executor = Execute(base_path, ref_file_path, chip_name, measure_date, process)
    executor.genReport()

    # base_path = r"D:\Pycharm Projects\PWB_calib\Data\1310_TE"
    # ref_file_path = r"D:\Pycharm Projects\PWB_calib\Data\1310_TE\used_ref_long_2_2\04-Jul-2024 17.21.04.csv"