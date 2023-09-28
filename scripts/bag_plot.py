import rosbag
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib


# bagファイルのパスを指定するリスト
bag_file_paths = ["/home/atsuki/lab_ws/src/experiment/2023-09-28/2_shiba_2023-09-28-10-56-59.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-09-26_1/6_shiba_2023-09-26-15-57-07.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-09-26_2/3_shiba_2023-09-26-17-46-16.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-2/5-shiba_2023-07-10-21-28-21.bag"]


# 各bagファイルに対して処理を行う
for bag_file_path in bag_file_paths:
    bag = rosbag.Bag(bag_file_path)

    # 初期化
    ranges_data = []
    intensities_data = []
    luminous_intensity_data = []  # luminous_intensityデータを格納するリストを追加

    # データを読み取り、/diag_scanトピックからデータを収集
    for topic, msg, t in bag.read_messages(topics=['/diag_scan']):
        for i in range(360):
            range_value = msg.ranges[i]
            if 3.0 <= range_value <= 10.0:  # 3〜8メートルの範囲内のデータのみ収集
                ranges_data.append(range_value)
                intensities_data.append(msg.intensities[i])

    # /luminous_intensityトピックからデータを収集
    for topic, msg, t in bag.read_messages(topics=['/luminous_intensity']):
        luminous_intensity_data.append(msg.data)

    # luminous_intensityの平均値を計算
    average_luminous_intensity = int(np.mean(luminous_intensity_data))
    print(
        f'Average Luminous Intensity ({bag_file_path}): {average_luminous_intensity}')

    # bagファイルを閉じる
    bag.close()

    plt.rcParams["xtick.direction"] = "in"  # x軸の目盛線を内向きへ
    plt.rcParams["ytick.direction"] = "in"  # y軸の目盛線を内向きへ
    plt.rcParams["xtick.minor.visible"] = True  # x軸補助目盛りの追加
    plt.rcParams["ytick.minor.visible"] = True  # y軸補助目盛りの追加

    # プロット
    plt.scatter(ranges_data, intensities_data, alpha=0.5,
                label=f'{average_luminous_intensity} lx')

# グラフの軸ラベルと凡例を設定
plt.title(
    "環境光と反射強度の関係", y=-0.16)
plt.xlabel('距離 / m')
plt.ylabel('反射強度')
plt.legend()

# 軸範囲設定
plt.xlim(3, 10)
plt.ylim(0, 3000)


# プロットを表示
plt.show()
