# Assignment 1

## Basic Part

Passed the test in WSL:

<img src="C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\basic.png" alt="basic" style="zoom:67%;" />

For packet capturing, I run the steps in 4.yml manually in Windows.

In agent.py:

<img src="C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\agent.png" alt="agent" style="zoom:67%;" />

In Wireshark:

<img src="C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\wireshark.png" alt="wireshark" style="zoom:67%;" />

To make things more clear, I also put the screenshot of the output of my server here:

<img src="C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\server.png" alt="server" style="zoom:67%;" />



## Bonus Part

### Error report

In POP, I implement several types of error reporting, including CONN_REFUSED, AUTH_FAILED, INVALID_COMMAND, INVALID_ARGUMENT.

The core part of the code is as follow:
```python
def pop_error_report(error_code, msg=None):
    error_msg = ''
    if error_code == CONN_REFUSED:
        error_msg = '-ERR Connection refused'
    elif error_code == AUTH_FAILED:
        error_msg = '-ERR Authentication failed'
    elif error_code == INVALID_COMMAND:
        error_msg = '-ERR Invalid command'
    elif error_code == INVALID_ARGUMENT:
        error_msg = '-ERR Invalid argument'
    else:
        error_msg = '-ERR Unknown error'
    if msg:
        error_msg += f': {msg}\r\n'
    else:
        error_msg += '\r\n'
    return error_msg.encode()
```

Here is the test for some of the errors:

<img src="C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\pop_err.png" alt="pop_err" style="zoom:67%;" />

In SMTP, I implement the types of error reporting including the syntax of the command, the existence of the user, and the existence of the receiver's domain server. Here is the test for some errors:

![smtp_err](C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\smtp_err.png)

### Peer Mailing

I finish this part with my classmate 秦颢轩(12111321). Assume that the mail server for ***lamptales.com*** is running on my computer, and the mail server for ***haoson.com*** is running on his computer. Now the users under the two servers want to communicate. We adjust the DNS config and the checkup method, so it becomes as follow:

<img src="C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\dns_config.png" alt="dns_config" style="zoom:67%;" />

![dns_look](C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\dns_look.png)

And now we can send mails to each other, here is an example.

On my computer:

<img src="file:///C:\Users\ASUS\AppData\Roaming\Tencent\Users\179500516\TIM\WinTemp\RichOle\$6V9Z7QMU4(MUY(M6UO$)N5.png" alt="img" style="zoom:50%;" />

On my lamptales server:

<img src="C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\lamp_ser.png" alt="lamp_ser" style="zoom: 50%;" />

On Qin's computer:

<img src="C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\qin.png" alt="qin" style="zoom: 50%;" />

### Extra Commands:

I implement the HELP command in POP. Send HELP to get the help message. In convenience, as RETR 0 will never be accepted, I will also return the help message to a RETR 0 command.

![help](C:\Users\ASUS\Desktop\materials\Network\assignments\png_save\help.png)