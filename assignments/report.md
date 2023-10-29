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
