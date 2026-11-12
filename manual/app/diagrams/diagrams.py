#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Graphviz sources of the manual's diagrams, one definition for every
# language: python3 diagrams.py <lang> <outdir> writes <name>.dot files.
# The states and transitions follow the activity model 1.0 (docs/ACTIVITY-MODEL.md of the app).

import os
import sys

L = {
	"it": {
		"active": "In corso", "work": "Lavoro", "travel": "Viaggio", "pause": "Pausa",
		"suspended": "Sospesa", "to_complete": "Da completare", "closed": "Chiusa",
		"start": "Avvio", "cmd_work": "Lavoro / Riprendi", "cmd_travel": "Viaggio", "cmd_pause": "Pausa",
		"cmd_suspend": "Sospendi", "cmd_stop": "Stop", "cmd_complete": "Completa", "cmd_reopen": "Riapri",
		"auto_close": "Stop con cliente e descrizione\n(non da un Da fare)",
		"t_open": "Aperta", "t_planned": "Pianificata", "t_done": "Fatta", "t_ignored": "Ignorata",
		"plan": "data e ora", "unplan": "togli pianificazione", "done": "Segna come fatta", "undo": "Segna come da fare",
		"ignore": "Ignora", "restore": "Ripristina", "postpone": "Posticipa", "overdue": "in ritardo: blocco o scadenza passati",
		"company": "Azienda", "client": "Cliente", "site": "Sede", "entry": "Attività", "segment": "Tratto",
		"expense": "Spesa", "attachment": "Allegato", "ref": "Riferimento esterno", "tag": "Tag", "role": "Ruolo",
		"todo": "Da fare", "preset": "Attività predefinita", "sample": "Punto di posizione",
		"place": "Luogo (casa, altro)", "schedule": "Orario di lavoro\nPausa pranzo\nGiorni liberi", "absence": "Assenza",
		"stop": "Stop", "q_work": "In lavoro?", "now": "Ferma ora", "return": "Avvia rientro",
		"short": "Meno di un minuto?", "discard": "Scarta", "keep": "Tieni e ferma",
		"complete_fields": "Cliente e descrizione\ncompilati?", "from_todo": "Da un Da fare?",
		"yes": "sì", "no": "no", "fill": "Completa i dettagli", "todo_done": "La voce Da fare\nè conclusa?",
		"end_time": "Fine (orario modificabili)",
		"a_todo": "Da fare", "a_running": "In corso", "a_closed": "Chiusa", "a_deleted": "Eliminata (Cestino)",
		"a_work": "Lavoro", "a_travel": "Viaggio", "a_pause": "Pausa", "a_susp": "Sospesa\n(nessun tratto aperto)",
		"a_done": "Fatta", "a_incomplete": "Incompleta", "c_start": "Avvia", "c_tick": "Fatta (spunta)", "c_untick": "Rimetti da fare",
		"c_stop": "Stop", "c_reopen": "Riapri (con conferma)", "c_delete": "Elimina", "c_restore": "Ripristina",
		"c_other": "parte un'altra attività\n(senza contemporanee)", "c_resume": "Lavoro / Viaggio",
		"complete": "Cliente, lavoro e campi\nobbligatori ci sono?", "ret_q": "Andata e lavoro,\nsenza ritorno?",
		"ret_3": "Avvia viaggio di ritorno\nTermina l'attività\nTermina e aggiungi il ritorno",
	},
	"en": {
		"active": "Running", "work": "Work", "travel": "Travel", "pause": "Pause",
		"suspended": "Suspended", "to_complete": "To complete", "closed": "Closed",
		"start": "Start", "cmd_work": "Work / Resume", "cmd_travel": "Travel", "cmd_pause": "Pause",
		"cmd_suspend": "Suspend", "cmd_stop": "Stop", "cmd_complete": "Complete", "cmd_reopen": "Reopen",
		"auto_close": "Stop with client and activity\n(not from a to-do)",
		"t_open": "Open", "t_planned": "Planned", "t_done": "Done", "t_ignored": "Ignored",
		"plan": "date and time", "unplan": "remove the plan", "done": "Mark as done", "undo": "Mark as to do",
		"ignore": "Ignore", "restore": "Restore", "postpone": "Postpone", "overdue": "overdue: block or due date passed",
		"company": "Company", "client": "Client", "site": "Site", "entry": "Activity", "segment": "Segment",
		"expense": "Expense", "attachment": "Attachment", "ref": "External reference", "tag": "Tag", "role": "Role",
		"todo": "To-do", "preset": "Preset activity", "sample": "Location sample",
		"place": "Place (home, other)", "schedule": "Working hours\nLunch break\nDays off", "absence": "Absence",
		"stop": "Stop", "q_work": "Working?", "now": "Stop now", "return": "Start return travel",
		"short": "Under a minute?", "discard": "Discard", "keep": "Keep and stop",
		"complete_fields": "Client and activity\nfilled in?", "from_todo": "From a to-do?",
		"yes": "yes", "no": "no", "fill": "Fill in the details", "todo_done": "Is the to-do\ndone?",
		"end_time": "End (editable times)",
		"a_todo": "To do", "a_running": "Running", "a_closed": "Closed", "a_deleted": "Deleted (Bin)",
		"a_work": "Work", "a_travel": "Travel", "a_pause": "Pause", "a_susp": "Suspended\n(no open segment)",
		"a_done": "Done", "a_incomplete": "Incomplete", "c_start": "Start", "c_tick": "Done (tick)", "c_untick": "Put back to do",
		"c_stop": "Stop", "c_reopen": "Reopen (with confirmation)", "c_delete": "Delete", "c_restore": "Restore",
		"c_other": "another activity starts\n(no concurrent ones)", "c_resume": "Work / Travel",
		"complete": "Client, work and required\nfields present?", "ret_q": "Outbound travel and work,\nno return?",
		"ret_3": "Start return trip\nEnd the activity\nEnd and add the return trip",
	},
}

