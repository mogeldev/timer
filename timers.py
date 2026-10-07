import time
import tkinter as tk


def parse_duration(text):
    """Accepts '90', '1:30' or '1:30:00' -> seconds."""
    parts = [int(p) for p in text.strip().split(":")]
    if len(parts) == 1:
        return parts[0] * 60  # plain number = minutes
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    raise ValueError("invalid duration")


def fmt(seconds):
    seconds = max(0, int(seconds + 0.5))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


class TimerRow:
    def __init__(self, parent, root, name, duration, on_delete):
        self.root = root
        self.duration = duration
        self.remaining = float(duration)
        self.running = False
        self.start_time = 0.0
        self.finished = False
        self.flash_state = False
        self.on_delete = on_delete

        self.frame = tk.Frame(parent)
        self.frame.pack(fill="x", padx=6, pady=2)

        self.name_label = tk.Label(self.frame, text=name, width=12, anchor="w")
        self.name_label.pack(side="left")
        self.time_label = tk.Label(self.frame, text=fmt(duration), width=9, font=("Consolas", 11))
        self.time_label.pack(side="left")
        self.toggle_btn = tk.Button(self.frame, text="Start", width=6, command=self.toggle)
        self.toggle_btn.pack(side="left", padx=2)
        tk.Button(self.frame, text="Reset", width=6, command=self.reset).pack(side="left", padx=2)
        tk.Button(self.frame, text="X", width=2, command=self.delete).pack(side="left", padx=2)

    def toggle(self):
        if self.finished:
            self.reset()
            return
        if self.running:
            self.remaining -= time.monotonic() - self.start_time
            self.running = False
            self.toggle_btn.config(text="Start")
        else:
            if self.remaining <= 0:
                return
            self.start_time = time.monotonic()
            self.running = True
            self.toggle_btn.config(text="Pause")

    def reset(self):
        self.remaining = float(self.duration)
        self.running = False
        self.finished = False
        self.toggle_btn.config(text="Start")
        self.set_color("SystemButtonFace", "black")
        self.time_label.config(text=fmt(self.duration))

    def delete(self):
        self.frame.destroy()
        self.on_delete(self)

    def set_color(self, bg, fg):
        for w in (self.frame, self.name_label, self.time_label):
            w.config(bg=bg)
        self.time_label.config(fg=fg)
        self.name_label.config(fg=fg)

    def update(self):
        if self.running:
            left = self.remaining - (time.monotonic() - self.start_time)
            if left <= 0:
                self.running = False
                self.remaining = 0.0
                self.finished = True
                self.toggle_btn.config(text="Start")
                self.root.bell()
            self.time_label.config(text=fmt(left))
        elif self.finished:
            # flash red
            self.flash_state = not self.flash_state
            if self.flash_state:
                self.set_color("red", "white")
            else:
                self.set_color("SystemButtonFace", "black")
            self.time_label.config(text="00:00:00")


class App:
    def __init__(self, root):
        self.root = root
        root.title("Timers")
        root.attributes("-topmost", True)
        root.resizable(False, False)

        self.timers = []

        add_frame = tk.Frame(root)
        add_frame.pack(fill="x", padx=6, pady=6)
        tk.Label(add_frame, text="Name:").pack(side="left")
        self.name_entry = tk.Entry(add_frame, width=10)
        self.name_entry.pack(side="left", padx=2)
        tk.Label(add_frame, text="Dauer:").pack(side="left")
        self.dur_entry = tk.Entry(add_frame, width=8)
        self.dur_entry.pack(side="left", padx=2)
        self.dur_entry.insert(0, "5:00")
        tk.Button(add_frame, text="+ Add", command=self.add_timer).pack(side="left", padx=4)
        self.dur_entry.bind("<Return>", lambda e: self.add_timer())
        self.name_entry.bind("<Return>", lambda e: self.add_timer())

        self.list_frame = tk.Frame(root)
        self.list_frame.pack(fill="both", expand=True)

        self.tick()

    def add_timer(self):
        name = self.name_entry.get().strip() or f"Timer {len(self.timers) + 1}"
        try:
            duration = parse_duration(self.dur_entry.get())
            if duration <= 0:
                raise ValueError
        except ValueError:
            self.dur_entry.config(bg="red")
            self.root.after(800, lambda: self.dur_entry.config(bg="white"))
            return
        self.name_entry.delete(0, "end")
        self.timers.append(TimerRow(self.list_frame, self.root, name, duration, self.remove_timer))

    def remove_timer(self, row):
        self.timers.remove(row)

    def tick(self):
        for t in self.timers:
            t.update()
        self.root.after(250, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
