import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'network-planner-exam-secret-key'

# 配置
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "data", "exam.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'data')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# 确保数据目录存在
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'data', 'notes'), exist_ok=True)

db = SQLAlchemy(app)


# ==================== 数据模型 ====================

class Question(db.Model):
    """题目模型"""
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    question_type = db.Column(db.String(20), nullable=False, index=True)  # single/multi/judge/case/essay
    content = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)
    answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
    difficulty = db.Column(db.Integer, default=1)
    category = db.Column(db.String(50), index=True)
    tags = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 间隔重复字段
    ease_factor = db.Column(db.Float, default=2.5)
    interval = db.Column(db.Integer, default=0, index=True)
    repetitions = db.Column(db.Integer, default=0, index=True)
    next_review = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_review = db.Column(db.DateTime)

    # 缓存解析后的 options
    _options_cache = None

    def get_options(self):
        """获取选项（带缓存）"""
        if self._options_cache is None:
            self._options_cache = json.loads(self.options) if self.options else []
        return self._options_cache

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.question_type,
            'content': self.content,
            'options': self.get_options(),
            'answer': self.answer,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'category': self.category,
            'tags': self.tags,
            'ease_factor': self.ease_factor,
            'interval': self.interval,
            'repetitions': self.repetitions,
            'next_review': self.next_review.isoformat() if self.next_review else None
        }


class StudyRecord(db.Model):
    """学习记录模型"""
    __tablename__ = 'study_record'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), index=True)
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean, index=True)
    score = db.Column(db.Integer)
    studied_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    question = db.relationship('Question', backref='records')


