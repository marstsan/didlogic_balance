from flask import Flask, render_template, request
import plotly.graph_objs as go
from lib.utils import *
import os.path
from lib.Didlogic import Didlogic
from datetime import datetime


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        number = int(request.form['number'])    # 從表單中獲取輸入的數字
    else:
        number = 14    # 預設查詢天數

    # 取的當前的餘額
    dl = Didlogic()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_balance = dl.get_balance()
    # 取得數據
    recent_dates = get_last_some_days(number)

    all_time_list, all_balance_list = [], []
    for date in recent_dates:
        file = f'csv/{date}.csv'
        if os.path.isfile(f'csv/{date}.csv'):
            time_list, balance_list = get_csv_data(file)
            all_time_list.extend(time_list)
            all_balance_list.extend(balance_list)

    # 把當下的時間與金額加到最後
    all_time_list.append(current_time)
    all_balance_list.append(current_balance)

    # 使用 Plotly 生成折線圖
    # plot = go.Figure(data=go.Scatter(x=all_time_list, y=all_balance_list, mode='lines+markers'))

    # text_balance = [y for y in all_balance_list]
    text_balance = []
    previous_balance, diff = None, None
    # line_color = []
    # plot = go.Figure()

    for i in range(len(all_balance_list)):
        if int(all_time_list[i][11:13]) % 24 == 0 and all_time_list[i][14] == '0':      # 加每日 0:00 的當下金額和與前一天的差
            if previous_balance is not None:
                diff = round(all_balance_list[i] - previous_balance, 2)

            text_balance.append(all_balance_list[i] if previous_balance is None else f'{all_balance_list[i]} ({"+" if diff > 0 else ""}{diff})')
            previous_balance = all_balance_list[i]

            # text_balance.insert(0, all_balance_list[i])
        elif i == len(all_balance_list) - 1:        # 加最後一筆
            text_balance.append(all_balance_list[i])
            previous_balance = all_balance_list[i]
        else:
            text_balance.append('')
            # text_balance.insert(0, '')
        # if i > 0:
        #     diff = all_balance_list[i - len(all_balance_list)] - all_balance_list[i-1 - len(all_balance_list)]
        #     if diff < 0:
        #         line_color.append('red')
        #     else:
        #         line_color.append('blue')
        #     plot.add_trace(go.Scatter(
        #         x=[all_time_list[i-1], all_time_list[i]],
        #         y=[all_balance_list[i-1], all_balance_list[i]],
        #         mode='lines+markers+text',
        #         text=text_balance,
        #         line=dict(color=line_color[len(all_balance_list)-1-i])))

    # 主要圖表
    plot = go.Figure(data=go.Scatter(
        x=all_time_list,
        y=all_balance_list,
        mode='lines+markers+text',
        text=text_balance,
        textposition="top center",
        marker={'color': '#8AD8FB'}
    ))

    # 水平線
    plot.add_shape(
        type='line',
        x0=all_time_list[0], y0=500, x1=all_time_list[-1], y1=500,
        line=dict(color='red', dash='dash', width=0.8),
        name='Threshold')

    # text 屬性
    plot.update_traces(textposition="top center", textfont=dict(
        family="Microsoft JhengHei",
        size=12,
        color='#222222'
    ))

    # 設置背景顏色和邊框寬度
    plot.update_layout(
        xaxis_title='Time',
        yaxis_title='Balance',
        plot_bgcolor='#F9F5E5',  # 設置背景顏色
        paper_bgcolor='#FFFBEB',  # 設置邊框顏色
        margin=dict(l=20, r=20, t=20, b=20),  # 設置圖表邊距
        xaxis=dict(gridcolor='#e0e0e0'), yaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#bdbdbd'),
        showlegend=False,
    )

    # 把 Plotly 圖轉換成 HTML 字符串
    plot_html = plot.to_html(full_html=False)

    # 將折線圖嵌入到模板中
    return render_template('index.html', plot_html=plot_html, number=number, current_balance=current_balance)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
