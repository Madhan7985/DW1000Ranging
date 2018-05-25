'''
The MIT License (MIT)
Copyright (c) 2015 Boudjada Messaoud
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
# input tree points
import socket
# make the points in a 2d tuple if you want to use static points later
R1 = (0.6,0.48)
R2 = (2.48,2.95)
R3 = (4.65,0.63)

host_ip = '10.2.129.175'
port = 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host_ip,port))


while (1):
	# you have to introduce the distances 
	try :
		d_string = s.recv(1024)
		a = d_string.split(",")
		d1 = float(a[1])
		d2 = float(a[0])
		d3 = float(a[2])
		if d1 > 10 or d2 > 10 or d3 > 10:
			continue
		# if d1 ,d2 and d3 in known
		# calculate A ,B and C coifficents
		A = R1[0]**2 + R1[1]**2 - d1**2
		B = R2[0]**2 + R2[1]**2 - d2**2
		C = R3[0]**2 + R3[1]**2 - d3**2
		X32 = R3[0] - R2[0]
		X13 = R1[0] - R3[0]
		X21 = R2[0] - R1[0]

		Y32 = R3[1] - R2[1]
		Y13 = R1[1] - R3[1]
		Y21 = R2[1] - R1[1]

		x = (A * Y32 + B * Y13 + C * Y21)/(2.0*(R1[0]*Y32 + R2[0]*Y13 + R3[0]*Y21))
		y = (A * X32 + B * X13 + C * X21)/(2.0*(R1[1]*X32 + R2[1]*X13 + R3[1]*X21))
		# prompt the result
		print "(x,y) = ("+str(x)+","+str(y)+")"
	except KeyboardInterrupt : 
		pass