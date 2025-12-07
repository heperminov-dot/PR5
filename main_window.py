import tkinter
from tkinter import messagebox, filedialog
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

GROUP = "526"         # <- замініть на свій номер групи
SURNAME = "PERMINOV"    # <- замініть на своє прізвище
NAME = "HERMAN"         # <- замініть на своє ім'я
APP_TITLE = f"lab5_{GROUP}-v10-{SURNAME}-{NAME}"

def fib(n: int) -> int:
    """
    Обчислити n-ий член послідовності Фібоначчі (F1=1, F2=1).
    Параметр n — позитивне ціле.
    Повертає ціле число.
    """
    if n <= 0:
        raise ValueError("N must be positive integer")
    if n == 1 or n == 2:
        return 1
    a, b = 1, 1
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b


def fib_list(ns):
    """Повертає список значень Fib(n) для списку індексів ns."""
    res = []
    for n in ns:
        res.append(fib(n))
    return res

def compute_recurrence_variant10(N_points: int = 200, T: float = 0.2, K: float = 3.0, U0: float = 2.0):
    """
    Обчислити масив y[k] по рекурентній формулі варіанту 10.
    Повертає numpy масиви (t, y, u), де t = k*T0, T0 = 2*T / N_points
    """
    if N_points < 2:
        raise ValueError("N_points must be >= 2")

    T0 = 2.0 * T / N_points
    t = np.array([k * T0 for k in range(N_points + 1)])  # 0..N
    u = np.full_like(t, fill_value=U0, dtype=float)  # U[k] = U0 constant (можна змінити)
    y = np.zeros_like(t, dtype=float)
    y[0] = 0.0
    coeff = T0 / T
    one_minus = 1.0 - coeff
    for k in range(1, len(t)):
        y[k] = one_minus * y[k - 1] + coeff * K * u[k - 1]  # note u[k-1] or u[k] - вибір моделі; використаємо u[k-1]
    return t, y, u


def save_xy_to_file(t, y, filename, sep='#'):
    """Зберегти пари (t, y) у файл з заданим роздільником"""
    with open(filename, 'w', encoding='utf-8') as f:
        for ti, yi in zip(t, y):
            f.write(f"{ti}{sep}{yi}\n")


def read_xy_from_file(filename, sep='#'):
    """Зчитати файл у форматі 'x{sep}y' -> повернути списки x,y.
       Генерує ValueError при некоректному форматі."""
    xs = []
    ys = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(sep)
            if len(parts) != 2:
                raise ValueError("Wrong file format: each line must contain exactly one separator")
            xs.append(float(parts[0]))
            ys.append(float(parts[1]))
    return np.array(xs), np.array(ys)

