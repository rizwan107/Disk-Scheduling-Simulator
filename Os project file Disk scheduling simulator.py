import tkinter as tk
from tkinter import messagebox, ttk
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import statistics
import random
import math

# FCFS Scheduler: Processes requests in order
def fcfs_scheduler(requests, start_head, max_cyl):
    head = start_head
    total_seek = 0
    sequence = [head]
    seek_times = []
    for req in requests:
        seek = abs(head - req)
        total_seek += seek
        seek_times.append(seek)
        head = req
        sequence.append(head)
    return sequence, total_seek, seek_times

# SSTF Scheduler: Shortest Seek Time First
def sstf_scheduler(requests, start_head, max_cyl):
    head = start_head
    total_seek = 0
    sequence = [head]
    seek_times = []
    remaining = requests.copy()
    while remaining:
        closest = min(remaining, key=lambda x: abs(head - x))
        seek = abs(head - closest)
        total_seek += seek
        seek_times.append(seek)
        head = closest
        sequence.append(head)
        remaining.remove(closest)
    return sequence, total_seek, seek_times

# SCAN Scheduler: Moves in one direction, then reverses
def scan_scheduler(requests, start_head, max_cyl):
    head = start_head
    total_seek = 0
    sequence = [head]
    seek_times = []
    remaining = sorted(requests)
    direction = 1
    processed = []

    while remaining:
        if direction == 1:
            targets = [r for r in remaining if r >= head]
            if not targets:
                seek = max_cyl - head
                total_seek += seek
                seek_times.append(seek)
                sequence.append(max_cyl)
                head = max_cyl
                direction = -1
                continue
        else:
            targets = [r for r in remaining if r <= head]
            if not targets:
                seek = head
                total_seek += seek
                seek_times.append(seek)
                sequence.append(0)
                head = 0
                direction = 1
                continue

        closest = min(targets, key=lambda x: abs(head - x))
        seek = abs(head - closest)
        total_seek += seek
        seek_times.append(seek)
        head = closest
        sequence.append(head)
        remaining.remove(closest)
        processed.append(closest)
        direction = 1 if not [r for r in remaining if r >= head] else -1 if not [r for r in remaining if r <= head] else direction

    return sequence, total_seek, seek_times

# C-SCAN Scheduler: Moves in one direction, jumps to start
def cscan_scheduler(requests, start_head, max_cyl):
    head = start_head
    total_seek = 0
    sequence = [head]
    seek_times = []
    remaining = sorted(requests)
    processed = []

    while remaining:
        targets = [r for r in remaining if r >= head]
        if not targets:
            if remaining:
                seek = max_cyl - head
                total_seek += seek
                seek_times.append(seek)
                sequence.append(max_cyl)
                seek = max_cyl
                total_seek += seek
                seek_times.append(seek)
                sequence.append(0)
                head = 0
                continue
        for req in sorted(targets):
            seek = abs(head - req)
            total_seek += seek
            seek_times.append(seek)
            head = req
            sequence.append(head)
            remaining.remove(req)
            processed.append(req)

    return sequence, total_seek, seek_times

# LOOK Scheduler: Like SCAN but stops at last request
def look_scheduler(requests, start_head, max_cyl):
    head = start_head
    total_seek = 0
    sequence = [head]
    seek_times = []
    remaining = sorted(requests)
    direction = 1
    processed = []

    while remaining:
        if direction == 1:
            targets = [r for r in remaining if r >= head]
        else:
            targets = [r for r in remaining if r <= head]

        if not targets:
            direction *= -1
            continue

        closest = min(targets, key=lambda x: abs(head - x))
        seek = abs(head - closest)
        total_seek += seek
        seek_times.append(seek)
        head = closest
        sequence.append(head)
        remaining.remove(closest)
        processed.append(closest)
        direction = 1 if not [r for r in remaining if r >= head] else -1

    return sequence, total_seek, seek_times

