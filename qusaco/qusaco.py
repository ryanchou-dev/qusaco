import argparse
import os
import subprocess
import time
import psutil
from rich.console import Console
from rich.columns import Table


def main():
    console = Console()
    prser = argparse.ArgumentParser(
        prog="qusaco",
        description="USACO Quick Judge (stdin/stdout)")
    prser.add_argument("run", metavar="ext", type=str,
                       nargs=1, help="command to execute the compiled program")
    prser.add_argument("tests", metavar="test_dir", type=str,
                       nargs=1, help="relative path of unzipped directory of USACO test cases")

    args = prser.parse_args()
    wa = True

    if os.path.exists(os.path.join(os.path.abspath(os.getcwd()), str(args.tests[0]))):

        status = []
        for sb, _, f in os.walk(os.path.join(os.path.abspath(os.getcwd()), str(args.tests[0]))):
            for i in f:
                pth = sb + os.sep + i
                if pth.endswith(".in"):
                    with open(pth, "r", encoding="utf-8") as fin:
                        timeStarted = time.time()
                        p = subprocess.Popen([j for j in str(args.run[0]).split()], stdin=fin, stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
                        pp = psutil.Process(p.pid)

                        try:
                            pp.wait(timeout=2.1)
                        except psutil.TimeoutExpired:
                            status.append([int(i.split(".")[0]), "TLE"])
                            continue
                        out, err = p.communicate()

                        time_delta = time.time() - timeStarted
                        if (time_delta > 2.1):
                            status.append([int(i.split(".")[0]), "TLE"])
                            continue
                        if not err:
                            out = str(out.decode("utf-8").strip())
                            arr = [o for o in os.listdir(str(args.tests[0]))]

                            fn = i[:i.index(".")] + ".out"

                            if fn not in arr:
                                print("No output file for test case: ", i)
                                return

                            of = open(sb + os.sep + fn, "r", encoding="utf-8")
                            correct = str(of.read().strip())
                            out = out.replace('\n', '')
                            out = out.replace('\r', '')
                            correct = correct.replace('\n', '')
                            correct = correct.replace('\r', '')
                            if str(out) != str(correct):
                                status.append([int(i.split(".")[0]), "WA"])
                            else:
                                status.append(
                                    [int(i.split(".")[0]), "AC", time_delta])

                        else:

                            status.append([int(i.split(".")[0]), "RE"])
    else:
        print("Files not found")
        return

    # print out status of test cases in a table
    table = Table(title="Test Cases")
    table.add_column("No.", style="cyan", no_wrap=True)
    table.add_column("Time", style="magenta")
    table.add_column("Status", justify="right")

    status.sort()
    for k in status:
        if (k[1] == "AC"):
            table.add_row(str(k[0]), (str(k[2])+"0000")[:4] +
                          "s", "[green]"+k[1]+"[/green]")
        else:
            table.add_row(str(k[0]), "n/a", "[red]"+k[1]+"[/red]")

    console.print(table)
