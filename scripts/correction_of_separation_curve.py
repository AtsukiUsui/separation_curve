import rosbag
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# bagファイルのパスを指定するリスト
bag_file_paths = ["/home/atsuki/lab_ws/src/experiment/2023-07-10-1/7-renga_2023-07-10-12-46-37.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-2/7-renga_2023-07-10-21-32-12.bag"]

# 平均値を計算するための関数


def calculate_mean(data_list):
    if len(data_list) == 0:
        return None
    return sum(data_list) / len(data_list)


# データの初期化
mean_intensities_list = []
mean_luminous_intensity_list = []

# 各bagファイルに対して処理を行う
for bag_file_path in bag_file_paths:
    bag = rosbag.Bag(bag_file_path)

    # 初期化
    ranges_data = []
    intensities_data = []
    luminous_intensity_data = []

    # データを読み取り、/diag_scanトピックからデータを収集
    for topic, msg, t in bag.read_messages(topics=['/diag_scan']):
        for i in range(360):
            range_value = msg.ranges[i]
            if 3.0 <= range_value <= 8.0:  # 3〜8メートルの範囲内のデータのみ収集
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

    # 結果を出力
    print(f"Bag File: {bag_file_path}")
    print(f"Mean Ranges: {mean_ranges}")
    print(f"Mean Intensities: {mean_intensities}")
    print(f"Mean Luminous Intensity: {mean_luminous_intensity}")
    print("")

    # bagファイルを閉じる
    bag.close()

# データをNumPy配列に変換
mean_intensities_array = np.array(mean_intensities_list)
mean_luminous_intensity_array = np.array(mean_luminous_intensity_list)

# 対数近似関数の定義（例として対数関数を使用）


def logarithmic_function(x, a, b):
    return a * np.log(x) + b


# 対数近似を実行
params, covariance = curve_fit(
    logarithmic_function, mean_luminous_intensity_array, mean_intensities_array)

# 対数近似結果からaとbの値を取得
a, b = params


# 対数近似のパラメータを出力
print(f'{a} * log(x) - {b}')


# プロット
plt.scatter(mean_luminous_intensity_array,
            mean_intensities_array, label='Data')
plt.plot(mean_luminous_intensity_array, logarithmic_function(
    mean_luminous_intensity_array, a, b), 'r', label='Logarithmic Fit')
plt.xlabel('Mean Luminous Intensity')
plt.ylabel('Mean Intensities')
plt.legend()

# プロットを表示
plt.show()
