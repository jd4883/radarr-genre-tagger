#!/usr/bin/env python3
from methods.radarr_api import Radarr
from pathlib import Path
import json
import logging
import os
import subprocess
import yaml


class Movies(object):
	def __init__(self, config: object):
		self.tags = config.radarr.get_tags()
		self.movies = config.radarr.get_movie()
		self.repo = "https://github.com/manami-project/anime-offline-database.git"
		process = subprocess.Popen(args = ["git", "clone", self.repo], stdout = subprocess.PIPE)
		output = process.communicate()[0]
		config.log.info(f"Git clone output:\t{output}")
		self.anidb = json.loads(open(Path(f"/config/anime-offline-database/anime-offline-database-minified.json")).read())["data"]
		self.aggregate = list()
		self.drop_tags = config.file["tagging"].get("drop", [])
		self.replacement_tags = config.file["tagging"].get("replacements", {})
		self.replacement_tags[" "] = "_"  # this doesnt translate nice from a configmap so I injected it; besides tags don't accept spacing in radarr


class Movie(object):
	def __init__(self, movie: dict):
		self.title = movie.get("title")
		self.tags = unique(movie.get("genres", []))
		self.tag_ids = unique(movie.get("tags", []))
		self.id = movie.get("id")
		self.radarr = dict()


class Config:
	def __init__(self, config_file = "/config/config.yaml"):
		defaults = {"tagging": {"drop": [], "replacements": {}}}
		self.file = yaml.load(open(config_file), Loader = yaml.FullLoader) if os.path.exists(Path(config_file)) else defaults
		self.log = logging
		self.log.basicConfig(format = '%(levelname)s:%(message)s', level = logging.INFO)
		self.radarr = Radarr(url = os.environ["RADARR_URL"], apikey = os.environ["RADARR_API"])
		self.movies = Movies(config = self)
		self.parser()
	
	def parser(self):
		self.movies.tags = self.radarr.get_tags()
		for s in self.movies.movies:
			movie = Movie(s)
			movie.tags += ["anime", "animated", "animation", "japanese"] if "anime" in movie.tags else []
			for anime in self.movies.anidb:
				if anime["title"] == movie.title:
					movie.tags += anime["tags"]
					break
			movie.tags = unique([cleanup_tags(tag = i, replacements = self.movies.replacement_tags) for i in sorted(list(set(movie.tags)))])
			self.write_tags(movie)
	
	def write_tags(self, movie):
		previous_tags = self.movies.tags
		self.log.info(f"Processing tags for {movie.title}")
		movie.radarr = [Movie for Movie in self.movies.movies if Movie["title"] == movie.title][0]
		add_tags(
			tags = aggregate_tags(drop_tags = self.movies.drop_tags, input_tags = movie.tags),
			tagmap = self.radarr.get_tags(),
			radarr = self.radarr,
		)
		try:
			self.movies.tags = self.radarr.get_tags()
		except:
			self.movies.tags = previous_tags
		[movie.tags.remove(i) for i in movie.tags if i in self.movies.drop_tags]
		movie.tag_ids = unique([i.get("id") for i in self.movies.tags if (i.get("label") in movie.tags)])
		movie.radarr.update({"tags": movie.tag_ids})
		try:
			self.log.info(f"Tagging has started for {movie.title}:\t{movie.tags}")
			self.log.info(self.radarr.update_movie(movie_id = movie.id, data = movie.radarr))
			self.log.info(f"Tagging has completed for {movie.title}")
		except:
			pass


def cleanup_tags(tag: str, replacements: dict):
	tag = tag.lower()
	if tag.endswith("ss"):
		tag = tag.rstrip(tag[-1])
	for before, after in replacements.items():
		tag = tag.replace(before, after)
	return tag


def aggregate_tags(drop_tags: list, input_tags: list):
	return unique([tag for tags in input_tags for tag in tags if tag not in drop_tags])


def add_tags(tags: list, tagmap: object, radarr: object):
	for tag in tags:
		for i in tagmap:
			if i.label == tag:
				try:
					radarr.add_tag(tag)
					logging.info(f"+ success adding tag {tag}")
					break
				except:
					pass


def unique(tags):
	return sorted(list(set(tags)))


if __name__ == "__main__":
	config = Config()
