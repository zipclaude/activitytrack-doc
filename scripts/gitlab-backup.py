#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# On-demand backup of everything a GitLab group (and, if asked, the projects
# owned by the token's user) holds. Standard library only; needs `git`.
#
#   scripts/gitlab-backup.py [--group activitytrack] [--out DIR] [--owned]
#                            [--no-packages] [--no-export] [--only NAME ...]
#
# The token is read from $GITLAB_TOKEN or from --token-file (default
# ~/API-keys/gitlab-token.txt). It needs the scope `api` and the role
# Maintainer on the projects (the project export asks for it). The group's own
# export (needs Owner) is not made; only the group's data is saved as JSON. The token is never printed, never
# put on a command line and never written to the backup.
#
# For every project the backup holds, under <out>/<stamp>/<path>/:
#   repo.git, repo.bundle   all branches and tags (mirror clone and a bundle)
#   wiki.git                the wiki, if it has pages
#   export.tar.gz           GitLab's own project export: issues, merge requests
#                           with their discussions and refs, labels, releases,
#                           milestones, pipelines' metadata, settings
#                           (restorable with Import project > GitLab export)
#   json/                   the same data as plain JSON, readable without GitLab
#   packages/               the files of the package registry (the release
#                           packages of 0.9.x live here)
#   variables.keys.json     NAMES and flags of the CI/CD variables, never values
# and a SHA256SUMS and a backup.json at the top. Not covered: job artifacts
# (they expire), CI/CD variable values, runners, access tokens, deploy keys'
# private halves; keep those in the places where they were created.

import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://gitlab.com/api/v4"
TOKEN = ""


class SameHostRedirect(urllib.request.HTTPRedirectHandler):
	"""Downloads may redirect to object storage: the token must not follow."""

	def redirect_request(self, req, fp, code, msg, headers, newurl):
		new = super().redirect_request(req, fp, code, msg, headers, newurl)
		if new is not None and urllib.parse.urlsplit(newurl).netloc != urllib.parse.urlsplit(req.full_url).netloc:
			for h in ("Private-token", "PRIVATE-TOKEN"):
				new.headers.pop(h, None)
				new.unredirected_hdrs.pop(h, None)
		return new


OPENER = urllib.request.build_opener(SameHostRedirect)


def scrub(obj):
	"""GitLab returns secrets (runners_token, ...) in project and group records: drop them."""
	if isinstance(obj, dict):
		return {k: scrub(v) for k, v in obj.items()
			if not any(w in k.lower() for w in ("token", "secret", "password"))}
	if isinstance(obj, list):
		return [scrub(v) for v in obj]
	return obj


def request(path, method="GET", raw=False, retries=5):
	url = path if path.startswith("http") else API + "/" + path
	for attempt in range(retries):
		req = urllib.request.Request(url, method=method, headers={"PRIVATE-TOKEN": TOKEN})
		try:
			with OPENER.open(req, timeout=120) as r:
				body = r.read()
				return body if raw else (json.loads(body) if body.strip() else None)
		except urllib.error.HTTPError as e:
			if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
				time.sleep(int(e.headers.get("Retry-After") or 5 * (attempt + 1)))
				continue
			raise
		except (urllib.error.URLError, TimeoutError):
			if attempt == retries - 1:
				raise
			time.sleep(5 * (attempt + 1))


def pages(path):
	sep = "&" if "?" in path else "?"
	page = 1
	while True:
		items = request("%s%sper_page=100&page=%d" % (path, sep, page))
		if not items:
			return
		yield from items
		if len(items) < 100:
			return
		page += 1


def save(path, data):
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		json.dump(scrub(data), f, indent=1, ensure_ascii=False)


def git(*args, cwd=None):
	subprocess.run(["git", *args], cwd=cwd, check=True, stdout=subprocess.DEVNULL,
		env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))


def sha256(path):
	h = hashlib.sha256()
	with open(path, "rb") as f:
		for chunk in iter(lambda: f.read(1 << 20), b""):
			h.update(chunk)
	return h.hexdigest()


