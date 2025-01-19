from backend.app import create_app
from backend.models import db, Usuario, Cliente, ItemMenu, Pedido, ItemPedido, Entrega

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Configura o contexto do shell Flask."""
    return {
        'db': db,
        'Usuario': Usuario,
        'Cliente': Cliente,
        'ItemMenu': ItemMenu,
        'Pedido': Pedido,
        'ItemPedido': ItemPedido,
        'Entrega': Entrega
    }

if __name__ == '__main__':
    app.run(debug=True) 