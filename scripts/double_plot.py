import rosbag
import numpy as np
import matplotlib.pyplot as plt

# bagファイルのパスを指定するリスト
bag_file_paths = ["/home/atsuki/lab_ws/src/experiment/2023-07-10-1/7-renga_2023-07-10-12-46-37.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-2/7-renga_2023-07-10-21-32-12.bag"]

# 各bagファイルに対して処理を行う
for bag_file_path in bag_file_paths:
    bag = rosbag.Bag(bag_file_path)

    # 初期化
    ranges_data = []
    intensities_data = []

    # データを読み取り、/diag_scanトピックからデータを収集
    for topic, msg, t in bag.read_messages(topics=['/diag_scan']):
        for i in range(360):
            range_value = msg.ranges[i]
            if 3.0 <= range_value <= 8.0:  # 3〜8メートルの範囲内のデータのみ収集
                ranges_data.append(range_value)
                intensities_data.append(msg.intensities[i])

    # プロット
    plt.scatter(ranges_data, intensities_data,
                label=f'Bag File: {bag_file_path}')

    # bagファイルを閉じる
    bag.close()

# グラフの軸ラベルと凡例を設定
plt.xlabel('Ranges')
plt.ylabel('Intensities')
plt.legend()

# プロットを表示
plt.show()
