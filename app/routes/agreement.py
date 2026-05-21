from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.models import agreement as agreement_model
from app.models import user as user_model

agreement_bp = Blueprint('agreement', __name__)

@agreement_bp.route('/agreements', methods=['GET'])
@login_required
@group_required
def list_agreements():
    try:
        agreements = agreement_model.get_by_group(current_user.group_id)
        return render_template('agreement/list.html', agreements=agreements)
    except Exception as e:
        flash(f"無法載入公約列表：{e}", "danger")
        return render_template('agreement/list.html', agreements=[])

@agreement_bp.route('/agreements/new', methods=['GET'])
@login_required
@group_required
def new_agreement():
    return render_template('agreement/form.html', agreement=None)

@agreement_bp.route('/agreements', methods=['POST'])
@login_required
@group_required
def create_agreement():
    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    content = request.form.get('content', '').strip()

    if not title or not category or not content:
        flash("所有欄位皆為必填！", "danger")
        return render_template('agreement/form.html', agreement=None)

    try:
        agreement_id = agreement_model.create({
            'group_id': current_user.group_id,
            'title': title,
            'category': category,
            'content': content,
            'status': 'pending',
            'created_by': current_user.id
        })

        # 建立版本歷史（v1）
        agreement_model.create_version({
            'agreement_id': agreement_id,
            'version_number': 1,
            'content_before': None,
            'content_after': content,
            'modified_by': current_user.id
        })

        # 建立提案者的同意記錄
        agreement_model.create_approval({
            'agreement_id': agreement_id,
            'user_id': current_user.id
        })

        # 檢查是否全數通過 (如果群組只有提案者一人)
        roommates = user_model.get_users_by_group(current_user.group_id)
        approvals = agreement_model.get_approvals_by_agreement(agreement_id)
        if len(approvals) >= len(roommates):
            agreement_model.update(agreement_id, {'status': 'active'})
            flash("公約建立成功並已自動生效！", "success")
        else:
            flash("公約提案已建立，等待其他室友同意！", "success")

        return redirect(url_for('agreement.detail_agreement', id=agreement_id))
    except Exception as e:
        flash(f"建立公約失敗，資料庫錯誤：{e}", "danger")
        return render_template('agreement/form.html', agreement=None)

@agreement_bp.route('/agreements/<int:id>', methods=['GET'])
@login_required
@group_required
def detail_agreement(id):
    agreement = agreement_model.get_by_id(id)
    if not agreement or agreement['group_id'] != current_user.group_id:
        abort(404)

    try:
        versions = agreement_model.get_versions_by_agreement(id)
        approvals = agreement_model.get_approvals_by_agreement(id)
        roommates = user_model.get_users_by_group(current_user.group_id)
        
        # 標記每位室友是否已同意
        approved_user_ids = {a['user_id'] for a in approvals}
        roommates_status = []
        for r in roommates:
            roommates_status.append({
                'nickname': r['nickname'],
                'has_approved': r['id'] in approved_user_ids
            })

        has_approved = current_user.id in approved_user_ids

        return render_template(
            'agreement/detail.html',
            agreement=agreement,
            versions=versions,
            approvals=approvals,
            roommates_status=roommates_status,
            has_approved=has_approved
        )
    except Exception as e:
        flash(f"載入詳情失敗：{e}", "danger")
        return redirect(url_for('agreement.list_agreements'))

@agreement_bp.route('/agreements/<int:id>/edit', methods=['GET'])
@login_required
@group_required
def edit_agreement(id):
    agreement = agreement_model.get_by_id(id)
    if not agreement or agreement['group_id'] != current_user.group_id:
        abort(404)
    return render_template('agreement/form.html', agreement=agreement)

