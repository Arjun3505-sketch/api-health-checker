from flask import Blueprint, jsonify, render_template, request
import requests
import time
from .dynamo import save_result, get_history, get_all_endpoints, add_endpoint, delete_endpoint, get_uptime_percentage

main = Blueprint('main', __name__)

def check_endpoint(name, url):
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        response_time = (time.time() - start) * 1000
        status = 'up' if response.status_code < 400 else 'degraded'
        return {
            'name': name,
            'url': url,
            'status_code': response.status_code,
            'response_time': round(response_time, 2),
            'status': status
        }
    except requests.exceptions.Timeout:
        return {'name': name, 'url': url, 'status_code': None, 'response_time': None, 'status': 'timeout'}
    except requests.exceptions.ConnectionError:
        return {'name': name, 'url': url, 'status_code': None, 'response_time': None, 'status': 'down'}
    except Exception:
        return {'name': name, 'url': url, 'status_code': None, 'response_time': None, 'status': 'error'}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/check', methods=['GET'])
def check_all():
    endpoints = get_all_endpoints()
    results = []
    for ep in endpoints:
        result = check_endpoint(ep['name'], ep['endpoint_url'])
        save_result(ep['endpoint_url'], result['status_code'], result['response_time'] or 0, result['status'])
        result['uptime'] = get_uptime_percentage(ep['endpoint_url'])
        results.append(result)
    return jsonify(results)

@main.route('/endpoints', methods=['GET'])
def list_endpoints():
    return jsonify(get_all_endpoints())

@main.route('/endpoints', methods=['POST'])
def create_endpoint():
    data = request.get_json()
    name = data.get('name', '').strip()
    url  = data.get('url', '').strip()
    if not name or not url:
        return jsonify({'error': 'Name and URL are required'}), 400
    if not url.startswith('http'):
        return jsonify({'error': 'URL must start with http:// or https://'}), 400
    add_endpoint(name, url)
    return jsonify({'success': True}), 201

@main.route('/endpoints', methods=['DELETE'])
def remove_endpoint():
    data = request.get_json()
    url  = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    delete_endpoint(url)
    return jsonify({'success': True})