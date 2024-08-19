import csv
import pathlib
import os.path
from datetime import datetime, timedelta


def create_folder(folder_name):
    pathlib.Path(folder_name).mkdir(parents=True, exist_ok=True)


def write_csv(file_path, time, balance):
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='') as lf:
        writer = csv.writer(lf, delimiter=',', lineterminator='\n')
        if not file_exists:
            writer.writerow(['time', 'balance'])
        writer.writerow([time, balance])


def get_csv_data(file):
    time_list, balance_list = [], []
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            time_list.append(row['time'])
            balance_list.append(float(row['balance']))
    return time_list, balance_list


def get_last_some_days(days):
    # 獲取當前日期
    current_date = datetime.now().date()

    # 生成最近 10 天的日期
    recent_dates = [current_date - timedelta(days=i) for i in range(days)]

    # 將日期排序（由小到大）
    recent_dates_sorted = sorted(recent_dates)

    # 將日期格式化為字符串
    recent_dates_str = [date.strftime('%Y-%m-%d') for date in recent_dates_sorted]

    return recent_dates_str


def save_the_last_balance(balance):
    with open('last_balance.txt', 'w') as f:
        f.write(str(balance))


def read_the_last_balance():
    with open('last_balance.txt', 'r') as f:
        last_balance = float(f.read())
    return last_balance
