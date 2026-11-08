#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Builds the documentation of every ActivityTrack project as PDF, it and en:
#   app      quick start, user manual and one guide per connector   (manual/app)
#   server   administrator's manual of ActivityTrack Web            (manual/server)
#   desktop  manual of ActivityTrack Desktop                        (manual/desktop)
#
#   scripts/build-manual.sh [version] [app|server|desktop]...   -> build/manual/*.pdf
#
# Without projects it builds all three. Needs pandoc, graphviz (dot, for the app's
# diagrams) and a Chromium for the PDF (Debian packages; no npm). The app's diagrams are
# regenerated into manual/app/<lang>/diagrams/ (committed, so the Markdown also reads on GitLab).
# Moved here from the three code repositories' scripts/build-manual.sh.

set -eu
cd "$(dirname "$0")/.."

VERSION=${1:-$(sed -n 's/^Versione \([0-9][0-9.]*\).*/\1/p' manual/app/it/manual.md | head -n 1)}
[ $# -gt 0 ] && shift
[ $# -gt 0 ] || set -- app server desktop
OUT=build/manual
CHROME=$(command -v chromium || command -v chromium-headless-shell || command -v chromium-browser || command -v google-chrome || true)
[ -n "$CHROME" ] || { echo "no Chromium for the PDF" >&2; exit 1; }

rm -rf "$OUT"
mkdir -p "$OUT"

# style: inside every page, no relative path that the PDF browser may not follow
style() { { echo "<style>"; cat "$1/style.css"; echo "</style>"; } > "$OUT/style-$2.html"; }

# html_pdf md-file html-file pdf-name title lang toc style   (toc: non-empty for a table of contents)
html_pdf() {
	toc=""
	[ -n "$6" ] && toc="--toc --toc-depth=2"
	# shellcheck disable=SC2086
	pandoc -f gfm+implicit_figures "$1" -s $toc -H "$OUT/style-$7.html" \
		--metadata title="$4" --metadata subtitle="$VERSION" --metadata lang="$5" -o "$2"
	"$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
		--print-to-pdf="$OUT/$3-$VERSION.pdf" "file://$PWD/$2" 2>/dev/null
	echo "$OUT/$3-$VERSION.pdf"
}

app() {
	style manual/app app
	for lang in it en; do
		src=manual/app/$lang
		python3 -I manual/app/diagrams/diagrams.py "$lang" "$OUT/dot-$lang"
		mkdir -p "$src/diagrams"
		for f in "$OUT/dot-$lang"/*.dot; do
			dot -Tsvg "$f" -o "$src/diagrams/$(basename "${f%.dot}").svg"
		done
		work=$OUT/app-$lang
		mkdir -p "$work"
		cp -r "$src"/* "$work"/
		for doc in quickstart manual; do
			case "$lang-$doc" in
				it-quickstart) title="ActivityTrack — Guida rapida"; name=GuidaRapida ;;
				it-manual) title="ActivityTrack — Manuale"; name=Manuale ;;
				en-quickstart) title="ActivityTrack — Quick start"; name=QuickStart ;;
				en-manual) title="ActivityTrack — User manual"; name=Manual ;;
			esac
			toc=""
			[ "$doc" = manual ] && toc=1
			html_pdf "$work/$doc.md" "$work/$doc.html" "ActivityTrack-$name" "$title" "$lang" "$toc" app
		done
		for f in "$work"/connectors/*.md; do
			[ -f "$f" ] || continue
			conn=$(basename "$f" .md)
			ctitle=$(sed -n '1s/^<!-- title: \(.*\) -->$/\1/p' "$f")
			[ "$lang" = it ] && suffix=Guida || suffix=Guide
			# capitalised name in the file name: antares -> Antares
			cname=$(printf '%s' "$conn" | sed 's/^./\U&/')
			html_pdf "$f" "${f%.md}.html" "ActivityTrack-$cname-$suffix" "ActivityTrack — ${ctitle:-$conn}" "$lang" "" app
		done
	done
}

# server and desktop: one document per language, the images shared in manual/<project>/img
single() { # project file prefix it-title it-name en-title en-name
	style "manual/$1" "$1"
	# one directory per project: the images of the server and of the desktop share names (home.png...)
	mkdir -p "$OUT/$1"
	cp -r "manual/$1/img" "$OUT/$1/img"
	for lang in it en; do
		case $lang in
			it) title=$4; name=$5 ;;
			en) title=$6; name=$7 ;;
		esac
		mkdir -p "$OUT/$1/$lang"
		# the document refers to ../img/<file>
		html_pdf "manual/$1/$lang/$2.md" "$OUT/$1/$lang/$2.html" "ActivityTrack-$3-$name" "$title" "$lang" 1 "$1"
	done
}

for p in "$@"; do
	case $p in
		app) app ;;
		server) single server admin Web "ActivityTrack Web — Manuale dell'amministratore" Amministratore \
			"ActivityTrack Web — Administrator's manual" Administrator ;;
		desktop) single desktop desktop Desktop "ActivityTrack Desktop — Manuale" Manuale \
			"ActivityTrack Desktop — Manual" Manual ;;
		*) echo "unknown project: $p" >&2; exit 2 ;;
	esac
done
