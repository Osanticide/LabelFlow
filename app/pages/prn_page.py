import os
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox

from modules.prn_excel.processor import processar_arquivos


class PRNPage(tk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["background"])

        self.colors = colors

        # Arquivos e configurações
        self.prn_path = tk.StringVar()
        self.excel_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.var_quebra = tk.BooleanVar(value=True)

        self.create_page()

    def create_page(self):
        # Área principal com rolagem
        self.canvas = tk.Canvas(
            self, bg=self.colors["background"], highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.form_frame = tk.Frame(self.canvas, bg=self.colors["background"])

        self.form_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.form_frame, anchor="nw"
        )

        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(
                self.canvas_window, width=event.width
            ),
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar.pack(side="right", fill="y")

        # Conteúdo
        self.create_file_section()
        self.create_mapping_section()
        self.create_output_section()
        self.create_footer()

    def create_section(self, parent, title):
        section = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            padx=20,
            pady=18,
        )

        section.pack(fill="x", pady=(0, 15))

        tk.Label(
            section,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["white"],
            fg=self.colors["text"],
        ).pack(anchor="w", pady=(0, 15))

        return section

    def create_file_section(self):
        section = self.create_section(self.form_frame, "Arquivos de entrada")

        self.create_file_field(
            section, "Arquivo de etiquetas (PRN)", self.prn_path, self.select_prn_file
        )

        self.create_file_field(
            section,
            "Planilha de dados (Excel)",
            self.excel_path,
            self.select_excel_file,
        )

    def create_file_field(self, parent, label, variable, command):
        field = tk.Frame(parent, bg=self.colors["white"])

        field.pack(fill="x", pady=6)

        tk.Label(
            field,
            text=label,
            font=("Segoe UI", 10),
            bg=self.colors["white"],
            fg=self.colors["text"],
        ).pack(anchor="w", pady=(0, 5))

        row = tk.Frame(field, bg=self.colors["white"])

        row.pack(fill="x")

        entry = tk.Entry(
            row, textvariable=variable, font=("Segoe UI", 10), relief="solid", bd=1
        )

        entry.pack(side="left", fill="x", expand=True, ipady=6)

        tk.Button(
            row,
            text="Procurar...",
            font=("Segoe UI", 9),
            bg="#E9EDF1",
            fg=self.colors["text"],
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=command,
        ).pack(side="left", padx=(8, 0))

    def create_mapping_section(self):
        section = self.create_section(self.form_frame, "Mapeamento de marcadores")

        tk.Label(
            section,
            text=(
                "Associe cada marcador existente no arquivo PRN "
                "à letra da coluna correspondente na planilha Excel."
            ),
            font=("Segoe UI", 9),
            bg=self.colors["white"],
            fg="#66717D",
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))

        # Opção de quebra automática
        tk.Checkbutton(
            section,
            text="Ativar quebra automática de linha",
            variable=self.var_quebra,
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["white"],
            fg=self.colors["text"],
            activebackground=self.colors["white"],
            selectcolor=self.colors["white"],
        ).pack(anchor="w", pady=(0, 12))

        # Tabela de mapeamentos
        table_frame = tk.Frame(section, bg=self.colors["white"])

        table_frame.pack(fill="x")

        self.mapping_table = ttk.Treeview(
            table_frame, columns=("marker", "column"), show="headings", height=5
        )

        self.mapping_table.heading("marker", text="Marcador no PRN")

        self.mapping_table.heading("column", text="Coluna no Excel")

        self.mapping_table.column("marker", width=250)

        self.mapping_table.column("column", width=150)

        self.mapping_table.pack(side="left", fill="x", expand=True)

        table_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.mapping_table.yview
        )

        table_scrollbar.pack(side="right", fill="y")

        self.mapping_table.configure(yscrollcommand=table_scrollbar.set)

        # Botões da tabela
        buttons = tk.Frame(section, bg=self.colors["white"])

        buttons.pack(fill="x", pady=(12, 0))

        tk.Button(
            buttons,
            text="Adicionar marcador",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["primary"],
            fg=self.colors["white"],
            activebackground="#A90D2D",
            activeforeground=self.colors["white"],
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.add_mapping,
        ).pack(side="left")

        tk.Button(
            buttons,
            text="Remover selecionado",
            font=("Segoe UI", 9),
            bg="#E9EDF1",
            fg=self.colors["text"],
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.remove_mapping,
        ).pack(side="left", padx=(8, 0))

        # Mapeamento inicial igual ao script original
        self.mapping_table.insert("", "end", values=("numeroloja - nome loja", "A"))

    def create_output_section(self):
        section = self.create_section(self.form_frame, "Destino dos arquivos gerados")

        self.create_file_field(
            section, "Pasta de saída", self.output_path, self.select_output_folder
        )

    def create_footer(self):
        footer = tk.Frame(self.form_frame, bg=self.colors["background"])

        footer.pack(fill="x", pady=(0, 25))

        self.status_label = tk.Label(
            footer,
            text="Aguardando configuração dos arquivos.",
            font=("Segoe UI", 9),
            bg=self.colors["background"],
            fg="#66717D",
            anchor="w",
        )

        self.status_label.pack(anchor="w", pady=(0, 12))

        self.progress = ttk.Progressbar(footer, mode="indeterminate")

        self.progress.pack(fill="x", pady=(0, 15))

        self.generate_button = tk.Button(
            footer,
            text="GERAR ETIQUETAS",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["primary"],
            fg=self.colors["white"],
            activebackground="#A90D2D",
            activeforeground=self.colors["white"],
            relief="flat",
            bd=0,
            padx=22,
            pady=12,
            cursor="hand2",
            command=self.run_processing,
        )

        self.generate_button.pack(anchor="w")

    def select_prn_file(self):
        path = filedialog.askopenfilename(
            title="Selecione o arquivo PRN",
            filetypes=[
                ("Arquivos PRN e ZPL", "*.prn *.zpl"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if path:
            self.prn_path.set(path)

    def select_excel_file(self):
        path = filedialog.askopenfilename(
            title="Selecione a planilha Excel",
            filetypes=[
                ("Planilhas Excel", "*.xlsx *.xlsm"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if path:
            self.excel_path.set(path)

    def select_output_folder(self):
        path = filedialog.askdirectory(title="Selecione a pasta de saída")

        if path:
            self.output_path.set(path)

    def add_mapping(self):
        marker = simpledialog.askstring(
            "Adicionar marcador",
            "Digite o marcador exatamente como aparece no PRN:",
            parent=self,
        )

        if marker is None:
            return

        marker = marker.strip()

        if not marker:
            messagebox.showwarning(
                "Marcador inválido", "Informe um marcador.", parent=self
            )
            return

        column = simpledialog.askstring(
            "Coluna do Excel",
            "Digite a letra da coluna correspondente (ex.: A, B, C):",
            parent=self,
        )

        if column is None:
            return

        column = column.strip().upper()

        if not column:
            messagebox.showwarning(
                "Coluna inválida", "Informe a coluna correspondente.", parent=self
            )
            return

        self.mapping_table.insert("", "end", values=(marker, column))

    def remove_mapping(self):
        selected = self.mapping_table.selection()

        if not selected:
            messagebox.showinfo(
                "Remover marcador", "Selecione um marcador na tabela.", parent=self
            )
            return

        for item in selected:
            self.mapping_table.delete(item)

    def run_processing(self):
        # Coleta os mapeamentos da tabela
        mapeamentos = []

        for item in self.mapping_table.get_children():
            marker, column = self.mapping_table.item(item, "values")

            mapeamentos.append({"marker": marker, "column": column})

        # Validação inicial
        if not self.prn_path.get():
            messagebox.showwarning(
                "Arquivo não selecionado", "Selecione o arquivo PRN.", parent=self
            )
            return

        if not self.excel_path.get():
            messagebox.showwarning(
                "Arquivo não selecionado", "Selecione a planilha Excel.", parent=self
            )
            return

        if not self.output_path.get():
            messagebox.showwarning(
                "Pasta não selecionada", "Selecione a pasta de saída.", parent=self
            )
            return

        if not mapeamentos:
            messagebox.showwarning(
                "Mapeamento ausente", "Adicione pelo menos um marcador.", parent=self
            )
            return

        # Inicia a operação
        self.generate_button.config(state="disabled")
        self.status_label.config(text="Processando arquivos... Aguarde.")

        self.progress.start(10)

        self.update_idletasks()

        try:
            resultado = processar_arquivos(
                caminho_modelo=self.prn_path.get(),
                caminho_excel=self.excel_path.get(),
                diretorio_saida=self.output_path.get(),
                mapeamentos=mapeamentos,
                usar_quebra=self.var_quebra.get(),
            )

            self.progress.stop()

            if resultado["total_arquivos"] == 0:
                self.status_label.config(
                    text="Processamento concluído, mas nenhum registro válido foi encontrado."
                )

                messagebox.showwarning(
                    "Nenhuma etiqueta gerada",
                    "A planilha foi lida, mas nenhum registro válido foi encontrado.",
                    parent=self,
                )

                return

            self.status_label.config(
                text=(
                    f"Concluído! {resultado['total_etiquetas']} etiqueta(s) gerada(s)."
                )
            )

            detalhes = []

            for arquivo in resultado["arquivos_gerados"]:
                detalhes.append(
                    f"Aba: {arquivo['aba']}\n"
                    f"Etiquetas: {arquivo['etiquetas']}\n"
                    f"Arquivo: {os.path.basename(arquivo['caminho'])}"
                )

            mensagem = (
                "Processamento concluído com sucesso!\n\n"
                f"Total de etiquetas: {resultado['total_etiquetas']}\n"
                f"Arquivos gerados: {resultado['total_arquivos']}\n\n"
                + "\n\n".join(detalhes)
            )

            messagebox.showinfo("Geração concluída", mensagem, parent=self)

        except Exception as erro:
            self.status_label.config(text="Ocorreu um erro durante o processamento.")

            messagebox.showerror("Erro no processamento", str(erro), parent=self)

        finally:
            self.progress.stop()
            self.generate_button.config(state="normal")
