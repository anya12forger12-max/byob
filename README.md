# BYOB — Build Your Own Botnet

BYOB is an open-source **post-exploitation framework for students, researchers, and developers**. This repository preserves the upstream [malwaredllc/byob](https://github.com/malwaredllc/byob) codebase together with later maintenance commits. It is offensive security tooling intended for **authorized education and research**, not for unauthorized access to systems.

## Overview

BYOB provides the pieces needed to study command-and-control (C2) architecture without writing a server or remote-access client from scratch:

- A console-based C2 server with a persistent SQLite database ([byob/server.py](byob/server.py), [byob/core/database.py](byob/core/database.py)).
- A client generator and stager/payload code ([byob/client.py](byob/client.py), [byob/core/generators.py](byob/core/generators.py), [payloads.py](byob/core/payloads.py), [stagers.py](byob/core/stagers.py)). Upstream documentation describes remote imports that load modules in memory rather than writing them to disk.
- Crypto helpers in [byob/core/security.py](byob/core/security.py): Diffie-Hellman key exchange, AES-256-CBC, and XOR-128 routines. Security claims in the upstream docs should be treated as design intent, not guarantees.
- A module directory ([byob/modules/](byob/modules/)) covering persistence, packet capture, privilege-escalation demonstrations, port scanning, keylogging, screenshots, Outlook/iCloud checks, process control, and phone utilities. Add your own modules there for lab exercises.
- A browser-based management interface ([web-gui/](web-gui/)) with a dashboard, payload generator, and terminal view; its entry point is `web-gui/run.py`.
- Cross-compilation scaffolding in [byob/crosscomp/](byob/crosscomp/) for experimenting with other target architectures.

## Install

Python 3 is required. The provided installer creates an isolated virtual environment and installs both dependency sets:

```sh
git clone https://github.com/anya12forger12-max/byob.git
cd byob
./install.sh
```

Afterwards, the console entry points are `byob/server.py` and `byob/client.py`, and the web GUI entry point is `web-gui/run.py`. Some dependencies (for example crypto or screenshot packages) may need system build tools such as CMake on Linux; see the upstream CLI walkthrough in [byob/README.md](byob/README.md) for argument details before running anything.

## Project layout

| Path | Purpose |
|---|---|
| [byob/](byob/) | Console application: server, client generator, core library, and modules |
| [web-gui/](web-gui/) | Web dashboard, API routes, and payload-generation frontend |
| [byob/crosscomp/](byob/crosscomp/) | Cross-compilation environment scripts and architecture lists |
| [install.sh](install.sh) | Virtual-environment setup for console and web dependencies |
| [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) | Contribution and vulnerability-reporting policies |
| [ONBOARDING.md](ONBOARDING.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Setup and diagnostics notes |
| [LICENSE](LICENSE) | GNU General Public License v3 |

## Responsible use

BYOB is an offensive security framework. Treat it as lab equipment:

- Use it **only** on systems you own or where you have explicit, written authorization — for example a dedicated lab, a CTF, or a sanctioned research engagement.
- Do not generate clients, run a C2 server, or collect data on networks and machines you do not control. Authorization from one owner does not extend to third parties on the same network.
- Know and follow the laws that apply to you, your institution, and your jurisdiction; interception, keylogging, and persistence features can carry serious legal consequences.
- Minimize and protect anything collected during a test, keep an audit trail, and disclose findings through the agreed channel.
- The upstream project's features are educational demonstrations, not reliability or detection-avoidance guarantees. Do not rely on them for operational security.

## License and attribution

Distributed under the **GNU General Public License, version 3** — see [LICENSE](LICENSE). The framework, branding, and documentation originate from [malwaredllc/byob](https://github.com/malwaredllc/byob); upstream copyright and license notices are retained. This repository adds maintenance commits under the same license. Provided without warranty.

## Quick start — 1 or 2 commands

```bash
./setup.sh          # install dependencies
./setup.sh run      # start the project (when a run target exists)
```

`setup.sh` detects this repository's build system and installs the right toolchain
dependencies. Use `./setup.sh test` to run the available checks. If a project has no
standard run target, the script prints the correct command from the sections above.
