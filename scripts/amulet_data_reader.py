'''
This is a program to pull biome names
from specified x and z coordinates using amulet
with a cache system for faster lookups

This program works for 1.13-1.15 Minecraft (2D chunk data)
'''

import os, shutil, tempfile
from functools import lru_cache
import amulet
from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist


# ---- SETTINGS ----

OVERWORLD 	= "minecraft:overworld"
NETHER 		= "minecraft:the_nether"
END 		= "minecraft:the_end"

# ---- HELPERS ----

def expand_directory(path: str) -> str:
	return os.path.abspath(os.path.expanduser(path))

def snapshot_world(src_dir: str) -> tuple[str, callable]:
	'''
	Copy the world to a temp dir and
	return (snap_path, cleanup_fn).
	'''
	src_dir = expand_directory(src_dir)
	tmp_root = tempfile.mkdtemp(prefix="amulet_world_")
	snap_path = os.path.join(tmp_root, os.path.basename(src_dir.rstrip("/")))
	shutil.copytree(src_dir, snap_path)
	def cleanup():
		try: shutil.rmtree(tmp_root)
		except Exception: pass
	return snap_path, cleanup

def return_biome_name(level, raw_val: int):
	'''
	Converts the biome number val to
	the name as a string
	'''
	if isinstance(raw_val, str):
		return raw_val
	try:
		return level.biome_palette[int(raw_val)]
	except Exception:
		return f"unknown({raw_val})"


# ---- BIOME READER ----

class BiomeReader:
	def __init__(self, world_directory: str, dimensions: str, cache_size: int=256, use_snapshot: bool=True):
		self.dimensions = dimensions
		if use_snapshot:
			print("Creating snapshot", flush=True)
			self.world_directory, self._cleanup = snapshot_world(world_directory)
			print(f"Snapshot at: {self.world_directory}", flush=True)
		else:
			self.world_directory = expand_directory(world_directory)
			self._cleanup = lambda: None

		print("Loading world...")
		self.level = amulet.load_level(self.world_directory)
		print("World opened", flush=True)

		@lru_cache(maxsize=cache_size)
		def get_chunk_from(chunk_x: int, chunk_z: int):
			return self.level.get_chunk(chunk_x, chunk_z, self.dimensions)

		self.get_chunk_from = get_chunk_from

	def close(self) -> None:
		self.level.close()
		self._cleanup()

	def get_biome(self, x: int, z: int) -> str | None:
		'''
		Gets the biome val at specified coords then calls
		return_biome_name() for the biome name as string,
		or None
		'''
		print(f"Grabbing biome at {x}, {z}.")

		chunk_x = x // 16
		chunk_z = z // 16
		local_x = x & 15
		local_z = z & 15

		if not self.level.has_chunk(chunk_x, chunk_z, self.dimensions):
			return None

		try:
			biomes = self.get_chunk_from(chunk_x, chunk_z).biomes
		except ChunkDoesNotExist:
			print("Error: Chunk does not exist")
			return None
		except ChunkLoadError:
			print("Error: Chunk load error")
			return None

		shape = getattr(biomes, "shape", None)
		if shape == (16, 16):
			val = biomes[local_x, local_z]
		elif shape == (4, 4):
			val = biomes[local_x >> 2, local_z >> 2]

		return return_biome_name(self.level, val)