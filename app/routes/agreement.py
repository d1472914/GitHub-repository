from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models.agreement import Agreement
from app.models.agreement_version import AgreementVersion
from app.models.agreement_approval import AgreementApproval
from app.models import db

agreement_bp = Blueprint('agreement', __name__, url_prefix='/agreements')


@agreement_bp.route('', methods=['GET'])
@login_required
def agreement_list():
    """公約列表"""
    if not current_user.group_id:
        flash('請先加入或建立群組。', 'warning')
        return redirect(url_for('group.create_page'))

    agreements_active = Agreement.get_by_group(current_user.group_id, status='active')
    agreements_pending = Agreement.get_by_group(current_user.group_id, status='pending')
    agreements_rejected = Agreement.get_by_group(current_user.group_id, status='rejected')

    return render_template(
        'agreement/list.html',
        agreements_active=agreements_active,
        agreements_pending=agreements_pending,
        agreements_rejected=agreements_rejected
    )


@agreement_bp.route('/new', methods=['GET'])
@login_required
def new_page():
    """新增公約頁面"""
    if not current_user.group_id:
        flash('請先加入或建立群組。', 'warning')
        return redirect(url_for('group.create_page'))
    return render_template('agreement/form.html', mode='create', agreement=None)


@agreement_bp.route('', methods=['POST'])
@login_required
def create():
    """新增公約處理"""
    if not current_user.group_id:
        return abort(403)

    title = request.form.get('title')
    category = request.form.get('category')
    content = request.form.get('content')

    if not title or not category or not content:
        flash('請填寫所有必要欄位。', 'danger')
        return redirect(url_for('agreement.new_page'))

    # 建立公約（內部會自動呼叫 save_version_snapshot 建立 V1 快照）
    agreement = Agreement.create(
        group_id=current_user.group_id,
        title=title,
        category=category,
        content=content,
        created_by=current_user.id,
        commit=True
    )

    # 提案者自動表態「同意」
    AgreementApproval.cast_vote(
        agreement_id=agreement.id,
        user_id=current_user.id,
        is_approved=True,
        comment="發起新公約提案",
        commit=True
    )

    flash('公約提案已成功發起！等待全體室友投票同意。', 'success')
    return redirect(url_for('agreement.detail', id=agreement.id))


@agreement_bp.route('/<int:id>', methods=['GET'])
@login_required
def detail(id):
    """公約詳情"""
    agreement = Agreement.get_by_id(id)
    if not agreement or agreement.group_id != current_user.group_id:
        flash('找不到該公約，或您沒有權限查看。', 'danger')
        return redirect(url_for('agreement.agreement_list'))

    # 投票進度報告
    progress = AgreementApproval.get_progress(id)
    
    # 檢查當前用戶是否已經投過票
    user_vote = AgreementApproval.query.filter_by(agreement_id=id, user_id=current_user.id).first()
    
    # 取得版本歷史
    versions = AgreementVersion.get_by_agreement(id)

    # 為了在前端能直接拿 diff_report，我們為每個非 V1 的版本計算 diff
    diff_reports = {}
    for ver in versions:
        diff_reports[ver.id] = ver.get_diff_report()

    return render_template(
        'agreement/detail.html',
        agreement=agreement,
        progress=progress,
        user_vote=user_vote,
        versions=versions,
        diff_reports=diff_reports
    )


@agreement_bp.route('/<int:id>/edit', methods=['GET'])
@login_required
def edit_page(id):
    """編輯公約頁面"""
    agreement = Agreement.get_by_id(id)
    if not agreement or agreement.group_id != current_user.group_id:
        flash('找不到該公約，或您沒有權限編輯。', 'danger')
        return redirect(url_for('agreement.agreement_list'))
    return render_template('agreement/form.html', mode='edit', agreement=agreement)


@agreement_bp.route('/<int:id>/update', methods=['POST'])
@login_required
def update(id):
    """更新公約"""
    agreement = Agreement.get_by_id(id)
    if not agreement or agreement.group_id != current_user.group_id:
        return abort(403)

    title = request.form.get('title')
    category = request.form.get('category')
    content = request.form.get('content')
    change_summary = request.form.get('change_summary', '修改公約條文')

    if not title or not category or not content:
        flash('請填寫所有必要欄位。', 'danger')
        return redirect(url_for('agreement.edit_page', id=id))

    # 更新公約並退回 pending，清空舊投票
    agreement.propose_revision(
        title=title,
        content=content,
        updater_id=current_user.id,
        change_summary=change_summary,
        commit=True
    )

    # 修改提案人自己自動表態「同意」
    AgreementApproval.cast_vote(
        agreement_id=agreement.id,
        user_id=current_user.id,
        is_approved=True,
        comment=f"提議修改並同意：{change_summary}",
        commit=True
    )

    flash('公約修改提案已提交，投票記錄已重設，等待室友重新表決。', 'success')
    return redirect(url_for('agreement.detail', id=id))


@agreement_bp.route('/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    """同意/反對公約"""
    agreement = Agreement.get_by_id(id)
    if not agreement or agreement.group_id != current_user.group_id:
        return abort(403)

    decision = request.form.get('decision')  # 'approve' 或 'reject'
    comment = request.form.get('comment', '').strip()

    if decision not in ['approve', 'reject']:
        flash('無效的表決決定。', 'danger')
        return redirect(url_for('agreement.detail', id=id))

    is_approved = (decision == 'approve')
    
    if not is_approved and not comment:
        flash('投反對票時，請填寫原因/反對理由。', 'warning')
        return redirect(url_for('agreement.detail', id=id))

    # 智慧投票與自動狀態結算
    AgreementApproval.cast_vote(
        agreement_id=id,
        user_id=current_user.id,
        is_approved=is_approved,
        comment=comment if comment else ("同意此公約" if is_approved else "反對此公約"),
        commit=True
    )

    flash('投票提交成功！', 'success')
    return redirect(url_for('agreement.detail', id=id))


@agreement_bp.route('/<int:id>/versions/<int:version_id>/rollback', methods=['POST'])
@login_required
def rollback(id, version_id):
    """還原公約到指定版本"""
    agreement = Agreement.get_by_id(id)
    if not agreement or agreement.group_id != current_user.group_id:
        return abort(403)

    version = AgreementVersion.get_by_id(version_id)
    if not version or version.agreement_id != id:
        flash('找不到該歷史版本。', 'danger')
        return redirect(url_for('agreement.detail', id=id))

    # 執行還原（內容覆蓋並重置 status 為 pending，清除舊投票）
    version.rollback_agreement(operator_id=current_user.id, commit=True)

    # 執行還原的人自動同意此還原版本
    AgreementApproval.cast_vote(
        agreement_id=id,
        user_id=current_user.id,
        is_approved=True,
        comment=f"執行版本回滾，還原至 V{version.version_number}",
        commit=True
    )

    flash(f'已將公約還原至 V{version.version_number} 快照！已啟動新一輪投票表決。', 'success')
    return redirect(url_for('agreement.detail', id=id))


@agreement_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """刪除公約"""
    agreement = Agreement.get_by_id(id)
    if not agreement or agreement.group_id != current_user.group_id:
        return abort(403)

    # 限制管理員或提案人才能刪除
    if current_user.role != 'admin' and agreement.created_by != current_user.id:
        flash('只有管理員或提案人才能刪除此公約。', 'danger')
        return redirect(url_for('agreement.detail', id=id))

    agreement.delete(commit=True)
    flash('公約已成功刪除。', 'success')
    return redirect(url_for('agreement.agreement_list'))
