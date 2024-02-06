#!/usr/bin/env python

import rospy
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import Path
import numpy as np
from queue import PriorityQueue


class AStarPlanner:
    def __init__(self):
        rospy.init_node('astar_planner')

        self.map_received = False
        self.map_width = 0
        self.map_height = 0
        self.resolution = 0.0
        self.origin = [0.0, 0.0, 0.0]
        self.obstacles = None

        self.start = (0, 0)
        self.goal = (0, 0)

        self.path_pub = rospy.Publisher('/planned_path', Path, queue_size=1)
        rospy.Subscriber('/map', OccupancyGrid, self.map_callback)
        rospy.Subscriber('/move_base_simple/goal',
                         PoseStamped, self.goal_callback)
        rospy.Subscriber(
            '/initialpose', PoseWithCovarianceStamped, self.start_callback)

    def map_callback(self, data):
        if not self.map_received:
            self.map_width = data.info.width
            self.map_height = data.info.height
            self.resolution = data.info.resolution
            self.origin = [data.info.origin.position.x,
                           data.info.origin.position.y, 0.0]

            data_array = np.array(data.data)
            data_array = data_array.reshape((self.map_height, self.map_width))

            # Convert unknown and obstacle values to binary obstacles (0 and 100 in typical occupancy grid)
            self.obstacles = np.logical_or(data_array == 100, data_array == -1)

            self.map_received = True

    def goal_callback(self, data):
        self.goal = (int(round((data.pose.position.x - self.origin[0]) / self.resolution)),
                     int(round((data.pose.position.y - self.origin[1]) / self.resolution)))

        if self.map_received:
            self.plan_path()

    def start_callback(self, data):
        self.start = (int(round((data.pose.pose.position.x - self.origin[0]) / self.resolution)),
                      int(round((data.pose.pose.position.y - self.origin[1]) / self.resolution)))

        if self.map_received:
            self.plan_path()

    def plan_path(self):
        obstacles = self.obstacles
        path = self.astar(self.start, self.goal, obstacles)

        if path:
            path_msg = Path()
            path_msg.header.stamp = rospy.Time.now()
            path_msg.header.frame_id = "map"

            for point in path:
                pose = PoseStamped()
                pose.pose.position.x = point[0] * \
                    self.resolution + self.origin[0]
                pose.pose.position.y = point[1] * \
                    self.resolution + self.origin[1]
                path_msg.poses.append(pose)

            self.path_pub.publish(path_msg)

    def astar(self, start, goal, obstacles):
        def heuristic(node):
            return np.linalg.norm(np.array(node) - np.array(goal))

        def is_valid(node):
            x, y = node
            return 0 <= x < self.map_width and 0 <= y < self.map_height and not obstacles[y, x]

        def reconstruct_path(came_from, current):
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.insert(0, current)
            return path

        open_set = PriorityQueue()
        open_set.put((0, start))

        came_from = {}
        cost_so_far = {start: 0}

        while not open_set.empty():
            current_cost, current_node = open_set.get()

            if current_node == goal:
                return reconstruct_path(came_from, goal)

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current_node[0] + dx, current_node[1] + dy)

                if not is_valid(neighbor):
                    continue

                new_cost = cost_so_far[current_node] + \
                    1  # Assuming uniform cost

                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + heuristic(neighbor)
                    open_set.put((priority, neighbor))
                    came_from[neighbor] = current_node

        return None  # No path found


if __name__ == '__main__':
    planner = AStarPlanner()
    rospy.spin()