HEAD = 'digraph G {\n\tgraph [rankdir=LR, fontname="Helvetica", fontsize=11, bgcolor="white", pad=0.2];\n' \
	'\tnode [fontname="Helvetica", fontsize=11, shape=box, style="rounded,filled", fillcolor="#eef2fb", color="#5b6bd6"];\n' \
	'\tedge [fontname="Helvetica", fontsize=9, color="#555555"];\n'


def q(s):
	return '"' + s.replace('"', '\\"').replace("\n", "\\n") + '"'


def entry_states(t):
	return HEAD + f"""	start [shape=circle, label="", width=0.2, fillcolor="#333333"];
	todo [label={q(t["a_todo"])}, fillcolor="#ffffff"];
	running [label={q(t["a_running"] + "\\n(" + t["a_work"] + " / " + t["a_travel"] + " / " + t["a_pause"] + ")")}, fillcolor="#d7efd9"];
	susp [label={q(t["a_susp"])}, fillcolor="#fde3cc"];
	closed [label={q(t["a_closed"] + "\\n(" + t["a_done"] + " / " + t["a_incomplete"] + ")")}, fillcolor="#e4e6ea"];
	bin [label={q(t["a_deleted"])}, fillcolor="#f2f2f2", style="rounded,filled,dashed"];
	start -> todo [label={q(t["a_todo"])}];
	start -> running [label={q(t["a_work"] + " / " + t["a_travel"])}];
	start -> closed [label={q(t["a_work"])}];
	todo -> running [label={q(t["c_start"])}];
	todo -> closed [label={q(t["c_tick"])}];
	closed -> todo [label={q(t["c_untick"])}];
	running -> susp [label={q(t["c_other"])}, style=dashed];
	susp -> running [label={q(t["c_resume"])}];
	running -> closed [label={q(t["c_stop"])}];
	susp -> closed [label={q(t["c_stop"])}];
	closed -> running [label={q(t["c_reopen"])}];
	todo -> bin [label={q(t["c_delete"])}];
	closed -> bin [label={q(t["c_delete"])}];
	bin -> todo [label={q(t["c_restore"])}, style=dashed];
}}
"""


