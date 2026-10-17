"""Item 1: does a Daytona box start, take a file, run code, and go away in under 30s?

Run:  .venv/bin/python smoke.py
Needs: DAYTONA_API_KEY in .env  (copy .env.example to .env and fill it in)
"""
import time
from dotenv import load_dotenv
from daytona import Daytona

load_dotenv()
t0 = time.time()
lap = lambda label: print(f"  {label:<28} {time.time() - t0:5.1f}s")

daytona = Daytona()                      # reads DAYTONA_API_KEY from the environment
box = daytona.create()
lap(f"box started  id={box.id}")

box.fs.upload_file(b"Saturday class: $45\n", "/home/daytona/brain.txt")
lap("file uploaded")

out = box.process.code_run("print(open('/home/daytona/brain.txt').read().strip())")
lap(f"code ran -> {out.result.strip()!r}")

box.delete()
lap("box deleted")

print("\nPASS" if time.time() - t0 < 30 else "\nSLOW: over 30s, we need a prebuilt snapshot")
