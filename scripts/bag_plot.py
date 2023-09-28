import rosbag
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib


# bagファイルのパスを指定するリスト
bag_file_paths = [
    "/home/atsuki/lab_ws/src/experiment/2023-09-28/1_renga_2023-09-28-10-53-29.bag"]


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


# 目盛り線の向きを内側に設定（補助目盛りも含む）
plt.tick_params(which='both', direction='in', top=True, right=True)
# plt.minorticks_on()  # 補助目盛りの表示

# プロットを表示
plt.show()
