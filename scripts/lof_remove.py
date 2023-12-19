import rosbag
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
import japanize_matplotlib
from concurrent.futures import ThreadPoolExecutor
import os

# LOFのパラメータ
n_neighbors = 100
contamination = 0.5


def read_bag_file(bag_file_path):
    bag = rosbag.Bag(bag_file_path)
    ranges_data = []
    intensities_data = []

    for topic, msg, t in bag.read_messages(topics=['/diag_scan']):
        range_values = np.array(msg.ranges)
        angles = np.arange(len(range_values)) * \
            msg.angle_increment + msg.angle_min
        valid_indices = np.where((2.4 <= range_values) & (
            range_values <= 5.0) & (-50 <= np.degrees(angles)) & (np.degrees(angles) <= 50))[0]

        ranges_data.extend(range_values[valid_indices])
        intensities_data.extend(np.array(msg.intensities)[valid_indices])

    bag.close()

    return ranges_data, intensities_data


def read_luminous_intensity(bag):
    luminous_intensity_data = [msg.data for topic, msg,
                               t in bag.read_messages(topics=['/luminous_intensity'])]
    return int(np.mean(luminous_intensity_data))


def process_bag_file(bag_file_path):
    bag = rosbag.Bag(bag_file_path)
    ranges_data, intensities_data = read_bag_file(bag_file_path)
    average_luminous_intensity = read_luminous_intensity(bag)
    data_points = np.stack((ranges_data, intensities_data), axis=-1)
    lof = LocalOutlierFactor(n_neighbors=n_neighbors,
                             contamination=contamination)
    outlier_labels = lof.fit_predict(data_points)

    # 外れ値を取り除く
    ranges_data_filtered = np.array(ranges_data)[outlier_labels != -1]
    intensities_data_filtered = np.array(intensities_data)[
        outlier_labels != -1]

    # ファイル名を作成（拡張子を除外）
    bag_file_name = os.path.splitext(os.path.basename(bag_file_path))[0]

    return ranges_data, intensities_data, ranges_data_filtered, intensities_data_filtered, average_luminous_intensity, bag_file_name


# bagファイルのパスを指定するリスト
bag_file_paths = [
    "/home/atsuki/lab_ws/src/experiment/2023-07-10-1/1_2023-07-10-11-42-50.bag"]

# 各bagファイルに対して処理を行う
with ThreadPoolExecutor() as executor:
    results = list(executor.map(process_bag_file, bag_file_paths))


# LOF処理されたデータを保存
for result in results:
    output_dir = '/home/atsuki/lab_ws/src/separation_curve/date/'
    filename = f'{output_dir}lof_processed_data_{result[5]}_neighbors_{n_neighbors}_contamination_{contamination}.csv'
    np.savetxt(filename, np.column_stack(
        [result[2], result[3]]), delimiter=',', header='距離,反射強度', comments='')

# グラフのサイズを設定
plt.figure(figsize=(12, 5))

# 処理前のグラフ
plt.subplot(1, 2, 1)
plt.scatter(results[0][0], results[0][1], alpha=1,
            label=f'{results[0][4]} lx', s=0.001)
plt.title("処理前")
plt.xlabel('距離 / m')
plt.ylabel('反射強度')
plt.legend()
# plt.ylim(2000, 3000)
plt.tick_params(which='both', direction='in', top=True, right=True)

# 処理後のグラフ
plt.subplot(1, 2, 2)
plt.scatter(results[0][2], results[0][3], alpha=1,
            label=f'{results[0][4]} lx', s=0.001)
plt.title("処理後")
plt.xlabel('距離 / m')
plt.ylabel('反射強度')
plt.legend()
# plt.ylim(2000, 3000)
plt.tick_params(which='both', direction='in', top=True, right=True)

# グラフを表示
plt.show()
