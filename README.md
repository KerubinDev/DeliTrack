# DeliTrack - Sistema de Gerenciamento de Pedidos e Entregas

Sistema web completo para gerenciamento de pedidos e entregas em restaurantes, desenvolvido com foco em usabilidade e eficiência.

## Requisitos

- Python 3.12+
- Pip (gerenciador de pacotes do Python)

## Inicialização Rápida

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o sistema:
```bash
python iniciar.py
```

3. Acesse no navegador:
```
http://localhost:5000
```

## Credenciais de Acesso

O sistema cria automaticamente os seguintes usuários:

- Gerente: admin@delitrack.com / admin123
- Garçom: garcom@delitrack.com / admin123
- Cozinheiro: cozinha@delitrack.com / admin123
- Entregador: entrega@delitrack.com / admin123

## Funcionalidades

### Gerente
- Dashboard com métricas em tempo real
- Gestão de usuários e produtos
- Relatórios de vendas e desempenho

### Garçom
- Cadastro de pedidos locais e delivery
- Acompanhamento de pedidos ativos
- Interface intuitiva para seleção de produtos

### Cozinha
- Visualização de pedidos pendentes
- Atualização de status de preparação
- Organização por ordem de chegada

### Entregador
- Lista de entregas pendentes e em andamento
- Navegação integrada com mapas
- Confirmação de entregas realizadas

## Tecnologias Utilizadas

- Backend: Python/Flask
- Banco de Dados: SQLite
- Frontend: HTML5, CSS3, JavaScript
- UI Framework: Bootstrap 5
- Animações: Particles.js
- Mapas: Google Maps API

## Estrutura do Projeto

```
delitrack/
├── backend/          # Lógica de negócios e modelos
├── templates/        # Templates HTML
├── static/          # Assets e scripts
├── uploads/         # Imagens de produtos
└── scripts/         # Scripts de inicialização
```

## Características Técnicas

- Arquitetura MVC
- Sistema de autenticação seguro
- APIs RESTful
- Atualizações em tempo real
- Design responsivo
- Interface moderna com efeitos visuais
- Validações de dados
- Tratamento de erros robusto

## Suporte e Contato

Para suporte técnico ou dúvidas:
- Email: kelvin.moraes117@gmail.com
- GitHub: [Reportar um problema](https://github.com/seu-usuario/delitrack/issues)

## Licença

Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU General Public License, conforme publicado pela Free Software Foundation, seja a versão 3 da Licença, ou (a seu critério) qualquer versão posterior.

Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM DETERMINADO PROPÓSITO. Veja a GNU General Public License para mais detalhes.

Você deve ter recebido uma cópia da GNU General Public License junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.

## Créditos

Desenvolvido por Kelvin Moraes 