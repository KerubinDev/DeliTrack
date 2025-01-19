from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .models import Usuario, db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Rota para login de usuários."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        erro = None
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario is None:
            erro = 'Email não cadastrado.'
        elif not usuario.check_senha(senha):
            erro = 'Senha incorreta.'
        elif not usuario.ativo:
            erro = 'Usuário inativo. Contate o administrador.'
            
        if erro is None:
            login_user(usuario)
            return redirect(url_for('main.index'))
            
        flash(erro)
    
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """Rota para logout de usuários."""
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/alterar_senha', methods=('GET', 'POST'))
@login_required
def alterar_senha():
    """Rota para alteração de senha."""
    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirma_senha = request.form['confirma_senha']
        erro = None
        
        if not current_user.check_senha(senha_atual):
            erro = 'Senha atual incorreta.'
        elif nova_senha != confirma_senha:
            erro = 'As senhas não conferem.'
        elif len(nova_senha) < 6:
            erro = 'A nova senha deve ter pelo menos 6 caracteres.'
            
        if erro is None:
            current_user.set_senha(nova_senha)
            db.session.commit()
            flash('Senha alterada com sucesso!')
            return redirect(url_for('main.index'))
            
        flash(erro)
    
    return render_template('auth/alterar_senha.html') 