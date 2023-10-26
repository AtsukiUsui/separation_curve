import rosbag
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# bagファイルのパスを指定するリスト
bag_file_paths = ["/home/atsuki/lab_ws/src/experiment/2023-07-10-2/1_2023-07-10-21-08-04.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-2/2_2023-07-10-21-12-41.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-2/3_2023-07-10-21-17-06.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-2/4_2023-07-10-21-23-25.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-09-26_1/1_2023-09-26-15-25-43.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-09-26_1/2_2023-09-26-15-36-27.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-09-26_1/3_2023-09-26-15-42-31.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-1/1_2023-07-10-11-42-50.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-1/2_2023-07-10-11-49-39.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-1/3_2023-07-10-12-31-25.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-1/4_2023-07-10-12-36-53.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-09-28/4_2023-09-28-11-04-12.bag"
                  ]

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

    angle_limit = 70

    # データを読み取り、/diag_scanトピックからデータを収集
    for topic, msg, t in bag.read_messages(topics=['/diag_scan']):
        angle_min = msg.angle_min  # 最小角度
        angle_increment = msg.angle_increment  # 角度の増分
        for i in range(360):
            angle = angle_min + i * angle_increment  # 各データ点の角度を計算
            range_value = msg.ranges[i]
            if 3 <= range_value <= 4.0 and -angle_limit <= np.degrees(angle) <= angle_limit:
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
def logarithmic_function(x, a1, b1):
    return a1 * np.log(x) + b1


# 対数近似を実行
params, covariance = curve_fit(
    logarithmic_function, mean_luminous_intensity_array, mean_intensities_array)
# 対数近似結果からaとbの値を取得
a1, b1 = params
# 対数近似のパラメータを出力
print(f'Logarithmic Fit:  {a1} * log(x) - {b1}')


# 線形近似関数の定義
def linear_function(x, a2, b2):
    return a2 * x + b2


# 線形近似を実行
params, covariance = curve_fit(
    linear_function, mean_luminous_intensity_array, mean_intensities_array)

# 線形近似結果からaとbの値を取得
a2, b2 = params

# 線形近似のパラメータを出力
print(f'Linear Fit: {a2} * x + {b2}')


# 2次近似関数の定義
def quadratic_function(x, a3, b3, c3):
    return a3 * x**2 + b3 * x + c3


# 2次近似を実行
params, covariance = curve_fit(
    quadratic_function, mean_luminous_intensity_array, mean_intensities_array)

# 2次近似結果からa, b, cの値を取得
a3, b3, c3 = params

# 2次近似のパラメータを出力
print(f'Quadratic Fit: {a3} * x^2 + {b3} * x + {c3}')


# プロット
plt.scatter(mean_luminous_intensity_array,
            mean_intensities_array, label='Data')
plt.plot(mean_luminous_intensity_array, logarithmic_function(
    mean_luminous_intensity_array, a1, b1), 'g', label='Logarithmic Fit')
plt.plot(mean_luminous_intensity_array, linear_function(
    mean_luminous_intensity_array, a2, b2), 'r', label='liner Fit')
plt.plot(mean_luminous_intensity_array, quadratic_function(
    mean_luminous_intensity_array, a3, b3, c3), 'b', label='Quadratic Fit')

plt.xlabel('Mean Luminous Intensity')
plt.ylabel('Mean Intensities')
plt.legend()

# プロットを表示
plt.show()
