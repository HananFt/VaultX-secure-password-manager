import customtkinter as ctk
from tkinter import messagebox
import pyperclip
from manager import create_vault, unlock_vault, add_entry, get_entries, get_security_health, calculate_password_strength
from hibp import check_password_breach
from vault import vault_exists

# Set global appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class VaultXApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VaultX - Secure Password Manager")
        self.geometry("950x650")
        self.minsize(850, 550)
        
        self.vault_key = None
        self.vault_data = None
        
        self._build_login_screen()

    def _clear_screen(self):
        """Destroys all widgets to prepare for a new screen."""
        for widget in self.winfo_children():
            widget.destroy()

    def _build_login_screen(self):
        self._clear_screen()
        frame = ctk.CTkFrame(self, width=400, height=350, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(frame, text="🔒 VaultX", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(25, 5))
        ctk.CTkLabel(frame, text="Your local, secure password vault", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 20))
        
        if vault_exists():
            ctk.CTkLabel(frame, text="Enter Master Password", font=ctk.CTkFont(size=14)).pack(pady=5)
            self.pwd_entry = ctk.CTkEntry(frame, placeholder_text="Master Password", show="*", width=280, height=35)
            self.pwd_entry.pack(pady=10)
            self.pwd_entry.bind("<Return>", lambda e: self._attempt_unlock())
            self.pwd_entry.focus()
            
            ctk.CTkButton(frame, text="Unlock Vault", command=self._attempt_unlock, width=280, height=35).pack(pady=10)
        else:
            ctk.CTkLabel(frame, text="Welcome! Let's create your vault.", font=ctk.CTkFont(size=14)).pack(pady=5)
            ctk.CTkLabel(frame, text="Set Master Password", font=ctk.CTkFont(size=12)).pack(pady=(15,0))
            self.pwd_entry = ctk.CTkEntry(frame, placeholder_text="Master Password", show="*", width=280, height=35)
            self.pwd_entry.pack(pady=5)
            self.pwd_entry.bind("<KeyRelease>", self._update_strength_meter)
            
            self.strength_bar = ctk.CTkProgressBar(frame, width=280, mode="determinate")
            self.strength_bar.pack(pady=8)
            self.strength_bar.set(0)
            self.strength_label = ctk.CTkLabel(frame, text="Strength: None", font=ctk.CTkFont(size=11))
            self.strength_label.pack()
            
            ctk.CTkButton(frame, text="Create Vault", command=self._attempt_create, width=280, height=35).pack(pady=20)

    def _update_strength_meter(self, event=None):
        pwd = self.pwd_entry.get()
        score = calculate_password_strength(pwd)
        self.strength_bar.set(score / 4.0)
        colors = ["#FF4136", "#FF851B", "#FFDC00", "#2ECC40", "#0074D9"]
        self.strength_bar.configure(progress_color=colors[score])
        labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]
        self.strength_label.configure(text=f"Strength: {labels[score]}")

    def _attempt_create(self):
        pwd = self.pwd_entry.get()
        if len(pwd) < 8:
            messagebox.showerror("Error", "Master password must be at least 8 characters.")
            return
            
        try:
            self.vault_key, self.vault_data, self.recovery_codes = create_vault(pwd)
            self._show_recovery_screen()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_recovery_screen(self):
        self._clear_screen()
        frame = ctk.CTkFrame(self, width=550, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(frame, text="⚠️ Save Your Recovery Codes", font=ctk.CTkFont(size=22, weight="bold"), text_color="#FF851B").pack(pady=(25, 10))
        ctk.CTkLabel(frame, text="If you forget your master password, these codes are the ONLY way to recover your vault.\nWrite them down on paper and store them in a safe place.", 
                     font=ctk.CTkFont(size=12), wraplength=450, justify="center", text_color="gray").pack(pady=5)
        
        codes_text = "\n".join(self.recovery_codes)
        self.codes_box = ctk.CTkTextbox(frame, width=450, height=150, font=ctk.CTkFont(size=16, family="Courier", weight="bold"))
        self.codes_box.pack(pady=20)
        self.codes_box.insert("1.0", codes_text)
        self.codes_box.configure(state="disabled")
        
        self.confirm_var = ctk.BooleanVar()
        ctk.CTkCheckBox(frame, text="I have securely saved these codes", variable=self.confirm_var, font=ctk.CTkFont(size=13)).pack(pady=10)
        
        self.continue_btn = ctk.CTkButton(frame, text="Continue to Dashboard", command=self._build_dashboard, state="disabled", width=250, height=35)
        self.continue_btn.pack(pady=15)
        self.confirm_var.trace_add("write", self._toggle_continue_btn)

    def _toggle_continue_btn(self, *args):
        if self.confirm_var.get():
            self.continue_btn.configure(state="normal")
        else:
            self.continue_btn.configure(state="disabled")

    def _attempt_unlock(self):
        pwd = self.pwd_entry.get()
        try:
            self.vault_key, self.vault_data = unlock_vault(pwd)
            self._build_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Invalid master password.")

    def _build_dashboard(self):
        self._clear_screen()
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        ctk.CTkLabel(sidebar, text="🔒 VaultX", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=25)
        
        ctk.CTkButton(sidebar, text="📊 Dashboard", command=lambda: self._show_page("dashboard"), anchor="w", height=35).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(sidebar, text="🔑 All Passwords", command=lambda: self._show_page("passwords"), anchor="w", height=35).pack(fill="x", padx=15, pady=5)
        
        ctk.CTkButton(sidebar, text="🔒 Lock Vault", command=self._build_login_screen, fg_color="transparent", text_color="gray", hover_color=("gray70", "gray30"), anchor="w", height=35).pack(side="bottom", fill="x", padx=15, pady=20)

        # Main Content Area
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True)
        
        self._show_page("dashboard")

    def _show_page(self, page_name):
        for widget in self.main_area.winfo_children():
            widget.destroy()
            
        if page_name == "dashboard":
            self._build_dashboard_page()
        elif page_name == "passwords":
            self._build_passwords_page()

    def _build_dashboard_page(self):
        header = ctk.CTkFrame(self.main_area, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))
        ctk.CTkLabel(header, text="Security Health", font=ctk.CTkFont(size=26, weight="bold")).pack(side="left")
        
        health = get_security_health(self.vault_key, self.vault_data)
        
        cards_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self._create_stat_card(cards_frame, "Total Passwords", health["total"], "#0074D9", 0, 0)
        self._create_stat_card(cards_frame, "Weak Passwords", health["weak"], "#FF4136", 0, 1)
        self._create_stat_card(cards_frame, "Reused Passwords", health["reused"], "#FF851B", 0, 2)
        
        score_color = "#2ECC40" if health["score"] > 70 else "#FFDC00" if health["score"] > 40 else "#FF4136"
        self._create_stat_card(cards_frame, "Security Score", f"{health['score']}%", score_color, 1, 0, colspan=3)

    def _create_stat_card(self, parent, title, value, color, row, col, colspan=1):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=row, column=col, columnspan=colspan, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14), text_color="gray").pack(pady=(20, 5))
        ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=36, weight="bold"), text_color=color).pack(pady=(0, 20))

    def _build_passwords_page(self):
        header = ctk.CTkFrame(self.main_area, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))
        ctk.CTkLabel(header, text="All Passwords", font=ctk.CTkFont(size=26, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="+ Add New", command=self._show_add_entry_modal, width=120, height=35).pack(side="right")
        
        self.list_frame = ctk.CTkScrollableFrame(self.main_area, corner_radius=10)
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        self._refresh_password_list()

    def _refresh_password_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        entries = get_entries(self.vault_key, self.vault_data)
        if not entries:
            ctk.CTkLabel(self.list_frame, text="No passwords saved yet. Click '+ Add New' to start.", text_color="gray", font=ctk.CTkFont(size=14)).pack(pady=60)
            return
            
        for entry in entries:
            row = ctk.CTkFrame(self.list_frame, corner_radius=10, height=60)
            row.pack(fill="x", pady=6)
            row.pack_propagate(False)
            
            ctk.CTkLabel(row, text=entry['service'], font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=20, pady=15)
            ctk.CTkLabel(row, text=entry['username'], font=ctk.CTkFont(size=12), text_color="gray").pack(side="left", padx=10)
            
            strength_colors = ["#FF4136", "#FF851B", "#FFDC00", "#2ECC40", "#0074D9"]
            ctk.CTkLabel(row, text="●", text_color=strength_colors[entry['strength']], font=ctk.CTkFont(size=24)).pack(side="right", padx=20)
            
            ctk.CTkButton(row, text="Copy", width=80, height=30, command=lambda p=entry['password']: self._copy_to_clipboard(p)).pack(side="right", padx=10)

    def _show_add_entry_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Add New Password")
        modal.geometry("400x380")
        modal.transient(self)
        modal.grab_set()
        modal.resizable(False, False)
        
        ctk.CTkLabel(modal, text="Service Name", anchor="w").pack(fill="x", padx=25, pady=(25, 5))
        service_entry = ctk.CTkEntry(modal, placeholder_text="e.g., github", height=32)
        service_entry.pack(fill="x", padx=25)
        
        ctk.CTkLabel(modal, text="Username / Email", anchor="w").pack(fill="x", padx=25, pady=(15, 5))
        user_entry = ctk.CTkEntry(modal, placeholder_text="e.g., user@email.com", height=32)
        user_entry.pack(fill="x", padx=25)
        
        ctk.CTkLabel(modal, text="Password", anchor="w").pack(fill="x", padx=25, pady=(15, 5))
        pwd_entry = ctk.CTkEntry(modal, placeholder_text="Enter password", show="*", height=32)
        pwd_entry.pack(fill="x", padx=25)
        
        def save():
            svc = service_entry.get().strip()
            usr = user_entry.get().strip()
            pwd = pwd_entry.get()
            if not svc or not pwd:
                messagebox.showerror("Error", "Service and Password are required.", parent=modal)
                return
            
            breach_count = check_password_breach(pwd)
            if breach_count > 0:
                if not messagebox.askyesno("Security Warning", f"This password has been found in {breach_count} data breaches!\n\nSave anyway?", parent=modal):
                    return
                    
            try:
                add_entry(self.vault_key, self.vault_data, svc, usr, pwd)
                modal.destroy()
                self._refresh_password_list()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=modal)

        ctk.CTkButton(modal, text="Save Password", command=save, height=35).pack(pady=25)

    def _copy_to_clipboard(self, text):
        pyperclip.copy(text)
        messagebox.showinfo("Copied", "Password copied to clipboard!\n(Clears in 20s)")

if __name__ == "__main__":
    app = VaultXApp()
    app.mainloop()