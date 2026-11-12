Version 1.0.0-alfa-1 (November 2026). ActivityTrack Desktop is the PC app of
ActivityTrack. It lives in the notification area, next to the clock, and keeps
the running activities and those to do a click away. So an activity, even a
short one, goes in from the keyboard instead of the phone.

The interface is in Italian; the screenshots show it as it is.

## 1. What it needs

- The organisation's **ActivityTrack Web** server: the PC pairs like a phone
  and syncs both ways.
- **Linux** with KDE Plasma or XFCE, on Wayland or X11, or **Windows 10 or 11**.

Without a network the PC keeps working: the changes leave when the network is
back. Reports, master data and management systems stay with the phone and the
web.

On the PC ActivityTrack is **one application** with three interfaces: this
one in the notification area, the command line (`activitytrack`, package
`activitytrack-cli`) and the full-screen terminal interface
(`activitytrack-tui`). They use the same data (`~/.local/share/activitytrack`,
on Windows `%APPDATA%\activitytrack`) and the same pairing: what is done with
one shows at once in the others. They all depend on the library
`python3-activitytrack`.

## 2. Installing

From the releases page
(<https://gitlab.com/activitytrack/activitytrack-desktop/-/releases>):

- **Debian 13 and 14, Ubuntu 24.04 and 26.04**: the package of one's
  distribution with the library's (from its page,
  <https://gitlab.com/activitytrack/python3-activitytrack/-/releases>), installed with
  `sudo apt install ./python3-activitytrack_<version>-1-<distro>_all.deb ./activitytrack-desktop_<version>-1-<distro>_all.deb`.
  ActivityTrack shows in the applications menu.
- **Other Linux distributions**: Python 3.11 or newer, PyQt6, cryptography and
  keyring from the distribution's packages, and the library (`pip install`
  from its repository). Unpack
  `activitytrack-desktop-<version>.tar.gz` and, in its folder, start
  `python3 -m activitytrack_desktop`.
- **Windows**: `ActivityTrackDesktop-<version>-setup.exe`. It installs for the
  current user, without administrator rights. The program is **not signed**
  (no certificate costs): at the first run Windows SmartScreen warns; choose
  **"More info" → "Run anyway"**. To check the file, compare its SHA-256 with
  `SHA256SUMS` of the same release.

On XFCE the icon shows when the panel has the **notification area** ("Status
Tray" or "Notification Area" plugin). GNOME without the AppIndicator extension
has no notification area: ActivityTrack then stays open in a window.

## 3. Pairing with the server

![Pairing](../img/pair.png)

1. On the web, open **Dispositivi → "Associa un dispositivo"** (Devices →
   Pair a device; on ActivityTrack Web 0.9.3: **Telefoni → "Associa un
   telefono"**, the link under "Non riesci a inquadrarlo?").
2. Copy the **link** starting with `activitytrack://pair`.
3. At the first start ActivityTrack opens **Impostazioni → Sincronizzazione**
   (settings → sync): **"Associa a un server…"** (pair with a server, on the
   Home too) opens the pairing window. When the link is in the clipboard it
   finds it by itself. Choose **"Associa"** (pair).

The link is good for 10 minutes and once. After pairing the PC downloads the
user's data and keeps them up to date.

![Sync](../img/sync.png)

**Impostazioni → Sincronizzazione** (settings → sync) shows server, user, organisation, the
changes waiting and those the server refused (**"Non sincronizzati"**), with
**"Sincronizza ora"** (sync now), **"Associa di nuovo…"** (pair again) and
**"Dissocia"** (unpair). Unpaired, the PC keeps its data; paired with another
server or user it starts again from nothing.

The access token is kept in the system's keyring (KWallet, GNOME Keyring,
Windows Credential Manager). Without one it is in a file only one's own user
reads, and the page says so.

## 4. The icon and the menu

The icon takes the colour of the running activity: **green** at work,
**yellow** on pause, **blue** travelling, grey when nothing runs. A **red dot**
says the sync has a problem (not paired, pairing revoked, incompatible
versions).

- **Hovering**: the running activities with the time so far.
- **Click**: opens or closes the window.
- **Middle click**: pauses or resumes the activity at work.
- **Menu** (right click): each running activity's commands (Pausa, Viaggio,
  Lavoro, Stop, Modifica… — pause, work, travel, stop, edit);
  **"Nuova attività…"** (new activity); **"Avvia Da fare ▸"** (start a to-do)
  with the overdue and today's ones; **"Nuovo Da fare…"** (new to-do); **"Nuova assenza…"** (new absence); the
  sync state; **"Esci"** (quit).

Closing the window only hides it: ActivityTrack stays in the notification area
until **"Esci"**.

