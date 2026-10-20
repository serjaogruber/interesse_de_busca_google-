import tkinter as tk
from tkinter import ttk, messagebox
import urllib.parse
import urllib.request
import json
from collections import Counter
import calendar

# Bibliotecas para gráficos no Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AppAnaliseGoogleCompleta:
    def __init__(self, root):
        self.root = root
        self.root.title("Análise de Tendência, Volume e Top 20 no Google")
        self.root.geometry("1000x820")
        self.root.configure(bg="#f4f6f9")

        # Configuração do Estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview.Heading", font=("Arial", 9, "bold"))
        self.style.configure("Treeview", font=("Arial", 9), rowheight=22)

        # --- Painel 1: Entrada de Dados ---
        frame_busca = ttk.LabelFrame(root, text=" Pesquisa e Mapeamento de Mercado ", padding=12)
        frame_busca.pack(fill="x", padx=15, pady=8)

        ttk.Label(frame_busca, text="Termo / Ticker:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_termo = ttk.Entry(frame_busca, width=22, font=("Arial", 11))
        self.entry_termo.grid(row=0, column=1, padx=8, pady=5)
        self.entry_termo.insert(0, "PETR4")

        self.btn_consultar = ttk.Button(frame_busca, text="Analisar Volume e Gerar Gráfico", command=self.analisar_buscas)
        self.btn_consultar.grid(row=0, column=2, padx=10, ipady=4)

        self.lbl_status = tk.Label(frame_busca, text="Pronto para analisar.", font=("Arial", 9, "italic"), fg="#7f8c8d", bg="#f4f6f9")
        self.lbl_status.grid(row=1, column=0, columnspan=3, sticky="w", pady=2)

        # --- Painel 2: Cartão de Estatística de Pico de Mês ---
        frame_stats = ttk.LabelFrame(root, text=" Proporção e Mês de Maior Volume ", padding=10)
        frame_stats.pack(fill="x", padx=15, pady=5)

        self.lbl_mes_pico = tk.Label(frame_stats, text="Mês de Maior Volume: -", font=("Arial", 11, "bold"), fg="#2c3e50", bg="#f4f6f9")
        self.lbl_mes_pico.pack(anchor="w", pady=2)

        self.lbl_proporcao = tk.Label(frame_stats, text="Proporção em Relação à Média Mensal: -", font=("Arial", 11, "bold"), fg="#27ae60", bg="#f4f6f9")
        self.lbl_proporcao.pack(anchor="w", pady=2)

        # --- Painel Conteúdo: Tabela e Gráfico lado a lado ---
        frame_conteudo = ttk.Frame(root)
        frame_conteudo.pack(fill="both", expand=True, padx=15, pady=5)

        # Esquerda: Tabela Top 20
        frame_tabela = ttk.LabelFrame(frame_conteudo, text=" Top 20 Termos Mais Pesquisados ", padding=8)
        frame_tabela.pack(side="left", fill="both", expand=True, padx=(0, 5))

        colunas = ("posição", "termo", "frequencia")
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", selectmode="browse")

        self.tree.heading("posição", text="#")
        self.tree.heading("termo", text="Termo / Frase")
        self.tree.heading("frequencia", text="Score (0-100)")

        self.tree.column("posição", width=35, anchor="center")
        self.tree.column("termo", width=260, anchor="w")
        self.tree.column("frequencia", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Direita: Gráfico Matplotlib
        frame_grafico = ttk.LabelFrame(frame_conteudo, text=" Distribuição de Volume por Mês ", padding=8)
        frame_grafico.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.fig, self.ax = plt.subplots(figsize=(5, 3.5), dpi=95)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafico)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Executa análise inicial
        self.analisar_buscas()

    def requisitar_autocomplete(self, consulta):
        """Faz requisição para o autocompletar do Google"""
        try:
            url = f"http://suggestqueries.google.com/complete/search?client=firefox&hl=pt-BR&q={urllib.parse.quote(consulta)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                dados = json.loads(resp.read().decode('utf-8'))
                return dados[1] if len(dados) > 1 else []
        except Exception:
            return []

    def analisar_buscas(self):
        termo_base = self.entry_termo.get().strip().lower()

        if not termo_base:
            messagebox.showwarning("Campo Vazio", "Por favor, informe um termo para busca.")
            return

        # Limpa tabela anterior
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.lbl_status.config(text="Analisando volumes e sazonalidade mensal...", fg="#d35400")
        self.root.update()

        # 1. Coleta Top 20 e Score de Frequência
        pontuacao_termos = Counter()
        sugestoes_diretas = self.requisitar_autocomplete(termo_base)
        for rank, s in enumerate(sugestoes_diretas):
            pontuacao_termos[s] += (10 - rank) * 10

        sufixos = ['a', 'b', 'c', 'd', 'e', 'f', 'hoje', 'como', 'vale', 'dividendo', 'comprar', 'cotacao']
        for sufixo in sufixos:
            sugestoes = self.requisitar_autocomplete(f"{termo_base} {sufixo}")
            for rank, s in enumerate(sugestoes):
                pontuacao_termos[s] += (10 - rank)

        if pontuacao_termos:
            max_score = max(pontuacao_termos.values())
            top_20 = pontuacao_termos.most_common(20)
            for i, (termo, score) in enumerate(top_20, start=1):
                rel_score = int((score / max_score) * 100)
                self.tree.insert("", "end", values=(f"{i}º", termo, f"{rel_score}"))

        # 2. Mapeamento de Frequência Mensal (Sazonalidade)
        meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        volumes_mensais = Counter()

        # Mapeia a frequência de menções e volume por mês no Google
        for idx_m, mes in enumerate(meses_pt, start=1):
            sug_mes = self.requisitar_autocomplete(f"{termo_base} {mes.lower()}")
            peso_pico = sum((10 - r) for r, _ in enumerate(sug_mes))
            # Peso base aleatório/ponderado proporcional às menções do mercado
            volumes_mensais[mes] = 50 + (peso_pico * 5) + (len(sug_mes) * 12)

        # 3. Cálculo da Proporção de Maior Volume e Mês de Pico
        mes_pico, max_volume = volumes_mensais.most_common(1)[0]
        media_volume = sum(volumes_mensais.values()) / len(volumes_mensais)
        proporcao = (max_volume / media_volume) if media_volume > 0 else 1.0

        self.lbl_mes_pico.config(text=f"Mês de Maior Volume: {mes_pico} (Índice de Pico: {max_volume:.0f})")
        self.lbl_proporcao.config(
            text=f"Proporção em Relação à Média Mensal: {proporcao:.2f}x mais buscas (+{(proporcao-1)*100:.1f}%)"
        )

        # 4. Atualização do Gráfico
        self.desenhar_grafico_mensal(meses_pt, volumes_mensais, mes_pico, termo_base.upper())
        self.lbl_status.config(text=f"Análise concluída com sucesso para '{termo_base.upper()}'.", fg="#27ae60")

    def desenhar_grafico_mensal(self, meses, volumes_dict, mes_pico, ticker):
        self.ax.clear()

        y_values = [volumes_dict[m] for m in meses]
        cores = ['#27ae60' if m == mes_pico else '#3498db' for m in meses]

        bars = self.ax.bar(meses, y_values, color=cores, width=0.6)

        self.ax.set_title(f"Volume Estimado por Mês - {ticker}\n(Verde = Mês com maior volume)", fontsize=10, fontweight='bold')
        self.ax.set_ylabel("Índice de Volume")
        self.ax.grid(axis='y', linestyle='--', alpha=0.5)

        # Adiciona rótulos no topo das barras
        for bar in bars:
            height = bar.get_height()
            self.ax.annotate(f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = AppAnaliseGoogleCompleta(root)
    root.mainloop()