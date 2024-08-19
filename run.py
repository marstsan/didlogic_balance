from lib.Didlogic import Didlogic
from lib.CinnoxTool import CinnoxTool
from lib.utils import *
from pathlib import Path


csv_root = 'csv'
create_folder(csv_root)
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
csv_file = f'{timestamp[:10]}.csv'
notification = f'- Query Time: {timestamp}\n'
send_notification = False

last_balance = None
if Path('last_balance.txt').exists():
    last_balance = read_the_last_balance()
    # print(last_balance)

try:
    dl = Didlogic()
    balance = dl.get_balance()
    save_the_last_balance(balance)

    write_csv(f'{csv_root}/{csv_file}', timestamp, balance)

    if balance <= 500:
        send_notification = True
        notification += f'- <p>Balance: <span style="color:red">{balance}</span></p>'
    elif last_balance is not None and balance - last_balance > 0:
        send_notification = True
        notification += f'- <p>Balance: <span style="color:green">{balance}</span> (Top-up Completed)</p>'

except Exception as e:
    send_notification = True
    notification = f'- Failed to get the balance\n- exception: [{e}]'

finally:
    if send_notification:
        ct = CinnoxTool()
        ct.send_notification(notification)
        # print(notification)