**New in 1.0.** The *To-do* is no longer a separate thing: it is an activity in the **To do** state, and one activity goes
from plan to closure. There are eleven displayed states (§7); there is no **Sospendi** (suspend) any more (an activity becomes
*Suspended* by itself only when another starts and concurrent ones are not allowed), no "Completa l'attività" sheet (a
closed activity without a client or work is **Incomplete** and is fixed like any other), no **Ignorate** (there is the
**Bin**); priorities have names (None … Emergency). There are **absences** (§6). The same goes for the phone and the web.

**Upgrading to 1.0.** Data converts by itself, and the server's backups of earlier versions are restored. Sync requires
**the server and every device to be on 1.0**: an older Desktop says "Update the app to sync"; update the server first. After
the upgrade the first sync realigns the data, and changes not yet synced are kept and pushed.

## 5. The window

The window looks like the app: on the left the green bar with **Home**, **Da
fare** (to-dos) and **Impostazioni** (settings) (Ctrl+1, Ctrl+2, Ctrl+3) and,
at the bottom, **Sincronizza** (sync, F5) with a red dot when the sync has a
problem. It is light or dark as the system.

![The Home](../img/home.png)

The **Home** is the phone's:

- at the top the **big card** of the latest activity: company, client and
  description, the state with its time (**"In lavoro dalle 07:46"**, working
  since), the work and travel totals, on the right the time of the running
  stretch and the tags' colours. Below, the round buttons with their names:
  **Pausa** or **Riprendi** (pause, resume), **Viaggio** (travel),
  **Stop**. On the card the state is a **pill** with icon and colour and, on the right, the total. A click on the
  card opens the activity;
- below, the **small cards** of the other activities running or suspended:
  one line with the state and the times, and the round button that resumes
  or pauses it. A click brings it to the big card;
- the Home's header (and, when nothing runs, the empty card) has four buttons: **Da fare** (to do), **Lavoro** (work),
  **Viaggio** (travel; starts at once, even without a client) and **Assenza** (absence);
- then the filters and the list of all the activities in their states (§7).

The coloured strip on the left of each card is the company's (or the
client's) colour chosen on the web or on the phone.

![The Home in the dark theme](../img/home-dark.png)

### Keyboard shortcuts

They work while the ActivityTrack window is active; the buttons' tooltips
recall them.

| Keys | What it does |
|---|---|
| **Ctrl+N** | New activity (quick entry) |
| **Ctrl+P** | Pause the activity at work or travelling; when none is, resume the paused one |
| **Ctrl+T** | Stop the big card's activity; asks for the return trip when needed |
| **Ctrl+D** | New *To-do* (an activity in the To do state) |
| **Ctrl+F** | Search the list |
| **Ctrl+1**, **Ctrl+2**, **Ctrl+3** | Home, Da fare, Impostazioni |
| **F5** | Sync now |
| **Ctrl+Enter** | Confirm the open form |

With several activities at work together (when the policy allows it) Ctrl+P
asks which, in a small list: Enter picks the first, the latest.

Start, pause and stop also have shortcuts that work from any program:
§10.

## 6. Activities

### A new activity

![New activity](../img/quick.png)

