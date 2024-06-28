import requests

def send_line_notify(user_id,message):
    line_token = "kjrfSbGh7jubA6T4MoatgxONys6KLK55C559wJ9CIad"
    headers = {
        'Authorization': f'Bearer {line_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {'message': message}
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=payload)
    return response.status_code



