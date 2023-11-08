import argparse
import os
import time
import asyncio

from tempfile import TemporaryDirectory
from asyncio import subprocess

from rich import print
from rich.console import Console
from rich.status import Status
from rich.live import Live
from rich.table import Table

in_suff = [".in"]
out_suff = [".out", ".ans"]

error_console = Console(stderr=True, style="bold red")

def check(out, correct):
	out = out.replace('\r', '').strip()
	correct = correct.replace('\r', '').strip()

	l1,l2=out.splitlines(), correct.splitlines()
	if len(l1)!=len(l2):
		return False
	
	for o,c in zip(l1,l2):
		x1,x2 = o.split(), c.split()
		if len(x1)!=len(x2):
			return False
		for a,b in zip(x1,x2):
			try:
				absd = abs(float(a)-float(b))
				if absd>1e-9 and absd>float(b)*1e-9:
					return False
			except ValueError:
				if a!=b:
					return False
	return True

class TC:
	time_stat = "??? s"
	verdict = Status("[italic gray] Waiting... [/]")

	def upd(self, v, dt):
		self.time_stat = f"{dt:0.4f} s"
		self.verdict = "[bold green]"+v+"[/]" if v=="AC" else "[bold red]"+v+"[/]"

	async def run_test_case_err(self):
		async def run(inp, cwd):
			p = await subprocess.create_subprocess_shell(self.run_cmd, stdin=inp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)

			self.verdict.update("[italic white] Running... [/]")

			timeStarted = time.time()
			try:
				await asyncio.wait_for(p.wait(), self.tle)
			except asyncio.exceptions.TimeoutError:
				p.kill()
				pass
				
			out, err = await p.communicate()

			time_delta = time.time() - timeStarted
			return {"out": out.decode(), "err": err, "dt": time_delta}
				
		with open(self.pth, "r", encoding="utf-8") as fin:
			res = None
			if self.file is not None:
				with TemporaryDirectory() as d:
					with open(os.path.join(d, f"{self.file[0]}.in"), "w") as f:
						f.write(fin.read())
					res = await run(None, d)
					try:
						with open(os.path.join(d, f"{self.file[0]}.out"), "r") as f:
								res["out"] = f.read()
					except IOError:
						self.upd("Missing file", res["dt"])
			else:
				res = await run(fin, None)

			if (res["dt"] >= self.tle):
				self.upd("TLE", res["dt"])
				return
			
			if not res["err"]:
				out = res["out"].strip()

				with open(self.outpth, "r", encoding="utf-8") as of:
					correct = str(of.read())

					if check(out,correct):
						self.upd("AC", res["dt"])
					else:
						self.upd("WA", res["dt"])
			else:
				self.upd("RE", res["dt"])
	
	async def run_test_case(self):
		try:
			await self.run_test_case_err()
		except Exception as e:
			error_console.print("Exception occurred while running test case:", e)
			self.verdict = "[bold red] Error [/]"

	def __init__(self, num, pth, outpth, run_cmd, file, tle):
		self.num = num
		self.pth = pth
		self.outpth = outpth
		self.run_cmd = run_cmd
		self.file = file
		self.tle = tle

def render(test_cases):
	table = Table(title="Test Cases")
	table.add_column("No.", style="cyan", no_wrap=True)
	table.add_column("Time", style="magenta")
	table.add_column("Status", justify="right")

	for x in test_cases:
		table.add_row(str(x.num), x.time_stat, x.verdict)

	return table

async def main():
	prser = argparse.ArgumentParser(
		prog="qusaco",
		description="USACO Quick Judge (stdin/stdout)")
	prser.add_argument("tests", metavar="test_dir", type=str,
						 nargs=1, help="relative path of unzipped directory of USACO test cases")
	prser.add_argument("run", metavar="ext", type=str,
						 nargs=argparse.REMAINDER, help="command to execute the compiled program")
	prser.add_argument("-t", "--tle", type=int,
						 nargs=1, help="Set time limit")
	prser.add_argument("-f", "--file", type=str,
						 nargs=1, help="If using file I/O, add this (if argument is x, x.in will be created and x.out will be read)")

	args = prser.parse_args()

	if os.path.exists(os.path.join(os.path.abspath(os.getcwd()), str(args.tests[0]))):
		test_cases = []
		run_cmd = " ".join(args.run)
		tle = args.tle[0] if args.tle is not None else 10

		for sb, _, f in os.walk(os.path.join(os.path.abspath(os.getcwd()), str(args.tests[0]))):
			for i in f:
				pth = os.path.join(sb,i)
				for suff in in_suff:
					if pth.endswith(suff):
						pref = pth.split(os.sep)[-1].split(".")[0]
						num = int(pref)

						out_path = None
						for suff in out_suff:
							outpth = os.path.join(pth.rsplit(os.sep, 1)[0], f"{pref}{suff}")
							if os.path.exists(outpth):
								out_path = outpth
								break

						if out_path is None:
							error_console.print(f"No output file for test case {i} (input {pth})")
						else:
							test_cases.append(TC(num, pth, out_path, run_cmd, args.file, tle))

						break

		if len(set(x.num for x in test_cases)) != len(test_cases):
			error_console.print("Test cases have overlapping numbers")
		test_cases.sort(key=lambda x: x.num)


	if len(test_cases)==0:
		error_console.print("Test cases not found")
	else:
		with Live(render(test_cases)) as live:
			for fut in asyncio.as_completed([x.run_test_case() for x in test_cases]):
				await fut
				live.update(render(test_cases))

if __name__ == "__main__":
	asyncio.run(main())
