# Blockchain Network Simulator

A Python Tkinter desktop application that simulates local network nodes, transactions and block mining.

## Features

- Local socket communication between nodes
- Transaction creation and broadcast
- Block mining and hash display
- Activity logs and statistics plots

## Technology

Python, Tkinter, sockets, pandas and Matplotlib.

## Local setup

Clone the repository:

```bash
git clone https://github.com/nasirabbas827/Simulating-finalcode.git
cd Simulating-finalcode
```

Use a virtual environment:

```bash
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate
python -m pip install pandas matplotlib
```

The install command lists packages used by the inspected source; this repository does not include a pinned dependency file. Saved machine learning models may require the versions used during training.

Start the desktop application from the repository root:

```bash
python main.py
```

## Project-specific setup

Tkinter must be available in your Python installation. Run `main.py` to start the simulator; keep its local socket ports free. Use a desktop session because the program opens GUI windows.

## Repository layout

| Path | Purpose |
|---|---|
| `blockchain.py` | Block and blockchain implementation |
| `main.py` | Desktop application entry point |

## Development notes

Setup steps describe local development. Configure your own database, mail and API credentials where applicable. Review debug settings and replace development secrets before deploying. The application was not executed as part of this documentation update.

Maintained by [Nasir Abbas](https://github.com/nasirabbas827).
