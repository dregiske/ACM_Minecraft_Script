'''
Move .png screenshots named: {x}_{z}_{rand}.png
into folders by biome while renaming them to: {rand}.png.

Usage:
python sort_photos.py \
  --world "~/Documents/saves/ACM" \
  --src "~/Desktop/biome_screenshots" \
  --out "~/Desktop/minecraft-biome-dev/data/other-data"

FOR ACM
python sort_photos.py \
  --world "~/Documents/saves/ACM" \
  --src "~/Desktop/biome_screenshots" \
  --out "~/Desktop/final_screenshots" \
  --dry-run

FOR ACM_mushroom_fields
python sort_photos.py \
  --world "~/Documents/saves/ACM_mushroom_fields" \
  --src "~/Desktop/biome_screenshots" \
  --out "~/Desktop/final_screenshots"

Dry run:
python sort_photos.py \
  --world "~/Documents/saves/ACM" \
  --src "~/Desktop/biome_screenshots" \
  --out "~/Desktop/minecraft-biome-dev/data/other-data" \
  --dry-run
'''

from __future__ import annotations
import argparse
import re
from pathlib import Path
from typing import Optional
from amulet_data_reader import BiomeReader, OVERWORLD, NETHER, END


# ---- SETTINGS ----

FNAME_RE = re.compile(r'^(-?\d+)_(-?\d+)_([^.]+)\.png$', re.IGNORECASE)

DIMENSION_MAP = {
	"overworld": OVERWORLD,
	"nether": NETHER,
	"end": END,
}


# ---- HELPERS ----

def parse_name(p: Path) -> Optional[tuple[int, int, str]]:
	'''
	Parses the x, z, and rand_id values from file name
	'''
	m = FNAME_RE.match(p.name)
	if not m:
		return None
	x = int(m.group(1))
	z = int(m.group(2))
	rand = int(m.group(3))
	return x, z, rand

def normalize_biome_dir(biome: Optional[str]) -> str:
	'''
	Converts 'universal_minecraft:plains' to 'plains'
	Handle None/'unknown(...)' -> 'unknown'
	'''
	if not biome:
		return "unknown"
	s = str(biome)
	if ":" in s:
		s = s.split(":")[-1]
	if s.lower().startswith("unknown"):
		return "unknown"
	s = s.replace("/", "_").replace("\\", "_").strip()
	return s or "unknown"

def unique_path(base_path: Path) -> Path:
	'''
	Ensures each file has unique path
	by appending _1, _2, _3 etc. before the suffix
	'''
	if not base_path.exists():
		return base_path
	stem, suffix = base_path.stem, base_path.suffix
	i = 1
	while True:
		candidate = base_path.with_name(f"{stem}_{i}{suffix}")
		if not candidate.exists():
			return candidate
		i += 1


# ---- MAIN ----

def main():
	ap = argparse.ArgumentParser(description="Sort PNGs into biome folders using Amulet.")
	ap.add_argument("--world", required=True, help="Path to Minecraft world directory.")
	ap.add_argument("--src", required=True, help="Folder containing PNG screenshots.")
	ap.add_argument("--out", required=True, help="Destination parent folder for biome directories.")
	ap.add_argument("--dimension", default="overworld", choices=DIMENSION_MAP.keys(),
					help="Dimension to read biomes from (default: overworld).")
	ap.add_argument("--no-snapshot", action="store_true",
					help="Open world in-place instead of copying a snapshot.")
	ap.add_argument("--dry-run", action="store_true",
					help="Print actions only; do not move files.")
	args = ap.parse_args()

	src_dir = Path(args.src).expanduser().resolve()
	out_dir = Path(args.out).expanduser().resolve()
	out_dir.mkdir(parents=True, exist_ok=True)

	dim_id = DIMENSION_MAP[args.dimension]

	reader = BiomeReader(
		world_directory=args.world,
		dimensions=dim_id,
		cache_size=256,
		use_snapshot=not args.no_snapshot
	)

	moved, skipped_badname, skipped_nochunk = 0, 0, 0
	try:
		for p in src_dir.iterdir():
			if not p.is_file() or p.suffix.lower() != ".png":
				continue

			parsed = parse_name(p)
			if not parsed:
				skipped_badname += 1
				print(f"[skip:name] {p.name} (expected {{x}}_{{z}}_{{rand}}.png)")
				continue

			x, z, rand = parsed
			biome = reader.get_biome(x, z)
			if biome is None:
				skipped_nochunk += 1
				print(f"[skip:chunk] No biome at ({x}, {z}) for {p.name}")
				continue

			dir_name = normalize_biome_dir(biome)
			dest_dir = out_dir / dir_name
			dest_dir.mkdir(parents=True, exist_ok=True)

			target = unique_path(dest_dir / f"{rand}.png")

			if args.dry_run:
				print(f"[dry-run] {p.name} -> {target}  (biome={biome})")
			else:
				p.replace(target)
				print(f"[move] {p.name} -> {target}  (biome={biome})")
				moved += 1
	finally:
		reader.close()

	print("\n--- Summary ---")
	print(f"Moved: {moved}")
	print(f"Skipped (name): {skipped_badname}")
	print(f"Skipped (nochunk): {skipped_nochunk}")

if __name__ == "__main__":
	main()
