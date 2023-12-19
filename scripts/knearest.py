import rosbag
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors


def read_rosbag_data(bag_file_path):
    ranges_data = []
    intensities_data = []

    with rosbag.Bag(bag_file_path, 'r') as bag:
        for topic, msg, t in bag.read_messages(topics=['/diag_scan']):
            for i, range_value in enumerate(msg.ranges):
                # データの処理ロジックを追加（例: 特定の条件を満たすデータのみ取得）
                if 2.4 <= range_value <= 5.0:
                    ranges_data.append(range_value)
                    intensities_data.append(msg.intensities[i])

    return np.array(ranges_data), np.array(intensities_data)


if __name__ == "__main__":
    bag_file_path = "/home/atsuki/lab_ws/src/experiment/2023-07-10-1/1_2023-07-10-11-42-50.bag"
    ranges_data, intensities_data = read_rosbag_data(bag_file_path)

    # データポイントを作成
    data_points = np.stack((ranges_data, intensities_data), axis=-1)

    neigh = NearestNeighbors(n_neighbors=2)
    knn_distances, _ = neigh.fit(data_points).kneighbors(data_points)

    # 距離のソート
    sorted_distances = np.sort(knn_distances[:, 1])  # 2番目の近傍までの距離を使用

    # ソートされた距離の可視化
    plt.plot(sorted_distances)
    plt.title('Sorted Distances between Data Points')
    plt.xlabel('Data Point Pairs')
    plt.ylabel('Distance')
    plt.ylim(0, 0.01)
    plt.show()
