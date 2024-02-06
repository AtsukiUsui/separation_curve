import rosbag
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# bagファイルのパスを指定するリスト
bag_file_paths = ["/home/atsuki/lab_ws/src/experiment/2023-09-28/2_shiba_2023-09-28-10-56-59.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-09-26_2/3_shiba_2023-09-26-17-46-16.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-07-10-2/5-shiba_2023-07-10-21-28-21.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-10-27/5_shiba_2023-10-27-12-03-22.bag",
                  "/home/atsuki/lab_ws/src/experiment/2023-09-26_1/6_shiba_2023-09-26-15-57-07.bag"
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


# 対数近似の計算
coefficients_log = np.polyfit(
    np.log(mean_luminous_intensity_array), mean_intensities_array, 1)
a1, b1 = coefficients_log
print(f'Logarithmic Fit: {a1} * log(x) + {b1}')

# 線形近似の計算
coefficients_linear = np.polyfit(
    mean_luminous_intensity_array, mean_intensities_array, 1)
a2, b2 = coefficients_linear
print(f'Linear Fit: {a2} * x + {b2}')

# 2次近似の計算
coefficients_quadratic = np.polyfit(
    mean_luminous_intensity_array, mean_intensities_array, 2)
a3, b3, c3 = coefficients_quadratic
print(f'Quadratic Fit: {a3} * x^2 + {b3} * x + {c3}')
# 2次近似のパラメータを出力（指数表記を使わない）
print(f'Quadratic Fit: {a3:.15f} * x^2 + {b3:.15f} * x + {c3:.15f}')


# プロット
plt.scatter(mean_luminous_intensity_array,
            mean_intensities_array, label='Data')
# plt.plot(mean_luminous_intensity_array, a2 *
#          mean_luminous_intensity_array + b2, 'r', label='Linear Fit')
# plt.plot(mean_luminous_intensity_array, a1 *
#          np.log(mean_luminous_intensity_array) + b1, 'g', label='Logarithmic Fit')
# plt.plot(mean_luminous_intensity_array, a3 * mean_luminous_intensity_array **
#          2 + b3 * mean_luminous_intensity_array + c3, 'b', label='Quadratic Fit')
plt.xlabel('Mean Luminous Intensity / lx')
plt.ylabel('Mean Intensities')


# x軸とy軸の最大値を設定
x_max = np.max(mean_luminous_intensity_array) + 5000
x_min = np.min(mean_luminous_intensity_array) - 5000
y_max = np.max(mean_intensities_array) + 50
y_min = np.min(mean_intensities_array) - 50
# plt.xlim(x_min, x_max)
# plt.ylim(y_min, y_max)
plt.xlim(-20000, x_max)
plt.ylim(2450, y_max)


# 目盛り線の向きを内側に設定（補助目盛りも含む）
plt.tick_params(which='both', direction='in', top=True, right=True)
# 補助目盛りの表示
# plt.minorticks_on()
plt.legend()

# プロットを表示
plt.show()
