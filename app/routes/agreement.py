<<<<<<< HEAD
"""
公約管理路由 — 公約列表、詳情、新增、編輯、刪除、同意
Blueprint prefix: /agreements
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models import Agreement, AgreementVersion, AgreementApproval, User

agreement_bp = Blueprint('agreement', __name__, url_prefix='/agreements')

@agreement_bp.route('', methods=['GET'])
@login_required
def list_page():
    """公約列表頁面
    - 輸出：agreement/list.html
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        agreements = Agreement.get_by_group_id(group_id)
        return render_template('agreement/list.html', agreements=agreements)
    except Exception as e:
        print(f"Error loading agreements list: {e}")
        flash("載入公約列表失敗。", "error")
        return redirect(url_for('dashboard.index'))

@agreement_bp.route('/new', methods=['GET'])
@login_required
def new_page():
    """顯示新增公約表單頁面
    - 輸出：agreement/form.html
    """
    if not g.user['group_id']:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))
    return render_template('agreement/form.html', agreement=None)

@agreement_bp.route('', methods=['POST'])
@login_required
def create():
    """新增公約處理
    - 輸入：title, category, content
    - 處理：Agreement.create() → AgreementVersion.create(v1) → AgreementApproval.create() (自動同意)
    - 輸出：重導向 /agreements/<id>
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("操作無效，您尚未加入群組！", "error")
        return redirect(url_for('dashboard.index'))
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b

    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    content = request.form.get('content', '').strip()

    if not title or not category or not content:
<<<<<<< HEAD
        flash("所有欄位皆為必填！", "error")
        return render_template('agreement/form.html', agreement=None)

    try:
        # 1. 建立公約記錄 (預設 status='pending')
        agreement_id = Agreement.create({
            'group_id': group_id,
            'title': title,
            'category': category,
            'content': content,
            'status': 'pending',
            'created_by': g.user['id']
        })

        if not agreement_id:
            flash("新增公約失敗，請稍後再試。", "error")
            return render_template('agreement/form.html', agreement=None)

        # 2. 建立版本記錄 v1
        AgreementVersion.create({
            'agreement_id': agreement_id,
            'version_number': 1,
            'content_before': None,
            'content_after': content,
            'modified_by': g.user['id']
        })

        # 3. 建立提案者的自動同意記錄
        AgreementApproval.create({
            'agreement_id': agreement_id,
            'user_id': g.user['id']
        })

        # 4. 檢查是否全體群組成員都已同意 (如果群組只有提案者一人，直接生效)
        members = User.get_by_group_id(group_id)
        approvals = AgreementApproval.get_by_agreement_id(agreement_id)
        if len(approvals) >= len(members):
            Agreement.update(agreement_id, {'status': 'active'})
            flash("公約提案成功，且已自動全票通過生效！", "success")
        else:
            flash("公約提案成功！已自動記錄您的同意，待全體成員同意後生效。", "success")

        return redirect(url_for('agreement.detail_page', agreement_id=agreement_id))

    except Exception as e:
        print(f"Error creating agreement: {e}")
        flash("伺服器錯誤，公約建立失敗。", "error")
        return render_template('agreement/form.html', agreement=None)

@agreement_bp.route('/<int:agreement_id>', methods=['GET'])
@login_required
def detail_page(agreement_id):
    """公約詳情與歷史版本
    - 輸出：agreement/detail.html
    """
    try:
        agreement = Agreement.get_by_id(agreement_id)
        if not agreement or agreement['group_id'] != g.user['group_id']:
            flash("找不到該公約，或您沒有權限存取！", "error")
            return redirect(url_for('agreement.list_page'))

        # 取得歷史版本與同意情況
        versions = AgreementVersion.get_by_agreement_id(agreement_id)
        approvals = AgreementApproval.get_by_agreement_id(agreement_id)
        
        # 整理已同意名單
        approved_user_ids = [appr['user_id'] for appr in approvals]
        members = User.get_by_group_id(g.user['group_id'])
        
        has_approved = g.user['id'] in approved_user_ids

        return render_template(
            'agreement/detail.html',
            agreement=agreement,
            versions=versions,
            members=members,
            approved_user_ids=approved_user_ids,
            has_approved=has_approved
        )
    except Exception as e:
        print(f"Error getting agreement detail: {e}")
        flash("載入公約詳情失敗。", "error")
        return redirect(url_for('agreement.list_page'))

@agreement_bp.route('/<int:agreement_id>/edit', methods=['GET'])
@login_required
def edit_page(agreement_id):
    """顯示編輯公約表單頁面
    - 輸出：agreement/form.html
    """
    try:
        agreement = Agreement.get_by_id(agreement_id)
        if not agreement or agreement['group_id'] != g.user['group_id']:
            flash("找不到該公約，或您沒有編輯權限！", "error")
            return redirect(url_for('agreement.list_page'))
            
        return render_template('agreement/form.html', agreement=agreement)
    except Exception as e:
        print(f"Error loading agreement edit page: {e}")
        flash("載入編輯頁面失敗。", "error")
        return redirect(url_for('agreement.list_page'))

@agreement_bp.route('/<int:agreement_id>/update', methods=['POST'])
@login_required
def update(agreement_id):
    """更新公約 (只接受 POST)
    - 輸入：title, category, content
    - 處理：AgreementVersion.create() → Agreement.update() → 重設同意記錄 (自動同意修改者)
    - 輸出：重導向 /agreements/<id>
    """
    try:
        agreement = Agreement.get_by_id(agreement_id)
        if not agreement or agreement['group_id'] != g.user['group_id']:
            flash("公約不存在，或您沒有權限修改！", "error")
            return redirect(url_for('agreement.list_page'))

        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not category or not content:
            flash("所有欄位皆為必填！", "error")
            return render_template('agreement/form.html', agreement=agreement)

        # 1. 取得現有版本數，以決定新版本號
        versions = AgreementVersion.get_by_agreement_id(agreement_id)
        new_version_num = len(versions) + 1 if versions else 2

        # 2. 建立版本變更記錄
        AgreementVersion.create({
            'agreement_id': agreement_id,
            'version_number': new_version_num,
            'content_before': agreement['content'],
            'content_after': content,
            'modified_by': g.user['id']
        })

        # 3. 更新公約主體，狀態重設為 pending 重新表決
        Agreement.update(agreement_id, {
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
            'title': title,
            'category': category,
            'content': content,
            'status': 'pending'
        })

<<<<<<< HEAD
        # 4. 重設同意記錄 (刪除舊的，並自動加入修改者的同意)
        AgreementApproval.delete_by_agreement_id(agreement_id)
        AgreementApproval.create({
            'agreement_id': agreement_id,
            'user_id': g.user['id']
        })

        # 5. 再次檢查是否全體成員同意 (單人寢室)
        members = User.get_by_group_id(g.user['group_id'])
        if len(members) <= 1:
            Agreement.update(agreement_id, {'status': 'active'})
            flash("公約更新成功並已自動生效！", "success")
        else:
            flash("公約更新成功！內容變更已重設同意記錄，需重新由室友投票表決。", "success")

        return redirect(url_for('agreement.detail_page', agreement_id=agreement_id))

    except Exception as e:
        print(f"Error updating agreement: {e}")
        flash("更新公約失敗。", "error")
        return redirect(url_for('agreement.list_page'))

@agreement_bp.route('/<int:agreement_id>/delete', methods=['POST'])
@login_required
def delete(agreement_id):
    """刪除公約 (只接受 POST)
    - 處理：Agreement.delete()
    - 輸出：重導向 /agreements
    """
    try:
        agreement = Agreement.get_by_id(agreement_id)
        if not agreement or agreement['group_id'] != g.user['group_id']:
            flash("找不到該公約或無刪除權限！", "error")
            return redirect(url_for('agreement.list_page'))

        # 外鍵已開 PRAGMA foreign_keys = ON; 會自動聯級刪除版本與同意記錄
        success = Agreement.delete(agreement_id)
        if success:
            flash("公約已成功刪除。", "success")
        else:
            flash("刪除公約失敗。", "error")
            
        return redirect(url_for('agreement.list_page'))
    except Exception as e:
        print(f"Error deleting agreement: {e}")
        flash("刪除公約發生伺服器錯誤。", "error")
        return redirect(url_for('agreement.list_page'))

@agreement_bp.route('/<int:agreement_id>/approve', methods=['POST'])
@login_required
def approve(agreement_id):
    """同意公約 (只接受 POST)
    - 處理：AgreementApproval.create() → 檢查全體同意 → Agreement.update(status='active')
    - 輸出：重導向 /agreements/<id>
    """
    try:
        agreement = Agreement.get_by_id(agreement_id)
        if not agreement or agreement['group_id'] != g.user['group_id']:
            flash("找不到公約，或無存取權限！", "error")
            return redirect(url_for('agreement.list_page'))

        # 1. 檢查是否已同意過
        existing = AgreementApproval.check_exists(agreement_id, g.user['id'])
        if existing:
            flash("您已同意過此公約提案！", "info")
            return redirect(url_for('agreement.detail_page', agreement_id=agreement_id))

        # 2. 建立同意記錄
        AgreementApproval.create({
            'agreement_id': agreement_id,
            'user_id': g.user['id']
        })

        # 3. 檢查是否全體同意
        members = User.get_by_group_id(g.user['group_id'])
        approvals = AgreementApproval.get_by_agreement_id(agreement_id)
        
        if len(approvals) >= len(members):
            Agreement.update(agreement_id, {'status': 'active'})
            flash("您已同意！本公約全體室友皆已同意，正式生效！", "success")
        else:
            flash("您已表示同意此公約，等待其他室友同意。", "success")

        return redirect(url_for('agreement.detail_page', agreement_id=agreement_id))

    except Exception as e:
        print(f"Error approving agreement: {e}")
        flash("表示同意失敗。", "error")
        return redirect(url_for('agreement.detail_page', agreement_id=agreement_id))
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
