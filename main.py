import os
from PwbCalib.Execute import Execute

if __name__ == "__main__":

    base_path = os.path.join(os.getcwd(), '01_Becky', '1550_TE')
    ref_file_path = os.path.join(os.getcwd(), '01_Becky', '1550_TE','ref_long_2_1','03-Jul-2024 18.07.47.csv')

    chip_name = ' 20240626_Chip5_Becky'
    measure_date = '2024-07-03'  # YYYY-MM-DD
    process = 'PWB'

    executor = Execute(base_path, ref_file_path, chip_name, measure_date, process)
    executor.genReport()