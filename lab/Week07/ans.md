Q1) how many fields are there in the UDP header.  

4

Q2) what are the name and value of each field in the UDP header.  

Q3) the length (in bytes) of each fields in the UDP header.

| name        | value  | Length(bit) |
| ----------- | ------ | ----------- |
| Source Port | 443    | 16          |
| Destination | 61008  | 16          |
| Length      | 1260   | 16          |
| Checksum    | 0x25f4 | 16          |

  

Q4) What is the maximum number of bytes of a UDP packet ?

65535 bytes

Q5) What is the largest possible destination port number? (Hint: same as the hint in Q4 above.)

65535

Q6) What is the protocol ID for UDP in IP protocol?(Give your answer in both hexadecimal and decimal notation. )

17   0x11









Q4)

seq==0	SYN==1

Q5)

seq==0	ack==1	ack = seq_from_client +1	SYN==1, ACK==1

Q6)

seq==1

Q7)

p1:  seq==1	estRTT==0.02746

p2:  seq==566	estRTT==0.02847

p3:  seq==2026	estRTT==0.03367

p4:  seq==3486	estRTT==0.04376

p5:  seq==4946	estRTT==0.05578

p6:  seq==6406	estRTT==0.07251

Q9)

62780

Q10)

NO

Q12)

177851 / 5.461175 = 32566.43