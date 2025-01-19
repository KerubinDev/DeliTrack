"""
Sistema de autenticação
"""
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import secrets
from .models import Usuario, TokenRedefinicaoSenha, db

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha_hash, senha):
            if not usuario.ativo:
                flash('Sua conta está desativada.', 'danger')
                return redirect(url_for('auth.login'))
                
            login_user(usuario)
            return redirect(url_for('main.welcome'))  # Redireciona para a tela de boas-vindas
            
        flash('Email ou senha incorretos.', 'danger')
    
    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    """Rota de logout"""
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    """Rota para alterar senha"""
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if not check_password_hash(current_user.senha_hash, senha_atual):
            flash('Senha atual incorreta.', 'error')
            return redirect(url_for('auth.alterar_senha'))
            
        if nova_senha != confirmar_senha:
            flash('As senhas não conferem.', 'error')
            return redirect(url_for('auth.alterar_senha'))
            
        if len(nova_senha) < 6:
            flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
            return redirect(url_for('auth.alterar_senha'))
            
        current_user.set_senha(nova_senha)
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('auth/alterar_senha.html')


@auth.route('/recuperar_senha', methods=('GET', 'POST'))
def recuperar_senha():
    """Rota para solicitar recuperação de senha."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form['email']
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            # Gerar token único
            token = secrets.token_urlsafe(32)
            expiracao = datetime.now() + timedelta(hours=1)
            
            # Salvar token no banco
            token_reset = TokenRedefinicaoSenha(
                token=token,
                usuario_id=usuario.id,
                expiracao=expiracao
            )
            db.session.add(token_reset)
            db.session.commit()
            
            # Enviar email com link para redefinição
            link = url_for('auth.redefinir_senha', token=token, _external=True)
            try:
                current_app.mail.send_message(
                    subject='Redefinição de Senha - DeliTrack',
                    recipients=[email],
                    html=render_template(
                        'email/redefinir_senha.html',
                        usuario=usuario,
                        link=link
                    )
                )
                flash(
                    'Um email foi enviado com instruções para redefinir sua senha.',
                    'info'
                )
            except Exception as e:
                db.session.delete(token_reset)
                db.session.commit()
                flash(
                    'Erro ao enviar email. Tente novamente mais tarde.',
                    'danger'
                )
        else:
            # Não revelar se o email existe ou não
            flash(
                'Se este email estiver cadastrado, você receberá instruções para redefinir sua senha.',
                'info'
            )
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/recuperar_senha.html')


@auth.route('/redefinir_senha/<token>', methods=('GET', 'POST'))
def redefinir_senha(token):
    """Rota para redefinir senha com token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    token_reset = TokenRedefinicaoSenha.query.filter_by(
        token=token,
        usado=False
    ).first()
    
    if not token_reset or token_reset.expirado:
        flash('Link de redefinição inválido ou expirado.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        nova_senha = request.form['nova_senha']
        confirma_senha = request.form['confirma_senha']
        erro = None
        
        if nova_senha != confirma_senha:
            erro = 'As senhas não conferem.'
        elif len(nova_senha) < 6:
            erro = 'A nova senha deve ter pelo menos 6 caracteres.'
            
        if erro is None:
            usuario = token_reset.usuario
            usuario.set_senha(nova_senha)
            token_reset.usado = True
            db.session.commit()
            
            flash('Senha redefinida com sucesso!', 'success')
            return redirect(url_for('auth.login'))
            
        flash(erro, 'danger')
    
    return render_template('auth/redefinir_senha.html', token=token) 