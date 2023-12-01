import rosbag
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import japanize_matplotlib


def read_bag_file(bag_file_path):
    bag = rosbag.Bag(bag_file_path)
    ranges_data, intensities_data = read_diag_scan(bag)
    average_luminous_intensity = read_luminous_intensity(bag)
    bag.close()

    return ranges_data, intensities_data, average_luminous_intensity


def read_diag_scan(bag):
    ranges_data = []
    intensities_data = []

    angle_limit = 10

    for topic, msg, t in bag.read_messages(topics=['/diag_scan']):
        for i, range_value in enumerate(msg.ranges):
            angle = msg.angle_min + i * msg.angle_increment
            if 2.4 <= range_value <= 5.0 and -angle_limit <= np.degrees(angle) <= angle_limit:
                ranges_data.append(range_value)
                intensities_data.append(msg.intensities[i])

    return ranges_data, intensities_data


def read_luminous_intensity(bag):
    luminous_intensity_data = [msg.data for topic, msg,
                               t in bag.read_messages(topics=['/luminous_intensity'])]
    return int(np.mean(luminous_intensity_data))


def cluster_data_points(ranges_data, intensities_data, n_clusters):
    data_points = list(zip(ranges_data, intensities_data))

    kmeans = KMeans(n_clusters=n_clusters).fit(data_points)

    cluster_centers = kmeans.cluster_centers_
    cluster_indices = kmeans.predict(data_points)

    return cluster_centers, cluster_indices, data_points


def plot_clustered_data_points(cluster_centers, cluster_indices, data_points, n_clusters):
    for i in range(n_clusters):
        cluster_data_points = [data_points[j] for j in range(
            len(data_points)) if cluster_indices[j] == i]
        plt.scatter(*zip(*cluster_data_points))

    plt.scatter(*zip(*cluster_centers), c='black')


# bagファイルのパスを指定するリスト
bag_file_paths = [
    "/home/atsuki/lab_ws/src/experiment/2023-10-27/1_2023-10-27-11-42-24.bag"]

# クラスタ数を設定します。
n_clusters = 2

# 各bagファイルに対して処理を行う
for bag_file_path in bag_file_paths:
    ranges_data, intensities_data, average_luminous_intensity = read_bag_file(
        bag_file_path)

    # プロット
    plt.scatter(ranges_data, intensities_data, alpha=0.5,
                label=f'{average_luminous_intensity} lx')

    cluster_centers, cluster_indices, data_points = cluster_data_points(
        ranges_data, intensities_data, n_clusters)

    plot_clustered_data_points(
        cluster_centers, cluster_indices, data_points, n_clusters)

# グラフの軸ラベルと凡例を設定
plt.title("環境光と反射強度の関係", y=-0.1)
plt.xlabel('距離 / m')
plt.ylabel('反射強度')
plt.legend()

# 軸範囲設定
# plt.xlim(0, 5)
# plt.ylim(0, 6000)


plt.tick_params(which='both', direction='in', top=True, right=True)

# プロットを表示
plt.show()
