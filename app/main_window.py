import tkinter as tk
from tkinter import ttk

from app.pages.home_page import HomePage
from app.pages.prn_page import PRNPage


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.title("LabelFlow")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg="#E9EDF1")

        # Cores do projeto
        self.colors = {
            "primary": "#C91035",
            "success": "#23C690",
            "sidebar": "#344252",
            "background": "#E9EDF1",
            "white": "#FFFFFF",
            "text": "#252B33",
            "border": "#D5DAE0",
            "sidebar_text": "#FFFFFF",
            "sidebar_hover": "#45566A",
        }

        # Estado do menu lateral
        self.sidebar_visible = True

        # Controle das páginas
        self.pages = {}
        self.current_page = None
        self.placeholder_page = None

        # Configuração dos estilos
        self.configure_styles()

        # Criação da estrutura principal
        self.create_layout()

        # Criação das páginas
        self.create_pages()

        # Inicia sempre na página inicial
        self.show_page("Início")

    def configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=self.colors["background"])

        style.configure(
            "TLabel",
            background=self.colors["background"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 20, "bold"),
            foreground=self.colors["text"],
        )

        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground="#66717D")

    def create_layout(self):
        # Cabeçalho
        self.header = tk.Frame(self, bg=self.colors["white"], height=60)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)

        self.menu_button = tk.Button(
            self.header,
            text="☰",
            font=("Segoe UI", 17),
            bg=self.colors["white"],
            fg=self.colors["text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.toggle_sidebar,
        )
        self.menu_button.pack(side="left", padx=(18, 12))

        self.header_title = tk.Label(
            self.header,
            text="LabelFlow",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors["white"],
            fg=self.colors["primary"],
        )
        self.header_title.pack(side="left")

        # Linha divisória
        tk.Frame(self, bg=self.colors["border"], height=1).pack(side="top", fill="x")

        # Área principal
        self.body = tk.Frame(self, bg=self.colors["background"])
        self.body.pack(side="top", fill="both", expand=True)

        # Menu lateral
        self.sidebar = tk.Frame(self.body, bg=self.colors["sidebar"], width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.create_sidebar()

        # Área de conteúdo
        self.content = tk.Frame(self.body, bg=self.colors["background"])
        self.content.pack(side="left", fill="both", expand=True)

    def create_sidebar(self):
        tk.Label(
            self.sidebar,
            text="MENU PRINCIPAL",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["sidebar"],
            fg="#B9C4CF",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(25, 12))

        menu_items = [
            ("Início", "Início"),
            ("Gerador Universal PRN", "Gerador Universal PRN"),
            ("Leitor PDF Individual", "Leitor PDF Individual"),
            ("Leitor PDF em Grade", "Leitor PDF em Grade"),
            ("Configurações", "Configurações"),
        ]

        for label, page_name in menu_items:
            button = tk.Button(
                self.sidebar,
                text=label,
                font=("Segoe UI", 10),
                bg=self.colors["sidebar"],
                fg=self.colors["sidebar_text"],
                activebackground=self.colors["sidebar_hover"],
                activeforeground=self.colors["white"],
                relief="flat",
                bd=0,
                anchor="w",
                padx=20,
                pady=12,
                cursor="hand2",
                command=lambda name=page_name: self.show_page(name),
            )
            button.pack(fill="x")

            button.bind(
                "<Enter>",
                lambda event, widget=button: widget.configure(
                    bg=self.colors["sidebar_hover"]
                ),
            )

            button.bind(
                "<Leave>",
                lambda event, widget=button: widget.configure(
                    bg=self.colors["sidebar"]
                ),
            )

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False

        else:
            self.sidebar.pack(side="left", fill="y", before=self.content)
            self.sidebar_visible = True

    def create_pages(self):
        # Cria as páginas apenas uma vez.
        # Não as posiciona aqui: isso será feito na navegação.

        self.pages["Início"] = HomePage(self.content, self.colors, self.show_page)

        self.pages["Gerador Universal PRN"] = PRNPage(self.content, self.colors)

    def show_page(self, page_name):
        # Esconde a página atualmente visível
        if self.current_page is not None:
            self.current_page.place_forget()
            self.current_page = None

        # Remove uma tela provisória anterior
        if self.placeholder_page is not None:
            self.placeholder_page.destroy()
            self.placeholder_page = None

        # Verifica se a página já existe
        if page_name in self.pages:
            page = self.pages[page_name]

            # Exibe somente a página solicitada
            page.place(x=0, y=0, relwidth=1, relheight=1)

            page.lift()
            self.current_page = page

        else:
            self.show_placeholder(page_name)

    def show_placeholder(self, page_name):
        self.placeholder_page = tk.Frame(self.content, bg=self.colors["background"])

        self.placeholder_page.place(x=0, y=0, relwidth=1, relheight=1)

        tk.Label(
            self.placeholder_page,
            text=page_name,
            font=("Segoe UI", 20, "bold"),
            bg=self.colors["background"],
            fg=self.colors["text"],
        ).pack(anchor="w", padx=30, pady=(30, 20))

        tk.Label(
            self.placeholder_page,
            text=(f"A ferramenta '{page_name}' será implementada nas próximas etapas."),
            font=("Segoe UI", 11),
            bg=self.colors["background"],
            fg="#66717D",
            wraplength=650,
            justify="left",
        ).pack(anchor="w", padx=30, pady=10)
