import rosbag
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import japanize_matplotlib


def read_bag_file(bag_file_path):
    bag = rosbag.Bag(bag_file_path)
    ranges_data, intensities_data = read_diag_scan(bag)
    average_luminous_intensity = read_luminous_intensity(bag)
    bag.close()

    return np.array(ranges_data), np.array(intensities_data), average_luminous_intensity


def read_diag_scan(bag, sample_rate=1):
    ranges_data = []
    intensities_data = []

    angle_limit = 50
    sample_counter = 0

    for topic, msg, t in bag.read_messages(topics=['/diag_scan']):
        for i, range_value in enumerate(msg.ranges):
            angle = msg.angle_min + i * msg.angle_increment
            if 2.4 <= range_value <= 5.0 and -angle_limit <= np.degrees(angle) <= angle_limit:
                # サンプリングレートに基づいてデータを選択
                if sample_counter % sample_rate == 0:
                    ranges_data.append(range_value)
                    intensities_data.append(msg.intensities[i])
                sample_counter += 1

    return np.array(ranges_data), np.array(intensities_data)


def read_luminous_intensity(bag):
    luminous_intensity_data = np.array([msg.data for topic, msg,
                                        t in bag.read_messages(topics=['/luminous_intensity'])])
    return int(np.mean(luminous_intensity_data))


def cluster_data_points(ranges_data, intensities_data, eps, min_samples):
    data_points = np.stack((ranges_data, intensities_data), axis=-1)

    dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(data_points)

    cluster_labels = dbscan.labels_

    return cluster_labels, data_points


def plot_clustered_data_points(cluster_labels, data_points, marker_size):
    unique_labels = set(cluster_labels)
    for i in unique_labels:
        if i != -1:  # -1 label indicates noisy points
            cluster_data_points = data_points[cluster_labels == i]
            plt.scatter(*zip(*cluster_data_points), s=marker_size)


bag_file_paths = [
    "/home/atsuki/lab_ws/src/experiment/2023-07-10-1/1_2023-07-10-11-42-50.bag"]

eps = 0.0000002

# min_samples = 1000
min_samples_ratio = 0.3


marker_size = 0.001

for bag_file_path in bag_file_paths:
    ranges_data, intensities_data, average_luminous_intensity = read_bag_file(
        bag_file_path)

    min_samples = int(len(np.array(ranges_data)) * min_samples_ratio)

    plt.scatter(ranges_data, intensities_data, alpha=0.1,
                label=f'{average_luminous_intensity} lx', s=marker_size)

    cluster_labels, data_points = cluster_data_points(
        ranges_data, intensities_data, eps, min_samples)

    plot_clustered_data_points(cluster_labels, data_points, marker_size)

plt.title("環境光と反射強度の関係", y=-0.1)
plt.xlabel('距離 / m')
plt.ylabel('反射強度')
plt.legend()

plt.ylim(2000, 3000)

plt.tick_params(which='both', direction='in', top=True, right=True)

plt.show()
