-- 网络规划师备考数据库 Schema
-- 创建时间: 2026-05-31
-- 更新: 2026-05-31 添加题库表

-- 每日学习内容表
CREATE TABLE IF NOT EXISTS daily_content (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL UNIQUE,          -- 日期 YYYY-MM-DD
  type TEXT NOT NULL,                 -- 类型: case/comprehensive/essay
  topic TEXT NOT NULL,                 -- 主题
  tags TEXT,                          -- 标签，逗号分隔
  knowledge TEXT NOT NULL,             -- 知识点 JSON
  framework TEXT,                     -- 答题框架 JSON (案例分析)
  essay_outline TEXT,                 -- 论文大纲 (论文类型)
  essay_template TEXT,               -- 论文模板 (论文类型)
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 学习进度表
CREATE TABLE IF NOT EXISTS learning_progress (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  task_type TEXT NOT NULL,            -- 综合知识/案例分析/论文
  status TEXT DEFAULT 'pending',      -- pending/completed
  score INTEGER,                      -- 自评分
  notes TEXT,                         -- 备注
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 薄弱点记录表
CREATE TABLE IF NOT EXISTS weak_points (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  topic TEXT NOT NULL,                -- 知识点
  category TEXT NOT NULL,             -- 分类：综合/案例/论文
  difficulty INTEGER DEFAULT 3,        -- 难度 1-5
  practice_count INTEGER DEFAULT 0,    -- 练习次数
  last_practiced TEXT,                -- 上次练习日期
  next_review TEXT,                   -- 下次复习日期
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 用户设置表
CREATE TABLE IF NOT EXISTS user_settings (
  id INTEGER PRIMARY KEY,
  exam_date TEXT DEFAULT '2026-11-14',
  daily_goal INTEGER DEFAULT 3,
  study_mode TEXT DEFAULT 'normal',
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 初始化用户设置
INSERT INTO user_settings (id, exam_date, daily_goal, study_mode) VALUES (1, '2026-11-14', 3, 'normal');

-- ===== 题库表（新增） =====

-- 真题题库表
CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL,                 -- single/multi/judge
  content TEXT NOT NULL,               -- 题目内容
  options TEXT NOT NULL,              -- 选项 JSON [A, B, C, D]
  answer TEXT NOT NULL,                -- 答案，多选用逗号分隔如 "0,2"
  explanation TEXT,                   -- 解析
  difficulty INTEGER DEFAULT 1,        -- 难度 1-3
  category TEXT NOT NULL,             -- 分类如 "2015年综合知识"
  tags TEXT,                          -- 标签如 "TCP,三次握手"
  year INTEGER,                       -- 年份
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 答题历史表
CREATE TABLE IF NOT EXISTS question_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id INTEGER NOT NULL,
  user_answer TEXT NOT NULL,           -- 用户答案
  is_correct INTEGER DEFAULT 0,        -- 0错 1对
  answered_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 错题本表
CREATE TABLE IF NOT EXISTS wrong_questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id INTEGER NOT NULL UNIQUE,
  count INTEGER DEFAULT 1,            -- 错误次数
  last_reviewed TEXT DEFAULT CURRENT_TIMESTAMP,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引加速查询
CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category);
CREATE INDEX IF NOT EXISTS idx_questions_tags ON questions(tags);
CREATE INDEX IF NOT EXISTS idx_question_history_qid ON question_history(question_id);
CREATE INDEX IF NOT EXISTS idx_wrong_questions_qid ON wrong_questions(question_id);