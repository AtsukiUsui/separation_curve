import rosbag
from std_msgs.msg import Float64

bag_file_path = "//home/atsuki/experiment/20203-07-03/2023-07-03-17-45-51.bag"
topic_name = "/luminous_intensity"

# メッセージの総数と合計値を初期化
count = 0
total_illumination = 0.0

# rosbagファイルを開く
bag = rosbag.Bag(bag_file_path)

# 指定したトピックのメッセージをイテレーション
for topic, msg, t in bag.read_messages(topics=[topic_name]):
    illumination = msg.data  # Float64メッセージのデータフィールドから値を取得
    total_illumination += illumination
    count += 1

# 平均値を計算
if count > 0:
    average_illumination = total_illumination / count
    rounded_illumination = round(average_illumination, 0)
    integer_illumination = int(rounded_illumination)
    print("Average Luminous Intensity:", integer_illumination)
else:
    print("No messages found on the", topic_name, "topic.")

# rosbagファイルを閉じる
bag.close()