## Assignment 01

#### Q1

| layer       | functionality                                      | protocols           |
| ----------- | -------------------------------------------------- | ------------------- |
| application | supporting network applications                    | IMAP, SMTP, HTTP    |
| transport   | process-process data transfer                      | TCP, UDP            |
| network     | routing of datagrams from source to destination    | IP, ICMP, FTP       |
| link        | data transfer between neighboring network elements | Ethernet, WIFI, PPP |
| physical    | physical structures transferring bit streams       |                     |



#### Q2

TCP:

​	applications that require no data loss but are not time-sensitive

​	file transfer, e-mail

UDP:

​	applications that can tolerate data loss at some level but are time-sensitive

​	live stream, Internet telephony

​	

#### Q3

(a)
$$
delay = K(\frac{L}{R} + d)
$$
(b)
$$
delay=\frac{LF}{R}
$$
(c)

We focus on the second packet.

At the source:

​	the second packet queue for the first one to transmit, so $d_{queue} = d_{trans}=\frac{L}{R}=50μs$

​	do the transmission, $d_{trans}=50μs$

​	to reach the router, $d_{prop}=10μs$

At the router:

​	do the processing, $d_{proc} = 5μs$

​	as the first packet has finished transmitting when the second one reached, no queue delay

​	do the transmission, $d_{trans} = 50μs$

​	to reach the destination, $d_{prop}=10μs$

in total, we have:
$$
delay = (50+50+10+5+50+10)μs=175μs
$$


#### Q4

(a)

​	No queuing delay.

(b)
$$
d_{avg} = \frac{1}{K}·\frac{(K - 1 + 1)(K - 1)}{2}·\frac{L}{R}=(\frac{K - 1}{2})s
$$
(c)

​	for (a) :
$$
intensity = \frac{λL}{R} = 1
$$
​	for (b) :

​		as $λ = \frac{K}{K} = 1$ , we have:
$$
intensity = \frac{λL}{R} = 1
$$
​	Insight: uneven packet-arrivals can lead to queuing delay, even if the average data arriving rate is equal to the transmission rate.



#### Q5

(a)

HTTP response message

(b)

It is a persistent connection. It hold the connection until it is not used for a period of time, so that the two ends can transfer multiple data using one connection, not having to set up a new connection every time when a file is transferring.

(c)

The blank line between the header and the body is absent.

(d)

The proxy server needs to save the last-modified entry for the files it stored, so that when a file is requested by a client, the proxy server can check from the origin server to see whether the file it stored is up-to-date, and update the file if needed.



#### Q6

(a)
$$
time = d_{internet} + d_{acc} = d_{internet} + \frac{Δ}{1-Δβ}= 2+\frac{0.05}{1- 0.05\cdot10}=2.1s
$$
(b)
$$
time' = (1- x) \cdot time < 1 \newline
x =1 - \frac{1}{2.1} = \frac{11}{21}
$$


#### Q7

(a)
$$
time = RTT_{0}+2RTT_{1}+\frac{L}{R}+12(2RTT_{1}+\frac{L}{R})=RTT_{0}+26RTT_{1}+13\cdot\frac{L}{R}
$$
(b)
$$
time=RTT_{0}+2RTT_{1}+\frac{L}{R}+\frac{12}{4}(2RTT_{1}+\frac{L}{R})=RTT_{0}+8RTT_{1}+4\cdot\frac{L}{R}
$$
(c)
$$
time=RTT_{0}+2RTT_{1}+\frac{L}{R}+RTT_{1}+12\cdot\frac{L}{R}=RTT_{0}+3RTT_{1}+13\cdot\frac{L}{R}
$$


#### Q8

(a)

HTTP:

* mainly used in the Web communication;

* a pull protocol, clients request data from the server;

* without status;

* the headers are encoded with ASCII;

SMTP:

* mainly used in e-mail delivering;

* a push protocol, the sender servers send data to the receiver servers;

* with status;

* the entire message is encoded with ASCII.

(b)

HTTP can actually be used to deliver emails. However, HTTP is not suitable to do the delivering between the sender servers and the receiver servers, because this process is regulated to use SMTP, using HTTP may cause chaos. HTTP is designed as a pull protocol, so using it to send emails are not as neutral as SMTP do. Also, HTTP lacks some useful features for e-mail businesses, For example, it is not convenient for HTTP to retrieval or delete emails.

(c)

* Placing the receiver's mail server at the receiver's PC is not a good idea. Without the dedicated mail server, the receiver's PC has to stably connect to the Internet all the time, otherwise it may lose some mails without the dedicated mail server storing them for it.

* Placing the sender's mail server at the sender's PC is not a good idea. Accepting the emails sent directly from the senders' PCs can lead to a brunch of security problems. It is safer if the sender's PC has a static IP address and a domain name, but this is usually impossible in our real lives.



#### Q9

(a) 

​	.com DNS server

(b)

​	(example.com, dns.example.com, NS)

​	(dns.example.com, 200.200.200.19, A)



#### Q10

(a)(b)

![plt](C:\Users\ASUS\Desktop\materials\Network\assignments\plt.png)

(c)

P2P is better. Because distribution time will not increase linearly as client-server model do when N grows. When $u$ is smaller than the upload speed of the server and the download rate of the peers(which is the usual case), the greater $u$ is, the less the distribution time is. When $u$ is greater than them, the distribution time is decided by the other two rates.





