**"Nuova attività"** (from the menu, the Home's **Lavoro** button or with **Ctrl+N**) opens the
quick entry, on top of the other windows:

- **Descrizione** (description), on several lines;
- **Cliente** (client): picked from the list or typed. A new name becomes a
  personal master record, when the policy allows it;
- **Tag**, separated by commas;
- **Lavoro** (work) or **Viaggio** (travel);
- **Adesso** (now), **Già iniziata** (already started: only the start, with the shortcuts 15 / 30 / 60 minutes ago; the
  activity stays running) or **Passata** (past: day, start and end, recorded already closed);
- the **activities running**: left running or stopped (without concurrent ones the new one sets the others aside, and
  they become *Suspended*).

**Ctrl+Enter** starts it. **"Altri campi…"** (more fields) goes to the full
form with what was typed.

The Home's **Viaggio** button starts an anonymous travel at once; while you are working it first asks **"Hai completato
l'attività lavorativa?"** (have you completed the work activity?): **Sì** (yes) closes the activity and starts a new travel
one, **No** makes the travel inside the same activity.

The full form opens from the Home's **⋯** menu too, **"Modulo completo…"**.

#### Absence

**"Assenza"** (Home or menu) asks the **kind** (Assenza, Ferie, Permesso, Malattia — absence, holiday, leave, sick leave),
the **company** (optional: empty = all), the **from / to** day and optional **times** (a leave). Without times one segment
is created per working day, following the working hours and skipping days off; future holidays can be planned. Absences are
counted apart in the reports.

### The full form

![Full form](../img/entry.png)

Company, client, role, quick pick, description, locality, notes and tags, as
the policy says (it may rename, hide or require them). For an existing
activity the top shows the **state** (pill "In <state> since", the work total and the state's buttons: Start, Pause, Stop,
Reopen, Restore…). **Reopen** always asks for confirmation. It also shows the **times**: each stretch (work, travel, pause) can
be changed or deleted, and a new one added, when the policy allows it. Two
overlapping stretches mark the activity **"da verificare"** (to check).

The **company** comes before the **client** and filters its list; a known
client chosen brings its company.

### Dates and times

Dates and times are typed in the format chosen in **Impostazioni → Generale**, or
picked: the calendar from the field's arrow and, for times, the app's
**5-minute grid** from the **▦** button next to the field. One row per hour,
12 hours at a time (**▲ Prima** / **Dopo ▼** move the window by 3 hours).
Start and end are chosen together: drag from the first cell to the last, or
click the first and then the last, and **OK**; at the top the range and its
length, the **hatched** cells are taken by other activities of that day.
**Orario esatto** (exact time) with **Usa** takes the minutes off the grid
(e.g. 09:37).

![The time grid](../img/grid.png)

### Stop and closing

**Stop** (or **Ctrl+T**) closes the activity at once: the "Complete the activity" sheet is gone. If the activity has an
outbound travel followed by work, and no travel after its last work, it asks: **Avvia viaggio di ritorno** (start the return
trip), **Termina l'attività** (end the activity) or **Termina l'attività ed aggiungi il viaggio di ritorno** (end it and add
the return trip: the same duration and km as the outbound, start and arrival swapped; only with editable times). With
editable times the end may lie up to 60 minutes in the future; if another activity starts earlier, the end is moved back
with a notice.

A closed activity with a client, at least one work segment and the required fields is **Done**; otherwise it is
**Incomplete** and is fixed by opening it, like any other.

## 7. To-dos and states

A *To-do* is an **activity in the To do state**: when you start it, it becomes Work or Travel and, at the end, Done or
Incomplete.

Below the running activities the Home has one list, as the app: **In ritardo** (late), **Oggi** (today), **Prossimi giorni**
(next days), **Giorni precedenti** (earlier days), **Senza data** (no date). The filters **period** (Oggi, 24 h, 3 gg…),
**state**, **company** and **tag** are buttons with their menu, coloured when they are not the initial ones, and are
remembered; **Cerca** (search, Ctrl+F) narrows the list to the rows with the words typed.

Each row has its **state's** icon on the left, eleven in all:

| State | Icon | Colour |
|---|---|---|
| To do | check box | white |
| Planned | clock | grey |
| Late | **!** | brown |
| Work | ▶ | green |
| Travel | car | blue |
| Pause | ⏸ | yellow |
| Suspended | moon | orange |
| Done | ✓ | greenish |
| Incomplete | ■ | reddish |
| Absence | dot | fuchsia |
| Deleted | bin | grey |

An activity to do has the round buttons **Avvia** (start) and **Fatto** (done) and, in the **⋯** menu, **Posticipa**
(postpone), **Elimina** (delete) and **Modifica…** (edit); one ticked by mistake (no segments) goes back with **"Rimetti da
fare"** (put back to do); a click on the row opens it. An **Incomplete** activity is opened and fixed like the others.

![The Da fare section](../img/todos.png)

The **Da fare** section (Ctrl+2) shows them all, by due date and plan, with **"Anche le fatte"** (done ones too), the
**Cestino** (bin), the company and the search; **"Nuovo Da fare"** (or **Ctrl+D**) makes one. **Elimina** moves the activity
to the **Cestino**, where **Ripristina** (restore) puts it back and **Elimina definitivamente** (delete permanently)
removes it.

![To-do](../img/todo.png)

The form has company, client, description, notes, references (tickets, links: one per line), **due date**, **plan** (day,
time, duration) and **priority** (None, Low, Medium, High, Urgent, Emergency; instead of P1…P5). A management-system item
that was deleted does not come back with the next import.

## 8. Reminders

The phone's, as desktop **notifications**:

- **"Ancora su …?"** (still on …?) while an activity runs: yes, pause, stop at
  the time of the last confirmation;
- **"Ancora in pausa?"** (still on pause?): resume, stop;
- **"Nessuna attività oggi"** (no activity today) after the working hours
  start: absent all day, start an activity;
- a **planned To-do** coming: start, postpone, re-plan;
- the **planned end** of an activity: yes, stop; no, go on.

On Linux the notifications have the buttons. On Windows, or where the
notifications have none, a click opens the question in a window:

![A question](../img/question.png)

![Reminders](../img/reminders.png)

**Impostazioni → Promemoria** (reminders) switches each on or off and sets the
intervals; those the policy fixes are grey. The phone shows the same
reminders: an answer that changes the activity or the *To-do* also counts on
the other device.

## 9. General

![General](../img/general.png)

**Impostazioni → Generale** has:

- **"Avvia ActivityTrack all'accesso"** (start at sign-in): it starts with the
  session, hidden in the notification area. On Linux it is switched on at the
  first start; on Windows the installer offers it;
- **dates and times**: the date format, European (31/12/2026), American
  (12/31/2026) or ISO (2026-12-31), and the time format, 24 hours (18:30) or
  12 hours (6:30 PM). The command line and the terminal follow them too, as
  the preferences of ActivityTrack Web;
- **updates**: new versions are announced by the **server the PC is paired
  with**, at every sync; **"Controlla ora"** (check now) asks at once. The
  announcement is signed and accepted only if the signature is the server's,
  whose key comes in the pairing link: with an older link (no key) or another
  signature the program says so and offers nothing. A new version shows as a
  notification with **"Scarica"** (download): the package comes from the
  server, its SHA-256 is checked, and then it opens with the system's
  installer. If ActivityTrack was installed by the package manager (`apt`),
  the new version is reported but **not downloaded**: the package manager
  updates it. **"Anche le versioni beta"** (betas too) includes the test
  versions. The policy may fix both.

## 10. Global shortcuts

Three key combinations work from any program, even with ActivityTrack's
window closed:

| Keys | What they do |
|---|---|
| **Ctrl+Alt+A** | opens the new activity's window in front |
| **Ctrl+Alt+P** | pauses the activity at work or travelling (the most recent); when there is none, resumes the one on pause |
| **Ctrl+Alt+S** | stops the running activity; asks for the return trip when needed |

When more than one activity qualifies (concurrent activities), a small window
asks which. Pause, resume and stop are confirmed by a notification.

In **Generale** → **Scorciatoie globali** (global shortcuts) each one is
switched on or off and takes other keys (Ctrl, Alt or Super are needed, except
for the function keys); **"Ripristina predefinite"** (restore defaults) goes
back to the ones above. The line below says how they work on this desktop:

- **Windows**: directly;
- **Linux on X11** (XFCE, KDE or GNOME on X11): with the `python3-xlib`
  package, which the `.deb` package installs; with the `.tar.gz`, install it
  from the distribution;
- **Linux on Wayland** (KDE Plasma 6, GNOME 48 or later): through the
  desktop portal. The first time the desktop asks to confirm the keys; then
  they are changed in its settings (KDE: System Settings → Shortcuts; GNOME:
  Settings → Keyboard → Shortcuts). On Wayland the desktop may not bring the
  window in front of the others: it flashes in the task bar instead.

When a key is already taken by another program, the line says so. Where the
shortcuts are not available, or to use keys of your own, assign a desktop
shortcut to one of these commands:

```sh
activitytrack-desktop --start    # new activity
activitytrack-desktop --pause    # pause or resume
activitytrack-desktop --stop     # stop
```

The command goes to the ActivityTrack already open; when it is not open it
starts it in the notification area and runs the command. On Windows the
program is `ActivityTrack.exe` in the installation folder
(`%LOCALAPPDATA%\Programs\ActivityTrack`), with the same options.

## 11. The policy on the PC

The PC gets the phone's policy and applies the keys that concern it: features
(activities, travels, to-dos, planning, deleting and restoring), fields (names,
required, hidden, read-only), editable times, free tags, activities only from
planned or assigned ones (`plannedOnly`, formerly `todosOnly`), central master data only, reminder intervals, updates. The
phone-only keys (location, calls, widgets…) do not concern it.

## 12. Common problems

| Problem | What to do |
|---|---|
| A shortcut does not work | Read the line under **Scorciatoie globali** in **Generale**: the key may be taken by another program, or `python3-xlib` may be missing (X11). Otherwise assign `activitytrack-desktop --pause` (or `--start`, `--stop`) to a key in the desktop's settings |
| The icon does not show | XFCE: add the notification area to the panel. GNOME: the AppIndicator extension is needed |
| Windows: "Windows protected your PC" | The program is not signed: "More info" → "Run anyway" |
| "Codice scaduto o già usato" (code expired or used) | The link is good for 10 minutes and once: make another on the web |
| "Il certificato del server non è valido" (certificate not valid) | The server has a self-signed certificate: use a link just made, which carries its key |
| "Il server ha revocato l'associazione" (pairing revoked) | Pair the PC again from the web: the data stay |
| "Aggiorna l'app per sincronizzare" (update the app to sync) | The server is on 1.0 and the PC is not: update ActivityTrack Desktop |
| "Il server non accetta più questa versione" (version no longer accepted) | Update ActivityTrack Desktop (Impostazioni → Generale, "Controlla ora") |
| "Va aggiornato il server" (the server must be updated) | Tell the ActivityTrack Web administrator |
| An activity made on the phone does not show | It comes within 30 seconds; **F5** ("Sincronizza") brings it at once |