class MainWindow(tkinter.Frame):
    """Main GUI window with widgets for Task1 (Fibonacci) and Task2 (recurrence variant 10)."""

    def __init__(self, parent):
        super(MainWindow, self).__init__(parent)
        self.parent = parent
        parent.title(APP_TITLE)
        self.pack(fill=tkinter.BOTH, expand=1)

        for r in range(6):
            self.grid_rowconfigure(r, weight=1)
        for c in range(4):
            self.grid_columnconfigure(c, weight=1)

        self.task1_label = tkinter.Label(self, text="Task1 (Func21): Введіть 5 індексів N (цілі >0), через пробіл:")
        self.task1_label.grid(row=0, column=0, columnspan=3, sticky=tkinter.W + tkinter.E, padx=5, pady=3)

        self.task1_entry = tkinter.Entry(self)
        self.task1_entry.grid(row=0, column=3, sticky=tkinter.EW, padx=5, pady=3)

        self.task1_button = tkinter.Button(self, text="Обчислити Fib(N)", command=self.on_task1_compute)
        self.task1_button.grid(row=1, column=3, sticky=tkinter.NSEW, padx=5, pady=3)

        self.task1_result_var = tkinter.StringVar()
        self.task1_result_label = tkinter.Label(self, textvariable=self.task1_result_var, anchor='w', justify='left')
        self.task1_result_label.grid(row=1, column=0, columnspan=3, sticky=tkinter.W + tkinter.E, padx=5, pady=3)

        self.task2_label = tkinter.Label(self, text="Task2 (Variant 10): Параметри генерації файлу і побудови графіка")
        self.task2_label.grid(row=2, column=0, columnspan=4, sticky=tkinter.W + tkinter.E, padx=5, pady=3)

        self.n_label = tkinter.Label(self, text="Кількість точок (N):")
        self.n_label.grid(row=3, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=3)
        self.n_entry = tkinter.Entry(self)
        self.n_entry.insert(0, "200")
        self.n_entry.grid(row=3, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=3)

        self.generate_button = tkinter.Button(self, text="Створити файл (generate)", command=self.on_generate_file)
        self.generate_button.grid(row=3, column=2, sticky=tkinter.NSEW, padx=5, pady=3)

        self.open_button = tkinter.Button(self, text="Відкрити файл", command=self.on_open_file)
        self.open_button.grid(row=3, column=3, sticky=tkinter.NSEW, padx=5, pady=3)

        self.show_stats_button = tkinter.Button(self, text="Показати min/max", command=self.on_show_stats)
        self.show_stats_button.grid(row=4, column=2, sticky=tkinter.NSEW, padx=5, pady=3)

        self.plot_button = tkinter.Button(self, text="Побудувати графік", command=self.on_plot)
        self.plot_button.grid(row=4, column=3, sticky=tkinter.NSEW, padx=5, pady=3)

        self.task2_info_var = tkinter.StringVar()
        self.task2_info_var.set("Файл: (не вибрано)")
        self.task2_info_label = tkinter.Label(self, textvariable=self.task2_info_var, anchor='w', justify='left')
        self.task2_info_label.grid(row=4, column=0, columnspan=2, sticky=tkinter.W + tkinter.E, padx=5, pady=3)

        self.canvas = None
        self.current_x = None
        self.current_y = None
        self.current_filename = None

    def on_task1_compute(self):
        """Обробник для Task1: зчитати 5 N, обчислити Fib і показати."""
        s = self.task1_entry.get().strip()
        if not s:
            messagebox.showerror("Data ERROR", "Введіть 5 індексів N через пропуск")
            return
        try:
            parts = s.split()
            nums = [int(p) for p in parts]
            if len(nums) != 5:
                raise ValueError("Потрібно введи 5 чисел")
            if any(n <= 0 for n in nums):
                raise ValueError("Індекси повинні бути додатні")
        except Exception as e:
            messagebox.showerror("Data ERROR", f"Неправильне введення: {e}")
            return

        # обчислення
        try:
            fibs = fib_list(nums)
        except Exception as e:
            messagebox.showerror("Compute ERROR", f"Помилка обчислення: {e}")
            return

        # показати результат
        result_str = " | ".join([f"N={n} -> Fib={f}" for n, f in zip(nums, fibs)])
        self.task1_result_var.set(result_str)

    def on_generate_file(self):
        """Згенерувати масив по рекурентній формулі і зберегти у файл (роздільник '#')."""
        try:
            N = int(self.n_entry.get())
            if N < 2:
                raise ValueError("N must be >= 2")
        except Exception as e:
            messagebox.showerror("Data ERROR", f"Неправильний N: {e}")
            return

        t, y, u = compute_recurrence_variant10(N_points=N, T=0.2, K=3.0, U0=2.0)

        fpath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not fpath:
            return
        try:
            save_xy_to_file(t, y, fpath, sep='#')
        except Exception as e:
            messagebox.showerror("File ERROR", f"Не вдалося записати файл: {e}")
            return

        self.current_filename = fpath
        self.current_x = t
        self.current_y = y
        self.task2_info_var.set(f"Файл: {fpath} (згенеровано)")
        messagebox.showinfo("Success", f"Файл згенеровано: {fpath}")

    def on_open_file(self):
        """Відкрити файл з даними (передбачається роздільник '#') і зберегти масиви."""
        fpath = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not fpath:
            return
        try:
            x, y = read_xy_from_file(fpath, sep='#')
        except Exception as e:
            messagebox.showerror("File ERROR", f"Не вдалося прочитати файл: {e}")
            return
        self.current_filename = fpath
        self.current_x = x
        self.current_y = y
        self.task2_info_var.set(f"Файл: {fpath} (завантажено)")
        messagebox.showinfo("Success", f"Файл завантажено: {fpath}")

    def on_show_stats(self):
        """Показати min/max для x і y у поточних масивах."""
        if self.current_x is None or self.current_y is None:
            messagebox.showwarning("No data", "Спочатку завантажте або згенеруйте файл")
            return
        try:
            min_x = float(np.min(self.current_x))
            max_x = float(np.max(self.current_x))
            min_y = float(np.min(self.current_y))
            max_y = float(np.max(self.current_y))
        except Exception as e:
            messagebox.showerror("Compute ERROR", f"Помилка при підрахунку: {e}")
            return
        messagebox.showinfo("Min/Max", f"x: min={min_x}, max={max_x}\ny: min={min_y}, max={max_y}")

    def on_plot(self):
        """Побудувати графік у вікні (matplotlib canvas)."""
        if self.current_x is None or self.current_y is None:
            messagebox.showwarning("No data", "Спочатку завантажте або згенеруйте файл")
            return

        try:
            fig = Figure(figsize=(6, 4))
            ax = fig.add_subplot(111)
            ax.plot(self.current_x, self.current_y)
            ax.set_title("Variant 10: y[k] (recurrence)")
            ax.set_xlabel("t (s)")
            ax.set_ylabel("y")
            ax.grid(True)
            min_i = int(np.argmin(self.current_y))
            max_i = int(np.argmax(self.current_y))
            ax.plot(self.current_x[min_i], self.current_y[min_i], marker='o')
            ax.text(self.current_x[min_i], self.current_y[min_i], f" min={self.current_y[min_i]:.3g}")
            ax.plot(self.current_x[max_i], self.current_y[max_i], marker='o')
            ax.text(self.current_x[max_i], self.current_y[max_i], f" max={self.current_y[max_i]:.3g}")

            if self.canvas is not None:
                try:
                    self.canvas.get_tk_widget().destroy()
                except Exception:
                    pass

            self.canvas = FigureCanvasTkAgg(fig, master=self)
            self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=4, sticky=tkinter.NSEW, padx=5, pady=5)
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Plot ERROR", f"Помилка побудови графіка: {e}")
            return


if __name__ == "__main__":
    app = tkinter.Tk()
    window = MainWindow(app)
    app.mainloop()
