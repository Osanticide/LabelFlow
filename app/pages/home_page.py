import tkinter as tk


class HomePage(tk.Frame):
    def __init__(self, parent, colors, on_open_page):
        super().__init__(parent, bg=colors["background"])

        self.colors = colors
        self.on_open_page = on_open_page

        self.create_page()

    def create_page(self):
        # Descrição da página inicial
        description = tk.Label(
            self,
            text="Selecione uma ferramenta para começar.",
            font=("Segoe UI", 11),
            bg=self.colors["background"],
            fg="#66717D",
        )
        description.pack(anchor="w", padx=30, pady=(0, 20))

        # Área dos cartões
        cards_frame = tk.Frame(self, bg=self.colors["background"])
        cards_frame.pack(fill="both", expand=True, padx=30, pady=10)

        tools = [
            (
                "Gerador Universal PRN",
                "Gere etiquetas Zebra utilizando planilhas Excel.",
            ),
            (
                "Leitor PDF Individual",
                "Extraia códigos e descrições de PDFs com uma etiqueta por página.",
            ),
            (
                "Leitor PDF em Grade",
                "Leia etiquetas organizadas em grades dentro de arquivos PDF.",
            ),
        ]

        for title, description in tools:
            self.create_tool_card(cards_frame, title, description)

    def create_tool_card(self, parent, title, description):
        card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            padx=20,
            pady=18,
        )
        card.pack(fill="x", pady=8)

        # Título do cartão
        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["white"],
            fg=self.colors["text"],
        ).pack(anchor="w")

        # Descrição do cartão
        tk.Label(
            card,
            text=description,
            font=("Segoe UI", 10),
            bg=self.colors["white"],
            fg="#66717D",
            wraplength=650,
            justify="left",
        ).pack(anchor="w", pady=(7, 12))

        # Botão para abrir a ferramenta
        tk.Button(
            card,
            text="Abrir ferramenta",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["primary"],
            fg=self.colors["white"],
            activebackground="#A90D2D",
            activeforeground=self.colors["white"],
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda: self.on_open_page(title),
        ).pack(anchor="w")
