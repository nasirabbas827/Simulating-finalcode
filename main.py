import tkinter as tk
from tkinter import ttk
import socket
import threading
import time
import json
import random
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from blockchain import Blockchain, Block

NODES = {'A': 5001, 'B': 5002, 'Attacker': 5003}
LOCALHOST = '127.0.0.1'

class Node:
    def __init__(self, name, port, peers):
        self.name = name
        self.port = port
        self.peers = peers
        self.blockchain = Blockchain()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((LOCALHOST, self.port))

        self.confirmed_blocks = []
        self.forks_detected = 0
        self.attacks_won = 0
        self.total_attacks = 0

        # For visualization tracking
        self.stats = {
            'time': [],
            'forks_detected': [],
            'attacks_won': [],
            'total_attacks': []
        }

        # GUI Setup
        self.root = tk.Tk()
        self.root.title(f"Blockchain Node: {self.name}")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f2f5")

        # Style configuration
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TLabel", font=("Helvetica", 12), background="#f0f2f5")
        style.configure("TEntry", font=("Helvetica", 12))

        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Node Activity Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_area = tk.Text(log_frame, height=10, width=60, font=("Courier New", 11), bg="#ffffff", fg="#333333")
        self.log_area.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_area.config(yscrollcommand=scrollbar.set)

        # Block info frame
        self.block_info_frame = ttk.LabelFrame(main_frame, text="Latest Block Info", padding=10)
        self.block_info_frame.pack(fill="x", padx=10, pady=5)
        self.nonce_label = ttk.Label(self.block_info_frame, text="Nonce: N/A")
        self.nonce_label.pack(anchor="w")
        self.prev_hash_label = ttk.Label(self.block_info_frame, text="Previous Hash: N/A")
        self.prev_hash_label.pack(anchor="w")
        self.new_hash_label = ttk.Label(self.block_info_frame, text="New Hash: N/A")
        self.new_hash_label.pack(anchor="w")

        # Transaction UI for Node A
        if self.name == "A":
            tx_frame = ttk.LabelFrame(main_frame, text="Create Transaction", padding=10)
            tx_frame.pack(fill="x", padx=10, pady=5)
            self.amount_input = ttk.Entry(tx_frame)
            self.amount_input.insert(0, "100")
            self.amount_input.pack(side="left", padx=5)
            ttk.Button(tx_frame, text="Start Transaction", command=self.start_transaction).pack(side="left", padx=5)

            # Plot for stats visualization
            self.fig, self.ax = plt.subplots(figsize=(6, 3), dpi=100)
            self.ax.set_title("Attack and Fork Statistics", fontsize=12, pad=10)
            self.ax.set_xlabel("Time (s)", fontsize=10)
            self.ax.set_ylabel("Count", fontsize=10)
            self.line_forks, = self.ax.plot([], [], label="Forks Detected", color="#1f77b4")
            self.line_won, = self.ax.plot([], [], label="Attacks Won", color="#ff7f0e")
            self.line_total, = self.ax.plot([], [], label="Total Attacks", color="#2ca02c")
            self.ax.legend(fontsize=8)
            self.ax.grid(True, linestyle="--", alpha=0.7)
            self.fig.patch.set_facecolor("#f0f2f5")
            self.ax.set_facecolor("#ffffff")

            canvas_frame = ttk.LabelFrame(main_frame, text="Statistics", padding=10)
            canvas_frame.pack(fill="both", padx=10, pady=5)
            self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

            self.update_plot()

        # Mine button for Node B and Attacker
        if self.name in ["B", "Attacker"]:
            ttk.Button(main_frame, text="Mine Block", command=self.mine_block).pack(pady=10)

        threading.Thread(target=self.listen, daemon=True).start()

    def log(self, text):
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} | {text}\n")
        self.log_area.see(tk.END)

    def start_transaction(self):
        try:
            amount = int(self.amount_input.get().strip())
            tx = {"sender": self.name, "receiver": "B", "amount": amount}
            if self.blockchain.add_transaction(tx):
                self.log(f"Created TX: {tx}")
                self.broadcast({"type": "tx", "data": tx})
            else:
                self.log("Invalid transaction: insufficient balance")
        except Exception as e:
            self.log(f"Transaction error: {e}")

    def mine_block(self):
        if self.name == "Attacker":
            self.total_attacks += 1
            tx1 = {"sender": self.name, "receiver": "B", "amount": 50}
            tx2 = {"sender": self.name, "receiver": "A", "amount": 50}
            self.blockchain.transaction_pool = [tx1, tx2]
            self.log("Attacker adds conflicting transactions!")

        if self.name == "B":
            time.sleep(random.uniform(1.5, 5.0))  # Simulate network delay

        block = self.blockchain.mine_pending_transactions(self.name)
        if block:
            self.log(f"Mined Block #{block.index} | Nonce: {block.nonce} | Prev Hash: {block.previous_hash[:8]}... | New Hash: {block.hash[:8]}...")
            # Update block info labels
            self.nonce_label.config(text=f"Nonce: {block.nonce}")
            self.prev_hash_label.config(text=f"Previous Hash: {block.previous_hash[:16]}...")
            self.new_hash_label.config(text=f"New Hash: {block.hash[:16]}...")
            self.broadcast({
                "type": "block",
                "data": [vars(b) for b in self.blockchain.chain]
            })
        else:
            self.log("Nothing to mine")

    def broadcast(self, msg):
        for peer_port in self.peers:
            try:
                self.sock.sendto(json.dumps(msg).encode(), (LOCALHOST, peer_port))
            except Exception as e:
                self.log(f"Broadcast error: {e}")

    def listen(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(65536)
                msg = json.loads(data.decode())
                if msg["type"] == "tx":
                    tx = msg["data"]
                    if self.blockchain.add_transaction(tx):
                        self.log(f"Received TX: {tx}")

                elif msg["type"] == "block":
                    chain_data = msg["data"]
                    new_chain = []
                    for blk in chain_data:
                        blk_data = blk.copy()
                        blk_data.pop("hash", None)
                        new_chain.append(Block(**blk_data))

                    if self.blockchain.resolve_chain(new_chain):
                        self.forks_detected += 1
                        self.log("Chain replaced via fork resolution!")
                        if self.name != "Attacker":
                            if any(b.miner == "Attacker" for b in new_chain):
                                self.attacks_won += 1
                        self.log(f"Forks: {self.forks_detected}, Attacks succeeded: {self.attacks_won}/{self.total_attacks}")
                        confirmed_txns = [tx for blk in self.blockchain.chain[:-2] for tx in blk.transactions]
                        for tx in confirmed_txns:
                            if tx not in self.confirmed_blocks:
                                self.confirmed_blocks.append(tx)
                                self.log(f"Confirmed TX: {tx}")
                        if self.name == "A":
                            self.record_stats()
            except Exception as e:
                self.log(f"Error: {e}")

    def record_stats(self):
        now = time.time()
        if not self.stats['time']:
            self.start_time = now
        elapsed = now - self.start_time
        self.stats['time'].append(elapsed)
        self.stats['forks_detected'].append(self.forks_detected)
        self.stats['attacks_won'].append(self.attacks_won)
        self.stats['total_attacks'].append(self.total_attacks)

    def update_plot(self):
        if self.stats['time']:
            self.line_forks.set_data(self.stats['time'], self.stats['forks_detected'])
            self.line_won.set_data(self.stats['time'], self.stats['attacks_won'])
            self.line_total.set_data(self.stats['time'], self.stats['total_attacks'])
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw_idle()
        self.root.after(2000, self.update_plot)

    def run(self):
        self.root.mainloop()

def run_node(name, port, peer_ports):
    node = Node(name, port, peer_ports)
    node.run()

if __name__ == "__main__":
    import multiprocessing
    processes = []
    for name, port in NODES.items():
        peers = [p for n, p in NODES.items() if p != port]
        p = multiprocessing.Process(target=run_node, args=(name, port, peers))
        p.start()
        processes.append(p)
        time.sleep(1)
    for p in processes:
        p.join()