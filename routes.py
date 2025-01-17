from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from database import db, Usuario, Produto, Pedido, ItemPedido
from werkzeug.security import check_password_hash

main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha_hash, senha):
            login_user(usuario)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.dashboard'))
        
        flash('Email ou senha inválidos', 'error')
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/')
@login_required
def dashboard():
    if current_user.tipo == 'garcom':
        return render_template('garcom/pedidos.html')
    elif current_user.tipo == 'cozinheiro':
        return render_template('cozinha/painel.html')
    elif current_user.tipo == 'entregador':
        return render_template('entregador/painel.html')
    elif current_user.tipo == 'gerente':
        return render_template('gerente/dashboard.html')
    
    return redirect(url_for('main.login'))
