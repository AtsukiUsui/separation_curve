import rosbag
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib


def read_bag_file(bag_file_path):
    bag = rosbag.Bag(bag_file_path)
    ranges_data, intensities_data = read_diag_scan(bag)
    average_luminous_intensity = read_luminous_intensity(bag)
    bag.close()

    return ranges_data, intensities_data, average_luminous_intensity


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

    return ranges_data, intensities_data


def read_luminous_intensity(bag):
    luminous_intensity_data = [msg.data for topic, msg,
                               t in bag.read_messages(topics=['/luminous_intensity'])]
    return int(np.mean(luminous_intensity_data))


# bagファイルのパスを指定するリスト
bag_file_paths = [
    "/home/atsuki/lab_ws/src/experiment/2023-07-10-1/1_2023-07-10-11-42-50.bag"]

# 各bagファイルに対して処理を行う
for bag_file_path in bag_file_paths:
    ranges_data, intensities_data, average_luminous_intensity = read_bag_file(
        bag_file_path)

    # プロット
    plt.scatter(ranges_data, intensities_data, alpha=1,
                label=f'{average_luminous_intensity} lx', s=0.001)

# グラフの軸ラベルと凡例を設定
plt.title("環境光と反射強度の関係", y=-0.1)
plt.xlabel('距離 / m')
plt.ylabel('反射強度')
plt.legend()

plt.ylim(2000, 3000)

plt.tick_params(which='both', direction='in', top=True, right=True)

# プロットを表示
plt.show()