@agreement_bp.route('/agreements/<int:id>/update', methods=['POST'])
@login_required
@group_required
def update_agreement(id):
    agreement = agreement_model.get_by_id(id)
    if not agreement or agreement['group_id'] != current_user.group_id:
        abort(404)

    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    content = request.form.get('content', '').strip()

    if not title or not category or not content:
        flash("所有欄位皆為必填！", "danger")
        return render_template('agreement/form.html', agreement=agreement)

    try:
        # 取得現有版本數以計算新版本號
        versions = agreement_model.get_versions_by_agreement(id)
        next_ver = len(versions) + 1

        # 新增版本歷史
        agreement_model.create_version({
            'agreement_id': id,
            'version_number': next_ver,
            'content_before': agreement['content'],
            'content_after': content,
            'modified_by': current_user.id
        })

        # 更新公約並重設狀態為 pending
        agreement_model.update(id, {
            'title': title,
            'category': category,
            'content': content,
            'status': 'pending'
        })

        # 重設同意記錄：刪除所有舊同意記錄，並為編輯者建立新的同意
        approvals = agreement_model.get_approvals_by_agreement(id)
        for a in approvals:
            agreement_model.delete_approval(id, a['user_id'])
            
        agreement_model.create_approval({
            'agreement_id': id,
            'user_id': current_user.id
        })

        # 再次檢查是否已全數通過 (如果群組只有提案者一人)
        roommates = user_model.get_users_by_group(current_user.group_id)
        new_approvals = agreement_model.get_approvals_by_agreement(id)
        if len(new_approvals) >= len(roommates):
            agreement_model.update(id, {'status': 'active'})
            flash("公約更新成功並已自動生效！", "success")
        else:
            flash("公約更新成功，已重設同意進度，等待其他室友重新同意！", "success")

        return redirect(url_for('agreement.detail_agreement', id=id))
    except Exception as e:
        flash(f"更新公約失敗，資料庫錯誤：{e}", "danger")
        return render_template('agreement/form.html', agreement=agreement)

@agreement_bp.route('/agreements/<int:id>/delete', methods=['POST'])
@login_required
@group_required
def delete_agreement(id):
    agreement = agreement_model.get_by_id(id)
    if not agreement or agreement['group_id'] != current_user.group_id:
        abort(404)

    try:
        # 刪除外鍵關聯 (approvals 和 versions) 以免外鍵約束失敗
        approvals = agreement_model.get_approvals_by_agreement(id)
        for a in approvals:
            agreement_model.delete_approval(id, a['user_id'])
            
        agreement_model.delete_versions_by_agreement(id)
        
        # 刪除公約主表
        agreement_model.delete(id)
        flash("公約刪除成功！", "success")
        return redirect(url_for('agreement.list_agreements'))
    except Exception as e:
        flash(f"刪除公約失敗：{e}", "danger")
        return redirect(url_for('agreement.detail_agreement', id=id))

@agreement_bp.route('/agreements/<int:id>/approve', methods=['POST'])
@login_required
@group_required
def approve_agreement(id):
    agreement = agreement_model.get_by_id(id)
    if not agreement or agreement['group_id'] != current_user.group_id:
        abort(404)

    try:
        # 取得現有同意記錄，檢查是否已同意
        approvals = agreement_model.get_approvals_by_agreement(id)
        already_approved = any(a['user_id'] == current_user.id for a in approvals)
        
        if not already_approved:
            agreement_model.create_approval({
                'agreement_id': id,
                'user_id': current_user.id
            })
            # 重新取得最新同意記錄
            approvals = agreement_model.get_approvals_by_agreement(id)

        # 檢查是否群組所有人皆已同意
        roommates = user_model.get_users_by_group(current_user.group_id)
        if len(approvals) >= len(roommates):
            agreement_model.update(id, {'status': 'active'})
            flash("所有室友皆已同意，公約正式生效！", "success")
        else:
            flash("您已同意此公約，等待其他室友確認！", "success")
            
        return redirect(url_for('agreement.detail_agreement', id=id))
    except Exception as e:
        flash(f"同意公約失敗：{e}", "danger")
        return redirect(url_for('agreement.detail_agreement', id=id))
