import json
import time
from methods.radarr_api import RadarrAPI
import requests


class Radarr(object):
	def __init__(self, url: str, apikey: str):
		self.host_url = url
		self.api_key = apikey
		self.api = RadarrAPI(host_url = url, api_key = apikey)
	
	def radarr_api_request(self, url, request_type = "get", data = dict()):
		backoff_timer = 2
		payload = json.dumps(data)
		request_payload = dict()
		headers = {
				'X-Api-Key':    self.api_key,
				"Content-Type": "application/json",
				"accept":       "application/json",
				}
		if request_type not in ["post", "put", "delete"]:
			request_payload = requests.get(url, headers = headers, data = payload)
		elif request_type == "put":
			request_payload = requests.put(url, headers = headers, data = payload)
		elif request_type == "post":
			request_payload = requests.post(url, headers = headers, data = payload)
		elif request_type == "delete":
			request_payload = requests.delete(url, headers = headers, data = payload)
		time.sleep(backoff_timer)
		return request_payload.json()
	
	def get_root_folder(self):
		return self.radarr_api_request(f"{self.host_url}/rootfolder")
	
	def get_movie(self):
		return self.radarr_api_request(f"{self.host_url}/movie")
	
	def update_movie(self, movie_id, data: dict):
		return self.radarr_api_request(f"{self.host_url}/movie/{movie_id}", "put", data)
	
	def refresh_movie(self, movie_id, data = dict()):
		return self.radarr_api_request(f"{self.host_url}/command/RefreshMovie&movieId={movie_id}", "post", data)
	
	def rescan_movie(self, movie_id, data = dict()):
		return self.radarr_api_request(f"{self.host_url}/command/RescanMovie&movieId={movie_id}", "post", data)
	
	def get_tags(self):
		return self.api.get_tags()
		#return self.radarr_api_request(f"{self.host_url}/tag")


def add_tag(self, tag: str):
	data = json.dumps({"label": tag})
	return self.radarr_api_request(url = f"{self.host_url}/tag", request_type = "post", data = data)