# Calculate additional metrics
def calculate_metrics(total_seek, seek_times, num_requests):
    avg_seek = total_seek / num_requests if num_requests > 0 else 0
    throughput = num_requests / (total_seek + 1)
    variance = statistics.variance(seek_times) if len(seek_times) > 1 else 0
    return total_seek, avg_seek, throughput, variance

# GUI Class for Interactive Disk Scheduling Simulation
class DiskSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Scheduling Simulator")
        self.root.geometry("1400x1000")
        self.anim_speed = 0.0025
        self.schedulers = {
            "FCFS": fcfs_scheduler,
            "SSTF": sstf_scheduler,
            "SCAN": scan_scheduler,
            "C-SCAN": cscan_scheduler,
            "LOOK": look_scheduler
        }
        self.colors = {
            "FCFS": "#e74c3c",
            "SSTF": "#3498db",
            "SCAN": "#2ecc71",
            "C-SCAN": "#f1c40f",
            "LOOK": "#e67e22"
        }
        self.request_objects = {}
        self.trail_objects = []
        self.setup_ui()

    def setup_ui(self):
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12), padding=8)
        self.style.configure("TLabel", font=("Arial", 12), background="#2c3e50", foreground="#ecf0f1")
        self.style.configure("TEntry", font=("Arial", 12))

        # Main canvas with scrollbar
        self.main_canvas = tk.Canvas(self.root, bg="#2c3e50", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)

        # Gradient background
        for i in range(1000):
            color = f"#{(0x34 + (0x2c - 0x34) * i // 1000):02x}{(0x49 + (0x3e - 0x49) * i // 1000):02x}{(0x5e + (0x50 - 0x5e) * i // 1000):02x}"
            self.main_canvas.create_line(0, i, 1400, i, fill=color)

        # Scrollable frame
        self.scrollable_frame = tk.Frame(self.main_canvas, bg="#2c3e50")
        self.main_canvas.create_window(700, 550, window=self.scrollable_frame, anchor="center")
        self.main_canvas.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.scrollable_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        # Title with increased top padding
        title_frame = tk.Frame(self.scrollable_frame, bg="#2c3e50")
        title_frame.pack(fill="x", pady=(80, 10))
        tk.Label(
            title_frame,
            text="Disk Scheduling Simulator",
            font=("Arial", 26, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(padx=20)

        # Input frame
        input_frame = ttk.Frame(self.scrollable_frame, padding=10, relief="flat")
        input_frame.pack(fill="x", padx=15, pady=8)

        ttk.Label(input_frame, text="Requests (e.g., 98, 183, 37):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.requests_entry = ttk.Entry(input_frame, width=50)
        self.requests_entry.grid(row=0, column=1, padx=10, pady=5)
        self.requests_entry.insert(0, "98, 183, 37, 122, 14, 124, 65, 67")

        ttk.Label(input_frame, text="Initial Head (0 to Max Cylinders-1):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.head_entry = ttk.Entry(input_frame, width=10)
        self.head_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.head_entry.insert(0, "53")

        ttk.Label(input_frame, text="Max Cylinders (100-1000):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.max_cyl_entry = ttk.Entry(input_frame, width=10)
        self.max_cyl_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.max_cyl_entry.insert(0, "200")

        ttk.Label(input_frame, text="Animation Speed:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.speed_scale = ttk.Scale(input_frame, from_=0.00125, to=0.0125, orient="horizontal", command=self.update_speed)
        self.speed_scale.set(self.anim_speed)
        self.speed_scale.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Buttons
        btn_frame = tk.Frame(self.scrollable_frame, bg="#2c3e50")
        btn_frame.pack(pady=8)
        run_btn = ttk.Button(btn_frame, text="Run Simulation", command=self.run)
        run_btn.pack(side="left", padx=10)
        reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset)
        reset_btn.pack(side="left", padx=10)
        random_btn = ttk.Button(btn_frame, text="Random Requests", command=self.generate_random)
        random_btn.pack(side="left", padx=10)

        # Animation canvas (2D graph-like representation)
        self.anim_canvas = tk.Canvas(self.scrollable_frame, bg="white", height=400, width=600, bd=2, relief="sunken")
        self.anim_canvas.pack(pady=8)
        self.canvas_x_min = 50  # Left margin
        self.canvas_x_max = 550  # Right margin
        self.canvas_y_min = 50  # Bottom margin
        self.canvas_y_max = 350  # Top margin
        # Draw axes
        self.anim_canvas.create_line(self.canvas_x_min, self.canvas_y_max, self.canvas_x_max, self.canvas_y_max, fill="black", width=2)  # X-axis
        self.anim_canvas.create_line(self.canvas_x_min, self.canvas_y_max, self.canvas_x_min, self.canvas_y_min, fill="black", width=2)  # Y-axis
        # Draw head icon (small circle)
        self.head_icon = self.anim_canvas.create_oval(
            self.canvas_x_min - 5, self.canvas_y_max - 5,
            self.canvas_x_min + 5, self.canvas_y_max + 5,
            fill="#f1c40f"
        )
        # Draw direction arrow (initially hidden)
        self.head_arrow = self.anim_canvas.create_line(
            self.canvas_x_min, self.canvas_y_max,
            self.canvas_x_min, self.canvas_y_max,
            fill="#f1c40f", arrow=tk.LAST, arrowshape=(10, 12, 5), width=2
        )
        self.head_text = self.anim_canvas.create_text(
            self.canvas_x_min, self.canvas_y_max - 20,
            text="", font=("Arial", 10, "bold")
        )

        # Results frame
        self.result_frame = ttk.Frame(self.scrollable_frame, padding=10, relief="flat")
        self.result_frame.pack(fill="x", padx=15, pady=8)
        self.result_labels = {}
        for i, scheduler in enumerate(self.schedulers):
            label = ttk.Label(self.result_frame, text=f"{scheduler}: Waiting...", font=("Arial", 11))
            label.grid(row=i, column=0, sticky="w", pady=3)
            self.result_labels[scheduler] = label

        # Best algorithm label
        self.best_label = ttk.Label(self.result_frame, text="Best Algorithm: None", font=("Arial", 11, "bold"))
        self.best_label.grid(row=len(self.schedulers), column=0, sticky="w", pady=5)

        # Graph
        self.fig, self.ax = plt.subplots(figsize=(12, 3.5))
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.2)
        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=self.scrollable_frame)
        self.graph_widget = self.graph_canvas.get_tk_widget()
        self.graph_widget.pack(pady=8, padx=15)

        # Enable mouse wheel scrolling
        def on_mouse_wheel(event):
            self.main_canvas.yview_scroll(-1 * (event.delta // 120), "units")
        self.main_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    def update_speed(self, value):
        self.anim_speed = float(value)

    def generate_random(self):
        try:
            max_cylinders = int(self.max_cyl_entry.get())
            if not 100 <= max_cylinders <= 1000:
                raise ValueError("Max cylinders must be between 100 and 1000!")
            num_requests = random.randint(5, 10)
            requests = random.sample(range(max_cylinders), num_requests)
            self.requests_entry.delete(0, tk.END)
            self.requests_entry.insert(0, ", ".join(map(str, requests)))
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def run(self):
        try:
            # Read and validate max cylinders
            max_cylinders = int(self.max_cyl_entry.get())
            if not 100 <= max_cylinders <= 1000:
                raise ValueError("Max cylinders must be between 100 and 1000!")
            self.max_cylinders = max_cylinders

            requests = [int(x.strip()) for x in self.requests_entry.get().split(',')]
            head = int(self.head_entry.get())
            if not all(0 <= r < self.max_cylinders for r in requests) or not 0 <= head < self.max_cylinders:
                raise ValueError(f"Values must be between 0 and {self.max_cylinders-1}!")

            # Clear previous canvas elements
            self.anim_canvas.delete("grid")
            self.anim_canvas.delete("label")
            self.anim_canvas.delete("request")
            self.anim_canvas.delete("trail")
            self.trail_objects = []

            # Draw grid and labels
            x_scale = (self.canvas_x_max - self.canvas_x_min) / self.max_cylinders
            step = max(self.max_cylinders // 5, 50)  # At least 5 grid lines
            for i in range(0, self.max_cylinders + 1, step):
                x = self.canvas_x_min + i * x_scale
                self.anim_canvas.create_line(x, self.canvas_y_max, x, self.canvas_y_min, fill="gray", dash=(2, 2), tags="grid")
                self.anim_canvas.create_text(x, self.canvas_y_max + 10, text=str(i), font=("Arial", 8), tags="label")
            # Y-axis labels (sequence steps, approximate)
            y_scale = (self.canvas_y_max - self.canvas_y_min) / (len(requests) + 1)
            for i in range(len(requests) + 2):
                y = self.canvas_y_max - i * y_scale
                self.anim_canvas.create_line(self.canvas_x_min, y, self.canvas_x_max, y, fill="gray", dash=(2, 2), tags="grid")
                self.anim_canvas.create_text(self.canvas_x_min - 20, y, text=str(i), font=("Arial", 8), tags="label")

            # Place request markers on the 2D canvas (at y=bottom initially)
            for req in requests:
                x = self.canvas_x_min + req * x_scale
                y = self.canvas_y_max  # Start at bottom (sequence step 0)
                obj_id = self.anim_canvas.create_oval(
                    x - 5, y - 5, x + 5, y + 5, fill="#3498db", tags="request"
                )
                self.request_objects[req] = obj_id

            results = {}
            for name, scheduler in self.schedulers.items():
                # Clear trails from previous algorithm
                self.anim_canvas.delete("trail")
                self.trail_objects = []
                seq, seek, times = scheduler(requests, head, self.max_cylinders)
                metrics = calculate_metrics(seek, times, len(requests))
                results[name] = {"seq": seq, "seek": seek, "times": times, "metrics": metrics}
                self.animate(seq, name)
                self.result_labels[name].config(
                    text=f"{name}: Total Seek={metrics[0]:.0f}, Avg Seek={metrics[1]:.2f}, "
                         f"Throughput={metrics[2]:.3f}, Variance={metrics[3]:.2f}"
                )

            best_algo = min(results.items(), key=lambda x: x[1]["seek"])[0]
            self.best_label.config(text=f"Best Algorithm: {best_algo}")

            self.plot(results)

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def animate(self, sequence, name):
        self.anim_canvas.itemconfig(self.head_icon, fill=self.colors[name])
        self.anim_canvas.itemconfig(self.head_arrow, fill=self.colors[name])
        serviced = set()
        x_scale = (self.canvas_x_max - self.canvas_x_min) / self.max_cylinders
        y_scale = (self.canvas_y_max - self.canvas_y_min) / (len(sequence) - 1) if len(sequence) > 1 else 1
        prev_x = self.canvas_x_min + sequence[0] * x_scale
        prev_y = self.canvas_y_max
        for i, pos in enumerate(sequence[1:], 1):
            x = self.canvas_x_min + pos * x_scale
            y = self.canvas_y_max - i * y_scale  # Move up as sequence progresses
            # Animate movement
            steps = max(int(abs(x - prev_x) / 2 + abs(y - prev_y) / 2), 1)
            for step in range(steps + 1):
                interp = step / steps
                current_x = prev_x + (x - prev_x) * interp
                current_y = prev_y + (y - prev_y) * interp
                # Draw trail (keep all segments)
                if step > 0:
                    trail_x1 = prev_x + (x - prev_x) * (step-1)/steps
                    trail_y1 = prev_y + (y - prev_y) * (step-1)/steps
                    trail_x2 = current_x
                    trail_y2 = current_y
                    trail_id = self.anim_canvas.create_line(
                        trail_x1, trail_y1, trail_x2, trail_y2,
                        fill=self.colors[name], width=2, tags="trail"
                    )
                    self.trail_objects.append(trail_id)
                # Move head
                self.anim_canvas.coords(self.head_icon,
                                       current_x - 5, current_y - 5,
                                       current_x + 5, current_y + 5)
                self.anim_canvas.coords(self.head_text,
                                       current_x, current_y - 20)
                self.anim_canvas.itemconfig(self.head_text, text=f"{pos} ({name})")
                # Update arrow direction
                if step < steps:  # Don't show arrow on final step
                    next_x = prev_x + (x - prev_x) * (step+1)/steps
                    next_y = prev_y + (y - prev_y) * (step+1)/steps
                    dx = next_x - current_x
                    dy = next_y - current_y
                    length = math.sqrt(dx**2 + dy**2)
                    if length > 0:
                        arrow_length = min(20, length)  # Cap arrow length at 20 pixels
                        dx = (dx / length) * arrow_length
                        dy = (dy / length) * arrow_length
                        self.anim_canvas.coords(self.head_arrow,
                                               current_x, current_y,
                                               current_x + dx, current_y + dy)
                    else:
                        self.anim_canvas.coords(self.head_arrow,
                                               current_x, current_y,
                                               current_x, current_y)
                else:
                    self.anim_canvas.coords(self.head_arrow,
                                           current_x, current_y,
                                           current_x, current_y)
                self.root.update()
                time.sleep(self.anim_speed)
            # Mark request as serviced
            if pos in self.request_objects and pos not in serviced:
                self.anim_canvas.itemconfig(self.request_objects[pos], fill="gray")
                serviced.add(pos)
            prev_x = x
            prev_y = y
        self.anim_canvas.itemconfig(self.head_text, text="")
        self.anim_canvas.coords(self.head_arrow,
                               self.canvas_x_min, self.canvas_y_max,
                               self.canvas_x_min, self.canvas_y_max)
        time.sleep(0.5)

    def plot(self, results):
        self.ax.clear()
        max_steps = max(len(data["times"]) for data in results.values())
        steps = list(range(max_steps))
        for name, data in results.items():
            times = data["times"] + [0] * (max_steps - len(data["times"]))
            self.ax.plot(
                steps,
                times,
                label=name,
                color=self.colors[name],
                marker="o",
                linewidth=2
            )

        self.ax.set_xlabel("Request Number")
        self.ax.set_ylabel("Seek Time")
        self.ax.set_title("Seek Time Comparison")
        self.ax.legend()
        self.ax.grid(True, linestyle="--", alpha=0.7)
        self.graph_canvas.draw()

    def reset(self):
        self.requests_entry.delete(0, tk.END)
        self.requests_entry.insert(0, "98, 183, 37, 122, 14, 124, 65, 67")
        self.head_entry.delete(0, tk.END)
        self.head_entry.insert(0, "53")
        self.max_cyl_entry.delete(0, tk.END)
        self.max_cyl_entry.insert(0, "200")
        self.speed_scale.set(0.0025)
        self.anim_speed = 0.0025
        for label in self.result_labels.values():
            label.config(text=f"{label.cget('text').split(':')[0]}: Waiting...")
        self.best_label.config(text="Best Algorithm: None")
        # Reset head to bottom-left
        self.anim_canvas.coords(self.head_icon,
                               self.canvas_x_min - 5, self.canvas_y_max - 5,
                               self.canvas_x_min + 5, self.canvas_y_max + 5)
        # Hide arrow
        self.anim_canvas.coords(self.head_arrow,
                               self.canvas_x_min, self.canvas_y_max,
                               self.canvas_x_min, self.canvas_y_max)
        self.anim_canvas.delete("grid")
        self.anim_canvas.delete("label")
        self.anim_canvas.delete("request")
        self.anim_canvas.delete("trail")
        self.trail_objects = []
        self.anim_canvas.itemconfig(self.head_text, text="")
        self.anim_canvas.itemconfig(self.head_icon, fill="#f1c40f")
        self.anim_canvas.itemconfig(self.head_arrow, fill="#f1c40f")
        self.request_objects = {}
        self.ax.clear()
        self.graph_canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = DiskSchedulerGUI(root)
    root.mainloop()