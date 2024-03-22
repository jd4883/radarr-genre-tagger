from pyarr.radarr import RadarrAPI


class Radarr(object):
	def __init__(self, url: str, apikey: str):
		self.api = RadarrAPI(host_url = url.replace("/api/v3", ""), api_key = apikey)
	
	def get_movie(self):
		return self.api.get_movie()
	
	def update_movie(self, movie_id, data: dict):
		return self.api.upd_movie(data)
	
	def get_tags(self):
		return self.api.get_tag()
	
	def add_tag(self, tag: str):
		return self.api.create_tag(label=tag)
