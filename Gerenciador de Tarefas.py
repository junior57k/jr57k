import customtkinter as ctk
from tkinter import messagebox, StringVar
import json
import os
import re
from datetime import datetime
from PIL import Image, ImageTk

# Tenta importar keyboard, mas tem fallback se não estiver disponível
try:
    import keyboard
    KEYBOARD_DISPONIVEL = True
except ImportError:
    KEYBOARD_DISPONIVEL = False

# Configurações globais do CustomTkinter
ctk.set_appearance_mode("System")  # Modos: "System" (padrão), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue" (padrão), "dark-blue", "green"

# Classe para criar tooltips
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        try:
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 25
            
            # Cria uma janela de nível superior para mostrar o tooltip
            self.tooltip = ctk.CTkToplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            # Frame para o tooltip
            frame = ctk.CTkFrame(self.tooltip, border_width=1)
            frame.pack(ipadx=5, ipady=5)
            
            # Label com o texto do tooltip
            label = ctk.CTkLabel(frame, text=self.text, font=('Helvetica', 10))
            label.pack()
        except Exception:
            # Se ocorrer algum erro ao mostrar o tooltip, ignora silenciosamente
            pass
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class SistemaTarefas:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Tarefas")
        self.root.geometry("1000x700")
        
        # Carrega os dados e cria ADM padrão se não existir
        self.carregar_dados()
        self.criar_adm_padrao()
        
        # Variáveis de controle
        self.usuario_atual = None
        self.tema_usuario = "System"  # Tema padrão
        
        # Domínios comuns para autocomplete
        self.dominios_email = ["gmail.com", "outlook.com", "hotmail.com"]
        
        # Status da barra de pesquisa
        self.pesquisa_ativa = False
        self.termo_pesquisa = StringVar()
        
        # Configura atalhos globais se disponível
        self.configurar_atalhos()
        
        # Mostra a tela de login inicialmente
        self.mostrar_tela_login()
    
    def configurar_atalhos(self):
        """Configura atalhos de teclado globais"""
        # Implementa apenas se a biblioteca keyboard estiver disponível
        if not KEYBOARD_DISPONIVEL:
            return
            
        try:
            # Tenta limpar atalhos existentes
            keyboard.unhook_all()
        except:
            # Ignora erros ao tentar desregistrar atalhos
            pass

    def verificar_senha_forte(self, senha):
        """
        Verifica se a senha atende aos critérios de segurança OWASP:
        - Mínimo de 6 caracteres
        - Pelo menos uma letra maiúscula
        - Pelo menos uma letra minúscula
        - Pelo menos um número
        - Pelo menos um caractere especial
        """
        if len(senha) < 6:
            return False, "A senha deve ter no mínimo 6 caracteres."
        
        # Verificações adicionais (opcional)
        tem_maiuscula = bool(re.search(r'[A-Z]', senha))
        tem_minuscula = bool(re.search(r'[a-z]', senha))
        tem_numero = bool(re.search(r'[0-9]', senha))
        tem_especial = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', senha))
        
        # Para senha ser considerada forte, precisa atender pelo menos 3 dos 4 critérios
        criterios_atendidos = sum([tem_maiuscula, tem_minuscula, tem_numero, tem_especial])
        
        if criterios_atendidos < 3:
            mensagem = "A senha é fraca. Recomendamos incluir:\n"
            if not tem_maiuscula:
                mensagem += "- Letra maiúscula\n"
            if not tem_minuscula:
                mensagem += "- Letra minúscula\n"
            if not tem_numero:
                mensagem += "- Número\n"
            if not tem_especial:
                mensagem += "- Caractere especial (ex: !@#$%)"
            return False, mensagem
        
        return True, ""

    def criar_adm_padrao(self):
        """Cria um usuário administrador padrão se não existir"""
        adm_existe = any(u['email'] == 'adm' for u in self.usuarios)
        if not adm_existe:
            adm_padrao = {
                'nome': 'Administrador',
                'email': 'adm',
                'senha': 'Admin123!',  # Senha forte para o admin
                'tipo': 'Administrador'
            }
            self.usuarios.append(adm_padrao)
            self.salvar_dados()

    def carregar_dados(self):
        """Carrega os dados de usuários e tarefas do arquivo JSON"""
        try:
            with open('dados.json', 'r') as f:
                dados = json.load(f)
                self.usuarios = dados.get('usuarios', [])
                self.tarefas = dados.get('tarefas', [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.usuarios = []
            self.tarefas = []

    def salvar_dados(self):
        """Salva os dados de usuários e tarefas no arquivo JSON"""
        dados = {
            'usuarios': self.usuarios,
            'tarefas': self.tarefas
        }
        with open('dados.json', 'w') as f:
            json.dump(dados, f, indent=2)

    def limpar_tela(self):
        """Remove todos os widgets da tela atual"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_tela_login(self):
        """Mostra a tela de login com novo design"""
        self.limpar_tela()
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Frame do formulário
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(expand=True, padx=30, pady=30)
        
        # Logo/Cabeçalho
        header_frame = ctk.CTkFrame(form_frame)
        header_frame.pack(pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="🔒", font=('Helvetica', 40)).pack()
        ctk.CTkLabel(header_frame, text="Login do Sistema", font=('Helvetica', 18, 'bold')).pack()
        ctk.CTkLabel(header_frame, text="Use suas credenciais para acessar", font=('Helvetica', 14)).pack()
        
        # Campos do formulário
        field_frame = ctk.CTkFrame(form_frame)
        field_frame.pack(pady=10)
        
        ctk.CTkLabel(field_frame, text="E-mail:").grid(row=0, column=0, sticky='w', pady=5)
        self.email_login = ctk.CTkEntry(field_frame, width=200)
        self.email_login.grid(row=0, column=1, pady=5, ipady=5)
        
        # Configuração do autocompletar para email
        self.email_login.bind('<KeyRelease>', self.autocomplete_email)
        
        # Sugestões de domínio
        self.sugestoes_frame = ctk.CTkFrame(field_frame)
        self.sugestoes_frame.grid(row=1, column=1, sticky='w', pady=0)
        self.sugestoes_frame.grid_remove()  # Inicialmente oculto
        
        ctk.CTkLabel(field_frame, text="Senha:").grid(row=2, column=0, sticky='w', pady=5)
        self.senha_login = ctk.CTkEntry(field_frame, width=200, show="*")
        self.senha_login.grid(row=2, column=1, pady=5, ipady=5)
        
        # Botões
        btn_frame = ctk.CTkFrame(form_frame)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Entrar", command=self.fazer_login).pack(side='left', padx=5, ipady=5, ipadx=20)
        # Mostra o botão de cadastro apenas se não for o ADM
        if not self.usuario_logado_como_adm():
            ctk.CTkButton(btn_frame, text="Cadastrar Usuário", command=self.mostrar_tela_cadastro).pack(side='left', padx=5, ipady=5, ipadx=20)
        
        # Rodapé
        footer_frame = ctk.CTkFrame(main_frame)
        footer_frame.pack(fill='x', pady=(20, 0))
        
        ctk.CTkLabel(footer_frame, text="© 2023 Sistema de Gestão de Tarefas", font=('Helvetica', 12)).pack()

    def autocomplete_email(self, event=None):
        """Autocompleta o email com domínios comuns"""
        # Limpa o frame de sugestões
        for widget in self.sugestoes_frame.winfo_children():
            widget.destroy()
        
        # Obtém o texto atual
        texto = self.email_login.get()
        
        # Verifica se tem o caractere @ 
        if '@' in texto:
            parte_local, dominio = texto.split('@', 1)
            
            # Se já tiver @ mas o domínio estiver incompleto, mostrar sugestões
            if dominio and not '.' in dominio:
                # Mostra o frame de sugestões
                self.sugestoes_frame.grid()
                
                # Cria um botão para cada domínio que começa com o texto digitado
                sugestoes_count = 0
                for i, dominio_completo in enumerate(self.dominios_email):
                    if dominio_completo.startswith(dominio):
                        sugestao = parte_local + '@' + dominio_completo
                        btn = ctk.CTkButton(
                            self.sugestoes_frame, 
                            text=sugestao,
                            width=200,
                            height=25,
                            fg_color="#6c757d",
                            command=lambda s=sugestao: self.aplicar_sugestao(s)
                        )
                        btn.grid(row=sugestoes_count, column=0, pady=2, padx=5, sticky='w')
                        sugestoes_count += 1
            else:
                # Se já tiver o ponto no domínio, esconde as sugestões
                self.sugestoes_frame.grid_remove()
        else:
            # Se não tiver @, esconde as sugestões
            self.sugestoes_frame.grid_remove()

    def aplicar_sugestao(self, sugestao):
        """Aplica a sugestão de email selecionada"""
        # Define o texto do email
        self.email_login.delete(0, 'end')
        self.email_login.insert(0, sugestao)
        
        # Esconde as sugestões
        self.sugestoes_frame.grid_remove()
        
        # Foca no campo de senha
        self.senha_login.focus_set()

    def usuario_logado_como_adm(self):
        """Verifica se o usuário logado é o ADM"""
        return self.usuario_atual and self.usuario_atual['email'] == 'adm'

    def mostrar_tela_cadastro(self):
        """Mostra a tela de cadastro apenas para usuários comuns"""
        self.limpar_tela()
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Frame do formulário
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(expand=True, padx=30, pady=30)
        
        # Logo/Cabeçalho
        header_frame = ctk.CTkFrame(form_frame)
        header_frame.pack(pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="👤", font=('Helvetica', 40)).pack()
        ctk.CTkLabel(header_frame, text="Cadastro de Usuário", font=('Helvetica', 18, 'bold')).pack()
        ctk.CTkLabel(header_frame, text="Preencha os dados abaixo", font=('Helvetica', 14)).pack()
        
        # Campos do formulário
        field_frame = ctk.CTkFrame(form_frame)
        field_frame.pack(pady=10)
        
        ctk.CTkLabel(field_frame, text="Nome:").grid(row=0, column=0, sticky='w', pady=5)
        self.nome_cadastro = ctk.CTkEntry(field_frame, width=200)
        self.nome_cadastro.grid(row=0, column=1, pady=5, ipady=5)
        
        ctk.CTkLabel(field_frame, text="E-mail:").grid(row=1, column=0, sticky='w', pady=5)
        self.email_cadastro = ctk.CTkEntry(field_frame, width=200)
        self.email_cadastro.grid(row=1, column=1, pady=5, ipady=5)
        
        # Configuração do autocompletar para email no cadastro
        self.email_cadastro.bind('<KeyRelease>', self.autocomplete_email_cadastro)
        
        # Sugestões de domínio para o cadastro
        self.sugestoes_cadastro_frame = ctk.CTkFrame(field_frame)
        self.sugestoes_cadastro_frame.grid(row=2, column=1, sticky='w', pady=0)
        self.sugestoes_cadastro_frame.grid_remove()  # Inicialmente oculto
        
        ctk.CTkLabel(field_frame, text="Senha:").grid(row=3, column=0, sticky='w', pady=5)
        self.senha_cadastro = ctk.CTkEntry(field_frame, width=200, show="*")
        self.senha_cadastro.grid(row=3, column=1, pady=5, ipady=5)
        
        # Requisitos de senha
        info_frame = ctk.CTkFrame(form_frame)
        info_frame.pack(pady=5)
        
        ctk.CTkLabel(info_frame, text="Requisitos de senha:", 
                  font=('Helvetica', 12, 'bold')).pack(anchor='w')
        ctk.CTkLabel(info_frame, text="- Mínimo de 6 caracteres", 
                  font=('Helvetica', 11)).pack(anchor='w')
        ctk.CTkLabel(info_frame, text="- Recomendado incluir letras maiúsculas, minúsculas, números e caracteres especiais", 
                  font=('Helvetica', 11)).pack(anchor='w')
        
        # Botões
        btn_frame = ctk.CTkFrame(form_frame)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Cadastrar", command=self.cadastrar_usuario).pack(side='left', padx=5, ipady=5, ipadx=20)
        ctk.CTkButton(btn_frame, text="Voltar", command=self.mostrar_tela_login).pack(side='left', padx=5, ipady=5, ipadx=20)
        
        # Rodapé
        footer_frame = ctk.CTkFrame(main_frame)
        footer_frame.pack(fill='x', pady=(20, 0))
        
        ctk.CTkLabel(footer_frame, text="© 2023 Sistema de Gestão de Tarefas", font=('Helvetica', 12)).pack()

    def autocomplete_email_cadastro(self, event=None):
        """Autocompleta o email com domínios comuns na tela de cadastro"""
        # Limpa o frame de sugestões
        for widget in self.sugestoes_cadastro_frame.winfo_children():
            widget.destroy()
        
        # Obtém o texto atual
        texto = self.email_cadastro.get()
        
        # Verifica se tem o caractere @ 
        if '@' in texto:
            parte_local, dominio = texto.split('@', 1)
            
            # Se já tiver @ mas o domínio estiver incompleto, mostrar sugestões
            if dominio and not '.' in dominio:
                # Mostra o frame de sugestões
                self.sugestoes_cadastro_frame.grid()
                
                # Cria um botão para cada domínio que começa com o texto digitado
                sugestoes_count = 0
                for i, dominio_completo in enumerate(self.dominios_email):
                    if dominio_completo.startswith(dominio):
                        sugestao = parte_local + '@' + dominio_completo
                        btn = ctk.CTkButton(
                            self.sugestoes_cadastro_frame, 
                            text=sugestao,
                            width=200,
                            height=25,
                            fg_color="#6c757d",
                            command=lambda s=sugestao: self.aplicar_sugestao_cadastro(s)
                        )
                        btn.grid(row=sugestoes_count, column=0, pady=2, padx=5, sticky='w')
                        sugestoes_count += 1
            else:
                # Se já tiver o ponto no domínio, esconde as sugestões
                self.sugestoes_cadastro_frame.grid_remove()
        else:
            # Se não tiver @, esconde as sugestões
            self.sugestoes_cadastro_frame.grid_remove()

    def aplicar_sugestao_cadastro(self, sugestao):
        """Aplica a sugestão de email selecionada na tela de cadastro"""
        # Define o texto do email
        self.email_cadastro.delete(0, 'end')
        self.email_cadastro.insert(0, sugestao)
        
        # Esconde as sugestões
        self.sugestoes_cadastro_frame.grid_remove()
        
        # Foca no campo de senha
        self.senha_cadastro.focus_set()

    def mostrar_tela_principal(self):
        """Mostra a tela principal após o login"""
        self.limpar_tela()
        
        # Barra de menu superior
        menu_bar = ctk.CTkFrame(self.root)
        menu_bar.pack(fill='x', pady=0)
        menu_bar.configure(fg_color="#343a40", corner_radius=0)
        
        # Botão de logout
        logout_btn = ctk.CTkButton(menu_bar, text=f"Sair ({self.usuario_atual['nome']})", 
                              fg_color='#343a40', text_color='white', font=('Helvetica', 12),
                              command=self.sair)
        logout_btn.pack(side='right', padx=20, ipadx=10, ipady=5)
        
        # Botão de perfil
        perfil_btn = ctk.CTkButton(menu_bar, text="👤 Meu Perfil", 
                              fg_color='#343a40', text_color='white', font=('Helvetica', 12),
                              command=lambda: self.mostrar_aba_perfil())
        perfil_btn.pack(side='right', padx=5, ipadx=10, ipady=5)
        
        # Título do sistema
        title_label = ctk.CTkLabel(menu_bar, text="Sistema de Gestão de Tarefas", 
                              fg_color='#343a40', text_color='white', font=('Helvetica', 16, 'bold'))
        title_label.pack(side='left', padx=20, pady=10)
        
        # Barra de pesquisa rápida 
        search_frame = ctk.CTkFrame(menu_bar, fg_color='#343a40')
        search_frame.pack(side='right', padx=10)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Pesquisar tarefas...", width=200)
        self.search_entry.pack(side='left', padx=5, pady=5)
        self.search_entry.bind("<Return>", self.pesquisar_tarefas)
        
        search_btn = ctk.CTkButton(search_frame, text="🔍", width=30, height=24, 
                               fg_color='#565e64', command=self.pesquisar_tarefas)
        search_btn.pack(side='left', padx=2)
        
        # Frame de conteúdo principal (substitui o Notebook que não existe em CTk)
        content_frame = ctk.CTkFrame(self.root)
        content_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Barra de navegação lateral para substituir abas
        nav_frame = ctk.CTkFrame(content_frame, width=200)
        nav_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        # Frame para conteúdo das "abas"
        self.tab_content = ctk.CTkFrame(content_frame)
        self.tab_content.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Botões de navegação
        tarefas_btn = ctk.CTkButton(nav_frame, text="📋 Tarefas", 
                               command=lambda: self.mostrar_aba_tarefas())
        tarefas_btn.pack(fill='x', padx=10, pady=5)
        
        # Botão de perfil na navegação lateral
        perfil_sidebar_btn = ctk.CTkButton(nav_frame, text="👤 Meu Perfil", 
                                     command=lambda: self.mostrar_aba_perfil())
        perfil_sidebar_btn.pack(fill='x', padx=10, pady=5)
        
        # Botões adicionais para ADM
        if self.usuario_logado_como_adm():
            nova_tarefa_btn = ctk.CTkButton(nav_frame, text="➕ Nova Tarefa", 
                                       command=lambda: self.mostrar_aba_nova_tarefa())
            nova_tarefa_btn.pack(fill='x', padx=10, pady=5)
            
            cadastro_usuario_btn = ctk.CTkButton(nav_frame, text="👥 Cadastrar Usuário", 
                                            command=lambda: self.mostrar_aba_cadastro_usuario())
            cadastro_usuario_btn.pack(fill='x', padx=10, pady=5)
        
        # Configuração de atalhos para tela principal
        self.configurar_atalhos_principal()
        
        # Mostrar a aba de tarefas por padrão
        self.mostrar_aba_tarefas()
    
    def configurar_atalhos_principal(self):
        """Configura atalhos específicos para a tela principal"""
        if not KEYBOARD_DISPONIVEL:
            return
            
        try:
            # Tenta limpar atalhos existentes
            keyboard.unhook_all()
            
            # Registra novos atalhos
            keyboard.add_hotkey('alt+t', lambda: self.mostrar_aba_tarefas())
            keyboard.add_hotkey('alt+p', lambda: self.mostrar_aba_perfil())
            keyboard.add_hotkey('alt+q', lambda: self.sair())
            keyboard.add_hotkey('ctrl+f', lambda: self.focar_pesquisa())
            
            # Atalhos para administrador
            if self.usuario_logado_como_adm():
                keyboard.add_hotkey('alt+n', lambda: self.mostrar_aba_nova_tarefa())
                keyboard.add_hotkey('alt+u', lambda: self.mostrar_aba_cadastro_usuario())
        except Exception as e:
            # Se ocorrer algum erro ao registrar atalhos, apenas ignora
            # Isso garante que o sistema continua funcionando mesmo sem atalhos
            pass

    def focar_pesquisa(self):
        """Foca na caixa de pesquisa"""
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()
    
    def pesquisar_tarefas(self, event=None):
        """Pesquisa tarefas com base no texto digitado"""
        if hasattr(self, 'search_entry'):
            termo = self.search_entry.get().strip().lower()
            if termo:
                self.termo_pesquisa.set(termo)
                self.pesquisa_ativa = True
                self.mostrar_aba_tarefas()  # Recarrega a aba de tarefas com o filtro
            else:
                self.pesquisa_ativa = False
                self.termo_pesquisa.set("")
                self.mostrar_aba_tarefas()  # Recarrega sem filtro
    
    def mostrar_aba_tarefas(self):
        """Limpa o conteúdo atual e mostra a aba de tarefas"""
        for widget in self.tab_content.winfo_children():
            widget.destroy()
        
        self.criar_aba_tarefas(self.tab_content)
    
    def mostrar_aba_nova_tarefa(self):
        """Limpa o conteúdo atual e mostra a aba de nova tarefa"""
        for widget in self.tab_content.winfo_children():
            widget.destroy()
        
        self.criar_aba_nova_tarefa(self.tab_content)
    
    def mostrar_aba_cadastro_usuario(self):
        """Limpa o conteúdo atual e mostra a aba de cadastro de usuário"""
        for widget in self.tab_content.winfo_children():
            widget.destroy()
        
        self.criar_aba_cadastro_usuario(self.tab_content)

    def mostrar_aba_perfil(self):
        """Limpa o conteúdo atual e mostra a aba de perfil"""
        for widget in self.tab_content.winfo_children():
            widget.destroy()
        
        self.criar_aba_perfil(self.tab_content)

    def criar_aba_perfil(self, frame):
        """Cria a aba de perfil do usuário para personalização"""
        # Frame principal
        main_frame = ctk.CTkFrame(frame)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Cabeçalho
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Meu Perfil", font=('Helvetica', 18, 'bold')).pack()
        ctk.CTkLabel(header_frame, text="Personalize suas informações e configurações", 
                  font=('Helvetica', 14)).pack()
        
        # Frame para conteúdo e botões
        container_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        container_frame.pack(fill='both', expand=True)
        
        # Área de rolagem para conteúdo principal
        scroll_frame = ctk.CTkScrollableFrame(container_frame)
        scroll_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Conteúdo dividido em duas colunas
        content_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Coluna da esquerda - Informações do perfil
        perfil_frame = ctk.CTkFrame(content_frame)
        perfil_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Título da seção
        ctk.CTkLabel(perfil_frame, text="Informações Pessoais", 
                  font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=10)
        
        # Formulário de edição
        form_frame = ctk.CTkFrame(perfil_frame)
        form_frame.pack(fill='x', pady=10)
        
        # Nome
        ctk.CTkLabel(form_frame, text="Nome:").grid(
            row=0, column=0, sticky='w', pady=5, padx=10)
        self.perfil_nome = ctk.CTkEntry(form_frame, width=250)
        self.perfil_nome.grid(row=0, column=1, pady=5, padx=10, sticky='ew')
        self.perfil_nome.insert(0, self.usuario_atual['nome'])
        
        # Email (somente leitura)
        ctk.CTkLabel(form_frame, text="E-mail:").grid(
            row=1, column=0, sticky='w', pady=5, padx=10)
        email_entry = ctk.CTkEntry(form_frame, width=250)
        email_entry.grid(row=1, column=1, pady=5, padx=10, sticky='ew')
        email_entry.insert(0, self.usuario_atual['email'])
        email_entry.configure(state='disabled')  # Desabilita edição
        
        # Tipo de usuário (somente leitura)
        ctk.CTkLabel(form_frame, text="Tipo de Usuário:").grid(
            row=2, column=0, sticky='w', pady=5, padx=10)
        tipo_entry = ctk.CTkEntry(form_frame, width=250)
        tipo_entry.grid(row=2, column=1, pady=5, padx=10, sticky='ew')
        tipo_entry.insert(0, self.usuario_atual['tipo'])
        tipo_entry.configure(state='disabled')  # Desabilita edição
        
        # Seção de mudança de senha
        senha_frame = ctk.CTkFrame(perfil_frame)
        senha_frame.pack(fill='x', pady=20)
        
        ctk.CTkLabel(senha_frame, text="Alterar Senha", 
                  font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=10)
        
        # Formulário de senha
        senha_form = ctk.CTkFrame(senha_frame)
        senha_form.pack(fill='x')
        
        # Senha atual
        ctk.CTkLabel(senha_form, text="Senha Atual:").grid(
            row=0, column=0, sticky='w', pady=5, padx=10)
        self.perfil_senha_atual = ctk.CTkEntry(senha_form, width=250, show="*")
        self.perfil_senha_atual.grid(row=0, column=1, pady=5, padx=10, sticky='ew')
        
        # Nova senha
        ctk.CTkLabel(senha_form, text="Nova Senha:").grid(
            row=1, column=0, sticky='w', pady=5, padx=10)
        self.perfil_senha_nova = ctk.CTkEntry(senha_form, width=250, show="*")
        self.perfil_senha_nova.grid(row=1, column=1, pady=5, padx=10, sticky='ew')
        
        # Confirmar nova senha
        ctk.CTkLabel(senha_form, text="Confirmar Nova Senha:").grid(
            row=2, column=0, sticky='w', pady=5, padx=10)
        self.perfil_senha_confirma = ctk.CTkEntry(senha_form, width=250, show="*")
        self.perfil_senha_confirma.grid(row=2, column=1, pady=5, padx=10, sticky='ew')
        
        # Requisitos de senha
        info_frame = ctk.CTkFrame(senha_frame)
        info_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(info_frame, text="Requisitos de senha:", 
                  font=('Helvetica', 12, 'bold')).pack(anchor='w')
        ctk.CTkLabel(info_frame, text="- Mínimo de 6 caracteres", 
                  font=('Helvetica', 11)).pack(anchor='w')
        ctk.CTkLabel(info_frame, text="- Recomendado incluir letras maiúsculas, minúsculas, números e caracteres especiais", 
                  font=('Helvetica', 11)).pack(anchor='w')
        
        # Coluna da direita - Preferências
        pref_frame = ctk.CTkFrame(content_frame)
        pref_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Título da seção
        ctk.CTkLabel(pref_frame, text="Preferências", 
                  font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=10)
        
        # Aparência
        tema_frame = ctk.CTkFrame(pref_frame)
        tema_frame.pack(fill='x', pady=10)
        
        ctk.CTkLabel(tema_frame, text="Tema da Interface:", 
                  font=('Helvetica', 12, 'bold')).pack(anchor='w', padx=10, pady=5)
        
        # Opções de tema
        self.tema_var = ctk.StringVar(value=ctk.get_appearance_mode())
        
        tema_options = ctk.CTkFrame(tema_frame)
        tema_options.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkRadioButton(tema_options, text="Claro", 
                        variable=self.tema_var, value="Light").pack(side='left', padx=20)
        ctk.CTkRadioButton(tema_options, text="Escuro", 
                        variable=self.tema_var, value="Dark").pack(side='left', padx=20)
        ctk.CTkRadioButton(tema_options, text="Sistema", 
                        variable=self.tema_var, value="System").pack(side='left', padx=20)
        
        # Opção para fixar o tema (adicionando layout responsivo)
        self.fixar_tema_frame = ctk.CTkFrame(tema_frame)
        self.fixar_tema_frame.pack(fill='x', padx=10, pady=10)
        
        self.fixar_tema_var = ctk.BooleanVar(value=False)
        fixar_tema_check = ctk.CTkCheckBox(self.fixar_tema_frame, text="Fixar este tema para todas as sessões",
                                     variable=self.fixar_tema_var)
        fixar_tema_check.pack(anchor='w')
        
        # Texto explicativo
        ctk.CTkLabel(self.fixar_tema_frame, text="Quando fixado, o tema será aplicado automaticamente em futuros logins",
                  font=('Helvetica', 10), text_color="gray").pack(anchor='w', pady=(0, 5))
        
        # Botão para aplicar tema - movido para perto das opções de tema
        self.btn_tema = ctk.CTkButton(self.fixar_tema_frame, text="Aplicar Tema", 
                                  width=120, height=32,
                   command=self.aplicar_tema,
                                  fg_color="#6c757d")
        self.btn_tema.pack(anchor='w', pady=10, padx=0)
        
        # Barra fixa na parte inferior para os botões de ação (sempre visível)
        self.btn_frame = ctk.CTkFrame(container_frame, height=50)
        self.btn_frame.pack(side='bottom', fill='x', pady=(5, 0))
        
        # Botões fixos com layout sempre horizontal
        # Botão para alterar apenas senha (agora à direita, junto do botão Salvar)
        self.btn_senha = ctk.CTkButton(self.btn_frame, text="Alterar Senha", 
                                   width=120, height=32,
                                   command=self.alterar_senha_perfil,
                                   fg_color="#007bff")
        self.btn_senha.pack(side='right', padx=10, pady=10)
        
        # Botão para salvar alterações (à direita)
        self.btn_salvar = ctk.CTkButton(self.btn_frame, text="Salvar Alterações", 
                                    width=140, height=32,
                                    command=self.salvar_alteracoes_perfil,
                                    fg_color="#28a745")
        self.btn_salvar.pack(side='right', padx=10, pady=10)
        
        # Verificar tamanho da janela e ajustar layout conforme necessário
        self.verificar_tamanho_janela()
        # Vincular função de verificação de tamanho ao redimensionamento da janela
        self.root.bind("<Configure>", lambda e: self.verificar_tamanho_janela())

    def verificar_tamanho_janela(self):
        """Verifica o tamanho da janela e ajusta o layout para responsividade"""
        try:
            largura_atual = self.root.winfo_width()
            
            # Se a largura for menor que 800px, ajustamos o layout para notebooks/telas menores
            if hasattr(self, 'fixar_tema_frame'):
                if largura_atual < 650:  # Para telas muito pequenas
                    # Layout compacto para telas muito pequenas
                    self.fixar_tema_frame.pack(fill='x', padx=2, pady=2)
                    # Texto e botões mais curtos
                    for widget in self.fixar_tema_frame.winfo_children():
                        if isinstance(widget, ctk.CTkCheckBox):
                            widget.configure(text="Fixar")
                        # Botão mais compacto
                        if isinstance(widget, ctk.CTkButton):
                            widget.configure(width=80, text="Aplicar")
                elif largura_atual < 800:  # Para telas médias/pequenas
                    # Para telas menores, garantimos que a opção de fixar tema continue visível
                    self.fixar_tema_frame.pack(fill='x', padx=5, pady=5)
                    # Ajuste no espaçamento para ocupar menos espaço horizontal
                    for widget in self.fixar_tema_frame.winfo_children():
                        if isinstance(widget, ctk.CTkCheckBox):
                            widget.configure(text="Fixar tema")
                        # Ajusta o botão de aplicar tema para telas menores
                        if isinstance(widget, ctk.CTkButton):
                            widget.configure(width=100, text="Aplicar tema")
                else:  # Para telas normais
                    # Para telas maiores, mantemos o layout normal
                    self.fixar_tema_frame.pack(fill='x', padx=10, pady=10)
                    # Restaura o texto original
                    for widget in self.fixar_tema_frame.winfo_children():
                        if isinstance(widget, ctk.CTkCheckBox):
                            widget.configure(text="Fixar este tema para todas as sessões")
                        # Restaura o botão de aplicar tema
                        if isinstance(widget, ctk.CTkButton):
                            widget.configure(width=120, text="Aplicar Tema")
            
            # Ajusta os tamanhos dos botões com base na largura da tela (apenas os que permanecem na barra inferior)
            if hasattr(self, 'btn_frame') and hasattr(self, 'btn_salvar') and hasattr(self, 'btn_senha'):
                if largura_atual < 550:  # Para telas muito pequenas
                    # Botões mais estreitos com ícones
                    self.btn_senha.configure(width=70, text="🔑")
                    self.btn_salvar.configure(width=70, text="💾")
                elif largura_atual < 650:  # Para telas pequenas
                    # Botões mais estreitos
                    self.btn_senha.configure(width=90, text="Senha")
                    self.btn_salvar.configure(width=90, text="Salvar")
                elif largura_atual < 800:  # Para telas médias/pequenas
                    # Botões com texto mais curto
                    self.btn_senha.configure(width=100, text="Alterar Senha")
                    self.btn_salvar.configure(width=100, text="Salvar")
                else:  # Para telas normais
                    # Tamanho e texto originais
                    self.btn_senha.configure(width=120, text="Alterar Senha")
                    self.btn_salvar.configure(width=140, text="Salvar Alterações")
        except Exception as e:
            # Tratamento de erros para não impactar a aplicação
            print(f"Erro ao verificar tamanho da janela: {e}")

    def salvar_alteracoes_perfil(self):
        """Salva as alterações feitas no perfil do usuário"""
        # Obtém o novo nome
        novo_nome = self.perfil_nome.get()
        
        # Validação básica
        if not novo_nome:
            messagebox.showerror("Erro", "O nome não pode ficar em branco!")
            return
        
        # Aplica a alteração de nome
        for usuario in self.usuarios:
            if usuario['email'] == self.usuario_atual['email']:
                usuario['nome'] = novo_nome
                self.usuario_atual['nome'] = novo_nome
                break
        
        # Verifica se também quer alterar a senha
        if self.perfil_senha_atual.get() and self.perfil_senha_nova.get() and self.perfil_senha_confirma.get():
            self.alterar_senha_perfil()
        else:
            # Salva apenas as alterações de nome
            self.salvar_dados()
            messagebox.showinfo("Sucesso", "Perfil atualizado com sucesso!")
        
        # Aplica tema se selecionado
        if self.tema_var.get() != ctk.get_appearance_mode():
            self.aplicar_tema()

    def alterar_senha_perfil(self):
        """Altera a senha do usuário atual"""
        senha_atual = self.perfil_senha_atual.get()
        senha_nova = self.perfil_senha_nova.get()
        senha_confirma = self.perfil_senha_confirma.get()
        
        # Validação básica
        if not all([senha_atual, senha_nova, senha_confirma]):
            messagebox.showerror("Erro", "Preencha todos os campos de senha para alterá-la!")
            return
        
        # Verifica se a senha atual está correta
        if senha_atual != self.usuario_atual['senha']:
            messagebox.showerror("Erro", "Senha atual incorreta!")
            return
        
        # Verifica se as senhas novas coincidem
        if senha_nova != senha_confirma:
            messagebox.showerror("Erro", "A nova senha e a confirmação não coincidem!")
            return
        
        # Verifica a força da nova senha
        senha_valida, msg_erro = self.verificar_senha_forte(senha_nova)
        if not senha_valida:
            messagebox.showerror("Erro na senha", msg_erro)
            return
        
        # Aplica a alteração de senha
        for usuario in self.usuarios:
            if usuario['email'] == self.usuario_atual['email']:
                usuario['senha'] = senha_nova
                self.usuario_atual['senha'] = senha_nova
                break
        
        # Salva os dados
        self.salvar_dados()
        messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
        
        # Limpa os campos de senha
        self.perfil_senha_atual.delete(0, 'end')
        self.perfil_senha_nova.delete(0, 'end')
        self.perfil_senha_confirma.delete(0, 'end')

    def aplicar_tema(self):
        """Aplica o tema selecionado à interface"""
        novo_tema = self.tema_var.get()
        ctk.set_appearance_mode(novo_tema)
        
        # Salvar o tema como preferência do usuário se a opção de fixar estiver marcada
        if hasattr(self, 'fixar_tema_var') and self.fixar_tema_var.get():
            for usuario in self.usuarios:
                if usuario['email'] == self.usuario_atual['email']:
                    usuario['tema_preferido'] = novo_tema
                    break
            self.salvar_dados()
            self.mostrar_feedback(f"O tema foi alterado para {novo_tema} e será mantido para futuros logins!", tipo="sucesso")
        else:
            self.mostrar_feedback(f"O tema foi alterado para {novo_tema}!", tipo="info")
        
        # Verificar novamente o layout após aplicar o tema
        self.verificar_tamanho_janela()

    def criar_aba_cadastro_usuario(self, frame):
        """Cria a aba para cadastro de novos usuários (apenas para ADM)"""
        # Frame principal
        main_frame = ctk.CTkFrame(frame)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Cabeçalho
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Cadastrar Novo Usuário", font=('Helvetica', 18, 'bold')).pack()
        ctk.CTkLabel(header_frame, text="Preencha os dados do novo usuário", 
                 font=('Helvetica', 14)).pack()
        
        # Formulário
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(expand=True, fill='both')
        
        # Campos do formulário
        ctk.CTkLabel(form_frame, text="Nome:").grid(
            row=0, column=0, sticky='w', pady=5)
        self.novo_usuario_nome = ctk.CTkEntry(form_frame, width=300)
        self.novo_usuario_nome.grid(row=0, column=1, pady=5, ipady=5, sticky='ew')
        
        ctk.CTkLabel(form_frame, text="E-mail:").grid(
            row=1, column=0, sticky='w', pady=5)
        self.novo_usuario_email = ctk.CTkEntry(form_frame, width=300)
        self.novo_usuario_email.grid(row=1, column=1, pady=5, ipady=5, sticky='ew')
        
        # Configuração do autocompletar para email no cadastro de ADM
        self.novo_usuario_email.bind('<KeyRelease>', self.autocomplete_email_admin)
        
        # Sugestões de domínio para o cadastro de ADM
        self.sugestoes_admin_frame = ctk.CTkFrame(form_frame)
        self.sugestoes_admin_frame.grid(row=2, column=1, sticky='w', pady=0)
        self.sugestoes_admin_frame.grid_remove()  # Inicialmente oculto
        
        ctk.CTkLabel(form_frame, text="Senha:").grid(
            row=3, column=0, sticky='w', pady=5)
        self.novo_usuario_senha = ctk.CTkEntry(form_frame, width=300, show="*")
        self.novo_usuario_senha.grid(row=3, column=1, pady=5, ipady=5, sticky='ew')
        
        # Requisitos de senha
        requisitos_frame = ctk.CTkFrame(main_frame)
        requisitos_frame.pack(fill='x', pady=10)
        
        ctk.CTkLabel(requisitos_frame, text="Requisitos de senha:", 
                  font=('Helvetica', 12, 'bold')).pack(anchor='w')
        ctk.CTkLabel(requisitos_frame, text="- Mínimo de 6 caracteres", 
                  font=('Helvetica', 11)).pack(anchor='w')
        ctk.CTkLabel(requisitos_frame, text="- Recomendado incluir letras maiúsculas, minúsculas, números e caracteres especiais", 
                  font=('Helvetica', 11)).pack(anchor='w')
        
        # Botão de envio
        btn_frame = ctk.CTkFrame(form_frame)
        btn_frame.grid(row=4, column=1, pady=20, sticky='e', padx=10)
        
        ctk.CTkButton(btn_frame, text="Cadastrar Usuário", command=self.cadastrar_novo_usuario).pack(side='right', ipady=5, ipadx=20)

    def autocomplete_email_admin(self, event=None):
        """Autocompleta o email com domínios comuns na tela de cadastro do administrador"""
        # Limpa o frame de sugestões
        for widget in self.sugestoes_admin_frame.winfo_children():
            widget.destroy()
        
        # Obtém o texto atual
        texto = self.novo_usuario_email.get()
        
        # Verifica se tem o caractere @ 
        if '@' in texto:
            parte_local, dominio = texto.split('@', 1)
            
            # Se já tiver @ mas o domínio estiver incompleto, mostrar sugestões
            if dominio and not '.' in dominio:
                # Mostra o frame de sugestões
                self.sugestoes_admin_frame.grid()
                
                # Cria um botão para cada domínio que começa com o texto digitado
                sugestoes_count = 0
                for i, dominio_completo in enumerate(self.dominios_email):
                    if dominio_completo.startswith(dominio):
                        sugestao = parte_local + '@' + dominio_completo
                        btn = ctk.CTkButton(
                            self.sugestoes_admin_frame, 
                            text=sugestao,
                            width=300,
                            height=25,
                            fg_color="#6c757d",
                            command=lambda s=sugestao: self.aplicar_sugestao_admin(s)
                        )
                        btn.grid(row=sugestoes_count, column=0, pady=2, padx=5, sticky='w')
                        sugestoes_count += 1
            else:
                # Se já tiver o ponto no domínio, esconde as sugestões
                self.sugestoes_admin_frame.grid_remove()
        else:
            # Se não tiver @, esconde as sugestões
            self.sugestoes_admin_frame.grid_remove()

    def aplicar_sugestao_admin(self, sugestao):
        """Aplica a sugestão de email selecionada na tela de cadastro do administrador"""
        # Define o texto do email
        self.novo_usuario_email.delete(0, 'end')
        self.novo_usuario_email.insert(0, sugestao)
        
        # Esconde as sugestões
        self.sugestoes_admin_frame.grid_remove()
        
        # Foca no campo de senha
        self.novo_usuario_senha.focus_set()

    def cadastrar_novo_usuario(self):
        """Cadastra um novo usuário (apenas para ADM)"""
        nome = self.novo_usuario_nome.get()
        email = self.novo_usuario_email.get()
        senha = self.novo_usuario_senha.get()
        
        # Validação básica
        if not all([nome, email, senha]):
            self.mostrar_feedback("Preencha todos os campos!", tipo="erro")
            return
        
        # Verificação de senha forte
        senha_valida, msg_erro = self.verificar_senha_forte(senha)
        if not senha_valida:
            self.mostrar_feedback(msg_erro, tipo="erro")
            return
        
        # Verifica se o e-mail já está cadastrado
        if any(u['email'] == email for u in self.usuarios):
            self.mostrar_feedback("Este e-mail já está cadastrado!", tipo="erro")
            return
        
        # Adiciona o novo usuário (sempre como usuário comum)
        novo_usuario = {
            'nome': nome,
            'email': email,
            'senha': senha,
            'tipo': 'Usuário'
        }
        
        self.usuarios.append(novo_usuario)
        self.salvar_dados()
        
        self.mostrar_feedback("Usuário cadastrado com sucesso!", tipo="sucesso")
        
        # Limpa os campos
        self.novo_usuario_nome.delete(0, "end")
        self.novo_usuario_email.delete(0, "end")
        self.novo_usuario_senha.delete(0, "end")

    def criar_aba_tarefas(self, frame):
        """Cria a aba de visualização de tarefas com detalhes expandidos e status em andamento"""
        # Filtra tarefas
        if self.usuario_logado_como_adm():
            tarefas = self.tarefas
            titulo = "Todas as Tarefas"
        else:
            tarefas = [t for t in self.tarefas if t['destinatario_email'] == self.usuario_atual['email']]
            titulo = "Minhas Tarefas"
        
        # Aplica filtro de pesquisa, se ativo
        if self.pesquisa_ativa and self.termo_pesquisa.get():
            termo = self.termo_pesquisa.get().lower()
            tarefas = [t for t in tarefas if 
                      termo in t['titulo'].lower() or 
                      termo in t['descricao'].lower() or
                      termo in t['remetente_nome'].lower() or
                      termo in t['destinatario_nome'].lower()]
            titulo = f"Resultados da pesquisa: {self.termo_pesquisa.get()}"
        
        # Cabeçalho
        header_frame = ctk.CTkFrame(frame)
        header_frame.pack(fill='x', pady=10, padx=10)
        
        title_label = ctk.CTkLabel(header_frame, text=titulo, font=('Helvetica', 18, 'bold'))
        title_label.pack(side='left')
        
        # Se estiver com pesquisa ativa, mostra botão para limpar
        if self.pesquisa_ativa:
            clear_btn = ctk.CTkButton(header_frame, text="❌ Limpar pesquisa", 
                                 fg_color='#dc3545', width=120, height=28,
                                 command=self.limpar_pesquisa)
            clear_btn.pack(side='left', padx=15)
        
        # Controles de filtro
        filter_frame = ctk.CTkFrame(header_frame)
        filter_frame.pack(side='right')
        
        self.filtro_var = ctk.StringVar(value="Todas")
        all_rb = ctk.CTkRadioButton(filter_frame, text="Todas", variable=self.filtro_var, value="Todas", 
                         command=self.atualizar_filtro_tarefas)
        all_rb.pack(side='left', padx=10)
        
        pending_rb = ctk.CTkRadioButton(filter_frame, text="Pendentes", variable=self.filtro_var, value="Pendentes", 
                         command=self.atualizar_filtro_tarefas)
        pending_rb.pack(side='left', padx=10)
        
        progress_rb = ctk.CTkRadioButton(filter_frame, text="Em Andamento", variable=self.filtro_var, value="Em Andamento", 
                         command=self.atualizar_filtro_tarefas)
        progress_rb.pack(side='left', padx=10)
        
        done_rb = ctk.CTkRadioButton(filter_frame, text="Concluídas", variable=self.filtro_var, value="Concluídas", 
                         command=self.atualizar_filtro_tarefas)
        done_rb.pack(side='left', padx=10)
        
        # Frame para tabela de tarefas
        self.list_frame = ctk.CTkFrame(frame)
        self.list_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Carregar tarefas iniciais
        self.tarefas_filtradas = tarefas
        self.exibir_tarefas()
        
        # Frame para detalhes da tarefa
        self.detalhes_frame = ctk.CTkFrame(frame)
        self.detalhes_frame.pack(fill='x', padx=10, pady=10)
        
        ctk.CTkLabel(self.detalhes_frame, text="Detalhes da Tarefa", font=('Helvetica', 14, 'bold')).pack(anchor='w', padx=10, pady=5)
        
        # Inicializa o frame de detalhes vazio
        self.detalhes_conteudo = ctk.CTkFrame(self.detalhes_frame)
        self.detalhes_conteudo.pack(fill='x', padx=10, pady=5)
        
        # Texto de instrução inicial para selecionar uma tarefa
        sem_selecao = ctk.CTkLabel(self.detalhes_conteudo, 
                               text="Selecione uma tarefa para ver seus detalhes",
                               font=('Helvetica', 12),
                               text_color="gray")
        sem_selecao.pack(pady=20)
        
        # Botões para usuários comuns - Agora em um frame separado para não afetar o layout geral
        if not self.usuario_logado_como_adm():
            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")  # Fundo transparente para não alterar o layout
            btn_frame.pack(pady=5, padx=10, fill='x')
            
            # Container para os botões centralizados
            btn_container = ctk.CTkFrame(btn_frame, fg_color="transparent")
            btn_container.pack(anchor='w')
            
            andamento_btn = ctk.CTkButton(btn_container, text="🔄 Em Andamento", 
                        fg_color="#FFC107", text_color="#000000",
                        command=self.marcar_tarefa_selecionada_andamento)
            andamento_btn.pack(side='left', padx=5, ipady=2, ipadx=5)
            
            concluir_btn = ctk.CTkButton(btn_container, text="✅ Concluir Tarefa",
                        fg_color="#28a745",
                        command=self.marcar_tarefa_selecionada_concluida)
            concluir_btn.pack(side='left', padx=5, ipady=2, ipadx=5)
        
        # Variável para armazenar o índice da tarefa selecionada
        self.tarefa_selecionada = None
        
        # Adicionar atalhos específicos para esta tela
        self.configurar_atalhos_tarefas()
    
    def configurar_atalhos_tarefas(self):
        """Configura atalhos específicos para a tela de tarefas"""
        if not KEYBOARD_DISPONIVEL:
            return
            
        try:
            if not self.usuario_logado_como_adm():
                # Adiciona atalhos para usuários comuns
                keyboard.add_hotkey('ctrl+a', lambda: self.marcar_tarefa_selecionada_andamento())
                keyboard.add_hotkey('ctrl+c', lambda: self.marcar_tarefa_selecionada_concluida())
        except Exception:
            # Ignora erros ao tentar registrar atalhos
            pass
    
    def limpar_pesquisa(self):
        """Limpa a pesquisa atual e retorna à visualização normal de tarefas"""
        self.pesquisa_ativa = False
        self.termo_pesquisa.set("")
        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, 'end')
        self.mostrar_aba_tarefas()
    
    def atualizar_filtro_tarefas(self):
        """Atualiza a lista de tarefas com base no filtro selecionado"""
        filtro = self.filtro_var.get()
        
        # Determinar quais tarefas devem ser mostradas
        if self.usuario_logado_como_adm():
            tarefas_base = self.tarefas
        else:
            tarefas_base = [t for t in self.tarefas if t['destinatario_email'] == self.usuario_atual['email']]
        
        # Aplicar filtro
        if filtro == "Todas":
            self.tarefas_filtradas = tarefas_base
        elif filtro == "Pendentes":
            self.tarefas_filtradas = [t for t in tarefas_base if not t['concluida'] and not t.get('em_andamento', False)]
        elif filtro == "Em Andamento":
            self.tarefas_filtradas = [t for t in tarefas_base if t.get('em_andamento', False)]
        elif filtro == "Concluídas":
            self.tarefas_filtradas = [t for t in tarefas_base if t['concluida']]
        
        # Limpar e recarregar as tarefas
        self.exibir_tarefas()
    
    def exibir_tarefas(self):
        """Exibe as tarefas filtradas na interface com suporte a drag-and-drop"""
        # Limpar o frame de lista
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        # Verifica se há tarefas para exibir
        if not self.tarefas_filtradas:
            # Mensagem quando não há tarefas
            empty_frame = ctk.CTkFrame(self.list_frame)
            empty_frame.pack(expand=True, fill='both', padx=20, pady=20)
            
            msg_sem_tarefas = "Nenhuma tarefa encontrada"
            if self.pesquisa_ativa:
                msg_sem_tarefas = f"Nenhuma tarefa encontrada para: '{self.termo_pesquisa.get()}'"
            
            ctk.CTkLabel(empty_frame, 
                      text=msg_sem_tarefas,
                      font=('Helvetica', 14)).pack(expand=True, pady=50)
            return
        
        # Cabeçalhos
        headers = ["ID", "Título", "Descrição", "Remetente", "Destinatário", "Data", "Status", "Ações"]
        header_frame = ctk.CTkFrame(self.list_frame)
        header_frame.pack(fill='x', pady=5)
        
        # Configurar cabeçalhos
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(header_frame, text=header, font=('Helvetica', 12, 'bold'))
            header_label.grid(row=0, column=i, padx=5, pady=5, sticky='w')
            header_frame.grid_columnconfigure(i, weight=1)
        
        # Frame para lista de tarefas com scroll
        tasks_container = ctk.CTkScrollableFrame(self.list_frame)
        tasks_container.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Variáveis para drag and drop
        self.drag_data = {"widget": None, "index": None, "x": 0, "y": 0}
        
        # Adicionar tarefas à lista
        self.task_rows = []
        for i, tarefa in enumerate(self.tarefas_filtradas):
            # Criar frame com altura fixa para cada tarefa
            task_frame = ctk.CTkFrame(tasks_container, height=32)
            task_frame.pack(fill='x', pady=2, padx=2)
            task_frame.pack_propagate(False)  # Impede que o conteúdo altere o tamanho do frame
            
            # Configurar grid interno
            grid_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
            grid_frame.pack(fill='both', expand=True)
            
            # Definir cores baseadas no status para melhor visibilidade
            if tarefa['concluida']:
                # Verde mais claro como fundo e texto bem escuro
                task_frame.configure(fg_color='#d4edda')
                grid_frame.configure(fg_color='#d4edda')
                text_color = '#0a3622'  # Verde muito escuro para texto
                status_text = "Concluída"
            elif tarefa.get('em_andamento', False):
                # Amarelo claro como fundo e texto escuro
                task_frame.configure(fg_color='#fff3cd')
                grid_frame.configure(fg_color='#fff3cd')
                text_color = '#533f03'  # Amarelo muito escuro para texto
                status_text = "Em Andamento"
            else:
                # Fundo vermelho claro para tarefas pendentes
                task_frame.configure(fg_color='#f8d7da')
                grid_frame.configure(fg_color='#f8d7da')
                text_color = '#721c24'  # Vermelho escuro para texto
                status_text = "Pendente"
            
            # Configurar grid colunas - larguras fixas para todas as tarefas
            for j in range(8):
                grid_frame.grid_columnconfigure(j, weight=1)
            grid_frame.grid_rowconfigure(0, weight=1)
            
            # Adicionar prioridade ao status se disponível
            if 'prioridade' in tarefa:
                status_text = f"{status_text} ({tarefa['prioridade']})"
            
            # Ícone de arrasto para drag-and-drop (se for o ADM)
            if self.usuario_logado_como_adm():
                drag_icon = ctk.CTkLabel(grid_frame, text="☰", font=('Helvetica', 12, 'bold'), 
                                     width=20, text_color="#6c757d", height=22)
                drag_icon.grid(row=0, column=0, padx=(0, 5), pady=2, sticky='w')
                
                # Configurar eventos de drag and drop
                drag_icon.bind("<ButtonPress-1>", lambda e, f=task_frame, idx=i: self.iniciar_arrasto(e, f, idx))
                drag_icon.bind("<B1-Motion>", self.arrastar)
                drag_icon.bind("<ButtonRelease-1>", self.finalizar_arrasto)
                
                # Mantemos apenas este tooltip importante
                ToolTip(drag_icon, "Arraste para reordenar a tarefa")
                
                # Dados da tarefa com tamanho uniforme, começando pela coluna 1
                id_label = ctk.CTkLabel(grid_frame, text=str(i+1), font=('Helvetica', 11), 
                                    width=30, text_color=text_color, height=22)
                id_label.grid(row=0, column=1, padx=2, pady=2, sticky='w')
                
                titulo_label = ctk.CTkLabel(grid_frame, text=tarefa['titulo'], font=('Helvetica', 11), 
                                        width=80, text_color=text_color, height=22)
                titulo_label.grid(row=0, column=2, padx=2, pady=2, sticky='w')
            else:
                # Layout normal para usuários não-admin (sem drag and drop)
                id_label = ctk.CTkLabel(grid_frame, text=str(i+1), font=('Helvetica', 11), 
                                    width=30, text_color=text_color, height=22)
                id_label.grid(row=0, column=0, padx=2, pady=2, sticky='w')
                
                titulo_label = ctk.CTkLabel(grid_frame, text=tarefa['titulo'], font=('Helvetica', 11), 
                                        width=80, text_color=text_color, height=22)
                titulo_label.grid(row=0, column=1, padx=2, pady=2, sticky='w')
            
            # Configuração do restante das colunas depende se é ADM ou não
            col_offset = 1 if self.usuario_logado_como_adm() else 0
            
            # Descrição truncada para evitar linhas muito longas
            desc_texto = tarefa['descricao'][:25] + "..." if len(tarefa['descricao']) > 25 else tarefa['descricao']
            desc_label = ctk.CTkLabel(grid_frame, text=desc_texto, font=('Helvetica', 11), 
                                   width=100, text_color=text_color, height=22)
            desc_label.grid(row=0, column=2+col_offset, padx=2, pady=2, sticky='w')
            
            remetente_label = ctk.CTkLabel(grid_frame, text=tarefa['remetente_nome'], font=('Helvetica', 11), 
                                        width=80, text_color=text_color, height=22)
            remetente_label.grid(row=0, column=3+col_offset, padx=2, pady=2, sticky='w')
            
            destinatario_label = ctk.CTkLabel(grid_frame, text=tarefa['destinatario_nome'], font=('Helvetica', 11), 
                                          width=80, text_color=text_color, height=22)
            destinatario_label.grid(row=0, column=4+col_offset, padx=2, pady=2, sticky='w')
            
            data_label = ctk.CTkLabel(grid_frame, text=tarefa['data_criacao'], font=('Helvetica', 11), 
                                   width=80, text_color=text_color, height=22)
            data_label.grid(row=0, column=5+col_offset, padx=2, pady=2, sticky='w')
            
            # Status com destaque apropriado para cada estado
            status_color = text_color
            if tarefa['concluida']:
                status_color = '#087f23'  # Verde mais escuro para destaque
            elif tarefa.get('em_andamento', False):
                status_color = '#b76e00'  # Amarelo escuro para destaque
            else:
                status_color = '#c62828'  # Vermelho escuro para pendentes
                
            status_label = ctk.CTkLabel(grid_frame, text=status_text, 
                                     text_color=status_color,
                                     fg_color="transparent",
                                     font=('Helvetica', 11, 'bold'),
                                     width=100, height=22)
            status_label.grid(row=0, column=6+col_offset, padx=2, pady=2, sticky='w')
            
            # Botões de ação com tamanho fixo
            btn_frame = ctk.CTkFrame(grid_frame, fg_color="transparent", height=22)
            btn_frame.grid(row=0, column=7+col_offset, padx=2, pady=2, sticky='e')
            
            # Tamanho uniforme para botões
            button_size = 20  # Reduzido para garantir consistência
            
            if not self.usuario_logado_como_adm() and not tarefa['concluida']:
                if not tarefa.get('em_andamento', False):
                    andamento_btn = ctk.CTkButton(btn_frame, text="▶️", width=button_size, height=button_size, 
                               fg_color="#FFC107", text_color="#000000",
                               hover_color="#e0a800",
                               corner_radius=3,
                               command=lambda idx=i: self.marcar_tarefa_andamento_direto(idx))
                    andamento_btn.pack(side='left', padx=1)
                
                concluir_btn = ctk.CTkButton(btn_frame, text="✓", width=button_size, height=button_size, 
                           fg_color="#28a745", text_color="#FFFFFF",
                           hover_color="#218838",
                           corner_radius=3,
                           command=lambda idx=i: self.marcar_tarefa_concluida_direto(idx))
                concluir_btn.pack(side='left', padx=1)
            
            # Índice na lista original
            idx_original = self.tarefas.index(tarefa)
            
            # Guardar referência às linhas para posterior seleção
            self.task_rows.append((task_frame, idx_original))
            
            # Adicionar evento de clique para selecionar
            task_frame.bind("<Button-1>", lambda e, idx=idx_original: self.selecionar_tarefa(idx))
            grid_frame.bind("<Button-1>", lambda e, idx=idx_original: self.selecionar_tarefa(idx))
            for widget in grid_frame.winfo_children():
                if not isinstance(widget, ctk.CTkButton):  # Não adiciona aos botões para evitar conflito
                    widget.bind("<Button-1>", lambda e, idx=idx_original: self.selecionar_tarefa(idx))

    def iniciar_arrasto(self, event, widget, index):
        """Inicia o arrastar de uma tarefa"""
        try:
            if not self.usuario_logado_como_adm():
                return  # Apenas ADM pode reordenar
                
            self.drag_data["widget"] = widget
            self.drag_data["index"] = index
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            # Destacar visualmente o item que está sendo arrastado
            widget.configure(border_width=2, border_color="#4a6da7")
        except Exception:
            # Se ocorrer algum erro, ignora e limpa os dados
            self.drag_data = {"widget": None, "index": None, "x": 0, "y": 0}
    
    def arrastar(self, event):
        """Arrasta uma tarefa"""
        try:
            if not self.usuario_logado_como_adm() or not self.drag_data["widget"]:
                return
            
            # Calcular a nova posição
            delta_y = event.y_root - self.drag_data["widget"].winfo_rooty() - self.drag_data["y"]
            
            # Mover o widget visualmente para dar feedback ao usuário
            if delta_y != 0:
                # Obter a posição atual no pack manager
                info = self.drag_data["widget"].pack_info()
                # Ajustar a posição levemente para dar feedback visual
                self.drag_data["widget"].pack_configure(pady=(2 + delta_y/10, 2))
        except Exception:
            # Em caso de erro, cancela o arrasto
            self.drag_data = {"widget": None, "index": None, "x": 0, "y": 0}
    
    def finalizar_arrasto(self, event):
        """Finaliza o arrastar e reorganiza as tarefas"""
        try:
            if not self.usuario_logado_como_adm() or not self.drag_data["widget"]:
                return
                
            # Determinar a nova posição com base na posição Y do mouse
            widget_atual = self.drag_data["widget"]
            index_atual = self.drag_data["index"]
            y_atual = event.y_root
            
            # Encontrar a tarefa mais próxima da posição atual do mouse
            novo_index = index_atual
            menor_distancia = float('inf')
            
            for i, (frame, _) in enumerate(self.task_rows):
                if i != index_atual:
                    try:
                        y_frame = frame.winfo_rooty() + frame.winfo_height() / 2
                        distancia = abs(y_atual - y_frame)
                        if distancia < menor_distancia:
                            menor_distancia = distancia
                            novo_index = i
                    except:
                        continue
            
            # Se a posição mudou, reorganizar as tarefas
            if novo_index != index_atual:
                # Mova a tarefa na lista filtrada
                tarefa = self.tarefas_filtradas.pop(index_atual)
                self.tarefas_filtradas.insert(novo_index, tarefa)
                
                # Atualizar a lista original também
                idx_original = self.tarefas.index(tarefa)
                nova_posicao = self.tarefas.index(self.tarefas_filtradas[0])  # Posição de referência
                
                # Remover da posição original e inserir na nova posição
                self.tarefas.remove(tarefa)
                self.tarefas.insert(nova_posicao + novo_index, tarefa)
                
                # Salvar as alterações
                self.salvar_dados()
                
                # Mostrar mensagem de feedback
                self.mostrar_feedback("Tarefa reorganizada com sucesso!", tipo="sucesso")
                
                # Atualizar a visualização
                self.exibir_tarefas()
            else:
                # Restaurar a aparência normal
                widget_atual.configure(border_width=0)
        except Exception:
            # Em caso de erro, tenta restaurar o estado e atualiza a interface
            try:
                self.exibir_tarefas()
            except:
                pass
        finally:
            # Sempre limpa os dados de arrasto
            self.drag_data = {"widget": None, "index": None, "x": 0, "y": 0}

    def mostrar_feedback(self, mensagem, tipo="info", duracao=2000):
        """Mostra um feedback temporário na interface"""
        try:
            # Definir cores com base no tipo de mensagem
            if tipo == "sucesso":
                bg_color = "#d4edda"
                text_color = "#155724"
                icone = "✅"
            elif tipo == "erro":
                bg_color = "#f8d7da"
                text_color = "#721c24"
                icone = "❌"
            elif tipo == "aviso":
                bg_color = "#fff3cd"
                text_color = "#856404"
                icone = "⚠️"
            else:  # info
                bg_color = "#d1ecf1"
                text_color = "#0c5460"
                icone = "ℹ️"
            
            # Criar um frame flutuante para o feedback
            feedback_frame = ctk.CTkFrame(self.root, fg_color=bg_color, corner_radius=10)
            feedback_frame.place(relx=0.5, rely=0.9, anchor='center')
            
            # Conteúdo do feedback
            msg_frame = ctk.CTkFrame(feedback_frame, fg_color=bg_color)
            msg_frame.pack(padx=15, pady=10)
            
            ctk.CTkLabel(msg_frame, text=f"{icone} {mensagem}", 
                     text_color=text_color,
                     font=('Helvetica', 12),
                     fg_color=bg_color).pack()
            
            # Agenda a remoção do feedback após o tempo especificado
            self.root.after(duracao, lambda: feedback_frame.destroy())
        except Exception:
            # Se falhar o feedback visual, usa MessageBox como fallback
            if tipo == "erro":
                messagebox.showerror("Erro", mensagem)
            elif tipo == "aviso":
                messagebox.showwarning("Aviso", mensagem)
            elif tipo == "sucesso":
                messagebox.showinfo("Sucesso", mensagem)
            else:
                messagebox.showinfo("Informação", mensagem)
    
    def selecionar_tarefa(self, idx):
        """Seleciona uma tarefa e exibe seus detalhes"""
        self.tarefa_selecionada = idx
        
        # Destacar a linha selecionada e remover destaque das outras
        for row, i in self.task_rows:
            if i == idx:
                row.configure(border_width=2, border_color="#4a6da7")
            else:
                row.configure(border_width=0)
        
        # Exibir detalhes
        self.mostrar_detalhes_tarefa()
    
    def mostrar_detalhes_tarefa(self):
        """Mostra os detalhes da tarefa selecionada"""
        if self.tarefa_selecionada is None:
            return
        
        # Limpa o frame de detalhes
        for widget in self.detalhes_conteudo.winfo_children():
            widget.destroy()
        
        # Obtém os dados da tarefa
        tarefa = self.tarefas[self.tarefa_selecionada]
        
        # Grid para organizar informações
        info_frame = ctk.CTkFrame(self.detalhes_conteudo)
        info_frame.pack(fill='x', pady=5)
        
        # Coluna 1: Informações básicas
        col1 = ctk.CTkFrame(info_frame)
        col1.pack(side='left', fill='both', expand=True, padx=10)
        
        # Título com feedback visual de clique
        titulo_frame = ctk.CTkFrame(col1)
        titulo_frame.pack(fill='x', anchor='w', pady=2)
        
        titulo_label = ctk.CTkLabel(titulo_frame, text=f"Título: {tarefa['titulo']}", 
                    font=('Helvetica', 12, 'bold'))
        titulo_label.pack(side='left')
        
        ctk.CTkLabel(col1, text=f"Remetente: {tarefa['remetente_nome']}", 
                    font=('Helvetica', 12)).pack(anchor='w', pady=2)
        ctk.CTkLabel(col1, text=f"Destinatário: {tarefa['destinatario_nome']}", 
                    font=('Helvetica', 12)).pack(anchor='w', pady=2)
        
        # Coluna 2: Mais informações
        col2 = ctk.CTkFrame(info_frame)
        col2.pack(side='right', fill='both', expand=True, padx=10)
        
        ctk.CTkLabel(col2, text=f"Data: {tarefa['data_criacao']}", 
                    font=('Helvetica', 12)).pack(anchor='w', pady=2)
        
        # Verificar se há prioridade
        if 'prioridade' in tarefa:
            prioridade_text = f"Prioridade: {tarefa['prioridade']}"
            ctk.CTkLabel(col2, text=prioridade_text, font=('Helvetica', 12)).pack(anchor='w', pady=2)
        
        # Status com cores melhoradas para visibilidade
        status = "Concluída" if tarefa['concluida'] else (
            "Em Andamento" if tarefa.get('em_andamento', False) else "Pendente")
        
        # Cores de status com melhor contraste
        if tarefa['concluida']:
            status_color = "#155724"  # Verde escuro
            status_bg = "#d4edda"     # Verde claro
        elif tarefa.get('em_andamento', False):
            status_color = "#856404"  # Amarelo escuro
            status_bg = "#fff3cd"     # Amarelo claro
        else:
            status_color = "#721c24"  # Vermelho escuro
            status_bg = "#f8d7da"     # Vermelho claro
        
        # Criar um badge personalizado para o status
        status_frame = ctk.CTkFrame(col2, fg_color=status_bg, corner_radius=4)
        status_frame.pack(anchor='w', pady=5)
        
        status_label = ctk.CTkLabel(status_frame, text=f" {status} ", 
                                  text_color=status_color,
                                  font=('Helvetica', 12, 'bold'),
                                  fg_color="transparent")
        status_label.pack(padx=8, pady=3)
        
        # Descrição em um frame com scroll
        desc_frame = ctk.CTkFrame(self.detalhes_conteudo)
        desc_frame.pack(fill='x', pady=10)
        
        desc_header = ctk.CTkFrame(desc_frame)
        desc_header.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(desc_header, text="Descrição:", font=('Helvetica', 12, 'bold')).pack(side='left')
        
        # Botão para editar descrição se o usuário é o destinatário ou administrador
        if self.usuario_atual['email'] == tarefa['destinatario_email'] or self.usuario_logado_como_adm():
            editar_btn = ctk.CTkButton(desc_header, text="Editar Descrição", 
                                  width=120, height=25, 
                                  command=lambda: self.editar_descricao_tarefa())
            editar_btn.pack(side='right')
        
        # Campo de texto com a descrição
        self.desc_text = ctk.CTkTextbox(desc_frame, width=400, height=100)
        self.desc_text.pack(padx=10, pady=5, fill='x')
        self.desc_text.insert('1.0', tarefa['descricao'])
        self.desc_text.configure(state='disabled')  # Inicialmente desabilitado
        
        # Feedback visual: piscar ao selecionar
        self.destacar_selecionado()
    
    def destacar_selecionado(self):
        """Fornece feedback visual ao selecionar uma tarefa"""
        # Encontra o frame selecionado
        for row, idx in self.task_rows:
            if idx == self.tarefa_selecionada:
                # Salva a cor original
                cor_original = row.cget("fg_color")
                # Destaca brevemente
                row.configure(fg_color="#4e95d3")
                # Agenda a restauração da cor original após 200ms
                self.root.after(200, lambda r=row, c=cor_original: r.configure(fg_color=c))
                break
    
    def editar_descricao_tarefa(self):
        """Permite editar a descrição da tarefa selecionada"""
        if self.tarefa_selecionada is None:
            return
        
        # Habilita a edição da descrição
        self.desc_text.configure(state='normal')
        
        # Cria botões para salvar/cancelar
        botoes_frame = ctk.CTkFrame(self.detalhes_conteudo)
        botoes_frame.pack(fill='x', padx=10, pady=5)
        
        # Botão para salvar alterações
        salvar_btn = ctk.CTkButton(botoes_frame, text="Salvar Alterações", 
                               fg_color="#28a745",
                               command=self.salvar_descricao_tarefa)
        salvar_btn.pack(side='right', padx=5)
        
        # Botão para cancelar
        cancelar_btn = ctk.CTkButton(botoes_frame, text="Cancelar", 
                                 fg_color="#dc3545",
                                 command=self.cancelar_edicao_descricao)
        cancelar_btn.pack(side='right', padx=5)
        
        # Foca no campo de texto
        self.desc_text.focus_set()
    
    def salvar_descricao_tarefa(self):
        """Salva a descrição editada da tarefa"""
        if self.tarefa_selecionada is None:
            return
        
        # Obtém a nova descrição
        nova_descricao = self.desc_text.get("0.0", "end").strip()
        
        # Validação básica
        if not nova_descricao:
            messagebox.showerror("Erro", "A descrição não pode ficar em branco!")
            return
        
        # Atualiza a descrição da tarefa
        self.tarefas[self.tarefa_selecionada]['descricao'] = nova_descricao
        self.salvar_dados()
        
        # Exibe mensagem de sucesso
        messagebox.showinfo("Sucesso", "Descrição da tarefa atualizada com sucesso!")
        
        # Atualiza a visualização
        self.mostrar_detalhes_tarefa()
        
        # Atualiza a lista de tarefas para refletir a mudança
        self.exibir_tarefas()
    
    def cancelar_edicao_descricao(self):
        """Cancela a edição da descrição e volta ao modo de visualização"""
        # Recarrega os detalhes da tarefa sem salvar as alterações
        self.mostrar_detalhes_tarefa()

    def marcar_tarefa_selecionada_andamento(self):
        """Marca a tarefa selecionada como em andamento"""
        if self.tarefa_selecionada is None:
            self.mostrar_feedback("Selecione uma tarefa primeiro!", tipo="erro")
            return
        
        # Atualiza o status da tarefa
        self.tarefas[self.tarefa_selecionada]['concluida'] = False
        self.tarefas[self.tarefa_selecionada]['em_andamento'] = True
        self.salvar_dados()
        
        self.mostrar_feedback("Tarefa marcada como em andamento!", tipo="sucesso")
        self.mostrar_aba_tarefas()

    def marcar_tarefa_selecionada_concluida(self):
        """Marca a tarefa selecionada como concluída"""
        if self.tarefa_selecionada is None:
            self.mostrar_feedback("Selecione uma tarefa primeiro!", tipo="erro")
            return
        
        # Atualiza o status da tarefa
        self.tarefas[self.tarefa_selecionada]['concluida'] = True
        self.tarefas[self.tarefa_selecionada]['em_andamento'] = False
        self.salvar_dados()
        
        self.mostrar_feedback("Tarefa marcada como concluída!", tipo="sucesso")
        self.mostrar_aba_tarefas()

    def criar_aba_nova_tarefa(self, frame):
        """Cria a aba para criação de novas tarefas (apenas para ADM)"""
        # Frame principal
        main_frame = ctk.CTkFrame(frame)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Cabeçalho
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Criar Nova Tarefa", font=('Helvetica', 18, 'bold')).pack()
        ctk.CTkLabel(header_frame, text="Atribua tarefas aos usuários", 
                 font=('Helvetica', 14)).pack()
        
        # Formulário
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(expand=True, fill='both')
        
        # Campos do formulário
        ctk.CTkLabel(form_frame, text="Título:", font=('Helvetica', 12)).grid(
            row=0, column=0, sticky='w', pady=5, padx=10)
        self.titulo_tarefa = ctk.CTkEntry(form_frame, width=300, height=30)
        self.titulo_tarefa.grid(row=0, column=1, pady=10, padx=10, sticky='ew')
        
        ctk.CTkLabel(form_frame, text="Descrição:", font=('Helvetica', 12)).grid(
            row=1, column=0, sticky='nw', pady=5, padx=10)
        self.descricao_tarefa = ctk.CTkTextbox(form_frame, width=300, height=150)
        self.descricao_tarefa.grid(row=1, column=1, pady=10, padx=10, sticky='ew')
        
        ctk.CTkLabel(form_frame, text="Atribuir a:", font=('Helvetica', 12)).grid(
            row=2, column=0, sticky='w', pady=5, padx=10)
        
        # Preenche a lista de usuários (exceto ADM)
        usuarios = [u for u in self.usuarios if u['email'] != 'adm']
        usuario_options = [f"{u['nome']} ({u['email']})" for u in usuarios]
        
        self.destinatario_tarefa = ctk.CTkComboBox(form_frame, width=300, height=30, values=usuario_options)
        self.destinatario_tarefa.grid(row=2, column=1, pady=10, padx=10, sticky='ew')
        if usuario_options:
            self.destinatario_tarefa.set(usuario_options[0])
        
        # Configuração de prioridade
        ctk.CTkLabel(form_frame, text="Prioridade:", font=('Helvetica', 12)).grid(
            row=3, column=0, sticky='w', pady=5, padx=10)
        
        prioridade_frame = ctk.CTkFrame(form_frame)
        prioridade_frame.grid(row=3, column=1, sticky='ew', pady=10, padx=10)
        
        self.prioridade_var = ctk.StringVar(value="Normal")
        
        ctk.CTkRadioButton(prioridade_frame, text="Baixa", 
                          variable=self.prioridade_var, value="Baixa").pack(side='left', padx=20)
        ctk.CTkRadioButton(prioridade_frame, text="Normal", 
                          variable=self.prioridade_var, value="Normal").pack(side='left', padx=20)
        ctk.CTkRadioButton(prioridade_frame, text="Alta", 
                          variable=self.prioridade_var, value="Alta").pack(side='left', padx=20)
        
        # Botão de envio
        btn_frame = ctk.CTkFrame(form_frame)
        btn_frame.grid(row=4, column=1, pady=20, sticky='e', padx=10)
        
        ctk.CTkButton(btn_frame, text="Criar Tarefa", command=self.criar_tarefa, 
                    width=150, height=35, font=('Helvetica', 12, 'bold')).pack(side='right')

    def criar_tarefa(self):
        """Cria uma nova tarefa (apenas para ADM)"""
        titulo = self.titulo_tarefa.get()
        descricao = self.descricao_tarefa.get("0.0", "end").strip()
        destinatario = self.destinatario_tarefa.get()
        prioridade = self.prioridade_var.get()
        
        # Extrai o e-mail do destinatário
        try:
            destinatario_email = destinatario.split("(")[1].rstrip(")")
        except (IndexError, AttributeError):
            messagebox.showerror("Erro", "Selecione um destinatário válido!")
            return
        
        # Validação básica
        if not all([titulo, descricao, destinatario]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        # Obtém o nome do remetente e destinatário
        remetente_nome = self.usuario_atual['nome']
        destinatario_nome = next(u['nome'] for u in self.usuarios if u['email'] == destinatario_email)
        
        # Cria a nova tarefa
        nova_tarefa = {
            'titulo': titulo,
            'descricao': descricao,
            'remetente_email': self.usuario_atual['email'],
            'remetente_nome': remetente_nome,
            'destinatario_email': destinatario_email,
            'destinatario_nome': destinatario_nome,
            'data_criacao': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'concluida': False,
            'em_andamento': False,
            'prioridade': prioridade
        }
        
        self.tarefas.append(nova_tarefa)
        self.salvar_dados()
        
        messagebox.showinfo("Sucesso", "Tarefa criada com sucesso!")
        
        # Limpa os campos
        self.titulo_tarefa.delete(0, "end")
        self.descricao_tarefa.delete("0.0", "end")

    def fazer_login(self):
        """Realiza o login do usuário"""
        email = self.email_login.get()
        senha = self.senha_login.get()
        
        usuario = next((u for u in self.usuarios if u['email'] == email and u['senha'] == senha), None)
        
        if usuario:
            self.usuario_atual = usuario
            
            # Aplicar tema preferido do usuário se estiver definido
            if 'tema_preferido' in usuario:
                ctk.set_appearance_mode(usuario['tema_preferido'])
            
            self.mostrar_tela_principal()
        else:
            messagebox.showerror("Erro", "E-mail ou senha incorretos!")

    def cadastrar_usuario(self):
        """Cadastra um novo usuário comum"""
        nome = self.nome_cadastro.get()
        email = self.email_cadastro.get()
        senha = self.senha_cadastro.get()
        
        # Validação básica
        if not all([nome, email, senha]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        # Verificação de senha forte
        senha_valida, msg_erro = self.verificar_senha_forte(senha)
        if not senha_valida:
            messagebox.showerror("Erro na senha", msg_erro)
            return
        
        # Verifica se o e-mail já está cadastrado
        if any(u['email'] == email for u in self.usuarios):
            messagebox.showerror("Erro", "Este e-mail já está cadastrado!")
            return
        
        # Adiciona o novo usuário (sempre como usuário comum)
        novo_usuario = {
            'nome': nome,
            'email': email,
            'senha': senha,
            'tipo': 'Usuário'
        }
        
        self.usuarios.append(novo_usuario)
        self.salvar_dados()
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
        self.mostrar_tela_login()

    def sair(self):
        """Realiza o logout do usuário"""
        self.usuario_atual = None
        self.mostrar_tela_login()

    def marcar_tarefa_andamento_direto(self, idx_filtrada):
        """Marca a tarefa diretamente na visualização de lista"""
        idx_original = self.tarefas.index(self.tarefas_filtradas[idx_filtrada])
        
        # Atualiza o status da tarefa
        self.tarefas[idx_original]['concluida'] = False
        self.tarefas[idx_original]['em_andamento'] = True
        self.salvar_dados()
        
        # Usar feedback visual em vez de messagebox para melhorar experiência
        self.mostrar_feedback("Tarefa marcada como em andamento!", tipo="sucesso")
        self.atualizar_filtro_tarefas()  # Recarrega a lista
    
    def marcar_tarefa_concluida_direto(self, idx_filtrada):
        """Marca a tarefa como concluída diretamente na visualização de lista"""
        idx_original = self.tarefas.index(self.tarefas_filtradas[idx_filtrada])
        
        # Atualiza o status da tarefa
        self.tarefas[idx_original]['concluida'] = True
        self.tarefas[idx_original]['em_andamento'] = False
        self.salvar_dados()
        
        # Usar feedback visual em vez de messagebox para melhorar experiência
        self.mostrar_feedback("Tarefa marcada como concluída!", tipo="sucesso")
        self.atualizar_filtro_tarefas()  # Recarrega a lista

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Sistema de Gestão de Tarefas")
    root.geometry("1200x700")
    root.minsize(800, 600)
    
    # Define o tema e modo de aparência
    ctk.set_appearance_mode("System")  # "System", "Dark" ou "Light"
    ctk.set_default_color_theme("blue")  # "blue", "dark-blue" ou "green"
    
    app = SistemaTarefas(root)
    root.mainloop()