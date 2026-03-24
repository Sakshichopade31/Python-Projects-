import customtkinter as ctk
from datetime import datetime
import sqlite3

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ExpenseTracker:

    def __init__(self):

        self.win = ctk.CTk()
        self.win.title("💰 Expense Tracker PRO")
        self.win.geometry("1000x600")

        self.init_db()
        self.ui()

    # ---------------- DATABASE ----------------

    def init_db(self):

        self.conn = sqlite3.connect("expenses.db")
        self.cur = self.conn.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            description TEXT,
            amount REAL
        )
        """)

        self.conn.commit()

    # ---------------- UI ----------------

    def ui(self):

        self.win.grid_columnconfigure(1, weight=1)
        self.win.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.side = ctk.CTkFrame(self.win, width=220)
        self.side.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            self.side,
            text="📊 Expense Tracker",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)

        add_frame = ctk.CTkFrame(self.side)
        add_frame.pack(padx=20, pady=20, fill="x")

        ctk.CTkLabel(add_frame, text="Add Expense").pack(pady=10)

        self.date = ctk.CTkEntry(add_frame)
        self.date.pack(pady=5)
        self.date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.cat = ctk.CTkComboBox(
            add_frame,
            values=["Food","Transport","Shopping","Entertainment","Bills","Other"]
        )
        self.cat.pack(pady=5)
        self.cat.set("Food")

        self.desc = ctk.CTkEntry(add_frame, placeholder_text="Description")
        self.desc.pack(pady=5)

        self.amt = ctk.CTkEntry(add_frame, placeholder_text="Amount")
        self.amt.pack(pady=5)

        ctk.CTkButton(
            add_frame,
            text="➕ Add Expense",
            command=self.add_expense
        ).pack(pady=10)

        # Main area
        self.main = ctk.CTkFrame(self.win)
        self.main.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.create_table()
        self.create_summary()

        self.refresh()

    # ---------------- TABLE ----------------

    def create_table(self):

        frame = ctk.CTkFrame(self.main)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.scroll = ctk.CTkScrollableFrame(frame, label_text="Recent Expenses")
        self.scroll.pack(fill="both", expand=True)

        headers = ["Date","Category","Description","Amount","Delete"]

        for i,h in enumerate(headers):

            ctk.CTkLabel(
                self.scroll,
                text=h,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0,column=i,padx=10,pady=5)

    # ---------------- SUMMARY ----------------

    def create_summary(self):

        frame = ctk.CTkFrame(self.main)
        frame.pack(fill="x", padx=10, pady=10)

        self.total_label = ctk.CTkLabel(
            frame,
            text="Total: ₹0",
            font=ctk.CTkFont(size=18, weight="bold")
        )

        self.total_label.pack(side="left", padx=20)

        self.avg_label = ctk.CTkLabel(
            frame,
            text="Average: ₹0"
        )

        self.avg_label.pack(side="left", padx=20)

    # ---------------- ADD ----------------

    def add_expense(self):

        try:

            date = self.date.get()
            cat = self.cat.get()
            desc = self.desc.get()
            amt = float(self.amt.get())

            self.cur.execute(
                "INSERT INTO expenses(date,category,description,amount) VALUES(?,?,?,?)",
                (date,cat,desc,amt)
            )

            self.conn.commit()

            self.desc.delete(0,"end")
            self.amt.delete(0,"end")

            self.refresh()

        except:
            pass

    # ---------------- REFRESH ----------------

    def refresh(self):

        for w in self.scroll.winfo_children():
            if int(w.grid_info()["row"]) > 0:
                w.destroy()

        self.cur.execute("SELECT * FROM expenses ORDER BY id DESC LIMIT 10")

        rows = self.cur.fetchall()

        total = 0

        for i,row in enumerate(rows,start=1):

            ctk.CTkLabel(self.scroll,text=row[1]).grid(row=i,column=0,padx=10,pady=2)
            ctk.CTkLabel(self.scroll,text=row[2]).grid(row=i,column=1,padx=10,pady=2)
            ctk.CTkLabel(self.scroll,text=row[3]).grid(row=i,column=2,padx=10,pady=2)
            ctk.CTkLabel(self.scroll,text=f"₹{row[4]:.2f}").grid(row=i,column=3,padx=10,pady=2)

            ctk.CTkButton(
                self.scroll,
                text="🗑",
                width=30,
                command=lambda r=row[0]: self.delete_expense(r)
            ).grid(row=i,column=4,padx=5)

            total += row[4]

        self.total_label.configure(text=f"Total: ₹{total:.2f}")

        avg = total/len(rows) if rows else 0

        self.avg_label.configure(text=f"Average: ₹{avg:.2f}")

    # ---------------- DELETE ----------------

    def delete_expense(self,id):

        self.cur.execute("DELETE FROM expenses WHERE id=?", (id,))
        self.conn.commit()

        self.refresh()

    # ---------------- RUN ----------------

    def run(self):
        self.win.mainloop()


if __name__ == "__main__":

    app = ExpenseTracker()
    app.run()