def modes(t):
	return HEAD + f"""	work [label={q(t["work"])}, fillcolor="#d7efd9"];
	travel [label={q(t["travel"])}, fillcolor="#d6e4fa"];
	pause [label={q(t["pause"])}, fillcolor="#fdf0c8"];
	work -> travel [label={q(t["cmd_travel"])}];
	travel -> work [label={q(t["cmd_work"])}];
	work -> pause [label={q(t["cmd_pause"])}];
	pause -> work [label={q(t["cmd_work"])}];
	travel -> pause [label={q(t["cmd_pause"])}];
	pause -> travel [label={q(t["cmd_travel"])}];
}}
"""




def entities(t):
	g = 'digraph G {\n\tgraph [rankdir=TB, fontname="Helvetica", fontsize=11, bgcolor="white", pad=0.2, nodesep=0.35, ranksep=0.5];\n' \
		'\tnode [fontname="Helvetica", fontsize=11, shape=box, style="rounded,filled", fillcolor="#eef2fb", color="#5b6bd6"];\n' \
		'\tedge [fontname="Helvetica", fontsize=9, color="#555555", arrowhead=crow, arrowtail=tee, dir=both];\n'
	n = {k: t[k] for k in ("company", "client", "site", "entry", "segment", "expense", "attachment", "ref", "tag", "role", "preset", "sample", "place", "schedule")}
	g += "".join(f"\t{k} [label={q(v)}];\n" for k, v in n.items())
	g += '\tentry [fillcolor="#d7efd9"];\n'
	for a, b in (("company", "client"), ("company", "site"), ("client", "site"), ("company", "entry"), ("client", "entry"),
			("entry", "segment"), ("segment", "sample"), ("entry", "expense"), ("entry", "attachment"), ("entry", "ref"),
			("entry", "tag"), ("role", "entry"), ("role", "preset"),
			("company", "preset")):
		g += f"\t{a} -> {b};\n"
	g += '\t{ rank=same; place; schedule; }\n\tplace -> schedule [style=invis];\n}\n'
	return g


def stop_flow(t):
	return HEAD.replace("rankdir=LR", "rankdir=TB") + f"""	stop [label={q(t["stop"])}, fillcolor="#f8d4d4"];
	short [shape=diamond, label={q(t["short"])}, fillcolor="#ffffff"];
	discard [label={q(t["discard"])}, fillcolor="#e4e6ea"];
	ret [shape=diamond, label={q(t["ret_q"])}, fillcolor="#ffffff"];
	three [label={q(t["ret_3"])}];
	full [shape=diamond, label={q(t["complete"])}, fillcolor="#ffffff"];
	done [label={q(t["a_done"])}, fillcolor="#e4f0dc"];
	inc [label={q(t["a_incomplete"])}, fillcolor="#f8d4d4"];
	stop -> short;
	short -> discard [label={q(t["yes"] + ": " + t["discard"])}];
	short -> ret [label={q(t["no"] + " / " + t["keep"])}];
	ret -> three [label={q(t["yes"])}];
	ret -> full [label={q(t["no"])}];
	three -> full;
	full -> done [label={q(t["yes"])}];
	full -> inc [label={q(t["no"])}];
}}
"""


def main():
	lang, out = sys.argv[1], sys.argv[2]
	t = L[lang]
	os.makedirs(out, exist_ok=True)
	for name, f in (("entry-states", entry_states), ("modes", modes), ("entities", entities), ("stop-flow", stop_flow)):
		with open(os.path.join(out, name + ".dot"), "w") as fh:
			fh.write(f(t))


if __name__ == "__main__":
	main()
