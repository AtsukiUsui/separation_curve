import rosbag
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
import japanize_matplotlib
from concurrent.futures import ThreadPoolExecutor

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

    return ranges_data, intensities_data, outlier_labels, average_luminous_intensity


# bagファイルのパスを指定するリスト
bag_file_paths = [
    "/home/atsuki/lab_ws/src/experiment/2023-07-10-1/1_2023-07-10-11-42-50.bag"]

ranges_data_all = []
intensities_data_all = []
outlier_labels_all = []
average_luminous_intensity_all = []

# 各bagファイルに対して処理を行う
with ThreadPoolExecutor() as executor:
    results = list(executor.map(process_bag_file, bag_file_paths))

for result in results:
    ranges_data_all.extend(result[0])
    intensities_data_all.extend(result[1])
    outlier_labels_all.extend(result[2])
    average_luminous_intensity_all.append(result[3])

# プロット
plt.scatter(ranges_data_all, intensities_data_all, c=outlier_labels_all, cmap='viridis',
            alpha=1, label=f'{average_luminous_intensity_all[0]} lx', s=0.001)

# グラフの軸ラベルと凡例を設定
plt.title("環境光と反射強度の関係", y=-0.1)
plt.xlabel('距離 / m')
plt.ylabel('反射強度')
plt.legend()

plt.ylim(2000, 3000)

plt.tick_params(which='both', direction='in', top=True, right=True)

# プロットを表示
plt.show()