def backup_git(project, dest, askpass, report):
	env = dict(os.environ, GIT_ASKPASS=askpass, GIT_TERMINAL_PROMPT="0", GITLAB_TOKEN=TOKEN)
	url = project["http_url_to_repo"]
	if project.get("wiki_enabled"):  # a wiki can exist in a project without commits
		wiki = os.path.join(dest, "wiki.git")
		r = subprocess.run(["git", "clone", "-q", "--mirror", url[:-4] + ".wiki.git", wiki],
			env=env, capture_output=True, text=True)
		if r.returncode == 0:
			report["wiki"] = "ok"
		elif "not found" in r.stderr.lower() or "does not appear to be a git repository" in r.stderr.lower():
			report["wiki"] = "none (no pages)"
		else:
			raise RuntimeError("wiki clone failed: " + r.stderr.strip()[:200].replace(TOKEN, "***"))
	if project.get("empty_repo"):
		report["repo"] = "empty"
		return
	repo = os.path.join(dest, "repo.git")
	subprocess.run(["git", "clone", "-q", "--mirror", url, repo], check=True, env=env)
	subprocess.run(["git", "bundle", "create", "-q", os.path.join(dest, "repo.bundle"), "--all"],
		cwd=repo, check=True, env=env)
	# refs/merge-requests/* are hidden from clones; the project export keeps them
	report["repo"] = "ok"


def backup_json(project, dest, report):
	pid = project["id"]
	j = os.path.join(dest, "json")
	save(os.path.join(j, "project.json"), request("projects/%d" % pid))
	for name, path in (
		("labels", "labels?with_counts=true"), ("milestones", "milestones?state=all"),
		("releases", "releases"), ("protected_branches", "protected_branches"),
		("protected_tags", "protected_tags"), ("members", "members/all"),
		("branches", "repository/branches"), ("tags", "repository/tags"),
		("hooks", "hooks"), ("pipeline_schedules", "pipeline_schedules"),
		("environments", "environments"), ("snippets", "snippets"),
	):
		try:
			save(os.path.join(j, name + ".json"), list(pages("projects/%d/%s" % (pid, path))))
		except urllib.error.HTTPError as e:
			report.setdefault("skipped", []).append("%s: HTTP %d" % (name, e.code))
	for kind, notes in (("issues", "issues"), ("merge_requests", "merge_requests")):
		items = list(pages("projects/%d/%s?state=all&scope=all" % (pid, kind)))
		for it in items:
			base = "projects/%d/%s/%d" % (pid, notes, it["iid"])
			it["_notes"] = list(pages(base + "/notes"))
			it["_discussions"] = list(pages(base + "/discussions"))
			if kind == "merge_requests":
				it["_changes"] = request(base + "/changes").get("changes", [])
				it["_commits"] = list(pages(base + "/commits"))
				it["_approvals"] = request(base + "/approvals")
		save(os.path.join(j, kind + ".json"), items)
		report[kind] = len(items)
	pipelines = list(pages("projects/%d/pipelines" % pid))
	save(os.path.join(j, "pipelines.json"), pipelines)
	report["pipelines"] = len(pipelines)
	# names and flags only: the value of a variable is a secret
	try:
		keys = [{k: v for k, v in var.items() if k != "value"}
			for var in pages("projects/%d/variables" % pid)]
		save(os.path.join(dest, "variables.keys.json"), keys)
		report["variables"] = len(keys)
	except urllib.error.HTTPError as e:
		report.setdefault("skipped", []).append("variables: HTTP %d" % e.code)


def backup_export(project, dest, report, timeout=1800):
	pid = project["id"]
	request("projects/%d/export" % pid, method="POST")
	start = time.time()
	while True:
		status = request("projects/%d/export" % pid)
		if status.get("export_status") == "finished":
			break
		if status.get("export_status") == "failed" or time.time() - start > timeout:
			report["export"] = "failed: %s" % status.get("export_status")
			return
		time.sleep(5)
	data = request("projects/%d/export/download" % pid, raw=True)
	with open(os.path.join(dest, "export.tar.gz"), "wb") as f:
		f.write(data)
	report["export"] = "ok (%d bytes)" % len(data)


def backup_packages(project, dest, report):
	pid = project["id"]
	count = size = 0
	for pkg in pages("projects/%d/packages" % pid):
		for f in pages("projects/%d/packages/%d/package_files" % (pid, pkg["id"])):
			if pkg["package_type"] == "generic":
				url = "projects/%d/packages/generic/%s/%s/%s" % (pid,
					urllib.parse.quote(pkg["name"], safe=""), urllib.parse.quote(pkg["version"], safe=""),
					urllib.parse.quote(f["file_name"], safe=""))
			else:
				report.setdefault("skipped", []).append("package %s %s (%s)" % (pkg["name"], pkg["version"], pkg["package_type"]))
				break
			out = os.path.join(dest, "packages", pkg["name"], pkg["version"], f["file_name"])
			if os.path.exists(out):  # the same file uploaded twice
				continue
			os.makedirs(os.path.dirname(out), exist_ok=True)
			data = request(url, raw=True)
			with open(out, "wb") as fh:
				fh.write(data)
			count += 1
			size += len(data)
	report["packages"] = "%d files, %d bytes" % (count, size)


