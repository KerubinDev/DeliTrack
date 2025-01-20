<div align="center">

```
██████╗ ███████╗██╗     ██╗████████╗██████╗  █████╗  ██████╗██╗  ██╗
██╔══██╗██╔════╝██║     ██║╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
██║  ██║█████╗  ██║     ██║   ██║   ██████╔╝███████║██║     █████╔╝ 
██║  ██║██╔══╝  ██║     ██║   ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ 
██████╔╝███████╗███████╗██║   ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗
╚═════╝ ╚══════╝╚══════╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
```

<h3>🍽️ Sistema Inteligente de Gerenciamento para Restaurantes</h3>

[![Status](https://img.shields.io/badge/Status-Em%20Produção-success?style=for-the-badge&logo=statuspage&logoColor=white)](https://github.com/KerubinDev/DeliTrack)
[![Python](https://img.shields.io/badge/Python-3.12+-4B8BBE?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-GPL%20v3-blue?style=for-the-badge&logo=gnu&logoColor=white)](LICENSE)

[📋 Sobre](#-sobre) • 
[🚀 Instalação](#-instalação) • 
[💡 Recursos](#-recursos) • 
[🛠️ Tecnologias](#️-tecnologias) • 
[📱 Demo](#-demo)

</div>

## 📋 Sobre

<div align="center">

```mermaid
graph LR
    A[Pedido] --> B[Cozinha]
    B --> C[Preparo]
    C --> D[Entrega]
    D --> E[Confirmação]
    
    style A fill:#ff9900,stroke:#fff
    style B fill:#f96,stroke:#fff
    style C fill:#9cf,stroke:#fff
    style D fill:#9f9,stroke:#fff
    style E fill:#c9f,stroke:#fff
```

DeliTrack é uma solução completa para restaurantes gerenciarem seus pedidos e entregas de forma eficiente e intuitiva. Do pedido à entrega, cada etapa é cuidadosamente monitorada para garantir a melhor experiência.

</div>

## 💡 Recursos por Perfil

<table align="center">
  <tr>
    <td align="center" width="25%">
      <img width="64" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Graph.svg" alt="Gerente"/>
      <br/><strong>👔 Gerente</strong>
      <br/>
      <sub>• Dashboard em tempo real<br/>• Gestão de usuários<br/>• Relatórios avançados</sub>
    </td>
    <td align="center" width="25%">
      <img width="64" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Notes.svg" alt="Garçom"/>
      <br/><strong>🍽️ Garçom</strong>
      <br/>
      <sub>• Registro de pedidos<br/>• Acompanhamento<br/>• Interface intuitiva</sub>
    </td>
    <td align="center" width="25%">
      <img width="64" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Kitchen.svg" alt="Cozinha"/>
      <br/><strong>👨‍🍳 Cozinha</strong>
      <br/>
      <sub>• Fila de pedidos<br/>• Gestão de preparo<br/>• Priorização</sub>
    </td>
    <td align="center" width="25%">
      <img width="64" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Route.svg" alt="Entregador"/>
      <br/><strong>🛵 Entregador</strong>
      <br/>
      <sub>• Rotas otimizadas<br/>• GPS integrado<br/>• Confirmações</sub>
    </td>
  </tr>
</table>

## 🚀 Início Rápido

<details>
<summary>📦 Requisitos</summary>

- Python 3.12+
- Pip (Gerenciador de pacotes)
- SQLite
</details>

<details>
<summary>⚡ Instalação</summary>

```bash
# Clone o repositório
git clone https://github.com/KerubinDev/delitrack.git

# Instale as dependências
pip install -r requirements.txt

# Execute o sistema
python iniciar.py

# Acesse em
http://localhost:5000
```
</details>

## 🔐 Acessos do Sistema

<div align="center">

| Perfil | Credenciais | Área de Atuação |
|--------|-------------|-----------------|
| 👔 **Gerente** | admin@delitrack.com<br>admin123 | Gestão completa |
| 🍽️ **Garçom** | garcom@delitrack.com<br>admin123 | Atendimento |
| 👨‍🍳 **Cozinha** | cozinha@delitrack.com<br>admin123 | Preparação |
| 🛵 **Entrega** | entrega@delitrack.com<br>admin123 | Delivery |

</div>

## 🛠️ Stack Tecnológica

<div align="center">

| Back-end | Front-end | Database | APIs |
|----------|-----------|----------|------|
| ![Python](https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Python-Dark.svg) | ![Bootstrap](https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Bootstrap.svg) | ![SQLite](https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/SQLite.svg) | ![Maps](https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/GoogleCloud-Dark.svg) |
| ![Flask](https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Flask-Dark.svg) | ![JavaScript](https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/JavaScript.svg) | ![Redis](https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Redis-Dark.svg) | ![REST](https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/OpenAPI-Dark.svg) |

</div>

## 📂 Estrutura

```plaintext
🍽️ DeliTrack/
├── 🎯 backend/
│   ├── 📊 models/
│   ├── 🛣️ routes/
│   └── ⚙️ utils/
├── 🎨 frontend/
│   ├── 📱 templates/
│   └── 🎭 static/
├── 🗺️ maps/
└── 📦 uploads/
```

## 🔄 Fluxo de Trabalho

```mermaid
sequenceDiagram
    Cliente->>Garçom: Faz pedido
    Garçom->>Sistema: Registra pedido
    Sistema->>Cozinha: Notifica novo pedido
    Cozinha->>Sistema: Atualiza status
    Sistema->>Entregador: Designa entrega
    Entregador->>Cliente: Realiza entrega
    Cliente->>Sistema: Confirma recebimento
```

## 👨‍💻 Autor

<div align="center">
  <img width="200" height="200" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Github-Dark.svg">
  <h3>Kelvin Moraes</h3>
  <p>Full Stack Developer | Restaurant Tech Specialist</p>
  
[![GitHub](https://img.shields.io/badge/GitHub-KerubinDev-181717?style=for-the-badge&logo=github)](https://github.com/KerubinDev)
[![Email](https://img.shields.io/badge/Email-kelvin.moraes117@gmail.com-EA4335?style=for-the-badge&logo=gmail)](mailto:kelvin.moraes117@gmail.com)

</div>

## 📄 Licença

Este projeto está licenciado sob a [GNU GPL v3](LICENSE) - veja o arquivo LICENSE para detalhes.

---

<div align="center">
  
  **[⬆ Voltar ao topo](#delitrack---sistema-de-gerenciamento-de-pedidos-e-entregas)**
  
  <sub>Desenvolvido com 🍳 por Kelvin Moraes</sub>
  
[![Stack](https://img.shields.io/badge/Stack-Python%20%7C%20Flask%20%7C%20SQLite-000000?style=for-the-badge)](https://github.com/KerubinDev/DeliTrack)
</div>
