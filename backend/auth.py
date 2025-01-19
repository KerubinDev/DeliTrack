from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import secrets
from .models import Usuario, TokenRedefinicaoSenha, db

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
            
        flash(erro, 'danger')
    
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
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('main.index'))
            
        flash(erro, 'danger')
    
    return render_template('auth/alterar_senha.html')


@bp.route('/recuperar_senha', methods=('GET', 'POST'))
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


@bp.route('/redefinir_senha/<token>', methods=('GET', 'POST'))
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