import rosbag
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import japanize_matplotlib

# bagファイルのパスを指定するリストを3つに分ける
bag_file_paths_c1 = [
    "/home/atsuki/lab_ws/src/experiment/2023-09-26_2/3_shiba_2023-09-26-17-46-16.bag",
    "/home/atsuki/lab_ws/src/experiment/2023-07-10-2/5-shiba_2023-07-10-21-28-21.bag"
]

bag_file_paths_c2 = [
    "/home/atsuki/lab_ws/src/experiment/2023-09-26_1/6_shiba_2023-09-26-15-57-07.bag"
]

bag_file_paths_c3 = [
    "/home/atsuki/lab_ws/src/experiment/2023-09-28/2_shiba_2023-09-28-10-56-59.bag",
    "/home/atsuki/lab_ws/src/experiment/2023-10-27/5_shiba_2023-10-27-12-03-22.bag"
]

# 平均値を計算するための関数


def calculate_mean(data_list):
    if len(data_list) == 0:
        return None
    return sum(data_list) / len(data_list)

# bagファイルからデータを収集し平均値を計算する関数


def process_bag_files(bag_file_paths):
    mean_intensities_list = []
    mean_luminous_intensity_list = []

    for bag_file_path in bag_file_paths:
        bag = rosbag.Bag(bag_file_path)

        # 初期化
        ranges_data = []
        intensities_data = []
        luminous_intensity_data = []

        angle_limit = 70

        # データを読み取り、/diag_scanトピックからデータを収集
        for topic, msg, t in bag.read_messages(topics=['/diag_scan']):
            angle_min = msg.angle_min  # 最小角度
            angle_increment = msg.angle_increment  # 角度の増分
            for i in range(360):
                angle = angle_min + i * angle_increment  # 各データ点の角度を計算
                range_value = msg.ranges[i]
                if 2.5 <= range_value <= 4.0 and -angle_limit <= np.degrees(angle) <= angle_limit:
                    ranges_data.append(range_value)
                    intensities_data.append(msg.intensities[i])

        # /luminous_intensityトピックからデータを収集
        for topic, msg, t in bag.read_messages(topics=['/luminous_intensity']):
            luminous_intensity_data.append(msg.data)

        # 平均値を計算
        mean_ranges = calculate_mean(ranges_data)
        mean_intensities = calculate_mean(intensities_data)
        mean_luminous_intensity = calculate_mean(luminous_intensity_data)

        # データをリストに追加
        mean_intensities_list.append(mean_intensities)
        mean_luminous_intensity_list.append(mean_luminous_intensity)

        # bagファイルを閉じる
        bag.close()

    return mean_intensities_list, mean_luminous_intensity_list


# 各カテゴリのファイルパスからデータを処理する
mean_intensities_c1, mean_luminous_intensity_c1 = process_bag_files(
    bag_file_paths_c1)
mean_intensities_c2, mean_luminous_intensity_c2 = process_bag_files(
    bag_file_paths_c2)
mean_intensities_c3, mean_luminous_intensity_c3 = process_bag_files(
    bag_file_paths_c3)

# ここからグラフ作成の処理を行います
# ...

# プロットするために全カテゴリのデータを統合する
mean_intensities_array = np.array(
    mean_intensities_c1 + mean_intensities_c2 + mean_intensities_c3)
mean_luminous_intensity_array = np.array(
    mean_luminous_intensity_c1 + mean_luminous_intensity_c2 + mean_luminous_intensity_c3)

# プロット
plt.scatter(mean_luminous_intensity_c1,
            mean_intensities_c1, label='夜間', color='blue')
plt.scatter(mean_luminous_intensity_c2,
            mean_intensities_c2, label='曇天', color='gray')
plt.scatter(mean_luminous_intensity_c3,
            mean_intensities_c3, label='晴天', color='red')

plt.xlabel('平均周辺照度 / lx')
plt.ylabel('平均反射強度')

plt.xlim(-20000, 120000)
plt.ylim(2450, 2680)


# 目盛り線の向きを内側に設定（補助目盛りも含む）
plt.tick_params(which='both', direction='in', top=True, right=True)
# 補助目盛りの表示
# plt.minorticks_on()
plt.legend()

# プロットを表示
plt.show()
