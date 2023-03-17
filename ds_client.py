"""
Clien module that allows user to upload post or bio
"""
# Replace the following placeholders with your information.

# Jyun Rong Liu
# jyunrl@uci.edu
# 16169703

import socket
import time
import ds_protocol
import ui


def send(
        server: str,
        port: int, username: str, password: str, message: str, bio: str = None
        ):
    '''
    The send function joins a ds server and sends a message, bio, or both

    :param server: The ip address for the ICS 32 DS server.
    :param port: The port where the ICS 32 DS server is accepting connections.
    :param username: The user name to be assigned to the message.
    :param password: The password associated with the username.
    :param message: The message to be sent to the server.
    :param bio: Optional, a bio for the user.
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((server, port))

        print(f'Client connected to {server} on {port}')

        join_msg = ds_protocol.join_txt(username, password)

        send_ = client.makefile('w')
        recv = client.makefile('r')

        try:
            join, post, _bio_ = ui.send_process()
            if join:
                flush_msg(send_, join_msg)
                resp = recv.readline()[:-1]
                print("Response received from server: ", resp)
                data_tuple = ds_protocol.extract_json(resp)
                usr_token = data_tuple.token

                publish_post = ds_protocol.post_msg(usr_token, message)
                publish_bio = ds_protocol.bio_msg(usr_token, bio)

                if post and (not _bio_):
                    flush_and_recv(send_, publish_post, recv)
                elif _bio_ and (not post):
                    flush_and_recv(send_, publish_bio, recv)
                elif post and _bio_:
                    flush_and_recv(send_, publish_post, recv)
                    time.sleep(0.1)
                    flush_and_recv(send_, publish_bio, recv)
                    print('Post and Bio successfully uploaded')
                else:
                    pass
            return True
        except Exception:
            return False


def only_join(server: str, port: int, username: str, password: str):
    """
    join the server and acquire user token
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))
    print(f'Client connected to {server} on {port}')

    send_ = client.makefile('w')
    recv = client.makefile('r')

    join_msg = ds_protocol.join_txt(username, password)
    flush_msg(send_, join_msg)
    resp = recv.readline()[:-1]
    print("Response received from server: ", resp)
    data_tuple = ds_protocol.extract_json(resp)
    usr_token = data_tuple.token

    return usr_token, send_, recv, client


def flush_msg(send_, msg):
    """
    flush data
    """
    send_.write(msg + "\r\n")
    send_.flush()


def flush_and_recv(send_, msg, recv_):
    """
    flushing and printing the response
    """
    send_.write(msg + "\r\n")
    send_.flush()
    resp = recv_.readline()[:-1]
    print("Response received from server: ", resp)
    return ds_protocol.from_json(resp)