class Note(db.Model):
    """知识点笔记模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== SM-2 间隔重复算法 ====================

def calculate_sm2(question, quality):
    """
    SM-2算法实现
    quality: 评分0-5 (0-完全忘记, 5-完美记住)
    """
    if quality < 3:
        # 重新学习
        question.repetitions = 0
        question.interval = 1
    else:
        if question.repetitions == 0:
            question.interval = 1
        elif question.repetitions == 1:
            question.interval = 6
        else:
            question.interval = int(question.interval * question.ease_factor)

        question.repetitions += 1

    # 更新难度因子
    question.ease_factor = max(1.3, question.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    question.last_review = datetime.utcnow()
    question.next_review = datetime.utcnow()

    return question


# ==================== 路由 ====================

@app.route('/')
def index():
    """首页/仪表盘 - 优化统计查询"""
    from sqlalchemy import func

    # 使用单次查询获取多个统计值
    stats = db.session.query(
        func.count(Question.id).label('total'),
        func.count(func.nullif(Question.next_review <= datetime.utcnow(), False)).label('due')
    ).first()

    total_questions = stats.total or 0
    due_review = stats.due or 0
    total_notes = Note.query.count()

    # 最近学习记录
    recent_records = StudyRecord.query.order_by(StudyRecord.studied_at.desc()).limit(10).all()

    return render_template('index.html',
                           total_questions=total_questions,
                           due_review=due_review,
                           total_notes=total_notes,
                           recent_records=recent_records)


@app.route('/questions')
def questions():
    """题库页面"""
    q_type = request.args.get('type', 'all')
    category = request.args.get('category', 'all')

    query = Question.query
    if q_type != 'all':
        query = query.filter(Question.question_type == q_type)
    if category != 'all':
        query = query.filter(Question.category == category)

    questions_list = query.order_by(Question.id.desc()).all()

    # 获取所有分类
    categories = db.session.query(Question.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    return render_template('questions.html',
                           questions=questions_list,
                           current_type=q_type,
                           current_category=category,
                           categories=categories)


@app.route('/question/<int:qid>')
def question_detail(qid):
    """题目详情"""
    question = Question.query.get_or_404(qid)
    return render_template('question_detail.html', question=question)


@app.route('/practice')
def practice():
    """练习模式选择"""
    return render_template('practice.html')


@app.route('/practice/single')
def practice_single():
    """单题练习"""
    qid = request.args.get('qid', type=int)
    if qid:
        question = Question.query.get_or_404(qid)
    else:
        # 随机获取一道题
        question = Question.query.order_by(db.func.random()).first()
        if not question:
            flash('题库为空，请先导入题目', 'warning')
            return redirect(url_for('questions'))

    return render_template('practice_single.html', question=question)


@app.route('/practice/submit', methods=['POST'])
def practice_submit():
    """提交答案"""
    qid = request.form.get('qid', type=int)
    user_answer = request.form.get('answer')
    score = request.form.get('score', type=int, default=3)

    question = Question.query.get_or_404(qid)

    # 判断是否正确
    is_correct = user_answer == question.answer

    # 记录学习
    record = StudyRecord(
        question_id=qid,
        user_answer=user_answer,
        is_correct=is_correct,
        score=score
    )
    db.session.add(record)

    # 更新间隔重复参数
    question = calculate_sm2(question, score)
    db.session.commit()

    return render_template('practice_result.html',
                           question=question,
                           user_answer=user_answer,
                           is_correct=is_correct)


@app.route('/practice/wrong')
def practice_wrong():
    """错题本 - 使用子查询优化"""
    # 使用子查询获取错题ID，然后一次性查询
    wrong_subquery = db.session.query(StudyRecord.question_id).filter(
        StudyRecord.is_correct == False
    ).distinct().subquery()

    questions_list = Question.query.filter(
        Question.id.in_(db.session.query(wrong_subquery))
    ).all() if db.session.query(wrong_subquery).count() > 0 else []

    return render_template('wrong_questions.html', questions=questions_list)


@app.route('/practice/review')
def practice_review():
    """复习模式 - 待复习的题目"""
    due_questions = Question.query.filter(
        Question.next_review <= datetime.utcnow()
    ).order_by(Question.next_review).all()

    return render_template('review.html', questions=due_questions)


@app.route('/exam/simulation')
def exam_simulation():
    """模拟考试 - 综合知识75题"""
    # 随机抽取75道选择题
    questions_list = Question.query.filter(
        Question.question_type.in_(['single', 'multi', 'judge'])
    ).order_by(db.func.random()).limit(75).all()

    return render_template('exam.html', questions=questions_list, exam_type='综合知识')


@app.route('/exam/submit', methods=['POST'])
def exam_submit():
    """提交试卷 - 优化批量查询"""
    answers = request.form.to_dict()
    questions_ids = [int(k) for k in answers.keys() if k.isdigit()]

    # 批量查询所有题目
    questions_dict = {q.id: q for q in Question.query.filter(Question.id.in_(questions_ids)).all()}

    results = []
    correct_count = 0

    for qid in questions_ids:
        question = questions_dict.get(qid)
        if question:
            user_ans = answers.get(str(qid), '')
            is_correct = user_ans == question.answer
            if is_correct:
                correct_count += 1
            results.append({
                'question': question,
                'user_answer': user_ans,
                'is_correct': is_correct
            })

    score = int(correct_count / len(results) * 100) if results else 0

    return render_template('exam_result.html',
                           results=results,
                           correct_count=correct_count,
                           total=len(results),
                           score=score)


@app.route('/notes')
def notes():
    """知识点列表"""
    category = request.args.get('category', 'all')
    query = Note.query
    if category != 'all':
        query = query.filter(Note.category == category)

    notes_list = query.order_by(Note.updated_at.desc()).all()

    # 获取所有分类
    categories = db.session.query(Note.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    return render_template('notes.html', notes=notes_list, categories=categories, current_category=category)


@app.route('/note/<int:nid>')
def note_detail(nid):
    """知识点详情"""
    note = Note.query.get_or_404(nid)
    return render_template('note_detail.html', note=note)


@app.route('/note/create', methods=['GET', 'POST'])
def note_create():
    """创建知识点"""
    if request.method == 'POST':
        note = Note(
            title=request.form.get('title'),
            content=request.form.get('content'),
            category=request.form.get('category'),
            tags=request.form.get('tags')
        )
        db.session.add(note)
        db.session.commit()
        flash('知识点创建成功', 'success')
        return redirect(url_for('note_detail', nid=note.id))

    return render_template('note_edit.html', note=None)


@app.route('/note/<int:nid>/edit', methods=['GET', 'POST'])
def note_edit(nid):
    """编辑知识点"""
    note = Note.query.get_or_404(nid)

    if request.method == 'POST':
        note.title = request.form.get('title')
        note.content = request.form.get('content')
        note.category = request.form.get('category')
        note.tags = request.form.get('tags')
        db.session.commit()
        flash('知识点更新成功', 'success')
        return redirect(url_for('note_detail', nid=note.id))

    return render_template('note_edit.html', note=note)


@app.route('/import', methods=['GET', 'POST'])
def import_questions():
    """导入题目"""
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.json'):
            try:
                data = json.load(file)
                imported_count = 0
                batch_size = 100

                # 批量插入
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    questions = []
                    for item in batch:
                        question = Question(
                            question_type=item.get('type', 'single'),
                            content=item.get('content', ''),
                            options=json.dumps(item.get('options', [])),
                            answer=item.get('answer', ''),
                            explanation=item.get('explanation', ''),
                            difficulty=item.get('difficulty', 1),
                            category=item.get('category', ''),
                            tags=item.get('tags', '')
                        )
                        questions.append(question)
                    db.session.bulk_save_objects(questions)
                    imported_count += len(batch)

                db.session.commit()
                flash(f'成功导入 {imported_count} 道题目', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'导入失败: {str(e)}', 'error')
        else:
            flash('请上传JSON文件', 'error')

        return redirect(url_for('import_questions'))

    return render_template('import.html')


@app.route('/export')
def export_questions():
    """导出题目"""
    questions = Question.query.all()
    data = []

    for q in questions:
        data.append({
            'type': q.question_type,
            'content': q.content,
            'options': json.loads(q.options) if q.options else [],
            'answer': q.answer,
            'explanation': q.explanation,
            'difficulty': q.difficulty,
            'category': q.category,
            'tags': q.tags
        })

    response = jsonify(data)
    response.headers['Content-Disposition'] = 'attachment; filename=questions.json'
    return response


@app.route('/stats')
def stats():
    """学习统计 - 优化查询"""
    from sqlalchemy import func, case

    # 总题目数
    total = db.session.query(func.count(Question.id)).scalar() or 0

    # 按类型统计 - 单次查询
    type_stats = db.session.query(
        Question.question_type,
        func.count(Question.id)
    ).group_by(Question.question_type).all()

    # 掌握程度 - 使用条件聚合
    mastery = db.session.query(
        func.sum(case((Question.repetitions == 0, 1), else_=0)).label('new'),
        func.sum(case((Question.repetitions > 0, Question.interval < 7, 1), else_=0)).label('learning'),
        func.sum(case((Question.interval >= 7, 1), else_=0)).label('review')
    ).first()

    mastery_stats = {
        'new': mastery.new or 0,
        'learning': mastery.learning or 0,
        'review': mastery.review or 0
    }

    # 正确率 - 优化为单次查询
    stats_result = db.session.query(
        func.count(StudyRecord.id).label('total'),
        func.sum(case((StudyRecord.is_correct == True, 1), else_=0)).label('correct')
    ).first()

    total_records = stats_result.total or 0
    correct = stats_result.correct or 0
    correct_rate = int(correct / total_records * 100) if total_records > 0 else 0

    return render_template('stats.html',
                           total=total,
                           type_stats=type_stats,
                           mastery_stats=mastery_stats,
                           correct_rate=correct_rate,
                           total_records=total_records)


@app.route('/db')
def db_status():
    """数据库状态"""
    import os
    from sqlalchemy import text

    db_path = os.path.join(BASE_DIR, 'data', 'exam.db')

    # 文件大小
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    db_size_mb = round(db_size / (1024 * 1024), 2)

    # 表统计
    tables = []
    table_names = ['question', 'study_record', 'note']

    for table_name in table_names:
        try:
            result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()

            # 获取表大小估计
            result = db.session.execute(text(f"SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}'"))
            index_count = result.scalar()

            tables.append({
                'name': table_name,
                'rows': count,
                'indexes': index_count
            })
        except Exception as e:
            tables.append({
                'name': table_name,
                'rows': 0,
                'error': str(e)
            })

    # 题目分类统计
    category_stats = db.session.query(
        Question.category,
        db.func.count(Question.id)
    ).order_by(db.func.count(Question.id).desc()).limit(20).all()

    # 学习记录统计
    study_stats = {
        'total_records': StudyRecord.query.count(),
        'correct_count': StudyRecord.query.filter(StudyRecord.is_correct == True).count(),
        'today_records': StudyRecord.query.filter(
            db.func.date(StudyRecord.studied_at) == db.func.date('now')
        ).count()
    }

    return render_template('db_status.html',
                           db_path=db_path,
                           db_size_mb=db_size_mb,
                           tables=tables,
                           category_stats=category_stats,
                           study_stats=study_stats)


@app.route('/db/query', methods=['GET', 'POST'])
def db_query():
    """SQL查询功能（仅支持SELECT）"""
    from sqlalchemy import text

    result_data = None
    columns = None
    error = None
    sql = ''

    if request.method == 'POST':
        sql = request.form.get('sql', '').strip()

        # 安全检查：只允许 SELECT 查询
        if not sql:
            error = '请输入SQL语句'
        elif not sql.upper().startswith('SELECT'):
            error = '只允许执行 SELECT 查询语句'
        else:
            try:
                result = db.session.execute(text(sql))
                if result.returns_rows:
                    columns = result.keys()
                    result_data = result.fetchall()
                else:
                    error = '查询无返回结果'
            except Exception as e:
                error = f'查询错误: {str(e)}'

    return render_template('db_query.html', sql=sql, result=result_data, columns=columns, error=error)


@app.route('/db/optimize', methods=['POST'])
def db_optimize():
    """数据库性能优化"""
    try:
        # VACUUM: 重建数据库文件，回收空间
        db.session.execute(text("VACUUM"))
        db.session.commit()

        # ANALYZE: 更新表统计信息，优化查询计划
        db.session.execute(text("ANALYZE"))
        db.session.commit()

        flash('数据库优化完成（VACUUM + ANALYZE）', 'success')
    except Exception as e:
        flash(f'优化失败: {str(e)}', 'error')

    return redirect(url_for('db_status'))


# ==================== 初始化 ====================

def create_indexes():
    """创建数据库索引以提升查询性能"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_question_type ON question(question_type)",
        "CREATE INDEX IF NOT EXISTS idx_question_category ON question(category)",
        "CREATE INDEX IF NOT EXISTS idx_question_next_review ON question(next_review)",
        "CREATE INDEX IF NOT EXISTS idx_question_interval ON question(interval)",
        "CREATE INDEX IF NOT EXISTS idx_question_repetitions ON question(repetitions)",
        "CREATE INDEX IF NOT EXISTS idx_study_record_question_id ON study_record(question_id)",
        "CREATE INDEX IF NOT EXISTS idx_study_record_is_correct ON study_record(is_correct)",
        "CREATE INDEX IF NOT EXISTS idx_study_record_studied_at ON study_record(studied_at)",
    ]
    with app.app_context():
        for idx_sql in indexes:
            try:
                db.session.execute(text(idx_sql))
            except Exception as e:
                print(f"索引创建跳过: {e}")
        db.session.commit()
        print("数据库索引创建完成")


def init_db():
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        create_indexes()
        print("数据库初始化完成")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)