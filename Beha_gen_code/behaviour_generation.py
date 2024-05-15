#!/usr/bin/python3

import sys
import os
import time
import math
import numpy as np
import rospy

import std_msgs
from std_msgs.msg import UInt8, UInt16, UInt32, Float32MultiArray, UInt16MultiArray, UInt32MultiArray
from nav_msgs.msg import Odometry

import geometry_msgs
from geometry_msgs.msg import Twist, TwistStamped
from sensor_msgs.msg import JointState, Imu

import miro2 as miro

################################################################

# constants
max_fwd_spd = 0.4
T_ramp_up_down = 2.0

def error(msg):

	print(msg)
	sys.exit(0)

################################################################

class Client:

	def callback_package(self, msg):

		# ignore until active
		if not self.active:
			return

		# extract opto data
		wheel_speed = np.array(msg.wheel_speed_opto.data)

		# update controller
		self.controller.update_sensors(wheel_speed)

		# write line to log file
		if self.write_log:
			w = wheel_speed
			w = np.append(w, self.controller.pose_tgt.x)
			w = np.append(w, self.controller.pose_tgt.y)
			w = np.append(w, self.controller.pose_tgt.theta)
			w = np.append(w, self.controller.pose_est.x)
			w = np.append(w, self.controller.pose_est.y)
			w = np.append(w, self.controller.pose_est.theta)
			w = np.append(w, self.cmd_vel.dr)
			w = np.append(w, self.cmd_vel.dtheta)
			sw = np.array2string(w, max_line_width=np.nan, precision=3)
			self.fid.write(sw[1:-1] + "\n")   

	def callback_kin(self, msg):

		# ignore until active
		if not self.active:
			return

		# report
		self.kin_sensor = msg.position

	def loop(self):
        # emo-pars
		A = 0.6# Arousal [-1,1]
		P = 0.6 # Pleasure
		D = 0.6 # Dominance
		E = A+P # Calculated Emotion
		# s = 0.4*A # relationship between arousal and awareness time step 
		if D < 0:
			Suppression = (P+1)/2*math.exp(D)     # [0,1]or (0,1]
			Velocity = math.exp(0.5*A+D-0.5)
			Amplitude = np.minimum(1, (P+1)*math.exp(0.5*A+D-0.5))
			Frequency = math.exp(A-1)
		else:
			Suppression = (P+1)/2     # [0,1]or (0,1]
			Velocity = math.exp(0.5*A-0.5)
			Amplitude = np.minimum(1, (P+1)*math.exp(0.5*A-0.5))
			Frequency = math.exp(A-1)
		s = 1/Frequency + 2.0  # seconds  +2.0 to prevent very frequent movement like one per sec
		d = int(5 * Amplitude) # duration time (wheel control) of going straight before turning away
		print("supp, Vel, Amp, Freq", Suppression, Velocity, Amplitude, Frequency)

		# beha-pars
		neut_tail_droop = 0.5  #neutral values
		neut_tail_wag = 0.5
		neut_eyes = 0.2
		neut_ears = 0.5
		neut_lift = np.radians(30.0)
		neut_yaw = np.radians(0.0)
		neut_pitch = np.radians(0.0)
		neut_vel_linear = 0.4
		neut_vel_angular = 0.3*np.pi  # just for one direction


		scale_tail_droop = 0.5  # Amplitude (half of the scale)
		scale_tail_wag = 0.5  
		scale_eyes = 0.2
		scale_ears = 0.5
		scale_lift = np.radians(20.0)
		scale_yaw = np.radians(45.0)
		scale_pitch = np.radians(15.0)
		scale_vel_linear = 0.4
		scale_vel_angular = 0.3*np.pi

        # pars
		f_kin = 0.25
		f_cos = 1.0

		# message
		msg_kin = JointState()
		msg_kin.position = [0.0, np.radians(30.0), 0.0, 0.0]

		# message
		msg_wheels = TwistStamped()
		msg_push = miro.msg.push()

		# message
		msg_cos = Float32MultiArray()
		msg_cos.data = [0.5, 0.5, 0.0, 0.0, 0.5, 0.5]

		# message
		msg_illum = UInt32MultiArray()
		msg_illum.data = [0, 0, 0, 0, 0, 0]

		# output
		msg_cmd_vel = geometry_msgs.msg.TwistStamped()


		# parameters
		T = 0.05
		
	
		theta_turn = np.pi * 0.5
		#theta_turn = np.pi

		
		# compute timings
		
		t = 0.0
		t_s1 = 0.0
		t_s2 = 0.0
		t_s3 = 0.0
		t_s4 = 0.0
		s_ran1 = np.random.randint(s-1, high = s+1)
		s_ran2 = np.minimum(2.0, np.random.randint(s-1, high = s+2))  # limit of eyes blinking frequency
		s_ran3 = np.random.randint(s-1, high = s+1)
		s_ran4 = np.random.randint(d-1, high = d+1)
		print("Initial S_random1, S_random2, S_random3", s_ran1, s_ran2, s_ran3)
		v = np.random.randint(0, high = 2)     # [0, 1]
		u = np.random.randint(0, high = 2)		# [0, 1]

		# loop
		while self.active and not rospy.core.is_shutdown():
            # break on loss of state file
			if not self.state_file is None:
				if not os.path.isfile(self.state_file):
					break

			# compute drive signals
			xk = math.sin(t * f_kin * 2 * math.pi)
			#xc = math.sin(t * f_cos * 2 * math.pi)
			xc = math.sin(t * (Frequency + 0.5) * 2 * math.pi)
			xcc = math.cos(t * f_cos * 2 * math.pi)
			xc2 = math.sin(t * f_cos * 1 * math.pi)

			# feedback to user
			c = self.count % 10
			if c == 0 and self.report_input and not self.sensors is None:
				print ("light", np.round(np.array(self.sensors.light.data) * 100.0))
				print ("battery", np.round(np.array(self.sensors.battery.voltage) * 100.0) / 100.0)
				print ("touch_body", '{0:016b}'.format(self.sensors.touch_body.data))
				x = self.sensors.imu_head.linear_acceleration
				print ("imu_head", [x.x, x.y, x.z])
				print ("----------------------------------------------------------------")

			# kin
			# Static
			msg_kin.position[1] = neut_lift - 2 * (Suppression - 0.5) * scale_lift
			#msg_kin.position[2] = neut_yaw + 2 * (Suppression - 0.5) * scale_yaw
			msg_kin.position[3] = neut_pitch - 2 * (Suppression - 0.5) * scale_pitch
				
			#msg_kin.position[1] = xk * np.radians(20.0) + np.radians(30.0)				
			#t = xk * np.radians(45.0)		
			#msg_kin.position[2] = t				
			#msg_kin.position[3] = xk * np.radians(15.0) + np.radians(-7.0)
			self.pub_kin.publish(msg_kin)

			if not self.kin_sensor is None:
				a = "[{:.3f}".format(msg_kin.position[1]) + "=" + "{:.3f}]".format(self.kin_sensor[1])
				b = "[{:.3f}".format(msg_kin.position[2]) + "=" + "{:.3f}]".format(self.kin_sensor[2])
				c = "[{:.3f}".format(msg_kin.position[3]) + "=" + "{:.3f}]".format(self.kin_sensor[3])
				print ("kin_sensors", a, b, c)

			# cos
			# Static
			msg_cos.data[0] = neut_tail_droop - 2 * (Suppression - 0.5) * scale_tail_droop
			#msg_cos.data[1] = neut_tail_wag + 2 * (Suppression - 0.5) * scale_tail_wag
			msg_cos.data[2] = neut_eyes - 2 * (Suppression - 0.5) * scale_eyes
			msg_cos.data[3] = neut_eyes - 2 * (Suppression - 0.5) * scale_eyes
			msg_cos.data[4] = neut_ears - 2 * (Suppression - 0.5) * scale_ears
			msg_cos.data[5] = neut_ears - 2 * (Suppression - 0.5) * scale_ears
			
			# Primary locomotion control
			if E >= 0.2:				
				if 0 <= (t_s1 - s_ran1) <= 1 :	# per s_ran time trigger movements
					i = np.minimum(t_s1 + 0.1 - s_ran1, 1.0 + s_ran1 - t_s1) #run for 1 sec, once t_s-s_ran=1, stop movement
					if i > 0:			
						msg_cos.data[1] = xc * 0.5 * Amplitude + 0.5  # wag tail
						print("move tail")
					else:
						t_s1 = 0
						s_ran1 = np.random.randint(s-1, high = s+1) #recount random number [s-1, s+2)
						#print("s_ran1 recalculate:", s_ran1)
				if 0 <= (t_s2 - s_ran2) <= 1:
					i = np.minimum(t_s2 + 0.1 - s_ran2, 1.0 + s_ran2 - t_s2) #run for 1 sec
					if i > 0:		
						for j in [2, 3]:  # eyes
							msg_cos.data[j] = xc * 0.5 + 0.5
						print("move eyes")
					else:
						t_s2 = 0
						s_ran2 = np.minimum(2.0, np.random.randint(s-1, high = s+1)) # to prevent blinking eyes too frequently
						#print("s_ran2 recalculate:", s_ran2)
				if 0 <= (t_s3 - s_ran3) <= 1:
					i = np.minimum(t_s3 + 0.1 - s_ran3, 1.0 + s_ran3 - t_s3) #run for 1 sec
					if i > 0:					
						for j in [4, 5]:  # ears
							msg_cos.data[j] = xc * 0.5 * Amplitude + 0.5
						print("move ears")
					else:
						t_s3 = 0
						s_ran3 = np.random.randint(s-1, high = s+1)
						#print("s_ran3 recalculate:", s_ran3)
			self.pub_cos.publish(msg_cos)
					
			
			# send illum
			if self.illum:
				q = int(xcc * -127 + 128)
				if t >= 4.0:
					self.active = False
					q = 0
				for i in range(0, 3):
					msg_illum.data[i] = (q << ((2-i) * 8)) | 0xFF000000
				for i in range(3, 6):
					msg_illum.data[i] = (q << ((i-3) * 8)) | 0xFF000000
				self.pub_illum.publish(msg_illum)
			
			
 			
			# yield
			time.sleep(T)
			t += T
			#print("t=", t)
			if t % 1.0 <= 0.05:
				t_s1 += 1
				t_s2 += 1
				t_s3 += 1
				t_s4 += 1
				print("t_s1, t_s2, t_s3, t_s4:", t_s1, t_s2, t_s3, t_s4)

			
			# Wheels
			

			'''			
			i = np.minimum(t - 0.5, 2.5 - t)
			if i >= 0:

				self.cmd_vel.dr = neut_vel_linear + (2.5-t) * scale_vel_linear
				self.cmd_vel.dtheta = neut_vel_angular + (-0.5*t) * scale_vel_angular

			i = np.minimum(t - 2.5, 4.5 - t)
			if i >= 0:

				self.cmd_vel.dr = neut_vel_linear + (t-2.5) * scale_vel_linear
				self.cmd_vel.dtheta = neut_vel_angular + (-t) * scale_vel_angular
			'''		
			#self.cmd_vel.dr = 0.6
			#self.cmd_vel.dtheta = 4
			#self.cmd_vel.dtheta = np.minimum(1.5, neut_vel_angular + 2 * (Amplitude - 0.5) * scale_vel_angular)

			#self.cmd_vel.dr = np.minimum(0.7, neut_vel_linear + 2 * (Velocity - 0.5) * scale_vel_linear)
			R = 0.1 / Amplitude
			#self.cmd_vel.dtheta = self.cmd_vel.dr / R    #turn left
			
			if E >= 0.2:				
				if 0 <= (t_s4 - s_ran4) <= 2 :	# per s_ran time trigger movements		
					#v = np.random.randint(0, high = 2)     # [0, 1]	
					v = u		
					i = np.minimum(t_s4 + 0.1 - s_ran4, 2.0 + s_ran4 - t_s4) #run for 2 sec
					if i > 0:	
						self.cmd_vel.dr = self.cmd_vel.dr / 2.0						
						if u == 0:						
							self.cmd_vel.dtheta = neut_vel_angular + 2 * (Amplitude - 0.5) * scale_vel_angular #turn left
						else:
							self.cmd_vel.dtheta = -neut_vel_angular - 2 * (Amplitude - 0.5) * scale_vel_angular #turn right
					else:
						t_s4 = 0
						s_ran4 = np.random.randint(s-1, high = s+1) #recount random number
						#print("s_ran1 recalculate:", s_ran1)
				else:
					self.cmd_vel.dr = np.minimum(0.7, neut_vel_linear + 2 * (Velocity - 0.5) * scale_vel_linear)					
					u = np.random.randint(0, high = 2)		# [0, 1]
					if A >= 0.7:
						self.cmd_vel.dtheta = 0
					else:
						if v == 0:
							self.cmd_vel.dtheta = self.cmd_vel.dr / R    #turn left
						else:
							self.cmd_vel.dtheta = -self.cmd_vel.dr / R    #turn right
						
			

			print("vel_linearX",self.cmd_vel.dr)
			print("vel_angularZ",self.cmd_vel.dtheta)
			
			
			
			# send velocity
			msg_cmd_vel.twist.linear.x = self.cmd_vel.dr
			msg_cmd_vel.twist.angular.z = self.cmd_vel.dtheta
			self.pub_cmd_vel.publish(msg_cmd_vel)
			
			
		# finalise report
		print ("\n\nexit...")
		print (" ")

	def __init__(self, args):
        
        # state
		self.state_file = None
		self.count = 0
		self.active = False
		self.forever = False

		# input
		self.report_input = True
		self.sensors = None

		self.kin_sensor = None

		# options
		self.report_wheels = False
		self.report_file = None
		self.wheels = None
		self.wheelsf = None
		self.spin = None
		self.kin = ""
		self.cos = ""
		self.illum = False
		self.push = False
		self.opts = []
        # from ^ client_test



		# state
		self.active = False
		self.controller = miro.lib.PoseController()
		self.cmd_vel = miro.lib.DeltaPose()

		# params
		self.closed_loop = True
		self.write_log = False
		
		# handle args
		for arg in args:

			if arg == "--open-loop":
				self.closed_loop = False
				continue

			if arg == "--write-log":
				self.write_log = True
				continue


			error("argument not recognised \"" + arg + "\"")

		# open log file
		if self.write_log:
			self.fid = open("/tmp/log", "w")

		# robot name
		topic_base_name = "/" + os.getenv("MIRO_ROBOT_NAME")

		# subscribe
		topic = topic_base_name + "/sensors/package"
		print ("subscribe", topic)
		self.sub_package = rospy.Subscriber(topic, miro.msg.sensors_package, self.callback_package, queue_size=1, tcp_nodelay=True)

		# publish
		topic = topic_base_name + "/control/cmd_vel"
		print ("publish", topic)
		self.pub_cmd_vel = rospy.Publisher(topic, geometry_msgs.msg.TwistStamped, queue_size=0)

		# publish
		topic = topic_base_name + "/control/flags"
		print ("publish", topic)
		self.pub_flags = rospy.Publisher(topic, std_msgs.msg.UInt32, queue_size=0)
        
        # publish
		topic = topic_base_name + "/control/kinematic_joints"
		print ("publish", topic)
		self.pub_kin = rospy.Publisher(topic, JointState, queue_size=0)

		# publish
		topic = topic_base_name + "/control/cosmetic_joints"
		print ("publish", topic)
		self.pub_cos = rospy.Publisher(topic, Float32MultiArray, queue_size=0)

		# publish
		topic = topic_base_name + "/control/illum"
		print ("publish", topic)
		self.pub_illum = rospy.Publisher(topic, UInt32MultiArray, queue_size=0)

		# publish
		topic = topic_base_name + "/core/mpg/push"
		print ("publish", topic)
		self.pub_push = rospy.Publisher(topic, miro.msg.push, queue_size=0)

		# wait for connect
		print ("\nwait for connect... ",)
		sys.stdout.flush()
		time.sleep(1)
		print ("OK")

		# send control flags
		default_flags = miro.constants.PLATFORM_D_FLAG_DISABLE_STATUS_LEDS
		msg = std_msgs.msg.UInt32()
		msg.data = default_flags
		msg.data |= miro.constants.PLATFORM_D_FLAG_PERSISTENT
		msg.data |= miro.constants.PLATFORM_D_FLAG_DISABLE_CLIFF_REFLEX
		print ("send control flags... ",)
		print (hex(msg.data),)
		self.pub_flags.publish(msg)
		print ("OK")

		# set to active
		self.active = True

if __name__ == "__main__":

	# normal singular invocation
	rospy.init_node("client_follower", anonymous=True)
	main = Client(sys.argv[1:])
	main.loop()
