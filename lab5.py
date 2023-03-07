import socket
import time
import sys
import time
import math
import numpy as np
from NatNetClient import NatNetClient
from util import quaternion_to_euler_angle_vectorized1

positions = {}
rotations = {}
target = [-2,1.8]
IP_ADDRESS = '192.168.0.212'
clientAddress = "192.168.0.30"
optitrackServerAddress = "192.168.0.4"
robot_id = 212
v = 0
omega = 0
distance = 10000

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receive_rigid_body_frame(robot_id, position, rotation_quaternion):
    # Position and rotation received
    positions[robot_id] = position
    # The rotation is in quaternion. We need to convert it to euler angles

    rotx, roty, rotz = quaternion_to_euler_angle_vectorized1(rotation_quaternion)

    rotations[robot_id] = rotz




def find_distance(positions, target):
    x_diff = target[0] - positions[0]
    y_diff = target[1] - positions[1]
    dis = x_diff * x_diff + y_diff * y_diff
    return math.sqrt(dis)

def find_orientation(positions, target):
    x_diff = target[0] - positions[0]
    y_diff = target[1] - positions[1]
    orientation = np.arctan2(y_diff, x_diff)
    return orientation

def send_speed(v, omega):
    u = np.array([v - omega, v + omega])
    u[u > 1500] = 1500
    u[u < -1500] = -1500
    # Send control input to the motors
    command = 'CMD_MOTOR#%d#%d#%d#%d\n'%(u[0], u[0], u[1], u[1])
    s.send(command.encode('utf-8'))

def find_orientation_error(desired_orientation, rotations_now):
    sin_tmp = math.sin(desired_orientation - math.radians(rotations_now))
    cos_tmp = math.cos(desired_orientation - math.radians(rotations_now))
    orientation_err = np.arctan2(sin_tmp, cos_tmp)
    orientation_err = math.degrees(orientation_err)
    return orientation_err
    
# Connect to the robot
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP_ADDRESS, 5000))
print('Connected')
# This will create a new NatNet client
streaming_client = NatNetClient()
streaming_client.set_client_address(clientAddress)
streaming_client.set_server_address(optitrackServerAddress)
streaming_client.set_use_multicast(True)
# Configure the streaming client to call our rigid body handler on the emulator to send data out.
streaming_client.rigid_body_listener = receive_rigid_body_frame

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
is_running = streaming_client.run()

time_index = 0
try:
    while is_running:
        if robot_id in positions:
            # last position
            # print('Last position', positions[robot_id], ' rotation', rotations[robot_id])
            time_index += 0.1
            # print("target: ",str(target))
            # print("time: ",time_index)

            distance = find_distance(positions[robot_id], target)
            # print('distance: ', distance)

            desired_orientation = find_orientation(positions[robot_id], target)
            # print('desired orientation: ', desired_orientation)
            # print('current orientation: ', rotations[robot_id])

            orientation_error = find_orientation_error(desired_orientation, rotations[robot_id])
            #print('orientation error: ', orientation_error)


            # print('Last position', positions[robot_id])
            

            print(time_index)
            print(distance)
            print(orientation_error)
            print('-----------------------------')
            
            v = 5000 * distance
            omega = 500 * orientation_error 
            send_speed(v, omega)

            time.sleep(0.1)

            if distance < 0.1:
                break
except KeyboardInterrupt:
    # STOP
    command = 'CMD_MOTOR#00#00#00#00\n'
    s.send(command.encode('utf-8'))

# Close the connection
command = 'CMD_MOTOR#00#00#00#00\n'
s.send(command.encode('utf-8'))
s.shutdown(2)
s.close()
streaming_client.shutdown()