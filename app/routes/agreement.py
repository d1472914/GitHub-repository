from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.models.agreement import Agreement
from app.models.agreement_version import AgreementVersion
from app.models.agreement_approval import AgreementApproval
from app.models.user import User
from app.models.notification import Notification

agreement_bp = Blueprint('agreement', __name__)

@agreement_bp.route('/')
@login_required
@group_required
def list_agreements():
    """公約列表頁"""
    agreements = Agreement.get_by_group(current_user.group_id)
    
    # 統計每個公約的同意進度
    members = User.get_by_group(current_user.group_id)
    total_members = len(members)
    
    agreements_data = []
    for ag in agreements:
        approvals = AgreementApproval.get_approvals_by_agreement(ag.id)
        user_approved = AgreementApproval.has_approved(ag.id, current_user.id)
        ag_dict = {
            'info': ag,
            'approval_count': len(approvals),
            'total_members': total_members,
            'user_approved': user_approved
        }
        agreements_data.append(ag_dict)
        
    return render_template('agreement/list.html', agreements=agreements_data)

@agreement_bp.route('/<int:agreement_id>')
@login_required
@group_required
def detail(agreement_id):
    """公約詳情頁，含同意狀態與版本歷史"""
    agreement = Agreement.get_by_id(agreement_id)
    if not agreement or agreement.group_id != current_user.group_id:
        flash('找不到該公約！', 'danger')
        return redirect(url_for('agreement.list_agreements'))
        
    members = User.get_by_group(current_user.group_id)
    approvals = AgreementApproval.get_approvals_by_agreement(agreement_id)
    approved_user_ids = {appr.user_id for appr in approvals}
    
    members_data = []
    for m in members:
        members_data.append({
            'user': m,
            'approved': m.id in approved_user_ids
        })
        
    versions = AgreementVersion.get_by_agreement(agreement_id)
    # 獲取修改者暱稱
    versions_data = []
    for v in versions:
        modifier = User.get_by_id(v.modified_by)
        versions_data.append({
            'version': v,
            'modifier_name': modifier.nickname if modifier else '未知使用者'
        })
        
    user_approved = AgreementApproval.has_approved(agreement_id, current_user.id)
    
    return render_template(
        'agreement/detail.html',
        agreement=agreement,
        members=members_data,
        versions=versions_data,
        user_approved=user_approved
    )

