import requests

api_key = '72100AqI6mYUkRhLx5563f6f2'
sender = 'iQubee'


def send_message(message, mobile_number):
    response = requests.get(
        url='http://api.msg91.com/api/sendhttp.php?authkey=' + api_key +
            '&mobiles=' + mobile_number + '&message=' + message + '&sender=' +
            sender + '&route=4&country=91')
    return response