def main():
	global TOKEN
	ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else None)
	ap.add_argument("--group", action="append", default=None, help="group path (default: activitytrack)")
	ap.add_argument("--owned", action="store_true", help="also the projects owned by the token's user")
	ap.add_argument("--out", default=os.path.expanduser("~/gitlab-backups"))
	ap.add_argument("--token-file", default=os.path.expanduser("~/API-keys/gitlab-token.txt"))
	ap.add_argument("--only", nargs="+", help="project paths or names to back up (default: all)")
	ap.add_argument("--no-export", action="store_true", help="skip GitLab's project export")
	ap.add_argument("--no-packages", action="store_true", help="skip the package registry files")
	ap.add_argument("--list", action="store_true", help="list the projects and exit")
	args = ap.parse_args()

	TOKEN = os.environ.get("GITLAB_TOKEN", "")
	if not TOKEN and os.path.exists(args.token_file):
		with open(args.token_file) as f:
			TOKEN = f.read().strip()
	if not TOKEN:
		sys.exit("no token: set GITLAB_TOKEN or use --token-file")

	projects = {}
	for g in args.group or ["activitytrack"]:
		for p in pages("groups/%s/projects?include_subgroups=true" % urllib.parse.quote(g, safe="")):
			projects[p["id"]] = p
	if args.owned:
		for p in pages("projects?owned=true"):
			projects[p["id"]] = p
	if args.only:
		projects = {i: p for i, p in projects.items()
			if p["path"] in args.only or p["path_with_namespace"] in args.only}
	if args.list:
		for p in projects.values():
			print(p["id"], p["path_with_namespace"])
		return
	if not projects:
		sys.exit("no project found")

	stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
	root = os.path.join(args.out, "gitlab-backup-" + stamp)
	os.makedirs(root, mode=0o700)
	tmp = tempfile.mkdtemp()
	askpass = os.path.join(tmp, "askpass.sh")
	with open(askpass, "w") as f:  # git asks for the user name, then for the password
		f.write('#!/bin/sh\ncase "$1" in Username*) echo oauth2;; *) echo "$GITLAB_TOKEN";; esac\n')
	os.chmod(askpass, 0o700)

	summary = {"started": stamp, "projects": {}}
	try:
		for g in args.group or ["activitytrack"]:
			try:
				gid = urllib.parse.quote(g, safe="")
				gj = os.path.join(root, "_groups", g)
				save(os.path.join(gj, "group.json"), request("groups/" + gid))
				save(os.path.join(gj, "members.json"), list(pages("groups/%s/members/all" % gid)))
				save(os.path.join(gj, "labels.json"), list(pages("groups/%s/labels" % gid)))
			except urllib.error.HTTPError as e:
				summary.setdefault("skipped", []).append("group %s: HTTP %d" % (g, e.code))
		for p in sorted(projects.values(), key=lambda p: p["path_with_namespace"]):
			name = p["path_with_namespace"]
			dest = os.path.join(root, name)
			os.makedirs(dest)
			report = summary["projects"].setdefault(name, {})
			print("==", name, flush=True)
			steps = [("git", lambda: backup_git(p, dest, askpass, report)),
				("json", lambda: backup_json(p, dest, report))]
			if not args.no_export:
				steps.append(("export", lambda: backup_export(p, dest, report)))
			if not args.no_packages:
				steps.append(("packages", lambda: backup_packages(p, dest, report)))
			for label, step in steps:
				try:
					step()
				except Exception as e:  # one failing step must not lose the others
					report.setdefault("errors", []).append("%s: %s" % (label, type(e).__name__ + " " + str(e)[:200].replace(TOKEN, "***")))
					print("   ", label, "FAILED", file=sys.stderr, flush=True)
	finally:
		shutil.rmtree(tmp, ignore_errors=True)

	summary["finished"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
	save(os.path.join(root, "backup.json"), summary)
	sums = []
	for d, _, files in os.walk(root):
		for fn in files:
			path = os.path.join(d, fn)
			sums.append((os.path.relpath(path, root), sha256(path)))
	with open(os.path.join(root, "SHA256SUMS"), "w") as f:
		for rel, digest in sorted(sums):
			f.write("%s  %s\n" % (digest, rel))
	failed = [n for n, r in summary["projects"].items() if r.get("errors")]
	skipped = [n for n, r in summary["projects"].items() if r.get("skipped")] + (["groups"] if summary.get("skipped") else [])
	print("backup in", root)
	if failed:
		print("with errors:", ", ".join(failed), "(see backup.json)", file=sys.stderr)
		sys.exit(1)
	if skipped:  # refused or unsupported parts: the backup is usable but not complete
		print("incomplete, some parts were skipped:", ", ".join(skipped), "(see backup.json)", file=sys.stderr)
		sys.exit(2)


if __name__ == "__main__":
	main()