@agreement_bp.route('/new', methods=['GET', 'POST'])
@login_required
@group_required
def create_agreement():
    """新增公約"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not category or not content:
            flash('所有欄位皆為必填！', 'warning')
            return render_template('agreement/form.html', title=title, category=category, content=content, action_type='new')
            
        data = {
            'group_id': current_user.group_id,
            'title': title,
            'category': category,
            'content': content,
            'status': 'pending',
            'created_by': current_user.id
        }
        
        new_ag = Agreement.create(data)
        if new_ag:
            # 建立者自動同意
            AgreementApproval.create({'agreement_id': new_ag.id, 'user_id': current_user.id})
            
            # 發送通知給其他室友
            members = User.get_by_group(current_user.group_id)
            for m in members:
                if m.id != current_user.id:
                    Notification.create({
                        'user_id': m.id,
                        'group_id': current_user.group_id,
                        'type': 'agreement',
                        'title': '新增公約提案',
                        'message': f'室友 {current_user.nickname} 提議了新公約：「{title}」，請前往確認。'
                    })
            
            # 檢查是否全體同意 (若是 1 人群組)
            check_and_update_agreement_status(new_ag.id)
            
            flash('公約提案建立成功！請等待室友確認同意。', 'success')
            return redirect(url_for('agreement.list_agreements'))
        else:
            flash('建立公約失敗，請重試。', 'danger')
            
    return render_template('agreement/form.html', action_type='new')

@agreement_bp.route('/<int:agreement_id>/edit', methods=['GET', 'POST'])
@login_required
@group_required
def edit_agreement(agreement_id):
    """編輯公約"""
    agreement = Agreement.get_by_id(agreement_id)
    if not agreement or agreement.group_id != current_user.group_id:
        flash('找不到該公約！', 'danger')
        return redirect(url_for('agreement.list_agreements'))
        
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not category or not content:
            flash('所有欄位皆為必填！', 'warning')
            return render_template('agreement/form.html', agreement=agreement, action_type='edit')
            
        # 取得當前最高版本號
        versions = AgreementVersion.get_by_agreement(agreement_id)
        next_ver = len(versions) + 1
        
        # 寫入版本歷史
        AgreementVersion.create({
            'agreement_id': agreement_id,
            'version_number': next_ver,
            'content_before': agreement.content,
            'content_after': content,
            'modified_by': current_user.id
        })
        
        # 更新公約並重設狀態為 pending
        Agreement.update(agreement_id, {
            'title': title,
            'category': category,
            'content': content,
            'status': 'pending'
        })
        
        # 清除所有同意記錄
        AgreementApproval.delete_by_agreement(agreement_id)
        
        # 修改者自動同意新版本
        AgreementApproval.create({'agreement_id': agreement_id, 'user_id': current_user.id})
        
        # 發送通知給其他室友
        members = User.get_by_group(current_user.group_id)
        for m in members:
            if m.id != current_user.id:
                Notification.create({
                    'user_id': m.id,
                    'group_id': current_user.group_id,
                    'type': 'agreement',
                    'title': '公約內容已修改',
                    'message': f'室友 {current_user.nickname} 修改了公約：「{title}」，同意狀態已重設，請重新確認。'
                })
                
        # 檢查是否全體同意 (若是 1 人群組)
        check_and_update_agreement_status(agreement_id)
        
        flash('公約修改成功，同意狀態已重設，已通知室友重新確認。', 'success')
        return redirect(url_for('agreement.detail', agreement_id=agreement_id))
        
    return render_template('agreement/form.html', agreement=agreement, action_type='edit')

@agreement_bp.route('/<int:agreement_id>/approve', methods=['POST'])
@login_required
@group_required
def approve_agreement(agreement_id):
    """同意公約"""
    agreement = Agreement.get_by_id(agreement_id)
    if not agreement or agreement.group_id != current_user.group_id:
        flash('找不到該公約！', 'danger')
        return redirect(url_for('agreement.list_agreements'))
        
    if AgreementApproval.has_approved(agreement_id, current_user.id):
        flash('您已經同意過此公約！', 'warning')
        return redirect(url_for('agreement.detail', agreement_id=agreement_id))
        
    AgreementApproval.create({
        'agreement_id': agreement_id,
        'user_id': current_user.id
    })
    
    # 檢查是否所有人皆同意
    check_and_update_agreement_status(agreement_id)
    
    flash('您已同意此公約！', 'success')
    return redirect(url_for('agreement.detail', agreement_id=agreement_id))

@agreement_bp.route('/<int:agreement_id>/delete', methods=['POST'])
@login_required
@group_required
def delete_agreement(agreement_id):
    """刪除公約"""
    agreement = Agreement.get_by_id(agreement_id)
    if not agreement or agreement.group_id != current_user.group_id:
        flash('找不到該公約！', 'danger')
        return redirect(url_for('agreement.list_agreements'))
        
    # 檢查是否為建立者或管理員
    group = User.get_by_group(current_user.group_id) # 這裡取得群組資訊，也可以直接 check role
    if agreement.created_by != current_user.id and current_user.role != 'admin':
        flash('只有提案人或群組管理員才能刪除此公約！', 'danger')
        return redirect(url_for('agreement.detail', agreement_id=agreement_id))
        
    # 刪除關聯的版本歷史與同意記錄
    # SQLite 雖然有 foreign keys，但為防萬一，先刪除關聯資料
    AgreementVersion.delete(agreement_id) # 這裡是 delete version，但 delete 實作需要傳 version_id
    # 為了簡化，在 Agreement.delete 內進行 cascade 刪除比較乾淨，或者寫 SQL
    # 讓我們檢查 Agreement.delete 在 agreement.py 中是否會自動刪除關聯，或我們在這裡手動呼叫
    # 我們在 delete_by_agreement 已經有了，讓我們手動執行 SQL 刪除關聯
    import sqlite3
    from app.models import get_db_connection
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM agreement_approvals WHERE agreement_id = ?", (agreement_id,))
        conn.execute("DELETE FROM agreement_versions WHERE agreement_id = ?", (agreement_id,))
        conn.execute("DELETE FROM agreements WHERE id = ?", (agreement_id,))
        conn.commit()
        conn.close()
        flash('公約已成功刪除！', 'info')
    except Exception as e:
        flash(f'刪除失敗：{e}', 'danger')
        
    return redirect(url_for('agreement.list_agreements'))


def check_and_update_agreement_status(agreement_id):
    """檢查是否全體成員皆同意公約，若是則將狀態更新為 active，並發布通知"""
    members = User.get_by_group(current_user.group_id)
    approvals = AgreementApproval.get_approvals_by_agreement(agreement_id)
    
    if len(approvals) >= len(members):
        Agreement.update(agreement_id, {'status': 'active'})
        agreement = Agreement.get_by_id(agreement_id)
        # 發送通知給全體室友
        for m in members:
            Notification.create({
                'user_id': m.id,
                'group_id': current_user.group_id,
                'type': 'agreement',
                'title': '公約已正式生效',
                'message': f'公約「{agreement.title}」已獲得所有室友同意，正式生效！'
            })
        return True
    return False
