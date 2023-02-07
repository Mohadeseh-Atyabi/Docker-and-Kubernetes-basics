import os
import requests
import flask
import json
import redis
import time


app = flask.Flask(__name__)
redis = redis.StrictRedis(host='172.17.0.2', port=6379)

API_KEY = os.environ.get('API_KEY')
CACHE_TIME = int(os.environ.get('CACHE_TIME'))
CURRENCY = os.environ.get('CURRENCY_NAME')
PORT = os.environ.get('SERVER_PORT')


@app.route('/getprice/', methods=['GET'])
def get_price():
    try:
        redis_response = json.loads(redis.get(CURRENCY))
    except TypeError:
        result = get_redis(CURRENCY)
        return json.dumps(result)

    if time.time() - redis_response["time"] > CACHE_TIME:
        result = get_redis(CURRENCY)
    else:
        result = redis_response
    return json.dumps(result)


def get_redis(input):
    url = 'https://rest.coinapi.io/v1/assets/' + input
    response = requests.get(url, headers={'X-CoinAPI-Key': API_KEY})
    result = {"name": response.json()[0]["name"], "price": response.json()[0]["price_usd"], "time": time.time()}
    redis.set(input, json.dumps(result))
    return result


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=PORT)